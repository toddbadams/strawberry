import pandas as pd
import logging

from src.config.table_config import TableConfig
from src.parquet.parquet_storage import ParquetStorage


class Consolidator:

    def __init__(self, ps: ParquetStorage, logger: logging.Logger):
        self.storage = ps
        self.logger = logger


    def _insider_transform(self, df: pd.DataFrame) -> pd.DataFrame:
        # make shares negative when disposing and positive when acquired
        df.loc[df["acquisition_or_disposal"] == "D", "shares"] *= -1

    def _dividen_transform(self, df: pd.DataFrame, date_col: str) -> pd.DataFrame:      
        # calc the fiscal date ending of each quarter 
        df[date_col] = (df[date_col] + pd.offsets.QuarterEnd(0)) - pd.offsets.QuarterEnd()
        
    def run(self, df: pd.DataFrame, config: TableConfig, ticker: str) -> pd.DataFrame:
        # if the file does not exist, return the incomming DataFrame
        if not self.storage.exists(config.name, ticker):
            return df
        
        df2 = self.storage.read_df(config.name, ticker)

        # get required columns
        df2 = df2[config.in_names()]        

        # rename columns
        df2.rename(columns=config.in_to_out_map(), inplace=True)

        # convert date
        dates = config.date_out_names()
        for item in dates:
            df2[item] = pd.to_datetime(df2[item])  
        
        # convert to number
        for item in config.date_out_names():
            df2[item] = pd.to_numeric(df2[item], errors='coerce')

        # SPECIAL CASES:
        if config.name == 'TIME_SERIES_MONTHLY_ADJUSTED':
            df2 = self._insider_transform(df2)

        if config.name == 'DIVIDENDS':
            df2 = self._dividen_transform(df2, dates[0])
              
        self.logger.info(f"Table {config.name} consolidated for {ticker}.")
        return df.merge(df2, on=dates[0], how="left")
   