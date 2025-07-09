import pandas as pd
from src.parquet.parquet_storage import ParquetStorage


class DividendConsolidator:

    def __init__(self, ps: ParquetStorage):
        self.storage = ps

        
    def consolidate(self, df: pd.DataFrame, ticker: str) -> pd.DataFrame:
        dv = self.storage.read_df("DIVIDENDS", ticker)

        # get required columns
        dv = dv[["ex_dividend_date", "amount"]]        

        # rename columns
        dv.rename(columns={'ex_dividend_date': 'date',
                           'amount': 'dividend'}, inplace=True)

        # convert date
        dv['date'] = pd.to_datetime(dv['date'])  
        
        # convert to number
        dv['dividend'] = pd.to_numeric(dv['dividend'], errors='coerce')

        # calc the fiscal date ending of each quarter 
        dv["qtr_end_date"] = (dv["date"] + pd.offsets.QuarterEnd(0)) - pd.offsets.QuarterEnd()

        # sum the dividends per quarter
        dv = (
            dv.groupby("qtr_end_date")["dividend"]
            .sum()
            .reset_index()
        )
        
        # Compound annual dividend growth rate over the past 5 years
        df['qtr_growth'] = (df['dividend'] / df['dividend'].shift(20))**(1/20) - 1
        df['dividend_growth_rate_5y'] = (1 + df['qtr_growth'])**4 - 1

        return df.merge(dv, on="qtr_end_date", how="left")
   