import pandas as pd
from src.data.parquet_storage import ParquetStorage


class CashflowConsolidator:

    def __init__(self, ps: ParquetStorage):
        self.storage = ps

    def consolidate(self, df: pd.DataFrame, ticker: str) -> pd.DataFrame:
        cf = self.storage.read_df("CASH_FLOW", ticker)

        # get required columns
        cf = cf[['fiscalDateEnding', 'operatingCashflow', 'capitalExpenditures']]
        
        # rename columns
        cf.rename(columns={'fiscalDateEnding': 'qtr_end_date',
                           'operatingCashflow': 'operating_cashflow',
                           'capitalExpenditures': 'capital_expenditures'}, inplace=True)

        # convert date
        cf['qtr_end_date'] = pd.to_datetime(cf['qtr_end_date'])  

        # conver to numbers
        cf['operating_cashflow'] = pd.to_numeric(cf['operating_cashflow'], errors="coerce")
        cf['capital_expenditures'] = pd.to_numeric(cf['capital_expenditures'], errors="coerce")

        # Calculate free cashflow:    FCF = Operating Cash Flow – Capital Expenditures
        cf['free_cashflow'] = (cf['operating_cashflow'] - cf['capital_expenditures'])

        # free cashflow for last 12 months (TTM)
        cf['free_cashflow_TTM'] = cf['free_cashflow'].rolling(window=4).sum()

        # merge 
        df = df.merge(cf, on="qtr_end_date", how="left")

        # free cashflow per share for last 12 months 
        df["free_cashflow_ps_TTM"] = (df['free_cashflow_TTM'] / df['shares_outstanding']).round(2)
       
        return df