
import logging
import os
import sys
from prefect import flow, task, get_run_logger
import csv
from src.alpha_vantage.injestor import Injestor
from src.alpha_vantage.alpha_vantage_api import AlphaVantageAPI
from src.parquet.parquet_storage import ParquetStorage
from src.logger_factory import LoggerFactory

class Loader:
    def __init__(self):
        api_key = os.getenv("ALPHA_VANTAGE_API_KEY")
        url =  os.getenv("ALPHA_VANTAGE_URL")
        data_path = os.getenv("OUTPUT_PATH", "data/")
        self.api = AlphaVantageAPI(api_key, url)
        self.storage = ParquetStorage(data_path)
        self.data_path = data_path
        #self.logger = get_run_logger() 
        factory = LoggerFactory(default_level=logging.DEBUG)
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
            if not i.injest('TIME_SERIES_MONTHLY_ADJUSTED', 'Monthly Adjusted Time Series', ticker):
                return False

            return True
        # return FinancialDataInjestor(api_key, dp, ticker, url).extract()

    def load_tickers(self):
            tickers = []
            path = os.path.join(self.data_path, "tickers.csv")
            self.logger.info(f"Loading tickers from {path}.")
            with open(path, newline='') as csvfile:
                reader = csv.reader(csvfile)
                for row in reader:
                    if row:  # skip empty rows
                        tickers.append(row[0])
            
            self.logger.info(f"Loaded {len(tickers)} tickers from {path}: {tickers}")
            return tickers

    #@flow
    def load(self):
        tickers = self.load_tickers()
        for ticker in tickers:
            if not self.load_ticker(ticker):
                self.logger.warning(f"Failed to load ticker: {ticker}. Stopping further processing.")
                break


Loader().load()