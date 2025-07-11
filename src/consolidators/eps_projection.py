from typing import List, Optional, Union, Dict, Any
import pandas as pd

class EPSProjection:
    def __init__(
        self,
        historical_eps_df: pd.DataFrame,
        date_col: str = 'qtr_end_date',
        eps_col: str = 'eps'):
        """
        Initialize with historical EPS DataFrame containing quarterly EPS and dates.
        :param historical_eps_df: DataFrame with columns for dates and EPS values.
        :param date_col: Name of the date column.
        :param eps_col: Name of the EPS column.
        """
        df = historical_eps_df.copy()
        df[date_col] = pd.to_datetime(df[date_col])
        df.set_index(date_col, inplace=True)
        df.sort_index(inplace=True)
        self.eps_series: pd.Series = df[eps_col].astype(float)

    def yoy_growth(self) -> pd.Series:
        """
        Calculate year-over-year quarterly growth rates (compare each quarter to the same quarter last year).
        :return: pandas Series of YoY growth rates indexed by date.
        Using the most recent YoY growth rate (i.e. the change from the same quarter last year) as your projected 
        annual EPS growth can be a simple starting point, but it has limitations:

            Single‑Period Volatility: Quarterly earnings can be lumpy due to one‑off items, seasonality, or 
            accounting adjustments. A single YoY figure may over‑ or under‑state the underlying trend.

            Smoothing with Multi‑Year Averages: Consider averaging YoY rates over several quarters or years to smooth 
            out volatility:
                avg_yoy = eps_proj.yoy_growth().dropna().rolling(window=4).mean().iloc[-1]

            Aligning with Business Cycle: Ensure your projection aligns with any known turning points 
            (e.g., product launches, economic cycles).

            Using Analyst Consensus: For more credibility, supplement your model with sell‑side or sell‑side 
            forecasts, which often reflect forward‑looking insights.

            Rule of Thumb: If your latest YoY falls within the range of your 3‑year average and analyst targets, it can 
            serve as a plausible projection. Otherwise, adjust your rate to reflect longer‑term trends or consensus views.
        """
        return self.eps_series.pct_change(periods=4)

    def cagr(self, start: pd.Timestamp, end: pd.Timestamp) -> float:
        """
        Calculate the Compound Annual Growth Rate (CAGR) between two dates.
        :param start_date: Start date as Timestamp.
        :param end_date: End date as Timestamp.
        :return: CAGR as a float.
        """
        eps_start: float = self.eps_series.loc[start]
        eps_end: float = self.eps_series.loc[end]
        years: float = (end - start).days / 365.25
        return (eps_end / eps_start) ** (1 / years) - 1

    def project(self, rate: float, periods: Union[int, List[int]]) -> pd.Series:
        """
        Project future EPS given an annual growth rate.
        :param rate: Annual growth rate as float (e.g., 0.10 for 10%).
        :param periods: Number of years (int) or list of years ahead (List[int]).
        :return: pandas Series of projected EPS values indexed by future dates (annual intervals).
        """
        last_date = self.eps_series.index[-1]
        last_eps: float = self.eps_series.iloc[-1]
        years_list: List[int] = [periods] if isinstance(periods, int) else periods
        projections: Dict[pd.Timestamp, float] = {}
        for n in years_list:
            future_date = last_date + pd.DateOffset(years=n)
            projections[future_date] = last_eps * ((1 + rate) ** n)
        return pd.Series(projections)

    def calculate(self) -> pd.DataFrame:
        """
        For each quarter in the historical series:
        - YOY growth (past 4 quarters)
        - CAGR (past 20 quarters)
        - Smoothed YOY (rolling average of past 20 quarters)
        - Projected EPS = eps * (1 + smooth_yoy)
        :return: DataFrame 
        """
        eps = self.eps_series
        df = pd.DataFrame({'eps': eps})
        # Year-over-Year growth (4-quarter)
        df['eps_yoy'] = eps.pct_change(periods=4)

        # CAGR over past 20 quarters (approx. 5 years)
        cagr_values: List[Optional[float]] = []
        for i in range(len(eps)):
            if i >= 20:
                start_eps: float = eps.iloc[i-20]
                end_eps: float = eps.iloc[i]
                years: float = 20 / 4
                cagr_values.append((end_eps / start_eps) ** (1 / years) - 1)
            else:
                cagr_values.append(None)
        df['eps_cagr'] = cagr_values

        # Smooth YOY with rolling window of 20 quarters
        df['eps_smooth_yoy'] = df['eps_yoy'].rolling(window=20, min_periods=1).mean()

        # Project EPS using smoothed YOY
        df['projected_eps_growth_rate'] = df['eps'] * (1 + df['eps_smooth_yoy'])

        # drop eps column
        df.drop('eps', axis=1, inplace=True)

        return df