import logging
import pandas as pd
from src.parquet.parquet_storage import ParquetStorage
from src.alpha_vantage.alpha_vantage_api import AlphaVantageAPI
from prefect import get_run_logger

class Injestor():
    def __init__(self, alpha_vantage: AlphaVantageAPI, storage: ParquetStorage, logger: logging.Logger):
        self.alpha_vantage = alpha_vantage
        self.storage = storage
        self.logger = logger
  
    def injest(self, name: str, attr: str, ticker: str):

        # Check if data already exists to avoid unnecessary API calls
        if self.storage.exists(name, ticker):
            self.logger.info(f"Table {name} already exist {ticker}.")
            return True
        
        data = self.alpha_vantage.fetch(name, ticker)
                
        # ensure we have data to proceed
        if data is None:
            self.logger.warning(f"No {name} data found for {ticker}.")
            return False        
        
        # ensure we have not reached API limit
        if 'Information' in data:
            self.logger.warning(f"{name} API limit reached for {ticker}.")
            return False
                
        # create data frame and store
        df = pd.DataFrame(data if attr is None else data[attr])
        df['symbol'] = ticker
        self.storage.write_df(df, name, partition_cols=['symbol'], index=False)
        self.logger.info(f"Table {name} ingested for {ticker}.")
        return True