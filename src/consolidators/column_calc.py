import pandas as pd
import logging

from src.consolidators.dcf_calculator import DCFCalculator
from src.consolidators.ddm_calculator import DDMCalculator
from src.consolidators.eps_projection import EPSProjection

class ColumnCalculator:

    def __init__(self, logger: logging.Logger):
        self.logger = logger

    def run(self, df: pd.DataFrame, ticker: str) -> pd.DataFrame:
        # sort by date
        df.sort_values('qtr_end_date')
        df.reset_index()

        # Calculate free cashflow:    FCF = operating Cash Flow – Capital Expenditures
        df['free_cashflow'] = (df['operating_cashflow'] - df['capital_expenditures'])

        # free cashflow for last 12 months (TTM)
        df['free_cashflow_TTM'] = df['free_cashflow'].rolling(window=4).sum()
        
        # free cashflow ps share for last 12 months 
        df["free_cashflow_ps_TTM"] = (df['free_cashflow_TTM'] / df['shares_outstanding']).round(2)
                
        # Compound annual dividend growth rate ovdf the past 5 years
        df['qtr_growth'] = (df['dividend'] / df['dividend'].shift(20))**(1/20) - 1
        df['dividend_growth_rate_5y'] = (1 + df['qtr_growth'])**4 - 1
        
        # Calculate TTM using trailing 4-period sum (current + previous 3)
        df["dividend_ttm"] = df["dividend"].rolling(window=4).sum()

        # Dividend yield 
        df['dividend_yield'] = df['dividend_ttm'] / df['share_price']

        # chowder rule: Dividend yield + dividen growth rate
        df['dividend_chowder_yield'] = df['dividend_yield'] + df['dividend_growth_rate_5y']

        # 20-quarter rolling (5-year) stats
        df['yield_historical_mean_5y'] = df['dividend_yield'].rolling(window=20, min_periods=1).mean()
        df['yield_historical_std_5y'] = df['dividend_yield'].rolling(window=20, min_periods=1).std()

        # Z-score  
        df['yield_zscore'] = (df['dividend_yield'] - df['yield_historical_mean_5y']) / df['yield_historical_std_5y']

        # total debt to fair value equity
        df['fair_value_equity'] = df['shares_outstanding'] * df['share_price']
        df['total_debt'] = df['short_term_debt'] + df['long_term_debt']
        df['debt_to_equity_fv'] = (df['total_debt']) / df['fair_value_equity']

        # P/E ratio
        df['pe_ratio'] = df['share_price'] / df['eps']

        # Projected EPS Growth Rate
        df = df.merge(EPSProjection(df).calculate(), on='qtr_end_date', how='left')
        
        # PEG ratio
        df['peg_ratio'] = df['pe_ratio'] / df['projected_eps_growth_rate']

        # Earnings Yield
        df['earnings_yield'] = df['eps'] / df['share_price']

        # ebitda vs free cashflow        
        df['ebitda_to_fcflow'] = df['ebitda'] / df['free_cashflow']  

        # Compute cumulative sum of quarterly insider_shares
        df['cumulative_insider_shares'] = df['insider_shares'].cumsum()

        # DCF valuation
        df['fair_value_dcf'] = DCFCalculator().calc(cashflow_series = df['free_cashflow_ps_TTM'], 
                                                        shares_series = df['share_price'])

        # DDM valuation
        df['fair_value_ddm'] = DDMCalculator().calc(dividend_series = df['dividend'])

        # DCF / DDM blended value
        df['fair_value_blended'] = (df['fair_value_dcf'] +  df['fair_value_ddm']) / 2

        # fair value gap
        df['fair_value_gap_pct'] = (df['fair_value_blended'] - df['share_price']) / df['fair_value_blended']

        # Net Income Adjusted
        # normalized tax rate is 0.15  TBD: extract to config
        df['net_income_adj'] = df['income_before_tax'] - (0.15 * df['income_before_tax'])

        self.logger.info(f"Column calculations completed for {ticker}.")
        return df