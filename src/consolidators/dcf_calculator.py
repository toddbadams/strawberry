import pandas as pd

class DCFCalculator:
    def __init__(self,
                    cf_high_gr: float = 0.05, # cashflow inital (high) growth rate
                    cf_high_gy: int = 10,     # cashflow inital (high) growth years
                    terminal_growth_rate: float = 0.029,
                    discount_rate: float = 0.0775):
        self.cashflow_high_growth_rate = cf_high_gr
        self.cashflow_high_growth_years = cf_high_gy
        self.cashflow_terminal_growth_rate = terminal_growth_rate
        self.discount_rate = discount_rate

    def _calc_two_stage_dcf(self, cashflow: float) -> float:
        # Stage 1: Sum of discounted cash flows during high growth
        stage1_value = 0
        for year in range(1, self.cashflow_high_growth_years + 1):
            projected_cash_flow = cashflow * ((1 + self.cashflow_high_growth_rate) ** year)
            discounted_cash_flow = projected_cash_flow / ((1 + self.discount_rate) ** year)
            stage1_value += discounted_cash_flow

        # Cash flow at end of high-growth period
        final_year_cash_flow = cashflow * ((1 + self.cashflow_high_growth_rate) ** self.cashflow_high_growth_years)

        # Stage 2: Terminal value using Gordon Growth Model
        terminal_value = (final_year_cash_flow * (1 + self.cashflow_terminal_growth_rate)) / (self.discount_rate - self.cashflow_terminal_growth_rate)
        discounted_terminal_value = terminal_value / ((1 + self.discount_rate) ** self.cashflow_high_growth_years)

        # Total DCF
        total_value = stage1_value + discounted_terminal_value
        return round(float(total_value), 2)

    def calc(self, cashflow_series: pd.Series, shares_series: pd.Series) -> list[float | None]:

        dcf_values: list[float | None] = []

        for cashflow, shares in zip(cashflow_series, shares_series):
            if pd.isna(cashflow) or pd.isna(shares) or shares == 0:
                dcf_values.append(None)
                continue

            dcf_per_share = round(self._calc_two_stage_dcf(cashflow=cashflow) / shares, 2)
            dcf_values.append(dcf_per_share)

        return dcf_values