import numpy as np
from sqlalchemy import true

from strawberry.config.config_loader import ConfigLoader
from strawberry.config.dtos import AcquisitionTableConfig
from strawberry.data_utilities.series_conversion import SeriesConversion
from strawberry.repository.storage import ParquetStorage
from strawberry.logging.logger_factory import LoggerFactory


class Validate:

    def __init__(self):
        self.logger = LoggerFactory().create_logger(__name__)
        self.config = ConfigLoader()
        self.env = self.config.environment()
        self.tickers = self.config.tickers()
        self.acq_cfg = self.config.acquisition()
        self.series = SeriesConversion()

        self.acq_store = ParquetStorage(self.env.acquisition_folder)
        self.val_store = ParquetStorage(self.env.validated_folder)

    def tickers_validated(self, tickers: list[str]) -> list[str]:
        """
        Return a set of tickers from the inputed tickers that have been validated
        """
        tables = self.acq_cfg.table_names()
        validated_tickers = [
            ticker
            for ticker in self.tickers
            if self.val_store.all_exist(tables, ticker)
        ]
        self.logger.info(f"{len(validated_tickers)} tickers validated.")
        return validated_tickers

    def tickers_not_validated(self, tickers: list[str]) -> list[str]:
        """
        Return a set of tickers from the inputed tickers that have not yet been acquired
        """
        tables = self.acq_cfg.table_names()
        acquired_tickers = [
            ticker
            for ticker in self.tickers
            if self.acq_store.all_exist(tables, ticker)
        ]
        validated_tickers = [
            ticker
            for ticker in self.tickers
            if self.val_store.all_exist(tables, ticker)
        ]

        # Now compute the difference, preserving acquisition order:
        validated_set = set(validated_tickers)
        not_validated = [t for t in acquired_tickers if t not in validated_set]
        self.logger.info(f"{len(not_validated)} tickers not validated.")
        return not_validated

    def validate_table(
        self, log_prefix: str, table: AcquisitionTableConfig, ticker: str
    ) -> bool:
        df = self.acq_store.read_df(table.name, ticker)
        for col in table.columns:
            if col.name not in df:
                self.logger.warning(f"{log_prefix} {col.name} does not exist.")
                return False
            df[col.name] = self.series.validate_column(log_prefix, df[col.name], col)

        # add a symbol column and store in validation directory
        df["symbol"] = ticker
        self.val_store.write_df(df, table.name, ["symbol"])
        self.logger.info(f"{log_prefix} validated")
        return true

    def validate(self):
        for ticker in self.tickers:
            self.validate_ticker(ticker)

    def validate_ticker(self, ticker: str):
        for table in self.acq_cfg.tables:
            log_prefix = f"{ticker} | {table.name} | "
            try:
                # if NOT exists as an acquired table, skip
                if not self.acq_store.exists(table.name, ticker):
                    self.logger.info(f"{log_prefix} not acquired, skipping")
                    continue

                # if exists as a validated table, skip
                if self.val_store.exists(table.name, ticker):
                    self.logger.info(f"{log_prefix} alreaded validated, skipping")
                    continue

                # validate the table
                if self.validate_table(log_prefix, table, ticker):
                    self.logger.info(f"{log_prefix} successfully validated")
                else:
                    self.logger.warning(f"{log_prefix} failed to validate")

            except (TypeError, ValueError) as e:
                exceptions = np.append(exceptions, [table.name, ticker, str(e)])
                self.logger.warning(f"{log_prefix} {str(e)}")
                return False

        return True


if __name__ == "__main__":
    validator = Validate()
    validator.validate()
