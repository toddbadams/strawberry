import pandas as pd
from abc import ABC, abstractmethod

from strawberry.config.config_loader import ConfigLoader
from strawberry.config.dtos import ValTableConfig
from strawberry.dimensions.dim_stocks import DimStocks
from strawberry.repository.storage import ParquetStorage
from strawberry.logging.logger_factory import LoggerFactory


class BaseFactProcessor(ABC):
    def __init__(self, config_loader_fn):
        self.logger = LoggerFactory().create_logger(self.__class__.__name__)
        self.config = ConfigLoader()
        self.env = self.config.environment()
        self.cfg = config_loader_fn()

        self.dim_store = ParquetStorage(self.env.dim_stocks_folder)
        self.val_store = ParquetStorage(self.env.validated_folder)

        self.dim_stock_srv = DimStocks()
        self.tickers = sorted(self.dim_stock_srv.tickers_dimensioned())

    def fact_ticker(self, ticker: str) -> bool:
        df = self.val_store.read_df(self.cfg.val_table_name, ticker)
        df = df[self.cfg.data_col_names()]

        if not df.empty:
            df["symbol"] = ticker
            self.dim_store.write_df(df, self.cfg.fact_table_name, ["symbol"])
            self.logger.info(f"FACT {self.cfg.fact_table_name} created for {ticker}.")
        else:
            self.logger.warning(
                f"Table {self.cfg.val_table_name} is empty for {ticker}."
            )
        return True

    def main(self):
        for ticker in self.tickers:
            self.fact_ticker(ticker)


class FactQtrIncomeProcessor(BaseFactProcessor):
    def __init__(self):
        super().__init__(ConfigLoader().fact_qtr_income)


class FactQtrBalanceProcessor(BaseFactProcessor):
    def __init__(self):
        super().__init__(ConfigLoader().fact_qtr_balance)


if __name__ == "__main__":
    processor = FactQtrIncomeProcessor()
    processor.main()
    processor = FactQtrBalanceProcessor()
    processor.main()
