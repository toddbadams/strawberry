import pandas as pd

class ValueRules:

    def __init__(self, undervalue_thr: float = 0.08, 
        discount_rate: float = 0.0775):
        
        self.undervalue_thr = undervalue_thr
        self.discount_rate = discount_rate

    def __calc_two_stage_dcf(self,                            
                            cashflow: float,
                            high_growth_rate: float,
                            terminal_growth_rate: float,
                            high_growth_years: int) -> float:
        # Stage 1: Sum of discounted cash flows during high growth
        stage1_value = 0
        for year in range(1, high_growth_years + 1):
            projected_cash_flow = cashflow * ((1 + high_growth_rate) ** year)
            discounted_cash_flow = projected_cash_flow / ((1 + self.discount_rate) ** year)
            stage1_value += discounted_cash_flow

        # Cash flow at end of high-growth period
        final_year_cash_flow = cashflow * ((1 + high_growth_rate) ** high_growth_years)

        # Stage 2: Terminal value using Gordon Growth Model
        terminal_value = (final_year_cash_flow * (1 + terminal_growth_rate)) / (self.discount_rate - terminal_growth_rate)
        discounted_terminal_value = terminal_value / ((1 + self.discount_rate) ** high_growth_years)

        # Total DCF
        total_value = stage1_value + discounted_terminal_value
        return round(float(total_value), 2)

    def __calc_dcf_per_share(self, 
                            cashflow_series: pd.Series,
                            shares_series: pd.Series,
                            high_growth_rate,
                            high_growth_years,
                            terminal_growth_rate) -> list[float | None]:

        dcf_values: list[float | None] = []

        for cashflow, shares in zip(cashflow_series, shares_series):
            if pd.isna(cashflow) or pd.isna(shares) or shares == 0:
                dcf_values.append(None)
                continue

            dcf_per_share = round(float(
                self.__calc_two_stage_dcf(cashflow=cashflow,
                                          high_growth_rate=high_growth_rate, 
                                          terminal_growth_rate=terminal_growth_rate,
                                          high_growth_years=high_growth_years) / shares
            ), 2)
            dcf_values.append(dcf_per_share)

        return dcf_values

    def __calc_ddm_per_share(self, 
            dividend_series: pd.Series,
            dividend_growth_rate: float) -> list[float]:

        ddm_values = []

        for dividend in dividend_series:
            # Ensure dividend is a valid number
            if pd.isna(dividend) or dividend <= 0:
                ddm_values.append(None)
                continue

            # Gordon Growth Model for DDM
            try:
                ddm_valuation = round(dividend * (1 + dividend_growth_rate) / (self.discount_rate - dividend_growth_rate),2)
            except ZeroDivisionError:
                ddm_valuation = None

            ddm_values.append(ddm_valuation)
        return ddm_values

    def dcf_ddm_value_rule(self, df: pd.DataFrame,
                            div_gr: float = 0.05,     # dividend growth rate
                            cf_high_gr: float = 0.05, # cashflow inital (high) growth rate
                            cf_high_gy: int = 10,     # cashflow inital (high) growth years
                            terminal_growth_rate: float = 0.029 # termninal cashflow growth rate
        ) -> pd.DataFrame:

        # DCF valuation
        df['fair_value_dcf'] = self.__calc_dcf_per_share(cashflow_series = df['free_cashflow_ps_TTM'], 
                                                        shares_series = df['sharePrice'],
                                                        high_growth_rate = cf_high_gr, 
                                                        high_growth_years = cf_high_gy, 
                                                        terminal_growth_rate = terminal_growth_rate)

        # DDM valuation
        df['fair_value_ddm'] = self.__calc_ddm_per_share(dividend_series = df['dividend'],
                                                         dividend_growth_rate = div_gr)

        # DCF / DDM blended value
        df['fair_value_blended'] = (df['fair_value_dcf'] +  df['fair_value_ddm'])/2

        # fair value gap
        df['fair_value_gap_pct'] = (df['fair_value_blended'] - df['sharePrice']) / df['fair_value_blended']

        # under value rule    
        df['rule_undervalued_stock'] = df['fair_value_gap_pct'] <= self.undervalue_thr
        return df
        
    def pe_value_rule(seld, df: pd.DataFrame) -> pd.DataFrame:

        # P/E ratio
        df['pe_ratio'] = df['sharePrice'] / df['reportedEPS']

        # P/E Vs Peers  - to do, need to find a way to put peer P/E ratio's into the df

        # PEG Ratio - to do, need to calc projected_EPS_growth_rate
        
        # PE valuation rule - todo

        return df