import pandas as pd
from parquet.storage import ParquetStorage

class HealthRules:

    def __init__(self, earnings_to_fcf_lower_threshold: float = 0.4,
                 earnings_to_fcf_upper_threshold: float = 0.6,
                 peg_upper_threshold: float = 1.0):
        self.earnings_to_fcf_lower_threshold = earnings_to_fcf_lower_threshold
        self.earnings_to_fcf_upper_threshold = earnings_to_fcf_upper_threshold
        self.peg_upper_threshold = peg_upper_threshold

    def cash_conversion_rule(self, df: pd.DataFrame) -> pd.DataFrame:
        df['rule_cash_conversion'] = (
            (df['ebitda_to_fcflow'] >= self.earnings_to_fcf_lower_threshold) &
            (df['ebitda_to_fcflow'] <= self.earnings_to_fcf_upper_threshold))

        return df
   
    def growth_adjusted_valuation_rule(self, df: pd.DataFrame) -> pd.DataFrame:
        df['rule_peg'] = df['peg_ratio'] < self.peg_upper_threshold 
        return
    
    def earnings_premium_rule(self, df: pd.DataFrame, bond_yield: float) -> pd.DataFrame:
        df['rule_earnings_premium'] = df['earnings_yield'] >= (bond_yield + 0.02)
        return df

    def debt_cushion_rule(self, df: pd.DataFrame) -> pd.DataFrame:
        df['rule_debt_cushion'] = df['debt_to_equity_fv'] <= 0.5
        return df

    def skin_in_the_game_rule(self, df: pd.DataFrame) -> pd.DataFrame:
        df['rule_skin_in_game'] = df['insider_pct'] >=  0.05
        return df  