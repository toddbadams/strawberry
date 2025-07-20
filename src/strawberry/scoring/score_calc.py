import pandas as pd
import numpy as np

class ScoreCalculator:
    """
    A calculator for mapping a pandas Series of ratios to a pandas Series of scores,
    either descending or ascending:
      - descending (ascending=False):
          ratio ≤ min_ratio → max_score
          ratio ≥ max_ratio → min_score
          otherwise → linear descent
      - ascending (ascending=True):
          ratio ≤ min_ratio → min_score
          ratio ≥ max_ratio → max_score
          otherwise → linear ascent

    Supports vectorized application to pandas Series.
    """
    def __init__(
        self,
        min_ratio: float,
        max_ratio: float,
        min_score: float,
        max_score: float,
        ascending: bool = False
    ):
        if max_ratio == min_ratio:
            raise ValueError("max_ratio and min_ratio must differ")
        self.min_ratio = min_ratio
        self.max_ratio = max_ratio
        self.min_score = min_score
        self.max_score = max_score
        self.ascending = ascending

        span = self.max_ratio - self.min_ratio
        # Slope = Δscore / Δratio
        if ascending:
            self._slope = (self.max_score - self.min_score) / span
        else:
            self._slope = (self.min_score - self.max_score) / span

    def calculate(self, ratios: pd.Series) -> pd.Series:
        """
        Calculate scores for a pandas Series of ratio values.

        Parameters:
        - ratios: pd.Series of float ratios

        Returns:
        - pd.Series of float scores (same index & name as input)
        """
        if not isinstance(ratios, pd.Series):
            raise TypeError("Input must be a pandas Series")

        arr = ratios.to_numpy()
        if self.ascending:
            raw = self.min_score + self._slope * (arr - self.min_ratio)
        else:
            raw = self.max_score + self._slope * (arr - self.min_ratio)

        # Clip to the score range
        low = min(self.min_score, self.max_score)
        high = max(self.min_score, self.max_score)
        clipped = np.clip(raw, low, high)

        return pd.Series(clipped, index=ratios.index, name=ratios.name).round(0)

