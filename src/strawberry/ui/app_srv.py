# services.py (new file)
from pathlib import Path

import pandas as pd
from strawberry.config.config_loader import ConfigLoader
from strawberry.repository.storage import ParquetStorage
from strawberry.acquisition.acquire import Acquire
from strawberry.validation.validate import Validate
from strawberry.dimensions.dim_stocks import DimStocks
from strawberry.logging.logger_factory import LoggerFactory


class AppServices:
    def __init__(self, caller_name: str):
        self.logger = LoggerFactory().create_logger(caller_name)
        self.logger.info(f"Initializing Service")

        # Load configuration and environment
        self.config = ConfigLoader()
        self.env = self.config.environment()
        self.all_tickers = self.config.tickers()
        self.acq_tables = self.config.acquisition().table_names()
        self.dim_stock_cfg = self.config.dim_stock()
        self.fact_qtr_income_config = self.config.fact_qtr_income()
        self.fact_qtr_balance_config = self.config.fact_qtr_balance()
        self.logger.info("Configuration initialized")

        # Storage backends
        self.acq_store = ParquetStorage(Path(self.env.acquisition_folder))
        self.val_store = ParquetStorage(Path(self.env.validated_folder))
        self.dim_store = ParquetStorage(Path(self.env.dim_stocks_folder))
        self.dim_stocks_df = self.dim_store.read_df("DIM_STOCKS")
        self.logger.info("Storage repositories initialized")

        # Services
        self.acq_srv = Acquire()
        self.acq_tickers = self.acq_srv.tickers_acquired(self.all_tickers)
        self.val_srv = Validate()
        self.val_tickers = self.val_srv.tickers_validated(self.all_tickers)
        self.dim_stock_srv = DimStocks()
        self.dim_stock_tickers = sorted(self.dim_stock_srv.tickers_dimensioned())
        self.logger.info("Domain Services initialized")

        # Tables
        self.table_loader = self.config.acquisition()
        self.tables = self.table_loader.table_names()

    def filter_dim_stocks_by_ticker(self, ticker) -> pd.DataFrame:
        df = (
            self.dim_stocks_df[self.dim_stocks_df["symbol"] == ticker]
            if self.dim_stocks_df is not None
            else None
        )
        return df if df is not None and not df.empty else None

    def stock_header(self, stock) -> str:
        return f"{stock['name']} ({stock['exchange']}: {stock['symbol']} {stock['currency']})"
