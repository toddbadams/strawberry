import pandas as pd
from src.data.parquet_storage import ParquetStorage


class InsiderConsolidator:

    def __init__(self, ps: ParquetStorage):
        self.storage = ps


    def consolidate(self, df: pd.DataFrame, ticker: str) -> pd.DataFrame:
        ins = self.storage.read_df("INSIDER_TRANSACTIONS", ticker)

        # convert date
        ins['transaction_date'] = pd.to_datetime(ins['transaction_date'], errors='coerce')  
        ins["year"] = ins["transaction_date"].dt.year
        ins["quarter"] = ins["transaction_date"].dt.quarter

        # sum net shares per quarter
        ins["net_shares"] = ins.apply(
            lambda r: r["shares"] if r["acquisition_or_disposal"] == "acquisition" 
                      else -pd.to_numeric(r["shares"], errors="coerce"),
            axis=1
        )
        ins_agg = (
            ins.groupby(["year", "quarter"])["net_shares"]
            .sum()
            .reset_index()
            .rename(columns={"net_shares": "insider_net_shares"})
        )

        # merge
        df = df.merge(ins_agg, on=["year", "quarter"], how="left")

        return df