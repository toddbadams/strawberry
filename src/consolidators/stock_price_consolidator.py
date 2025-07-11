import pandas as pd
import logging
from src.parquet.parquet_storage import ParquetStorage


class StockPriceConsolidator:

    def __init__(self, ps: ParquetStorage, logger: logging.Logger):
        self.storage = ps
        self.logger = logger


    def consolidate(self, df: pd.DataFrame, name: str, ticker: str) -> pd.DataFrame:
        # if the file does not exist, return the incomming DataFrame
        if not self.storage.exists(name, ticker):
            return df
        
        ps = self.storage.read_df(name, ticker)
        
        # get required columns
        ps = ps[['date', '5. adjusted close']]
        
        # rename columns
        ps.rename(columns={'date': 'qtr_end_date',
                           '5. adjusted close': 'share_price'}, inplace=True)

        # convert date
        ps['qtr_end_date'] = pd.to_datetime(ps['qtr_end_date'])  
        
        # convert to number
        ps['share_price'] = pd.to_numeric(ps['share_price'], errors='coerce')

        # get adjusted closing price at end of quarter
        ps = ps.set_index('qtr_end_date').resample('Q')['share_price'].last().reset_index()
        
        # total debt to fair value equity
        ps['fair_value_equity'] = df['shares_outstanding'] * ps['share_price']
        ps['debt_to_equity_fv'] = (df['short_term_debt'] + df['long_term_debt']) / ps['fair_value_equity']
        
        self.logger.info(f"Table {name} consolidated for {ticker}.")
        return df.merge(ps, on='qtr_end_date', how='left')