import pandas as pd
import logging
from src.parquet.parquet_storage import ParquetStorage


class IncomeStatementConsolidator:

    def __init__(self, ps: ParquetStorage, logger: logging.Logger):
        self.storage = ps
        self.logger = logger


    def consolidate(self, df: pd.DataFrame, name: str, ticker: str) -> pd.DataFrame:
        inc = self.storage.read_df(name, ticker)

        # get required columns
        inc = inc[["fiscalDateEnding", "netIncome", "ebit", "ebitda"]].copy()

        # rename columns
        inc.rename(columns={'fiscalDateEnding': 'qtr_end_date',
                           'netIncome': 'net_income'}, inplace=True)
        # convert date
        inc['qtr_end_date'] = pd.to_datetime(inc['qtr_end_date'])  

        # convert numbers
        for col in ["net_income", "ebit", "ebitda"]:
            inc[col] = pd.to_numeric(inc[col], errors="coerce")

        
        inc['ebitda_to_fcflow'] = inc['ebitda'] / df['free_cashflow']  
        
        self.logger.info(f"Table {name} consolidated for {ticker}.")
        return df.merge(inc, on="qtr_end_date", how="left")