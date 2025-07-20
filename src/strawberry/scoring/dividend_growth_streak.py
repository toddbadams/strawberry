import pandas as pd

class DividendGrowthStreak:
    """
    Compute the run of consecutive periods where dividends strictly grow.
    """
    def __init__(self):
        # No parameters needed for now
        pass

    def transform(self, div: pd.Series) -> pd.Series:
        """
        Parameters
        ----------
        div : pd.Series
            A series of dividend values (e.g. TTM), indexed by period and sorted ascending.

        Returns
        -------
        pd.Series
            A series with the same index as `div`, where each value is the number
            of consecutive prior periods with strictly growing dividends.
        """
        # Boolean mask: True where current > previous
        growth = div > div.shift(1)
        # First element has no prior, so mark as False
        growth.iloc[0] = False

        # Assign group ids: increment whenever growth is False (streak reset)
        group_id = (~growth).cumsum()

        # Cumulative sum of True values within each group gives the streak length
        streak = growth.groupby(group_id).cumsum().astype(int)
        streak.name = 'dividend_growth_streak'
        return streak




