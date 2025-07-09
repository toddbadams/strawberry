import pandas as pd

class DividendRules:

    def __init__(self, div_gr_thr: float = 0.05, div_chowder_threshold: float = 0.12):
        self.div_gr_threshold = div_gr_thr
        self.div_chowder_threshold = div_chowder_threshold

    def dividend_growth_rule(self, df: pd.DataFrame) -> pd.DataFrame:

        # True if 5-10 yr annual dividend growth rate > 5%
        df['rule_dividend_growth'] = df['dividend_growth_rate_5y'] >= self.div_gr_threshold

        # True if (current yield) + (5-10 yr avg dividend growth) > 12 %
        df['rule_dividend_chowder'] = (df['dividend_yield'] + df['dividend_growth_rate_5y']) >= self.div_chowder_threshold

        return df

           
    def dividend_yield_rule(self, df: pd.DataFrame) -> pd.DataFrame:

        # True if dividend yield ≥ 1 σ above its 5-year historical average
        df['rule_dividend_yield'] = df['yield_zscore'] >= 1

        return df