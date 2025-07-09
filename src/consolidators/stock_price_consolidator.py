import pandas as pd
from src.parquet.parquet_storage import ParquetStorage


class StockPriceConsolidator:

    def __init__(self, ps: ParquetStorage):
        self.storage = ps


    def consolidate(self, df: pd.DataFrame, ticker: str) -> pd.DataFrame:
        ps = self.storage.read_df('TIME_SERIES_MONTHLY_ADJUSTED', ticker)
        
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
        price_q = (
            ps.set_index('qtr_end_date')
            .resample('Q')['share_price'].last()
            .reset_index()
        )

        return df.merge(ps, on='qtr_end_date', how='left')