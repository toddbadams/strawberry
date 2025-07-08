import pandas as pd
from src.data.parquet_storage import ParquetStorage

class DividendRules:

    def __init__(self, div_gr_thr: float = 0.05, div_chowder_threshold: float = 0.12):
        self.div_gr_threshold = div_gr_thr
        self.div_chowder_threshold = div_chowder_threshold

    def dividend_growth_rule(self, df: pd.DataFrame) -> pd.DataFrame:

        # Compound annual dividend growth rate over the past 5 years
        df['qtr_growth'] = (df['dividend'] / df['dividend'].shift(20))**(1/20) - 1
        df['dividend_growth_rate_5y'] = (1 + df['qtr_growth'])**4 - 1

        # True if 5-10 yr annual dividend growth rate > 5%
        df['rule_dividend_growth'] = df['dividend_growth_rate_5y'] >= self.div_gr_threshold

        # True if (current yield) + (5-10 yr avg dividend growth) > 12 %
        df['rule_dividend_chowder'] = (df['dividend_yield'] + df['dividend_growth_rate_5y']) >= self.div_chowder_threshold

        return df

           
    def dividend_yield_rule(self, df: pd.DataFrame) -> pd.DataFrame:

        # Calculate TTM using trailing 4-period sum (current + previous 3)
        df[f"dividendTTM"] = df["dividend"].rolling(window=4).sum()

        # Dividend yield 
        df['dividend_yield'] = df['dividendTTM'] / df['sharePrice']

        # 20-quarter rolling (5-year) stats
        df['yield_historical_mean_5y'] = df['dividend_yield'].rolling(window=20, min_periods=1).mean()
        df['yield_historical_std_5y'] = df['dividend_yield'].rolling(window=20, min_periods=1).std()

        # Z-score  
        df['yield_zscore'] = (df['dividend_yield'] - df['yield_historical_mean_5y']) / df['yield_historical_std_5y']

        # True if dividend yield ≥ 1 σ above its 5-year historical average
        df['rule_dividend_yield'] = df['yield_zscore'] >= 1

        return df