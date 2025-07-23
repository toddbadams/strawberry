from pathlib import Path

from strawberry.config.config_loader import ConfigLoader
from strawberry.repository.storage import ParquetStorage
from strawberry.logging.logger_factory import LoggerFactory

from .alpha_vantage_api import APILimitReachedError, AlphaVantageAPI, DataNotFoundError
from .injestor import Injestor, PriceInjestor

class Acquire:

    def __init__(self):
        self.logger = LoggerFactory().create_logger(__name__)
        self.config = ConfigLoader()
        self.env = self.config.environment()
        self.tickers = self.config.tickers()
        self.acq_cfg = self.config.acquisition() 

        self.api = AlphaVantageAPI(self.env.alpha_vantage_api_key, self.env.alpha_vantage_url)
        self.storage = ParquetStorage(self.env.acquisition_folder)
        self.injestor_map = {
            'Injestor': Injestor,
            'PriceInjestor': PriceInjestor,
        }
        
        # Build ingestion steps dynamically from JSON config
        self.steps = [(self._get_injestor(cfg.injestor), cfg.name, cfg.attribute) for cfg in self.acq_cfg.tables]

    def _get_injestor(self, injestor_name: str):
        try:
            return self.injestor_map[injestor_name](self.api)
        except KeyError:
            raise ValueError(f"Unknown injestor '{injestor_name}' in acquisition config")
        
    def _ingest_step(self, injestor, table_name, attr, ticker) -> bool:
        log_prefix = f"{ticker} | {table_name} | "

        if self.storage.exists(table_name, ticker):
            self.logger.info(f"{log_prefix} already exists")
            return True

        try:
            df = injestor.injest(table_name, attr, ticker)
            self.storage.write_df(df, table_name, ["symbol"], index=False)
            self.logger.info(f"{log_prefix} acquired")
            return True

        except DataNotFoundError as e:
            self.logger.warning(f"{log_prefix}{e}")
            return False

        except APILimitReachedError as e:
            self.logger.warning(f"{log_prefix}{e}")
            raise

    def acquire_ticker(self, ticker: str) -> Path:
        self.logger.info(f"Acquiring {ticker}")
        for inj, name, attr in self.steps:
            if not self._ingest_step(inj, name, attr, ticker):
                break
        return self.env.acquisition_folder

    def tickers_not_acquired(self, tickers: list[str]) -> list[str]:
        """
            Return a set of tickers from the inputed tickers that have not yet been acquired
        """
        tables = self.acq_cfg.table_names()
        not_acquired = []
        for t in tickers:
            if not self.storage.all_exist(tables, t):
                not_acquired.append(t)

        return not_acquired

    def main(self):
        for ticker in self.tickers:
            self.acquire_ticker(ticker)


if __name__ == "__main__":
    acquirer = Acquire()
    acquirer.main()

