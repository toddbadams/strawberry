import pandas as pd
import logging
from src.parquet.parquet_storage import ParquetStorage


class ValueConsolidator:

    def __init__(self, logger: logging.Logger, 
                    div_gr: float = 0.05,     # dividend growth rate
                    cf_high_gr: float = 0.05, # cashflow inital (high) growth rate
                    cf_high_gy: int = 10,     # cashflow inital (high) growth years
                    terminal_growth_rate: float = 0.029,
                    discount_rate: float = 0.775): # discount rate aka cost of money
        self.logger = logger
        self.dividend_growth_rate = div_gr
        self.cashflow_high_growth_rate = cf_high_gr
        self.cashflow_high_growth_years = cf_high_gy
        self.cashflow_terminal_growth_rate = terminal_growth_rate
        self.discount_rate = discount_rate

    def __calc_two_stage_dcf(self, cashflow: float) -> float:
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

    def __calc_dcf_per_share(self, cashflow_series: pd.Series, shares_series: pd.Series) -> list[float | None]:

        dcf_values: list[float | None] = []

        for cashflow, shares in zip(cashflow_series, shares_series):
            if pd.isna(cashflow) or pd.isna(shares) or shares == 0:
                dcf_values.append(None)
                continue

            dcf_per_share = round(self.__calc_two_stage_dcf(cashflow=cashflow) / shares, 2)
            dcf_values.append(dcf_per_share)

        return dcf_values

    def __calc_ddm_per_share(self, dividend_series: pd.Series) -> list[float]:

        ddm_values = []

        for dividend in dividend_series:
            # Ensure dividend is a valid number
            if pd.isna(dividend) or dividend <= 0:
                ddm_values.append(None)
                continue

            # Gordon Growth Model for DDM
            try:
                ddm_valuation = round(dividend * (1 + self.dividend_growth_rate) / 
                                      (self.discount_rate - self.dividend_growth_rate), 2)
            except ZeroDivisionError:
                ddm_valuation = None

            ddm_values.append(ddm_valuation)
        return ddm_values

    def consolidate(self, df: pd.DataFrame) -> pd.DataFrame:

        # DCF valuation
        df['fair_value_dcf'] = self.__calc_dcf_per_share(cashflow_series = df['free_cashflow_ps_TTM'], 
                                                        shares_series = df['share_price'])

        # DDM valuation
        df['fair_value_ddm'] = self.__calc_ddm_per_share(dividend_series = df['dividend'])

        # DCF / DDM blended value
        df['fair_value_blended'] = (df['fair_value_dcf'] +  df['fair_value_ddm']) / 2

        # fair value gap
        df['fair_value_gap_pct'] = (df['fair_value_blended'] - df['share_price']) / df['fair_value_blended']

        self.logger.info(f"Valution calculated and consolidated.")   
        return df