import pandas as pd
import logging
from src.consolidators.eps_projection import EPSProjection
from src.parquet.parquet_storage import ParquetStorage

class EarningsConsolidator:

    def __init__(self, ps: ParquetStorage, logger: logging.Logger):
        self.storage = ps
        self.logger = logger

    def consolidate(self, df: pd.DataFrame, name: str, ticker: str) -> pd.DataFrame:
        er = self.storage.read_df(name, ticker)

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
        
        # P/E ratio
        er['pe_ratio'] = df['share_price'] / er['eps']

        # Projected EPS Growth Rate
        er = er.merge(EPSProjection(er).calculate(), on='qtr_end_date', how='left')
        
        # PEG ratio
        er['peg_ratio'] = er['pe_ratio'] / er['projected_eps_growth_rate']

        # Earnings Yield
        er['earnings_yield'] = er['eps'] / df['share_price']

        self.logger.info(f"Table {name} consolidated for {ticker}.")
        return df.merge(er, on='qtr_end_date', how='left')