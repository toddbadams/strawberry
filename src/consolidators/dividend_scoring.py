import pandas as pd

from src.consolidators.cash_dividend_coverage_calc import CashDividendCoverageCalculator
from src.consolidators.dividend_growth_streak import DividendGrowthStreak
from src.consolidators.score_calc import ScoreCalculator

class DividendScoring:
    """
    Extracts and applies dividend-related scoring metrics to a DataFrame.
    """
    def __init__(self):
        # Initialize ScoreCalculators with their respective parameters
        self.earnings_payout_ratio_calc = ScoreCalculator(min_ratio=0,   max_ratio=120, min_score=10, max_score=100, ascending=False)
        self.fcf_payout_ratio_calc      = ScoreCalculator(min_ratio=0,   max_ratio=120, min_score=10, max_score=100, ascending=False)
        self.debt_to_equity_ratio_calc  = ScoreCalculator(min_ratio=0,   max_ratio=20,  min_score=10, max_score=100, ascending=False)
        self.interest_coverage_ratio_calc = ScoreCalculator(min_ratio=0, max_ratio=10,  min_score=10, max_score=100, ascending=True)
        self.fcf_volatility_ratio_calc  = ScoreCalculator(min_ratio=0,   max_ratio=50,   min_score=20, max_score=100, ascending=False)
        self.growth_streak_calc         = ScoreCalculator(min_ratio=0,   max_ratio=25,  min_score=10, max_score=100, ascending=True)
        self.quick_ratio_calc           = ScoreCalculator(min_ratio=50,  max_ratio=200, min_score=20, max_score=100, ascending=True)
        self.cash_dividend_coverage_calc = ScoreCalculator(min_ratio=0, max_ratio=5,   min_score=20, max_score=100, ascending=True)

    def apply(self, df: pd.DataFrame) -> pd.DataFrame:
        # Earnings Payout Ratio
        df['earnings_payout_ratio'] = (df['dividend'] / df['net_income_adj']) * 100
        df['earnings_payout_ratio_score'] = self.earnings_payout_ratio_calc.calculate(df['earnings_payout_ratio'])

        # Free Cash Flow Payout Ratio
        df['fcf_payout_ratio'] = (df['dividend'] / df['free_cashflow']) * 100
        df['fcf_payout_ratio_score'] = self.fcf_payout_ratio_calc.calculate(df['fcf_payout_ratio'])

        # Debt-to-Equity Ratio
        df['debt_to_equity_ratio'] = (df['total_debt'] / df['total_shareholder_equity']) * 100
        df['debt_to_equity_ratio_score'] = self.debt_to_equity_ratio_calc.calculate(df['debt_to_equity_ratio'])

        # Interest Coverage Ratio
        df['interest_coverage_ratio'] = (df['ebit'] / df['interest_expense']) * 100
        df['interest_coverage_ratio_score'] = self.interest_coverage_ratio_calc.calculate(df['interest_coverage_ratio'])

        # Free Cash Flow Volatility Ratio
        df['fcf_volatility_ratio'] = (df['free_cashflow'].std() / df['free_cashflow'].mean()) * 100
        df['fcf_volatility_ratio_score'] = self.fcf_volatility_ratio_calc.calculate(df['fcf_volatility_ratio'])

        # Dividend Growth Streak (TTM)
        df['dividend_ttm_growth_streak'] = DividendGrowthStreak().transform(df['dividend_ttm'])
        df['dividend_ttm_growth_streak_score'] = self.growth_streak_calc.calculate(df['dividend_ttm_growth_streak'])

        # Quick Ratio
        df['quick_ratio'] = ((df['cash_and_cash_equivalents'] + df['current_net_receivables']) / df['current_liabilities']) * 100
        df['quick_ratio_score'] = self.quick_ratio_calc.calculate(df['quick_ratio'])

        # Cash Dividend Coverage
        df['cash_dividend_coverage'] = CashDividendCoverageCalculator(
            df['cash_and_cash_equivalents'], df['dividend']
        ).compute()
        df['cash_dividend_coverage_score'] = self.cash_dividend_coverage_calc.calculate(df['cash_dividend_coverage'])

        # Composite Dividend Safety Score
        df['dividend_safety_score'] = (
            df['earnings_payout_ratio_score']  * 0.15 +
            df['fcf_payout_ratio_score']       * 0.15 +
            df['debt_to_equity_ratio_score']   * 0.10 +
            df['interest_coverage_ratio_score']* 0.10 +
            df['fcf_volatility_ratio_score']   * 0.10 +
            df['dividend_ttm_growth_streak_score'] * 0.10 +
            df['quick_ratio_score']            * 0.05 +
            df['cash_dividend_coverage_score'] * 0.05
        )
        return df



