import pandas as pd
from src.data.parquet_storage import ParquetStorage


class DividendConsolidator:

    def __init__(self, ps: ParquetStorage):
        self.storage = ps

        
    def consolidate(self, df: pd.DataFrame, ticker: str) -> pd.DataFrame:
        dv = self.storage.read_df("DIVIDENDS", ticker)

        # get required columns
        dv = dv[["ex_dividend_date", "amount"]].copy()

        # calc the fiscal date ending of each quarter
        dv['ex_dividend_date'] = pd.to_datetime(dv['ex_dividend_date'])  
        dv["fiscalDateEnding"] = (dv["ex_dividend_date"] + pd.offsets.QuarterEnd(0)) - pd.offsets.QuarterEnd()

        # convert to number        
        dv['amount'] = pd.to_numeric(dv['amount'], errors="coerce")

        # sum the dividen amounts per quarter
        div_agg = (
            dv.groupby("fiscalDateEnding")["amount"]
            .sum()
            .reset_index()
            .rename(columns={"amount": "dividend"})
        )

        # merge on fiscalDateEnding
        df = df.merge(div_agg, on="fiscalDateEnding", how="left")
        return df

    