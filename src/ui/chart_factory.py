# src/chart_factory.py
import logging
import streamlit as st
import pandas as pd
import altair as alt

from src.ui.year_chart import YearChart
from config.RuleConfig  import RuleConfig


class ConsoiidatedDataChartFactory:

    def __init__(self, df: pd.DataFrame, logger: logging.Logger):
        self.df = df
        self.logger = logger
        # A placeholder so old charts get wiped out cleanly on ticker change
        self.subhead = st.empty()
        self.controls = st.empty()
        self.chart_slot1 = st.empty()
        self.chart_slot2 = st.empty()

    
    def _select_date_range(self) -> int | None:
        """
        Render a dropdown to select the date range: 1y, 3y, 5y, 10y, or All
        Returns the number of years or None for all.
        """
        options = {
            'All': None,
            '1 Year': 1,
            '3 Years': 3,
            '5 Years': 5,
            '10 Years': 10,
        }
        choice = self.controls.selectbox(
            'Select date range:',
            list(options.keys()),
            index=0,
            key='date_range_selector'
        )
        return options[choice]
   
    def chart(self, rule: RuleConfig, ticker: str) -> list[alt.Chart]:
        self.logger.info(f"{rule.head} rendered for {ticker}.")
        df_t = self.df[self.df['symbol'] == ticker].copy().reset_index(drop=True)
        yc = YearChart(df_t, self.logger)

        charts: list[alt.Chart] = []
        for chart_conf in rule.charts:
            c = yc.plot(
                ticker=ticker,
                config=chart_conf)
            charts.append(c)
        return charts

    def create_chart(self, rule_card: RuleConfig, ticker: str): 
        # fill the placeholders
        self.subhead.markdown(f"_{rule_card.subhead}_")

        # Date range selector control
       # x = self._select_date_range()

        # Generate charts
        charts = self.chart(rule=rule_card, ticker=ticker)

        if charts:
            self.chart_slot1.altair_chart(charts[0], use_container_width=True)
        if len(charts) > 1:
            self.chart_slot2.altair_chart(charts[1], use_container_width=True)
