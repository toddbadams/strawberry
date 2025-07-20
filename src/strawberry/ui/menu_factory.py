# src/chart_factory.py
import logging
import streamlit as st
from streamlit_option_menu import option_menu
import streamlit_shadcn_ui as ui
import pandas as pd
import altair as alt
from src.config.config_loader import ConfigLoader
from src.ui.chart_factory import ConsoiidatedDataChartFactory
from src.ui.dividend_score import DividendScoreDashboard

class MenuFactory: 

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

        # chart factory
        self.chart_factory = ConsoiidatedDataChartFactory(consolidated_df, self.logger)

        # Load rules config 
        cl = ConfigLoader(self.logger)
        self.rules = cl.load_rules()
        
        # will be set in run()
        self.selected_ticker: str | None = None

    def rules_item(self) -> list[alt.Chart]:
        self.logger.info(f"Rules menu item selected.")

        # Create 2 columns: name, and ticker dropdown on the far right
        col_name, col_ticker = st.columns([3, 1])

        # select a ticker
        self.selected_ticker = col_ticker.selectbox("Select Ticker", self.tickers)

        # display selected ticker details
        overview_row = self.overview_df.loc[self.overview_df["symbol"] == self.selected_ticker]
        
        if not overview_row.empty:
            row = overview_row.iloc[0]
            col_name.markdown(f"# {row['Name']} ({row['Exchange']}: {row['symbol']})")
            st.markdown(f"{row["Description"]}   {row['Name']} is in the **{row['Sector']}** sector, in **{row['Industry']}**.")
            # st.write(overview_row.iloc[0])
        else:
            col_name.warning("No overview data for this ticker.")

        # build the list of heads
        heads = [r.head for r in self.rules]
        # select a head (string)
        selected_head = ui.tabs(options=heads, default_value=heads[0], key="rule_selector")
        # find the rule dict that matches
        rule = next(r for r in self.rules if r.head == selected_head)        

        # Use factory to render the appropriate Altair chart
        self.chart_factory.create_chart(rule, ticker=self.selected_ticker)
        return []

    def top_buys_item(self) -> list[alt.Chart]:
        self.logger.info(f"Top buys menu item selected.")
        self.selected_ticker = None
        return []

    def rule_timeline_item(self) -> list[alt.Chart]:
        self.logger.info(f"Rule timeline menu item selected.")
        self.selected_ticker = None
        return []

    def default_item(self) -> list[alt.Chart]:
        self.logger.info(f"Default menu item.")
        self.selected_ticker = None
        return []
    
    def dividend_score_item(self):
        DividendScoreDashboard(tickers=self.tickers, 
                               consolidated_df=self.consolidated_df,
                               overview_df=self.overview_df,
                               config_loader=self.config_loader,
                               logger=self.logger).render()
        return []

    def run(self): 
        # Map each menu item to it's function
        mapping = {
          #  "Rules": self.rules_item,
          #  "Top Buys": self.top_buys_item,
            "Dividends": self.dividend_score_item
          #  "Rule Timeline": self.rule_timeline_item,
          #  "Data Table": self.default_item
        }

        with st.sidebar:
            menu_choice = option_menu(
                menu_title=None,
                options=list(mapping.keys()),
                icons=["list-check",    # Rules
                        "cart-plus",     # Top Buys
                        "clock-history", # Rule Timeline
                        "table"],        # Data Table
                default_index=0,
                orientation="vertical"
            )
        
        # Select the appropriate function, defaulting if head is unknown
        menu_func = mapping.get(menu_choice, self.default_item)

        menu_func()


