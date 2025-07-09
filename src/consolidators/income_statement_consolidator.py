import pandas as pd
from src.parquet.parquet_storage import ParquetStorage


class IncomeStatementConsolidator:

    def __init__(self, ps: ParquetStorage):
        self.storage = ps


    def consolidate(self, df: pd.DataFrame, ticker: str) -> pd.DataFrame:
        inc = self.storage.read_df("INCOME_STATEMENT", ticker)

        # get required columns
        inc = inc[["fiscalDateEnding", "netIncome", "ebit", "ebitda"]].copy()

        # rename columns
        inc.rename(columns={'fiscalDateEnding': 'qtr_end_date',
                           'netIncome': 'net_income'}, inplace=True)
        # convert date
        inc['qtr_end_date'] = pd.to_datetime(inc['qtr_end_date'])  

        # conver numbers
        for col in ["net_income", "ebit", "ebitda"]:
            inc[col] = pd.to_numeric(inc[col], errors="coerce")

        return df.merge(inc, on="qtr_end_date", how="left")