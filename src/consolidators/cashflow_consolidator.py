import pandas as pd
from src.data.parquet_storage import ParquetStorage


class CashflowConsolidator:

    def __init__(self, ps: ParquetStorage):
        self.storage = ps

    def consolidate(self, df: pd.DataFrame, ticker: str) -> pd.DataFrame:
        cf = self.storage.read_df("CASH_FLOW", ticker)
        # merge columns
        df = self._merge_columns(df, cf, ['fiscalDateEnding', 'operatingCashflow', 'capitalExpenditures'])

        df['operatingCashflow'] = df['operatingCashflow'].astype(float)
        df['capitalExpenditures'] = df['capitalExpenditures'].astype(float)

        # Calculate free cashflow:    FCF = Operating Cash Flow – Capital Expenditures
        df['freeCashflow'] = (df['operatingCashflow'] - df['capitalExpenditures'])
        self._calc_per_share_TTM(df, 'freeCashflow')
       
        # Remove columns that are not needed
        df.drop(columns=['operatingCashflow', 'capitalExpenditures', 'freeCashflow'], inplace=True)      
        return df