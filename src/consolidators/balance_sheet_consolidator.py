import logging
import pandas as pd
from src.parquet.parquet_storage import ParquetStorage


class BalanceSheetConsolidator:

    def __init__(self, ps: ParquetStorage, logger: logging.Logger):
        self.storage = ps
        self.logger = logger
  

    def consolidate(self, name: str, ticker: str) -> pd.DataFrame:               
        df = self.storage.read_df(name, ticker)

        # get required columns
        df = df[['fiscalDateEnding', 'commonStockSharesOutstanding', 'shortTermDebt', 'longTermDebt']].copy()
        
        # rename columns
        df.rename(columns={'fiscalDateEnding': 'qtr_end_date',
                           'commonStockSharesOutstanding': 'shares_outstanding',
                           'shortTermDebt': 'short_term_debt',
                           'longTermDebt': 'long_term_debt'}, inplace=True)
        
        # convert to date
        df['qtr_end_date'] = pd.to_datetime(df['qtr_end_date'], errors='coerce') 

        # convert to number
        for col in ["shares_outstanding", "short_term_debt", "long_term_debt"]:
            df[col] = pd.to_numeric(df[col], errors="coerce")

        #  year and quarter
        df["year"] = df["qtr_end_date"].dt.year
        df["quarter"] = df["qtr_end_date"].dt.quarter
        df['year_quarter'] = (df["year"].astype(str).str[-2:] + 'QE' + df["quarter"].astype(str))

        self.logger.info(f"Table {name} consolidated for {ticker}.")
        return df