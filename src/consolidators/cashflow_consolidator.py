import pandas as pd
import logging
from src.parquet.parquet_storage import ParquetStorage


class CashflowConsolidator:

    def __init__(self, ps: ParquetStorage, logger: logging.Logger):
        self.storage = ps
        self.logger = logger

    def consolidate(self, df: pd.DataFrame, name: str, ticker: str) -> pd.DataFrame:
        cf = self.storage.read_df(name, ticker)

        # get required columns
        cf = cf[['fiscalDateEnding', 'operatingCashflow', 'capitalExpenditures']]
        
        # rename columns
        cf.rename(columns={'fiscalDateEnding': 'qtr_end_date',
                           'operatingCashflow': 'operating_cashflow',
                           'capitalExpenditures': 'capital_expenditures'}, inplace=True)

        # convert date
        cf['qtr_end_date'] = pd.to_datetime(cf['qtr_end_date'])  

        # conver to numbers
        for col in ["operating_cashflow", "capital_expenditures"]:
            cf[col] = pd.to_numeric(cf[col], errors="coerce")

        # Calculate free cashflow:    FCF = Operating Cash Flow – Capital Expenditures
        cf['free_cashflow'] = (cf['operating_cashflow'] - cf['capital_expenditures'])

        # free cashflow for last 12 months (TTM)
        cf['free_cashflow_TTM'] = cf['free_cashflow'].rolling(window=4).sum()
        
        # free cashflow per share for last 12 months 
        cf["free_cashflow_ps_TTM"] = (cf['free_cashflow_TTM'] / df['shares_outstanding']).round(2)

        self.logger.info(f"Table {name} consolidated for {ticker}.")       
        return df.merge(cf, on="qtr_end_date", how="left")