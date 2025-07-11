import pandas as pd
import logging
from src.parquet.parquet_storage import ParquetStorage


class DividendConsolidator:

    def __init__(self, ps: ParquetStorage, logger: logging.Logger):
        self.storage = ps
        self.logger = logger

        
    def consolidate(self, df: pd.DataFrame, name: str, ticker: str) -> pd.DataFrame:
        # if the file does not exist, return the incomming DataFrame
        if not self.storage.exists(name, ticker):
            return df
        
        dv = self.storage.read_df(name, ticker)

        # get required columns
        dv = dv[["ex_dividend_date", "amount"]]        

        # rename columns
        dv.rename(columns={'ex_dividend_date': 'date',
                           'amount': 'dividend'}, inplace=True)

        # convert date
        dv['date'] = pd.to_datetime(dv['date'])  
        
        # convert to number
        dv['dividend'] = pd.to_numeric(dv['dividend'], errors='coerce')

        # calc the fiscal date ending of each quarter 
        dv["qtr_end_date"] = (dv["date"] + pd.offsets.QuarterEnd(0)) - pd.offsets.QuarterEnd()
        
        # Compound annual dividend growth rate over the past 5 years
        dv['qtr_growth'] = (dv['dividend'] / dv['dividend'].shift(20))**(1/20) - 1
        dv['dividend_growth_rate_5y'] = (1 + dv['qtr_growth'])**4 - 1
        
        # Calculate TTM using trailing 4-period sum (current + previous 3)
        dv[f"dividendTTM"] = dv["dividend"].rolling(window=4).sum()

        # Dividend yield 
        dv['dividend_yield'] = dv['dividendTTM'] / df['share_price']

        # 20-quarter rolling (5-year) stats
        dv['yield_historical_mean_5y'] = dv['dividend_yield'].rolling(window=20, min_periods=1).mean()
        dv['yield_historical_std_5y'] = dv['dividend_yield'].rolling(window=20, min_periods=1).std()

        # Z-score  
        dv['yield_zscore'] = (dv['dividend_yield'] - dv['yield_historical_mean_5y']) / dv['yield_historical_std_5y']
        
        self.logger.info(f"Table {name} consolidated for {ticker}.")
        return df.merge(dv, on="qtr_end_date", how="left")
   