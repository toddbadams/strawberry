import pandas as pd
from src.data.parquet_storage import ParquetStorage


class DividendConsolidator:

    def __init__(self, ps: ParquetStorage):
        self.storage = ps

        
    def consolidate(self, df: pd.DataFrame, ticker: str) -> pd.DataFrame:
        dv = self.storage.read_df("DIVIDENDS", ticker)
        # calc the fiscal date ending of each quarter
        dv['ex_dividend_date'] = pd.to_datetime(dv['ex_dividend_date'])  
        dv["fiscalDateEnding"] = (dv["ex_dividend_date"] + pd.offsets.QuarterEnd(0)) - pd.offsets.QuarterEnd()

        # sum the dividen amounts per quarter
        self._column_to_numeric(dv, 'amount')
        div_agg = (
            dv.groupby("fiscalDateEnding")["amount"]
            .sum()
            .reset_index()
            .rename(columns={"amount": "dividend"})
        )

        # merge on fiscalDateEnding
        df = df.merge(div_agg, on="fiscalDateEnding", how="left")
        return df

    def dividend_growth_rule(self, df: pd.DataFrame) -> pd.DataFrame:
        # or quarterly growth and then annualized
        df['qtr_growth'] = (df['dividend'] / df['dividend'].shift(20))**(1/20) - 1
        df['dividend_growth_rate_5y'] = (1 + df['qtr_growth'])**4 - 1
        return df
    
    def dividend_return_rule(self, df: pd.DataFrame) -> pd.DataFrame:
        # or quarterly growth and then annualized
        df['qtr_growth'] = (df['dividend'] / df['dividend'].shift(20))**(1/20) - 1
        df['dividend_growth_rate_5y'] = (1 + df['qtr_growth'])**4 - 1
        return df
           
    def dividend_yield_rule(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        High Relative Yield Rule
            – Dividend yield at least 1 σ (standard deviation) above its 5-year historical average.

        `rule_high_relative_yield`   | 🟢 True if dividend yield ≥ 1 σ above its 5-year historical average 
        `dividend_yield`             | Annual dividend per share ÷ share price                                      
        `yield_historical_mean_5y`   | 5-year historical average dividend yield                                     
        `yield_historical_std_5y`    | 5-year historical standard deviation of dividend yield                       
        `yield_zscore`               | (dividend\_yield – yield\_historical\_mean\_5y) ÷ yield\_historical\_std\_5y 
        """
        # Calculate TTM using trailing 4-period sum (current + previous 3)
        df[f"dividendTTM"] = df["dividend"].rolling(window=4).sum()
        # Dividend yield 
        df['dividend_yield'] = df['dividendTTM'] / df['sharePrice']
        # 20-quarter rolling (5-year) stats
        df['yield_historical_mean_5y'] = df['dividend_yield'].rolling(window=20, min_periods=1).mean()
        df['yield_historical_std_5y'] = df['dividend_yield'].rolling(window=20, min_periods=1).std()
        # Z-score  
        df['yield_zscore'] = (df['dividend_yield'] - df['yield_historical_mean_5y']) / df['yield_historical_std_5y']
        df['rule_high_relative_yield'] = df['yield_zscore'] >= 1
        # Define conditions in priority order
        conditions = [
            df['yield_zscore'] >=  2,                         # strong buy
            df['yield_zscore'] >=  1,                         # buy (1 ≤ z < 2)
            df['yield_zscore'] <= -2,                         # strong sell
            df['yield_zscore'] <= -1,                         # sell (-2 < z ≤ -1)
            (df['yield_zscore'] > -1) & (df['yield_zscore'] < 1)  # hold
        ]
        # Corresponding labels
        choices = [
            'strong buy',
            'buy',
            'strong sell',
            'sell',
            'hold'
        ]
        # Create the action column
        df['action_high_relative_yield'] = np.select(conditions, choices, default='hold')
        return df