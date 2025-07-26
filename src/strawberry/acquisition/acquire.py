import pandas as pd
from strawberry.config.config_loader import ConfigLoader
from strawberry.repository.storage import ParquetStorage
from strawberry.logging.logger_factory import LoggerFactory
from strawberry.acquisition.alpha_vantage_api import AlphaVantageAPI
from strawberry.acquisition.injestor import Injestor, PriceInjestor


class Acquire:

    def __init__(self):
        self.logger = LoggerFactory().create_logger(__name__)
        self.config = ConfigLoader()
        self.env = self.config.environment()
        self.tickers = self.config.tickers()
        self.acq_cfg = self.config.acquisition()

        self.api = AlphaVantageAPI(
            self.env.alpha_vantage_api_key, self.env.alpha_vantage_url
        )
        self.storage = ParquetStorage(self.env.acquisition_folder)
        self.injestor_map = {
            "Injestor": Injestor,
            "PriceInjestor": PriceInjestor,
        }

        # Build ingestion steps dynamically from JSON config
        self.steps = [
            (self._get_injestor(cfg.injestor), cfg.name, cfg.attribute)
            for cfg in self.acq_cfg.tables
        ]

    def tickers_acquired(self, tickers: list[str]) -> list[str]:
        """
        Return a set of tickers from the inputed tickers that have been acquired
        """
        tables = self.acq_cfg.table_names()
        acq_tickers = []
        for t in tickers:
            if self.storage.all_exist(tables, t):
                acq_tickers.append(t)

        self.logger.info(f"{len(acq_tickers)} tickers aquired.")
        return sorted(acq_tickers)

    def tickers_not_acquired(self, tickers: list[str]) -> list[str]:
        """
        Return a set of tickers from the inputed tickers that have not yet been acquired
        """
        tables = self.acq_cfg.table_names()
        not_acquired = []
        for t in tickers:
            if not self.storage.all_exist(tables, t):
                not_acquired.append(t)

        self.logger.info(f"{len(not_acquired)} tickers not aquired.")
        return not_acquired

    def _get_injestor(self, injestor_name: str):
        try:
            return self.injestor_map[injestor_name](self.api)
        except KeyError:
            raise ValueError(
                f"Unknown injestor '{injestor_name}' in acquisition config"
            )

    def _ingest_step(self, injestor, table_name, attr, ticker) -> bool:
        log_prefix = f"{ticker} | {table_name} | "

        if self.storage.exists(table_name, ticker):
            self.logger.info(f"{log_prefix} already exists")
            # to do: merge the request with existing data
            return True

        df: pd.DataFrame = injestor.injest(table_name, attr, ticker)

        # if not data, then return a False to indicate did not complete
        if df.empty:
            return False

        self.storage.write_df(df, table_name, ["symbol"], index=False)
        self.logger.info(f"{log_prefix} acquired")
        return True

    def acquire_ticker(self, ticker: str) -> bool:
        self.logger.info(f"Acquiring {ticker}")
        for inj, name, attr in self.steps:
            if not self._ingest_step(inj, name, attr, ticker):
                # tables did not load, issue logged
                self.logger.warning(f"Failed to acquire {ticker}")
                return False

        self.logger.info(f"Successfully acquired {ticker}")
        return True

    def main(self):
        for ticker in self.tickers_not_acquired(self.tickers):
            if not self.acquire_ticker(ticker):
                return


if __name__ == "__main__":
    acquirer = Acquire()
    acquirer.main()
