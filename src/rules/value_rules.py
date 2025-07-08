

import pandas as pd


def __calc_two_stage_dcf(
    cashflow: float,
    high_growth_rate: float,
    terminal_growth_rate: float,
    discount_rate: float,
    high_growth_years: int
) -> float:
    # Stage 1: Sum of discounted cash flows during high growth
    stage1_value = 0
    for year in range(1, high_growth_years + 1):
        projected_cash_flow = cashflow * ((1 + high_growth_rate) ** year)
        discounted_cash_flow = projected_cash_flow / ((1 + discount_rate) ** year)
        stage1_value += discounted_cash_flow

    # Cash flow at end of high-growth period
    final_year_cash_flow = cashflow * ((1 + high_growth_rate) ** high_growth_years)

    # Stage 2: Terminal value using Gordon Growth Model
    terminal_value = (final_year_cash_flow * (1 + terminal_growth_rate)) / (discount_rate - terminal_growth_rate)
    discounted_terminal_value = terminal_value / ((1 + discount_rate) ** high_growth_years)

    # Total DCF
    total_value = stage1_value + discounted_terminal_value
    return round(float(total_value), 2)

def calc_dcf_per_share(
    cashflow_series: pd.Series,
    shares_series: pd.Series,
    dividend_growth_rate = 0.03,
    high_growth_rate: float = 0.05,
    high_growth_years: int = 10,
    terminal_growth_rate: float = 0.029
) -> list[float | None]:
    dcf_values: list[float | None] = []

    for cashflow, shares in zip(cashflow_series, shares_series):
        if pd.isna(cashflow) or pd.isna(shares) or shares == 0:
            dcf_values.append(None)
            continue

        dcf_per_share = round(float(
            __calc_two_stage_dcf(
                cashflow, high_growth_rate, terminal_growth_rate,
                discount_rate, high_growth_years
            ) / shares
        ), 2)
        dcf_values.append(dcf_per_share)

    return dcf_values


def calc_ddm_per_share(
    dividend_series: pd.Series,
    dividend_growth_rate: float,
    discount_rate: float
) -> list[float]:
    """
    Calculate the Dividend Discount Model (DDM) valuation per share.
    Args:
        dividend_series (pd.Series): Series of dividends per share.
        dividend_growth_rate (float): Expected growth rate of dividends.
        discount_rate (float): Discount rate to apply.
    Returns:
        list[float]: List of DDM valuations per share, rounded to 2 decimal places.
    """
    ddm_values = []

    for dividend in dividend_series:
        # Ensure dividend is a valid number
        if pd.isna(dividend) or dividend <= 0:
            ddm_values.append(None)
            continue

        # Gordon Growth Model for DDM
        try:
            ddm_valuation = round(dividend * (1 + dividend_growth_rate) / (discount_rate - dividend_growth_rate),2)
        except ZeroDivisionError:
            ddm_valuation = None

        ddm_values.append(ddm_valuation)
    return ddm_values