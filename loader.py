
import logging
import os
import sys
#from prefect import flow, task, get_run_logger
import csv
from src.alpha_vantage.price_injestor import PriceInjestor
from src.consolidators.value_consolidator import ValueConsolidator
from src.alpha_vantage.injestor import Injestor
from src.alpha_vantage.alpha_vantage_api import AlphaVantageAPI
from src.parquet.parquet_storage import ParquetStorage
from src.logger_factory import LoggerFactory
from src.ticker_loader import TickerLoader
from src.consolidators.dividend_consolidator import DividendConsolidator
from src.consolidators.earnings_consolidator import EarningsConsolidator
from src.consolidators.income_statement_consolidator import IncomeStatementConsolidator
from src.consolidators.insiders_consolidator import InsiderConsolidator
from src.consolidators.stock_price_consolidator import StockPriceConsolidator
from src.consolidators.balance_sheet_consolidator import BalanceSheetConsolidator
from src.consolidators.cashflow_consolidator import CashflowConsolidator
from src.parquet.parquet_storage import ParquetStorage

class Loader:
    def __init__(self):
        api_key = os.getenv("ALPHA_VANTAGE_API_KEY")
        url =  os.getenv("ALPHA_VANTAGE_URL")
        self.data_path = os.getenv("OUTPUT_PATH", "data/")
        self.api = AlphaVantageAPI(api_key, url)
        self.storage = ParquetStorage(self.data_path)
        #self.logger = get_run_logger() 
        factory = LoggerFactory()
        self.logger = factory.create_logger(__name__)

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

    #@task
    def consolidate_ticker(self, ticker: str) -> bool:
        self.logger.info(f"Consolidating ticker: {ticker}")
        table_name = 'CONSOLIDATED'

        # if the consolidated table exists, overwrite it
        if self.storage.exists(table_name, ticker):
             if not self.storage.remove_partition_by_symbol(table_name, ticker):
                 return False
        
        df = BalanceSheetConsolidator(self.storage, self.logger).consolidate('BALANCE_SHEET', ticker)
        df = CashflowConsolidator(self.storage, self.logger).consolidate(df, 'CASH_FLOW', ticker)
        df = StockPriceConsolidator(self.storage, self.logger).consolidate(df, 'TIME_SERIES_MONTHLY_ADJUSTED', ticker)
        df = DividendConsolidator(self.storage, self.logger).consolidate(df, 'DIVIDENDS', ticker)
        df = EarningsConsolidator(self.storage, self.logger).consolidate(df, 'EARNINGS', ticker)
        df = IncomeStatementConsolidator(self.storage, self.logger).consolidate(df, 'INCOME_STATEMENT', ticker)
        df = InsiderConsolidator(self.storage, self.logger).consolidate(df, 'INSIDER_TRANSACTIONS', ticker)
        df = ValueConsolidator(self.logger).consolidate(df)

        # tidy 
        df["symbol"] = ticker
        df.sort_values('qtr_end_date')
        df.reset_index()
        self.storage .write_df(df, table_name, partition_cols=["symbol"], index=False)
        ## let's write a CSV file for ease of validating
        path = f"{self.data_path}/{table_name}/symbol={ticker}/{table_name}_{ticker}.csv"
        df.to_csv(path, index=False, header=True, encoding='utf-8')
        return True

    #@flow
    def run(self):
        tickers = TickerLoader(self.data_path, self.logger).run()
        for ticker in tickers:
            if not self.load_ticker(ticker):
                self.logger.warning(f"Failed to load ticker: {ticker}. Stopping further processing.")
                break
            self.consolidate_ticker(ticker)
Loader().run()