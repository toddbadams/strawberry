import pandas as pd
from src.data.parquet_storage import ParquetStorage


class StockPriceConsolidator:

    def __init__(self, ps: ParquetStorage):
        self.storage = ps


    def consolidate(self, df: pd.DataFrame, ticker: str) -> pd.DataFrame:
        ps = self.storage.read_df("TIME_SERIES_MONTHLY_ADJUSTED", ticker)
        
        # convert date
        ps['date'] = pd.to_datetime(ps['date'])  

        # get adjusted closing price at end of quarter
        price_q = (
            ps.set_index("date")
            .resample("Q")["5. adjusted close"].last()
            .reset_index()
            .rename(columns={"date": "fiscalDateEnding", "5. adjusted close": "sharePrice"})
        )
        price_q["sharePrice"] = pd.to_numeric(price_q["sharePrice"], errors="coerce")

        # merge
        df = df.merge(price_q[["fiscalDateEnding", "sharePrice"]],on="fiscalDateEnding", how="left")
       
        #df['sharePrice_avg_5Y'] = df['sharePrice'].rolling(window=20).mean()
        #df['sharePrice_avg_10Y'] = df['sharePrice'].rolling(window=40).mean()
        return df