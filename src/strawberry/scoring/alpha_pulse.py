import pandas as pd
from .score_calc import ScoreCalculator

class AlphaPulseScoring:
    """
    Extracts and applies Alpha Pulse scoring metrics to a DataFrame.
    """
    def __init__(self, weights: dict = None):
        # Initialize ScoreCalculators for each factor
        self.roa_calc = ScoreCalculator(min_ratio=5, max_ratio=20, min_score=0, max_score=100, ascending=True)
        self.rev_growth_calc = ScoreCalculator(min_ratio=0, max_ratio=0.3, min_score=0, max_score=100, ascending=True)
        self.de_ratio_calc = ScoreCalculator(min_ratio=50, max_ratio=200, min_score=0, max_score=100, ascending=False)
        self.ey_calc = ScoreCalculator(min_ratio=2, max_ratio=10, min_score=0, max_score=100, ascending=True)
        self.momentum_calc = ScoreCalculator(min_ratio=-0.1, max_ratio=0.5, min_score=0, max_score=100, ascending=True)
        self.volatility_calc = ScoreCalculator(min_ratio=5, max_ratio=15, min_score=0, max_score=100, ascending=False)

        # Default weights for composite score
        default_weights = {
            'return_on_assets_ratio_score': 0.20,
            'revenue_growth_score': 0.20,
            'debt_to_equity_ratio_score': 0.15,
            'earnings_yield_score': 0.15,
            'momentum_score': 0.20,
            'return_on_assets_volatility_score': 0.10
        }

        # Validate and set weights
        if weights is None:
            self.weights = default_weights
        else:
            if set(weights.keys()) != set(default_weights.keys()):
                raise ValueError(f"Weight config must contain exactly these keys: {set(default_weights.keys())}")
            total = sum(weights.values())
            if abs(total - 1.0) > 1e-8:
                raise ValueError("Sum of all weights must equal 1.0")
            if any(v < 0 for v in weights.values()):
                raise ValueError("All weights must be non-negative")
            self.weights = weights

    def apply(self, df: pd.DataFrame) -> pd.DataFrame:
        # 1. Return on Assets
        df['return_on_assets_ratio'] = (df['net_income'] / df['total_assets']) * 100
        df['return_on_assets_ratio_score'] = self.roa_calc.calculate(df['return_on_assets_ratio'])

        # 2. Quarterly Revenue Growth
        df['revenue_growth'] = (df['revenue'] - df['revenue'].shift(4)) / df['revenue'].shift(4)
        df['revenue_growth_score'] = self.rev_growth_calc.calculate(df['revenue_growth'])

        # 3. Debt / Equity Ratio
        df['debt_to_equity_ratio'] = (df['total_debt'] / df['total_shareholder_equity']) * 100
        df['debt_to_equity_ratio_score'] = self.de_ratio_calc.calculate(df['debt_to_equity_ratio'])

        # 4. Earnings Yield
        df['earnings_yield'] = (df['eps'] / df['share_price']) * 100
        df['earnings_yield_score'] = self.ey_calc.calculate(df['earnings_yield'])

        # 5. Price Surge (Momentum)
        df['momentum'] = (df['share_price'] - df['share_price'].shift(4)) / df['share_price'].shift(4)
        df['momentum_score'] = self.momentum_calc.calculate(df['momentum'])

        # 6. ROA Volatility
        df['return_on_assets_volatility'] = df['return_on_assets_ratio'].rolling(window=8).std()
        df['return_on_assets_volatility_score'] = self.volatility_calc.calculate(df['return_on_assets_volatility'])

        # Composite Alpha Pulse Score
        df['alpha_pulse_score'] = (
            df['return_on_assets_ratio_score']  * self.weights['return_on_assets_ratio_score'] +
            df['revenue_growth_score']          * self.weights['revenue_growth_score'] +
            df['debt_to_equity_ratio_score']    * self.weights['debt_to_equity_ratio_score'] +
            df['earnings_yield_score']          * self.weights['earnings_yield_score'] +
            df['momentum_score']                * self.weights['momentum_score'] +
            df['return_on_assets_volatility_score'] * self.weights['return_on_assets_volatility_score']
        )

        return df
