import pandas as pd

class ValueRules:

    def __init__(self, undervalue_thr: float = 0.08, 
        discount_rate: float = 0.0775):        
        self.undervalue_thr = undervalue_thr
        self.discount_rate = discount_rate

    def dcf_ddm_value_rule(self, df: pd.DataFrame) -> pd.DataFrame:

        # under value rule    
        df['rule_undervalued_stock'] = df['fair_value_gap_pct'] <= self.undervalue_thr
        return df
        
    def pe_value_rule(seld, df: pd.DataFrame) -> pd.DataFrame:



        # P/E Vs Peers  - to do, need to find a way to put peer P/E ratio's into the df
        
        # PE valuation rule - todo

        return df