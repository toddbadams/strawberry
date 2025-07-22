from pathlib import Path

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

    def acquire(self):
        # Build ingestion steps dynamically from JSON config
        steps = [(self._get_injestor(cfg.injestor), cfg.name, cfg.attribute) for cfg in self.acq_cfg.tables]

        for ticker in self.tickers:
            self.logger.info(f"Acquiring {ticker}")
            for inj, name, attr in steps:
                try:
                    if not self._ingest_step(inj, name, attr, ticker):
                        break
                except APILimitReachedError:
                    return


if __name__ == "__main__":
    acquirer = Acquire()
    acquirer.acquire()

