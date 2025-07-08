import pandas as pd
from src.data.parquet_storage import ParquetStorage


class BalanceSheetConsolidator:

    def __init__(self, ps: ParquetStorage):
        self.storage = ps

    def consolidate(self, ticker: str) -> pd.DataFrame:        
        df = self.storage.read_df("BALANCE_SHEET", ticker)
        
        # fiscal quarter date ending
        df['fiscalDateEnding'] = pd.to_datetime(df['fiscalDateEnding'], errors='coerce')    
        df.sort_values('fiscalDateEnding')
        
        # shares outstanding
        df.rename(columns={'commonStockSharesOutstanding': 'sharesOutstanding'}, inplace=True)
        df['sharesOutstanding'] = pd.to_numeric(df['sharesOutstanding'], errors="coerce")

        #  year and quarter
        df["year"] = df["fiscalDateEnding"].dt.year
        df["quarter"] = df["fiscalDateEnding"].dt.quarter
        df['year_quarter'] = (df["year"].astype(str).str[-2:] + 'QE' + df["quarter"].astype(str))

        return df