import pandas as pd
from src.parquet.parquet_storage import ParquetStorage

class EarningsConsolidator:

    def __init__(self, ps: ParquetStorage):
        self.storage = ps

    def consolidate(self, df: pd.DataFrame, ticker: str) -> pd.DataFrame:
        er = self.storage.read_df('EARNINGS', ticker)

        # get required columns
        er = er[['fiscalDateEnding', 'reportedEPS', 'estimatedEPS', 'surprisePercentage']].copy()

        # rename reportedEPS to EPS
        er = er.rename(columns={'fiscalDateEnding': 'qtr_end_date', 
                                'reportedEPS': 'eps',
                                'estimatedEPS': 'estimated_eps',
                                'surprisePercentage': 'surprise_eps_pct'})

        # convert date
        er['qtr_end_date'] = pd.to_datetime(er['qtr_end_date'])  

        # convert numbers
        for col in ['eps', 'estimated_eps', 'surprise_eps_pct']:
            er[col] = pd.to_numeric(er[col], errors='coerce')

        return df.merge(er, on='qtr_end_date', how='left')