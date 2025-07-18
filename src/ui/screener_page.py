from src.ui.page import Page
import streamlit as st
import pandas as pd

class ScreenerPage(Page):

    def render(self):
        # define columns to display
        columns = [
            'symbol', 'year_quarter', 
            'earnings_payout_ratio_score', 'fcf_payout_ratio_score', 
            'debt_to_equity_ratio_score', 'interest_coverage_ratio_score', 'interest_coverage_ratio',
            'fcf_volatility_ratio', 'fcf_volatility_ratio_score', 'dividend_ttm_growth_streak', 'dividend_ttm_growth_streak_score', 
            'quick_ratio', 'quick_ratio_score', 'cash_dividend_coverage', 'cash_dividend_coverage_score', 'dividend_score'
        ]

        # header area
        header_cols = st.columns([3, 1])
        with header_cols[0]:
            st.header("📊 Screener Page")

        # Year / Quarter selection box
        with header_cols[1]:
            self.selected_year_quarter = st.selectbox("Select Date/Quarter", options=self.unique_year_quarters,
                index=0, key="selected_quarter")
            
        # filter DataFrame by selected quarter-end date
        df_filtered = self.consolidated_df[
            self.consolidated_df['year_quarter'] == self.selected_year_quarter
        ]

        # display filtered table
        st.dataframe(self.consolidated_df[columns], height=800)
