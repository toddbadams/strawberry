import pandas as pd
import numpy as np

class CashDividendCoverageCalculator:
    """
    Calculates the number of consecutive years for which cash and equivalents
    cover dividend payments on a trailing twelve months basis.
    """
    def __init__(self, cash_and_equiv: pd.Series, dividends_paid: pd.Series):
        self.cash_and_equiv = cash_and_equiv
        self.dividends_paid = dividends_paid

    def compute(self) -> pd.Series:
        """
        Computes the coverage run lengths per year.

        Returns:
            pd.Series: The consecutive-year coverage counts named
                       'cash_dividend_coverage_years'.
        """
        # Compute ratio and guard against infinities/nans
        ratio = self.cash_and_equiv.div(self.dividends_paid)
        ratio = ratio.replace([np.inf, -np.inf], np.nan).fillna(0)

        # Boolean mask where coverage >= 1
        good = ratio >= 1

        # Group identifier resets on False
        groups = (~good).cumsum()

        # Within each group, count consecutive True values
        run_lengths = good.groupby(groups).cumcount() + 1

        # Zero out where coverage is False
        coverage = run_lengths.where(good, 0)
        coverage.name = 'cash_dividend_coverage_years'

        return coverage

