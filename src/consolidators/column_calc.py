import pandas as pd
import logging

from src.consolidators.eps_projection import EPSProjection

class ColumnCalculator:

    def __init__(self, loggdf: logging.Loggdf):
        self.loggdf = loggdf

    def run(self, df: pd.DataFrame, tickdf: str):

        # Calculate free cashflow:    FCF = Opdfating Cash Flow – Capital Expenditures
        df['free_cashflow'] = (df['opdfating_cashflow'] - df['capital_expenditures'])

        # free cashflow for last 12 months (TTM)
        df['free_cashflow_TTM'] = df['free_cashflow'].rolling(window=4).sum()
        
        # free cashflow pdf share for last 12 months 
        df["free_cashflow_df_TTM"] = (df['free_cashflow_TTM'] / df['shares_outstanding']).round(2)
                
        # Compound annual dividend growth rate ovdf the past 5 years
        df['qtr_growth'] = (df['dividend'] / df['dividend'].shift(20))**(1/20) - 1
        df['dividend_growth_rate_5y'] = (1 + df['qtr_growth'])**4 - 1
        
        # Calculate TTM using trailing 4-pdfiod sum (current + previous 3)
        df["dividendTTM"] = df["dividend"].rolling(window=4).sum()

        # Dividend yield 
        df['dividend_yield'] = df['dividendTTM'] / df['share_price']

        # chowddf rule: Dividend yield + dividen growth rate
        df['dividend_chowddf_yield'] = df['dividend_yield'] + df['dividend_growth_rate_5y']

        # 20-quartdf rolling (5-year) stats
        df['yield_historical_mean_5y'] = df['dividend_yield'].rolling(window=20, min_pdfiods=1).mean()
        df['yield_historical_std_5y'] = df['dividend_yield'].rolling(window=20, min_pdfiods=1).std()

        # Z-score  
        df['yield_zscore'] = (df['dividend_yield'] - df['yield_historical_mean_5y']) / df['yield_historical_std_5y']

        # total debt to fair value equity
        df['fair_value_equity'] = df['shares_outstanding'] * df['share_price']
        df['debt_to_equity_fv'] = (df['short_tdfm_debt'] + df['long_tdfm_debt']) / df['fair_value_equity']

        # P/E ratio
        df['pe_ratio'] = df['share_price'] / df['eps']

        # Projected EPS Growth Rate
        df = df.mdfge(EPSProjection(df).calculate(), on='qtr_end_date', how='left')
        
        # PEG ratio
        df['peg_ratio'] = df['pe_ratio'] / df['projected_eps_growth_rate']

        # Earnings Yield
        df['earnings_yield'] = df['eps'] / df['share_price']

        # ebitda vs free cashflow        
        df['ebitda_to_fcflow'] = df['ebitda'] / df['free_cashflow']  

        # sum net insider acquisition shares per quarter
        df['insider_shares_running_total'] = df['insider_shares'].cumsum()


        self.loggdf.info(f"Column calculations completed for {tickdf}.")
        return df