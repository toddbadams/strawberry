import pandas as pd
from src.rules.health_rules import HealthRules
from src.rules.dividend_rules import DividendRules
from src.rules.value_rules import ValueRules

class Rules:

    def apply(self, df: pd.DataFrame):
                
        dv_rules = DividendRules()
        df = dv_rules.dividend_yield_rule(df)
        df = dv_rules.dividend_growth_rule(df)

        v_rules = ValueRules()
        df = v_rules.dcf_ddm_value_rule(df) # todo:  find a way to introduce growth rates
        df = v_rules.pe_value_rule(df) # todo:   P/E v Peers and PEG

        h_rules = HealthRules()
        df = h_rules.cash_conversion_rule(df)
        df = h_rules.growth_adjusted_valuation_rule(df)
        df = h_rules.earnings_premium_rule(df)
        df = h_rules.debt_cushion_rule(df)
        df = h_rules.skin_in_the_game_rule(df)