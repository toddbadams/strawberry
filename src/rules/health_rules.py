import pandas as pd
from src.data.parquet_storage import ParquetStorage

class HealthRules:

    def __init__(self, earnings_to_fcf_lower_threshold: float,
                 earnings_to_fcf_upper_threshold: float):
        self.earnings_to_fcf_lower_threshold = earnings_to_fcf_lower_threshold
        self.earnings_to_fcf_upper_threshold = earnings_to_fcf_upper_threshold

    def cash_conversion_rule(self, df: pd.DataFrame) -> pd.DataFrame:

        df['ebitda_to_fcflow'] = df['ebitda'] / df['free_cash_flow']
        df['rule_cash_conversion'] = (
            (df['ebitda_to_fcflow'] >= self.earnings_to_fcf_lower_threshold) &
            (df['ebitda_to_fcflow'] <= self.earnings_to_fcf_upper_threshold))

        return df
   
    def growth_adjusted_valuation_rule(self, df: pd.DataFrame) -> pd.DataFrame:

        df['peg_ratio'] = df['pe_ratio'] / df['projected_EPS_growth_rate']
        df['rule_peg'] = df['peg_ratio'] < 1.0
        return
    
    def earnings_premium_rule(self, df: pd.DataFrame, bond_yield: float) -> pd.DataFrame:

        df['earnings_yield'] = df['EPS'] / df['share_price']
        df['rule_earnings_premium'] = df['earnings_yield'] >= (bond_yield + 0.02)
        return df

    def debt_cushion_rule(self, df: pd.DataFrame) -> pd.DataFrame:

        df['debt_to_equity_fv'] = df['total_debt'] / df['fair_value_equity']
        df['rule_debt_cushion'] = df['debt_to_equity_fv'] <= 0.5
        return df

    def skin_in_the_game_rule(self, df: pd.DataFrame) -> pd.DataFrame:

        df['rule_skin_in_game'] = df['insider_pct'] >=  0.05
        return df  