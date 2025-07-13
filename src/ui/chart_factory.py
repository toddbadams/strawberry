# src/chart_factory.py
import logging
import streamlit as st
import pandas as pd
import altair as alt

from src.ui.year_chart import YearChart


class ConsoiidatedDataChartFactory:

    def __init__(self, df: pd.DataFrame, logger: logging.Logger):
        self.df = df
        self.logger = logger
        # A placeholder so old charts get wiped out cleanly on ticker change
        self.head = st.empty()
        self.subhead = st.empty()
        self.chart_slot1 = st.empty()
        self.chart_slot2 = st.empty()

    def dividend_growth_chart(self, ticker: str) -> list[alt.Chart]:
        self.logger.info(f"Dividend Growth Chart Rendered for {ticker}.")
        df = self.df[self.df["symbol"] == ticker].copy().reset_index()
        c = YearChart(df, self.logger)

        chart1 = c.plot(ticker = ticker, 
                     title='Compound annual dividend growth rate over the past 5 years',
                     metrics=['dividend_growth_rate_5y'],
                     y_label='yeild %')

        return [chart1]

    def dividend_chowder_chart(self, ticker: str) -> list[alt.Chart]:
        self.logger.info(f"Dividend Chowder Chart Rendered for {ticker}.")
        df = self.df[self.df["symbol"] == ticker].copy().reset_index()
        c = YearChart(df, self.logger)

        chart1 = c.plot(ticker = ticker, 
                     title='Dividend Yield + 5-Year Dividend Growth Rate',
                     metrics=['dividend_chowder_yield'],
                     y_label='yeild %')

        return [chart1]

    def dividend_yield_chart(self, ticker: str):
        df = self.df[self.df["symbol"] == ticker].copy().reset_index()
        c = YearChart(df, self.logger)

        chart1 = c.plot(ticker = ticker, 
                     title='Dividend Yield vs. 5-Year Historical Average',
                     metrics=['dividend_yield', 'yield_historical_mean_5y'],
                     y_label='yeild %')

        chart2 = c.plot(ticker = ticker, 
                     title='Dividend Yield Z Score',
                     metrics=['yield_zscore'],
                     y_label='z score')
        return [chart1, chart2]

    def value_estimate_chart(self, ticker: str) -> list[alt.Chart]:
        self.logger.info(f"Value Estimation Chart Rendered for {ticker}.")
        df = self.df[self.df["symbol"] == ticker].copy().reset_index()
        c = YearChart(df, self.logger)

        chart1 = c.plot(ticker = ticker, 
                     title='DCF and DDM value estimates (per share)',
                     metrics=['fair_value_dcf', 'fair_value_ddm', 'fair_value_blended', 'share_price'],
                     y_label='yeild %')

        chart2 = c.plot(ticker = ticker, 
                     title='Fair Value Gap',
                     metrics=['fair_value_gap_pct'],
                     y_label='Gap (%)')
        return [chart1, chart2]

    def pe_value_chart(self, ticker: str) -> list[alt.Chart]:
        self.logger.info(f"P/E Valuation Chart Rendered for {ticker}.")
        df = self.df[self.df["symbol"] == ticker].copy().reset_index()
        c = YearChart(df, self.logger)

        chart1 = c.plot(ticker = ticker, 
                     title='P/E and PEG Ratios',
                     metrics=['pe_ratio', 'peg_ratio'],
                     y_label='ratio')

        return [chart1]

    def cash_conversion_chart(self, ticker: str) -> list[alt.Chart]:
        self.logger.info(f"Cash Conversion Chart Rendered for {ticker}.")
        df = self.df[self.df["symbol"] == ticker].copy().reset_index()
        c = YearChart(df, self.logger)

        chart1 = c.plot(ticker = ticker, 
                     title='Earnings-to-free-cash-flow ratio ',
                     metrics=['ebitda_to_fcflow'],
                     y_label='ratio')

        return [chart1]

    def peg_health_chart(self, ticker: str) -> list[alt.Chart]:
        self.logger.info(f"PEG Health Chart Rendered for {ticker}.")
        df = self.df[self.df["symbol"] == ticker].copy().reset_index()
        c = YearChart(df, self.logger)

        chart1 = c.plot(ticker = ticker, 
                     title='PEG ratio ',
                     metrics=['peg_ratio'],
                     y_label='ratio')

        return [chart1]

    def earning_premium_chart(self, ticker: str) -> list[alt.Chart]:
        self.logger.info(f"Earning Premium Chart Rendered for {ticker}.")
        df = self.df[self.df["symbol"] == ticker].copy().reset_index()
        c = YearChart(df, self.logger)

        chart1 = c.plot(ticker = ticker, 
                     title='Earnings Yield',
                     metrics=['earnings_yield'],
                     y_label='yeild')

        return [chart1]

    def debt_cushion_chart(self, ticker: str) -> list[alt.Chart]:
        self.logger.info(f"Debt Cushion Chart Rendered for {ticker}.")
        return []

    def default_chart(self, ticker: str) -> list[alt.Chart]:
        self.logger.info(f"Default Chart Rendered for {ticker}.")
        return []

    def create_chart(self, head: str, subhead: str, ticker: str): 
        # Map each rule head to its plotting function
        mapping = {
            "Dividend Growth": self.dividend_growth_chart,
            "Dividend Chowder": self.dividend_chowder_chart,
            "Dividend Yield": self.dividend_yield_chart,
            "DCF/DDM Value": self.value_estimate_chart,
            "P/E Value": self.pe_value_chart,
            "Health Cash Conversion": self.cash_conversion_chart,
            "Health PEG": self.peg_health_chart,
            "Health Earning Premium": self.earning_premium_chart,
            "Health Debt Cushion": self.debt_cushion_chart,
        }
        # Select the appropriate function, defaulting if head is unknown
        plot_func = mapping.get(head, self.default_chart)

       # Reserve placeholders in exact order
        header_slot   = st.empty()
        subheader_slot= st.empty()
        chart_slot1   = st.empty()
        chart_slot2   = st.empty()

        # fill the placeholders
        # header_slot.header(head)
        subheader_slot.markdown(f"_{subhead}_")  # or subheader_slot.subheader(subhead)

        charts = plot_func(ticker)

        if len(charts) > 0:
            chart_slot1.altair_chart(charts[0], use_container_width=True)
        if len(charts) > 1:
            chart_slot2.altair_chart(charts[1], use_container_width=True)
