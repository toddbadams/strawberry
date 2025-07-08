import pandas as pd
from src.data.parquet_storage import ParquetStorage


class EarningsConsolidator:

    def __init__(self, ps: ParquetStorage):
        self.storage = ps


    def consolidate(self, df: pd.DataFrame, ticker: str) -> pd.DataFrame:
        er = self.storage.read_df("EARNINGS", ticker)
        # get required columns
        er_sel = er[["fiscalDateEnding", "reportedEPS", "estimatedEPS", "surprisePercentage"]].copy()

        # convert date
        er_sel['fiscalDateEnding'] = pd.to_datetime(er_sel['fiscalDateEnding'])  

        # convert numbers
        for col in ["reportedEPS", "estimatedEPS", "surprisePercentage"]:
            er_sel[col] = pd.to_numeric(er_sel[col], errors="coerce")

        # merge
        df = df.merge(er_sel, on="fiscalDateEnding", how="left")
        return df