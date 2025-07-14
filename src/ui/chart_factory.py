# src/chart_factory.py
import logging
import streamlit as st
import pandas as pd
import altair as alt

from src.ui.year_chart import YearChart
from src.ui.rule import RuleConfig


class ConsoiidatedDataChartFactory:

    def __init__(self, df: pd.DataFrame, logger: logging.Logger):
        self.df = df
        self.logger = logger
        # A placeholder so old charts get wiped out cleanly on ticker change
        self.head = st.empty()
        self.subhead = st.empty()
        self.chart_slot1 = st.empty()
        self.chart_slot2 = st.empty()
   
    def chart(self, rule: RuleConfig, ticker: str) -> list[alt.Chart]:
        self.logger.info(f"{rule.head} Rendered for {ticker}.")
        df = self.df[self.df["symbol"] == ticker].copy().reset_index()
        c = YearChart(df, self.logger)

        charts = []

        for chart in rule.charts:
            c = c.plot(ticker = ticker, config=chart)
            charts.append(c)

        return charts

    def create_chart(self, rule_card: RuleConfig, ticker: str): 

       # Reserve placeholders in exact order
        subheader_slot= st.empty()
        chart_slot1   = st.empty()
        chart_slot2   = st.empty()

        # fill the placeholders
        subheader_slot.markdown(f"_{rule_card.subhead}_")  # or subheader_slot.subheader(subhead)

        charts = self.chart(rule=rule_card, ticker=ticker) # plot_func(ticker)

        if len(charts) > 0:
            chart_slot1.altair_chart(charts[0], use_container_width=True)
        if len(charts) > 1:
            chart_slot2.altair_chart(charts[1], use_container_width=True)
