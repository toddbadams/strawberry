from datetime import datetime
from pathlib import Path
import pandas as pd

from strawberry.config.config_loader import ConfigLoader
from strawberry.repository.storage import ParquetStorage
from strawberry.logging.logger_factory import LoggerFactory

from .alpha_vantage_api import AlphaVantageAPI
from .injestor import (
    Injestor,
    PriceInjestor,
    DataNotFoundError,
    APILimitReachedError,
)

class AcquireStocks:
    def __init__(self):
        logger = LoggerFactory().create_logger(__name__)
        loader = ConfigLoader(logger)
        env    = loader.environment()

        self.logger   = logger
        self.env      = env
        self.api      = AlphaVantageAPI(env.alpha_vantage_api_key, env.alpha_vantage_url)
        self.storage  = ParquetStorage(env.output_path)
        self.tickers  = loader.load_tickers()
        self.acq_cfg  = loader.load_acquisition_config()

    def _ingest_step(self, injestor, table_name, attr, ticker) -> bool:
        path   = self.env.acquisition_path / Path(table_name)
        prefix = f"{ticker} | {table_name} | "

        if self.storage.exists(path, ticker):
            self.logger.info(f"{prefix} already exists")
            return True

        try:
            df = injestor.injest(table_name, attr, ticker)
            self.storage.write_df(df, path, ["symbol"], index=False)
            return True

        except DataNotFoundError as e:
            self.logger.warning(f"{prefix} | {e}")
            return False   # skip to next table

        except APILimitReachedError as e:
            self.logger.warning(f"{prefix} | {e}")
            raise         # abort entire acquisition

    def acquire(self):
        steps = ([(Injestor(self.api), t.name, t.attribute) for t in self.acq_cfg]
            + [(PriceInjestor(self.api), "TIME_SERIES_MONTHLY_ADJUSTED", "Monthly Adjusted Time Series")])

        for ticker in self.tickers:
            self.logger.info(f"Acquiring {ticker}")
            for inj, name, attr in steps:
                try:
                    if not self._ingest_step(inj, name, attr, ticker):
                        break
                except APILimitReachedError:
                    return  # hit rate limit → stop


    def get_clean_tickers(self, records: pd.DataFrame) -> list[str]:
        """
        Given the validation DataFrame with columns
        ['table_name','ticker','missing_quarters','missing_columns',…],
        return a list of tickers for which, *across every table*:
          • missing_quarters == 0
          • missing_columns == []
        """
        clean = []
        # group by ticker and apply both conditions
        for ticker, grp in records.groupby("ticker"):
            no_mq = grp["missing_quarters"].eq(0).all()
            no_mc = grp["missing_columns"].apply(lambda cols: len(cols) == 0).all()
            if no_mq and no_mc:
                clean.append(ticker)
        return clean

    def validate(self):
        records = []

        for cfg in self.acq_cfg:
            table = cfg.name
            expected_cols = set(cfg.columns)
            table_path = self.env.acquisition_path / Path(table)

            for ticker in self.tickers:
                # --- did we even ingest this ticker/table? ---
                if not self.storage.exists(table_path, ticker):
                    self.logger.warning(f"No data for {ticker} in {table}")
                    records.append({
                        "table_name": table,
                        "ticker": ticker,
                        "last_update": None,
                        "oldest_record": None,
                        "newest_record": None,
                        "missing_quarters": None,
                        "missing_columns": list(expected_cols),
                    })
                    continue

                # --- read the parquet back into a DataFrame ---
                df = self.storage.read_df(table_path, ticker)

                # --- figure out the last‐modified timestamp on disk ---
                # look for either a single .parquet or partitioned dataset
                parquet_files = []
                single = "data" / table_path / f"{ticker}.parquet"
                if single.exists():
                    parquet_files = [single]
                else:
                    part_dir = "data" / table_path / f"symbol={ticker}"
                    parquet_files = list(part_dir.glob("*.parquet"))

                latest_mtime = max(f.stat().st_mtime for f in parquet_files)
                last_update = datetime.fromtimestamp(latest_mtime)

                # --- parse fiscalDateEnding and find min/max + missing quarters ---
                if "fiscalDateEnding" in df.columns:
                    df["fiscalDateEnding"] = pd.to_datetime(df["fiscalDateEnding"])
                    oldest = df["fiscalDateEnding"].min()
                    newest = df["fiscalDateEnding"].max()

                    # build all expected quarter‐ends between oldest→newest
                    all_quarters = pd.period_range(start=oldest, end=newest, freq="Q")
                    expected_dates = set(all_quarters.end_time.normalize())
                    actual_dates = set(df["fiscalDateEnding"].dt.normalize())
                    missing_quarters = len(expected_dates - actual_dates)
                else:
                    oldest = newest = None
                    missing_quarters = None

                # --- check for any missing columns ---
                actual_cols = set(df.columns)
                missing_cols = sorted(expected_cols - actual_cols)

                records.append({
                    "table_name": table,
                    "ticker": ticker,
                    "last_update": last_update,
                    "oldest_record": oldest,
                    "newest_record": newest,
                    "missing_quarters": missing_quarters,
                    "missing_columns": missing_cols,
                })
        self.storage.write_df(pd.DataFrame(records), "acquisition/VALIDATION", index=False)

        tkrs = self.get_clean_tickers(pd.DataFrame(records))
        self.storage.write_df(pd.DataFrame(tkrs), "acquisition/TICKERS_TO_TRANSFORM", index=False)




if __name__ == "__main__":
    a = AcquireStocks()
    #a.acquire()
    a.validate()
