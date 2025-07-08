import pandas as pd
from src.data.parquet_storage import ParquetStorage


class IncomeStatementConsolidator:

    def __init__(self, ps: ParquetStorage):
        self.storage = ps


    def consolidate(self, df: pd.DataFrame, ticker: str) -> pd.DataFrame:
        inc = self.storage.read_df("INCOME_STATEMENT", ticker)

        # get required columns
        inc_sel = inc[["fiscalDateEnding", "netIncome", "ebit", "ebitda"]].copy()

        # convert date
        inc_sel['fiscalDateEnding'] = pd.to_datetime(inc_sel['fiscalDateEnding'])  

        # conver numbers
        for col in ["netIncome", "ebit", "ebitda"]:
            inc_sel[col] = pd.to_numeric(inc_sel[col], errors="coerce")

        # merge
        df = df.merge(inc_sel, on="fiscalDateEnding", how="left")
        return df