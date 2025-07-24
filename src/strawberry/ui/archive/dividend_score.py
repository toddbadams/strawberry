import logging
import streamlit as st
import streamlit_shadcn_ui as ui
import pandas as pd

from config.RuleConfig import RuleConfig
from src.config.config_loader import ConfigLoader
from src.ui.chart_factory import ConsoiidatedDataChartFactory
from src.ui.year_chart import YearChart


class DividendScoreDashboard:
    """
    Encapsulates the rendering logic for the Dividend Score dashboard.
    """
    def __init__(self, tickers: list[str], 
                 consolidated_df: pd.DataFrame, 
                 overview_df: pd.DataFrame,
                 config_loader: ConfigLoader,                  
                 logger: logging.Logger):
        self.tickers = tickers
        self.logger = logger
        self.consolidated_df = consolidated_df
        self.overview_df = overview_df
        self.config_loader = config_loader
        # will be set in run()
        self.selected_ticker: str | None = None
        
        # load config of parameters
        self.params = self.config_loader.load_dividend_params()
        self.params_df = pd.DataFrame(self.params,
                                      columns=['name','description','raw_value','raw_score','weight'])
        
        
        # chart factory
        self.chart_factory = ConsoiidatedDataChartFactory(consolidated_df, self.logger)
        self.rule = self.config_loader.load_dividend_score_rules()[0]

        # scaffold the layout
        # Header area
        self.header_cols = st.columns([2, 1, 1])
        with self.header_cols[1]:
            self.selected_ticker = st.empty
        with self.header_cols[2]:
            self.selected_quarter = st.empty        
        # Main area
        self.row2_cols = st.columns([1, 4])
        with self.row2_cols[0]:
            self.row2_col1 = st.empty
        with self.row2_cols[1]:
            self.row2_col2 = st.empty

        # Chart Area
        self.row3_cols = st.columns([1])
        with self.row3_cols[0]:
            self.chart = st.empty
            self.table = st.empty

    def render(self):
        self.logger.info("Dividend score dashboard selected.")
        # Dummy data
        dividend_score = 82

        # Header
        
        with self.header_cols[1]:
            self.selected_ticker = st.selectbox("Select Ticker", self.tickers)
        
        with self.header_cols[2]:
            self.selected_quarter = st.selectbox("Select Date/Quarter", ["Q1 2025", "Q2 2025", "Q3 2025"])

        # filter the consolidate table        
        df = self.consolidated_df[self.consolidated_df['symbol'] == self.selected_ticker].copy().reset_index(drop=True)
        yc = YearChart(df, self.logger)

        # display selected ticker details
        overview_row = self.overview_df.loc[self.overview_df["symbol"] == self.selected_ticker].iloc[0]

        with self.header_cols[0]:
            if not overview_row.empty:
                st.markdown(f"# {overview_row['Name']} ({overview_row['Exchange']}: {overview_row['symbol']})")
                st.markdown(f"{overview_row["Description"]}   {overview_row['Name']} is in the **{overview_row['Sector']}** sector, in **{overview_row['Industry']}**.")
            else:
                st.warning("No overview data for this ticker.")

        # Main Area
        with self.row2_cols[0]:
            st.metric(
                label="Composite Score",
                value=f"{dividend_score} / 100",
                help="How likely a company is to maintain its dividend over a full economic cycle.",
                border=True)
        with self.row2_cols[1]:
            st.table(self.params_df)

        # Chart
        with self.row3_cols[0]:
            st.markdown(f"## {self.rule.head}")
            self.chart = st.altair_chart(yc.plot(ticker=self.selected_ticker, config=self.params[0].chart))
            self.table = st.dataframe(df)

        return

