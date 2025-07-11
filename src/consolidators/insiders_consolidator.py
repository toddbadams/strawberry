import pandas as pd
import logging
from src.parquet.parquet_storage import ParquetStorage


class InsiderConsolidator:

    def __init__(self, ps: ParquetStorage, logger: logging.Logger):
        self.storage = ps
        self.logger = logger


    def consolidate(self, df: pd.DataFrame, name: str, ticker: str) -> pd.DataFrame:
        # if the file does not exist, return the incomming DataFrame
        if not self.storage.exists(name, ticker):
            return df
        
        ins = self.storage.read_df(name, ticker)
        
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
        ins = (
            ins.groupby(["year", "quarter"])["net_shares"]
            .sum()
            .reset_index()
            .rename(columns={"net_shares": "insider_net_shares"})
        )

        self.logger.info(f"Table {name} consolidated for {ticker}.")
        return df.merge(ins, on=["year", "quarter"], how="left")