import pandas as pd
import logging

from src.config.config_loader import ConsolidationTableConfig
from src.parquet.parquet_storage import ParquetStorage


class Consolidator:

    def __init__(self, ps: ParquetStorage, logger: logging.Logger):
        self.storage = ps
        self.logger = logger


    def _insider_transform(self, df: pd.DataFrame, date_col: str) -> pd.DataFrame:
        df = df.copy()

        # make shares negative when disposing and positive when acquired
        df.loc[df["acquisition_or_disposal"] == "D", "insider_shares"] *= -1

        # setup datetime index
        df[date_col] = pd.to_datetime(df[date_col])
        df.set_index(date_col, inplace=True)

        # Resample by quarter and sum
        quarterly = df['insider_shares'].resample('Q').sum()

        # Build result: quarter‐end dates and summed shares
        result = (quarterly
            .reset_index()
            .rename(columns={'date': 'quarter_end', 'insider_shares': 'insider_shares'}))

        return result

    def _dividen_transform(self, df: pd.DataFrame, date_col: str) -> pd.DataFrame:      
        # calc the fiscal date ending of each quarter 
        df[date_col] = (df[date_col] + pd.offsets.QuarterEnd(0)) - pd.offsets.QuarterEnd()
        return df
    
    def _pricing_transform(self, df: pd.DataFrame, date_col: str) -> pd.DataFrame:
        df = df.copy()
        df[date_col] = pd.to_datetime(df[date_col])
        df.set_index(date_col, inplace=True)

        # Resample to quarter-end, taking the last available record
        quarterly_last = df['share_price'].resample('Q').last()

        # Build result DataFrame
        df = (
            quarterly_last
            .reset_index()
            .rename(columns={date_col: 'qtr_end_date', 'share_price': 'share_price'})
        )
        return df
        
    def run(self, df: pd.DataFrame, config: ConsolidationTableConfig, ticker: str) -> pd.DataFrame:
        # if the file does not exist, return the incomming DataFrame
        if not self.storage.exists(config.name, ticker):
            self.logger.warning(f"Acquisition table: {config.name} does NOT exist, cannot consolidate")
            return df
        
        df2 = self.storage.read_df(config.name, ticker)

        # get required columns
        df2 = df2[config.in_names()]        

        # rename columns
        df2.rename(columns=config.in_to_out_map(), inplace=True)

        # convert date
        dates = config.date_out_names()
        for item in dates:
            df2[item] = pd.to_datetime(df2[item], errors='coerce')  
        
        # convert to number
        for item in config.number_out_names():
            df2[item] = pd.to_numeric(df2[item], errors='coerce')

        # SPECIAL CASES:
        if config.name == 'INSIDER_TRANSACTIONS':
            df2 = self._insider_transform(df2, dates[0])

        if config.name == 'DIVIDENDS':
            df2 = self._dividen_transform(df2, dates[0])

        if config.name == 'TIME_SERIES_MONTHLY_ADJUSTED':
            df2 = self._pricing_transform(df2, dates[0])
              
        self.logger.info(f"Table {config.name} consolidated for {ticker}.")
        return df2 if df.empty else df.merge(df2, on=dates[0], how="left")

   