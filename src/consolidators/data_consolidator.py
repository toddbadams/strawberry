import numpy as np
import pandas as pd
from typing import List
from src.consolidators.balance_sheet_consolidator import BalanceSheetConsolidator
from src.consolidators.cashflow_consolidator import CashflowConsolidator
from src.data.parquet_storage import ParquetStorage
from src.utils.calc_dcf_per_share_utils import *

class DataConsolidator:
    def __init__(self, data_path: str):
        self.storage = ParquetStorage(data_path)

    def _column_to_numeric(self, df: pd.DataFrame, col_name: str):
        """
        Convert a specified column in the DataFrame to numeric type, coercing errors to NaN.
        """
        # convert the column to numeric, coercing errors to NaN.
        df[col_name] = pd.to_numeric(df[col_name], errors='coerce')
        # Propagates the last known (non-NaN) value forward into subsequent NaNs.
        df[col_name].fillna(method='ffill', inplace=True)
        return df
    
    def _calc_per_share_TTM(self, df: pd.DataFrame, col_name: str) -> pd.DataFrame:
        # Calculate TTM using trailing 4-period sum (current + previous 3)
        df[f"{col_name}TTM"] = df[col_name].rolling(window=4).sum()
        # calculate per share TTM
        df[f"{col_name}PerShareTTM"] = (df[f"{col_name}TTM"] / df['sharesOutstanding']).round(2)
        # calculate average per share TTM for 5Y and 10Y
        df[f"{col_name}PerShareTTM_avg_5Y"] = df[f"{col_name}PerShareTTM"].rolling(window=20).mean().round(2)
        df[f"{col_name}PerShareTTM_avg_10Y"] = df[f"{col_name}PerShareTTM"].rolling(window=40).mean().round(2)
        # remove the TTM column
        df.drop(columns=[f"{col_name}TTM"], inplace=True) 
        return df
    
    def _merge_columns(self, df: pd.DataFrame, other_df: pd.DataFrame, selected_cols: List[str]) -> pd.DataFrame:
        other_df['fiscalDateEnding'] = pd.to_datetime(other_df['fiscalDateEnding'])
        df = df.merge(other_df[selected_cols], on='fiscalDateEnding', how='inner')
        return df

    def _quarterly_summary(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Given a DataFrame with columns:
        - 'date'               : dates (string or datetime)
        - '5. adjusted close'  : adjusted closing price
        
        Returns a DataFrame indexed by quarter-end date with:
        - 'sharePrice'          : last adjusted close of that quarter
        - 'fiscalDateEnding'    : same as the new index (quarter-end)
        """
        # Copy & ensure datetime
        df = df.copy()
        df['date'] = pd.to_datetime(df['date'])
        
        # Set date as index and sort
        df = df.set_index('date').sort_index()
        
        # Resample by calendar quarter-end
        q = df.resample('QE').agg({'5. adjusted close': 'last'})
                
        # Reset index so 'date' is a column again
        q = q.reset_index()
        
        # Tidy up column names
        q = q.rename(columns={'5. adjusted close' : 'sharePrice', 'date': 'fiscalDateEnding'})

        # set sharePrice and dividend to numeric, coercing errors to NaN
        q['sharePrice'] = pd.to_numeric(q['sharePrice'], errors='coerce').round(2)
        
        return q

    def __map_to_fiscal_date_ending(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Given a DataFrame with:
        - 'ex_dividend_date': date of dividend payment (datetime or string)
        - 'amount': dividend amount
        Returns a new DataFrame with:
        - 'fiscalDateEnding': the prior fiscal quarter-end date
        - 'amount': original dividend amount
        """
        df = df.copy()
        # Ensure payment_date is datetime
        df['ex_dividend_date'] = pd.to_datetime(df['ex_dividend_date'])        
        # Roll forward to the quarter-end containing ex_dividend_date
        current_qe = df['ex_dividend_date'] + pd.offsets.QuarterEnd(0)
        # Subtract one quarter-end to get the prior quarter-end
        df['fiscalDateEnding'] = current_qe - pd.offsets.QuarterEnd()
        
        return df[['fiscalDateEnding', 'amount']].rename(columns={'amount': 'dividend'})

    def __blance_sheet_columns(self, df: pd.DataFrame) -> pd.DataFrame:

        df['fiscalDateEnding'] = pd.to_datetime(df['fiscalDateEnding'], errors='coerce')    
        df.sort_values('fiscalDateEnding')
        df.rename(columns={'commonStockSharesOutstanding': 'sharesOutstanding'}, inplace=True)
        self._column_to_numeric(df, 'sharesOutstanding') 

        # create year and quarter
        df["year"] = df["fiscalDateEnding"].dt.year
        df["quarter"] = df["fiscalDateEnding"].dt.quarter
        df['year_quarter'] = (df["year"].astype(str).str[-2:] + 'QE' + df["quarter"].astype(str))

        return df
    
    def __merge_cashflow_columns(self, df: pd.DataFrame, cashflow_df: pd.DataFrame) -> pd.DataFrame:

        df = self._merge_columns(df, cashflow_df, ['fiscalDateEnding', 'operatingCashflow', 'capitalExpenditures'])
        df['operatingCashflow'] = df['operatingCashflow'].astype(float)
        df['capitalExpenditures'] = df['capitalExpenditures'].astype(float)

        # Calculate free cashflow:    FCF = Operating Cash Flow – Capital Expenditures
        df['freeCashflow'] = (df['operatingCashflow'] - df['capitalExpenditures'])
        self._calc_per_share_TTM(df, 'freeCashflow')
       
        # Remove columns that are not needed
        df.drop(columns=['operatingCashflow', 'capitalExpenditures', 'freeCashflow'], inplace=True)      
        return df

    def __merge_price_columns(self, df: pd.DataFrame, ps: pd.DataFrame) -> pd.DataFrame:
        ps['date'] = pd.to_datetime(ps['date'])  
        price_q = (
            ps.set_index("date")
            .resample("Q")["5. adjusted close"].last()
            .reset_index()
            .rename(columns={"date": "fiscalDateEnding", "5. adjusted close": "sharePrice"})
        )
        price_q["sharePrice"] = pd.to_numeric(price_q["sharePrice"], errors="coerce")
        df = df.merge(
            price_q[["fiscalDateEnding", "sharePrice"]],
            on="fiscalDateEnding", how="left"
        )
       
        df['sharePrice_avg_5Y'] = df['sharePrice'].rolling(window=20).mean()
        df['sharePrice_avg_10Y'] = df['sharePrice'].rolling(window=40).mean()
        return df
    
    def __high_relative_dividend_yield_rule(self, df: pd.DataFrame) -> pd.DataFrame:
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
    
    def __dividend_growth_rule(self, df: pd.DataFrame) -> pd.DataFrame:
        # or quarterly growth and then annualized
        df['qtr_growth'] = (df['dividend'] / df['dividend'].shift(20))**(1/20) - 1
        df['dividend_growth_rate_5y'] = (1 + df['qtr_growth'])**4 - 1
        return df

    def __merge_dividend_columns(self, df: pd.DataFrame, dv: pd.DataFrame) -> pd.DataFrame:
        dv['ex_dividend_date'] = pd.to_datetime(dv['ex_dividend_date'])  
        dv["fiscalDateEnding"] = (
            dv["ex_dividend_date"] + pd.offsets.QuarterEnd(0)
        ) - pd.offsets.QuarterEnd()
        self._column_to_numeric(dv, 'amount')
        div_agg = (
            dv.groupby("fiscalDateEnding")["amount"]
            .sum()
            .reset_index()
            .rename(columns={"amount": "dividend"})
        )
        df = df.merge(div_agg, on="fiscalDateEnding", how="left")

        df = self.__high_relative_dividend_yield_rule(df)
        df = self.__dividend_growth_rule(df)

        # Combined yield + growth
        df['dividend_yield_plus_growth'] = (df['dividend_yield'] + df['dividend_growth_rate_5y'])
        return df

    def __merge_earnings_columns(self, df: pd.DataFrame, er: pd.DataFrame) -> pd.DataFrame:
        er_sel = er[["fiscalDateEnding", "reportedEPS", "estimatedEPS", "surprisePercentage"]].copy()
        er_sel['fiscalDateEnding'] = pd.to_datetime(er_sel['fiscalDateEnding'])  
        for col in ["reportedEPS", "estimatedEPS", "surprisePercentage"]:
            er_sel[col] = pd.to_numeric(er_sel[col], errors="coerce")
        df = df.merge(er_sel, on="fiscalDateEnding", how="left")
        return df

    def __merge_income_columns(self, df: pd.DataFrame, inc: pd.DataFrame) -> pd.DataFrame:
        inc_sel = inc[["fiscalDateEnding", "netIncome", "ebit", "ebitda"]].copy()
        inc_sel['fiscalDateEnding'] = pd.to_datetime(inc_sel['fiscalDateEnding'])  
        for col in ["netIncome", "ebit", "ebitda"]:
            inc_sel[col] = pd.to_numeric(inc_sel[col], errors="coerce")
        df = df.merge(inc_sel, on="fiscalDateEnding", how="left")
        return df

    def __merge_insider_trading_columns(self, df: pd.DataFrame, ins: pd.DataFrame) -> pd.DataFrame:
        ins['transaction_date'] = pd.to_datetime(ins['transaction_date'], errors='coerce')  
        ins["year"] = ins["transaction_date"].dt.year
        ins["quarter"] = ins["transaction_date"].dt.quarter
        ins["net_shares"] = ins.apply(
            lambda r: r["shares"] if r["acquisition_or_disposal"] == "acquisition" 
                      else -pd.to_numeric(r["shares"], errors="coerce"),
            axis=1
        )
        ins_agg = (
            ins.groupby(["year", "quarter"])["net_shares"]
            .sum()
            .reset_index()
            .rename(columns={"net_shares": "insider_net_shares"})
        )
        df = df.merge(ins_agg, on=["year", "quarter"], how="left")

        return df

    def __calc_DCF(self, df: pd.DataFrame) -> pd.DataFrame:
            df['fair_value_dcf'] =  calc_dcf_per_share(df['freeCashflowPerShareTTM'], df['sharesOutstanding'], 0.1, 0.775, 5, 0.03)
            return df

    def consolidate(self, symbol: str) -> pd.DataFrame:
        """
        Consolidate data from multiple sources into a single DataFrame.
        This method should be implemented to read from various data sources,
        process the data, and return a consolidated DataFrame.
        """
        # Read data frames from storage
        bs = self.storage.read_df("BALANCE_SHEET", symbol)
        cf = self.storage.read_df("CASH_FLOW", symbol)
        ps = self.storage.read_df("TIME_SERIES_MONTHLY_ADJUSTED", symbol)
        dv = self.storage.read_df("DIVIDENDS", symbol)
        er = self.storage.read_df("EARNINGS", symbol)
        inc = self.storage.read_df("INCOME_STATEMENT", symbol)
        ins = self.storage.read_df("INSIDER_TRANSACTIONS", symbol)


        # Merge and process data as needed
        df = self.__blance_sheet_columns(bs)
        df = self.__merge_cashflow_columns(df, cf)
        df = self.__merge_price_columns(df, ps)
        df = self.__merge_dividend_columns(df, dv)
        df = self.__merge_earnings_columns(df, er) 
        df = self.__merge_income_columns(df, inc)
        df = self.__merge_insider_trading_columns(df, ins)

        # rule calculations
        df = self.__high_relative_dividend_yield_rule(df)
        df = self.__dividend_growth_rule(df)

        # Combined yield + growth
        df['dividend_yield_plus_growth'] = (df['dividend_yield'] + df['dividend_growth_rate_5y'])
        df = self.__calc_DCF(df)

        df["symbol"] = symbol
        df.sort_values('fiscalDateEnding')
        self.storage.write_df(df, "CONSOLIDATED", partition_cols=["symbol"], index=False)

    def consolidate2(self, ticker: str):
        """
        Consolidate data from multiple sources into a single DataFrame.
        This method should be implemented to read from various data sources,
        process the data, and return a consolidated DataFrame.
        """
        bs = BalanceSheetConsolidator(self.storage)
        cf = CashflowConsolidator(self.storage)
        
        df = bs.consolidate(ticker)
        df = cf.consolidate(df, ticker)