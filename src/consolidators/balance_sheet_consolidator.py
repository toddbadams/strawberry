import pandas as pd
from src.parquet.parquet_storage import ParquetStorage


class BalanceSheetConsolidator:

    def __init__(self, ps: ParquetStorage):
        self.storage = ps

    def consolidate(self, ticker: str) -> pd.DataFrame:        
        df = self.storage.read_df("BALANCE_SHEET", ticker)

        # get required columns
        df = df[['fiscalDateEnding', 'commonStockSharesOutstanding']].copy()
        
        # rename columns
        df.rename(columns={'fiscalDateEnding': 'qtr_end_date',
                           'commonStockSharesOutstanding': 'shares_outstanding'}, inplace=True)
        
        # convert to date
        df['qtr_end_date'] = pd.to_datetime(df['qtr_end_date'], errors='coerce') 

        # convert to number
        df['shares_outstanding'] = pd.to_numeric(df['shares_outstanding'], errors="coerce")

        #  year and quarter
        df["year"] = df["qtr_end_date"].dt.year
        df["quarter"] = df["qtr_end_date"].dt.quarter
        df['year_quarter'] = (df["year"].astype(str).str[-2:] + 'QE' + df["quarter"].astype(str))

        return df