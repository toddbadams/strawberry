from datetime import datetime
from pathlib import Path
import pandas as pd
import logging

from strawberry.config.config_loader import ConfigLoader
from strawberry.repository.storage import ParquetStorage
from strawberry.logging.logger_factory import LoggerFactory


class Validate:
    """
    Validates acquired stock data, recording missing records and columns.
    """
    def __init__(self):
        logger = LoggerFactory(e='DEV', default_level=logging.WARNING).create_logger(__name__)
        loader = ConfigLoader(logger)
        env = loader.environment()

        self.logger = logger
        self.env = env
        self.read_storage = ParquetStorage(env.acquisition_folder) # we read from acquisition folder
        self.write_storage = ParquetStorage(env.validated_folder) # we write to the validation folder
        self.tickers = loader.load_tickers()
        self.acq_cfg = loader.load_acquisition_config()

    def _get_clean_tickers(self, records: pd.DataFrame) -> list[str]:
        clean = []
        for ticker, grp in records.groupby("ticker"):
            no_mq = grp["missing_quarters"].eq(0).all()
            no_mc = grp["missing_columns"].apply(lambda cols: cols == 0).all()
            if no_mc: # for later  no_mq and 
                clean.append(ticker)
        return clean

    def _count_missing_quarters(self, log_prefix: str,  df: pd.DataFrame, date_col: str) -> int:
        if date_col is None:
            return 0
        
        if date_col not in df:
            self.logger.warning(f"{log_prefix} | {date_col} column is missing")
            return None

        # Ensure datetime
        series = self._to_datetime(log_prefix, df[date_col]) 
        if series is None:
            return None
        # Compute full quarter range
        oldest = series.min()
        newest = series.max()
        all_quarters = pd.period_range(start=oldest, end=newest, freq="Q")
        expected = set(all_quarters.end_time.normalize())
        actual = set(series.dt.normalize())
        return len(expected - actual)
    
    def _count_missing_columns(self, df: pd.DataFrame, expected_cols: set[str]) -> int:
        actual_columns = set(df.columns)
        missing = expected_cols - actual_columns
        return len(missing)

    def _get_oldest_record(self, log_prefix: str, df: pd.DataFrame, date_col: str) -> datetime:
        if date_col is None:
            return 0
        
        if date_col not in df:
            self.logger.warning(f"{log_prefix} | {date_col} column is missing")
            return None

        series = self._to_datetime(log_prefix, df[date_col])
        return series.min() if series is not None else  None


    def _get_newest_record(self, log_prefix: str,  df: pd.DataFrame, date_col: str) -> datetime:
        if date_col is None:
            return 0
        
        if date_col not in df:
            self.logger.warning(f"{log_prefix} | {date_col} column is missing")
            return None
        series = self._to_datetime(log_prefix, df[date_col])
        return series.max() if series is not None else  None

    
    def _to_datetime(self, log_prefix: str, series: pd.Series) -> datetime:
        try:
            # remove any HTML‑like tag <…>
            clean = series.str.replace(r'<[^>]+>', '', regex=True)  
            clean = clean.str.replace('\n', '', regex=False)  
            series = pd.to_datetime(clean)
            return series
        except (TypeError, ValueError) as e:
            self.logger.warning(f"{log_prefix} {e}")
            return None

    def validate(self):
        records = []

        for cfg in self.acq_cfg:
            for ticker in self.tickers:
                log_prefix = f"{ticker} | {cfg.name} | "
                # skip any tickers in the list that have not been acquired
                if not self.read_storage.exists(cfg.name, ticker):
                    self.logger.info(f"{log_prefix} not yet acquired")
                    continue

                # read the table and append a validation record
                self.logger.info(f"{log_prefix} validating")
                df = self.read_storage.read_df(cfg.name, ticker)
                records.append({
                    "table_name": cfg.name,
                    "ticker": ticker,
                    "last_update": self.read_storage.last_update(cfg.name, ticker),
                    "oldest_record": self._get_oldest_record( log_prefix,df, cfg.date_column),
                    "newest_record": self._get_newest_record( log_prefix,df, cfg.date_column),
                    "missing_quarters": self._count_missing_quarters(log_prefix, df, cfg.date_column),
                    "missing_columns": self._count_missing_columns(df, set(cfg.columns)),
                })

        # Write validation records and clean ticker list
        df_records = pd.DataFrame(records)
        self.write_storage.write_df(df_records, "acquisition/VALIDATION", index=False)

        clean = self._get_clean_tickers(df_records)
        self.write_storage.write_df(pd.DataFrame(clean), "acquisition/TICKERS_TO_TRANSFORM", index=False)


if __name__ == "__main__":
    validator = Validate()
    validator.validate()
