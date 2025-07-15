
import pandas as pd
#from prefect import flow, task, get_run_logger

from src.consolidators.column_calc import ColumnCalculator
from src.consolidators.consolidator import Consolidator
from src.config.config_loader import ConfigLoader
from src.alpha_vantage.price_injestor import PriceInjestor
from src.alpha_vantage.injestor import Injestor
from src.alpha_vantage.alpha_vantage_api import AlphaVantageAPI
from src.parquet.parquet_storage import ParquetStorage
from src.logger_factory import LoggerFactory
from src.ticker_loader import TickerLoader
from src.parquet.parquet_storage import ParquetStorage

class Loader:
    def __init__(self):
        self.logger = LoggerFactory().create_logger(__name__)
        self.config_loader = ConfigLoader(self.logger)
        self.env = self.config_loader.environment()
        self.api = AlphaVantageAPI(self.env.alpha_vantage_api_key, self.env.alpha_vantage_url)
        self.storage = ParquetStorage(self.env.output_path)
        #self.logger = get_run_logger() 

    #@task
    def load_ticker(self, ticker: str) -> bool:
        self.logger.info(f"extracting ticker: {ticker}")

        i = Injestor(self.api, self.storage, self.logger)
        if not i.injest('DIVIDENDS', 'data', ticker):
            return False
        if not i.injest('INSIDER_TRANSACTIONS', 'data', ticker):
            return False
        if not i.injest('EARNINGS', 'quarterlyEarnings', ticker):
            return False
        if not i.injest('CASH_FLOW', 'quarterlyReports', ticker):
            return False
        if not i.injest('BALANCE_SHEET', 'quarterlyReports', ticker):
            return False
        if not i.injest('INCOME_STATEMENT', 'quarterlyReports', ticker):
            return False
        if not i.injest('OVERVIEW', None, ticker):
            return False
        p = PriceInjestor(self.api, self.storage, self.logger)
        if not p.injest('TIME_SERIES_MONTHLY_ADJUSTED', 'Monthly Adjusted Time Series', ticker):
            return False
        
        return True

    def consolidate_tickers(self, ticker: str) -> bool:
        self.logger.info(f"Consolidating ticker: {ticker}")
        table_name = 'CONSOLIDATED'
        
        tables = self.config_loader.load_table_consolidation_config()
        df = pd.DataFrame()
        consolidator = Consolidator(self.storage, self.logger)
        for table in tables:
            df = consolidator.run(df, table, ticker)

        # run colum level calculations to enrich the consolidated dataset
        df = ColumnCalculator(self.logger).run(df, ticker)

        # tidy 
        df["symbol"] = ticker
        df.sort_values('qtr_end_date')
        df.reset_index()
        self.storage .write_df(df, table_name, partition_cols=["symbol"], index=False)
        return True

    #@flow
    def run(self):
        tickers = TickerLoader(self.env.output_path, self.logger).run()
        for ticker in tickers:
            if not self.load_ticker(ticker):
                self.logger.warning(f"Failed to load ticker: {ticker}. Stopping further processing.")
                break
            self.consolidate_tickers(ticker)
Loader().run()