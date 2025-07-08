import pandas as pd
from src.data.parquet_storage import ParquetStorage


class CashflowConsolidator:

    def __init__(self, ps: ParquetStorage):
        self.storage = ps

    def consolidate(self, df: pd.DataFrame, ticker: str) -> pd.DataFrame:
        cf = self.storage.read_df("CASH_FLOW", ticker)

        # get required columns
        cf = cf[['fiscalDateEnding', 'operatingCashflow', 'capitalExpenditures']]

        # convert date
        cf['fiscalDateEnding'] = pd.to_datetime(cf['fiscalDateEnding'])  

        # merge columns
        df = df.merge(cf, on="fiscalDateEnding", how="left")

        # conver to numbers
        df['operatingCashflow'] = pd.to_numeric(df['operatingCashflow'], errors="coerce")
        df['capitalExpenditures'] = pd.to_numeric(df['capitalExpenditures'], errors="coerce")

        # Calculate free cashflow:    FCF = Operating Cash Flow – Capital Expenditures
        df['free_cashflow'] = (df['operatingCashflow'] - df['capitalExpenditures'])

        # free cashflow for last 12 months (TTM)
        df['free_cashflow_TTM'] = df['free_cashflow'].rolling(window=4).sum()

        # free cashflow per share for last 12 months 
        df["free_cashflow_ps_TTM"] = (df['free_cashflow_TTM'] / df['sharesOutstanding']).round(2)
       
        # Remove columns that are not needed
        df.drop(columns=['operatingCashflow', 'capitalExpenditures', 'free_cashflow'], inplace=True)      
        return df