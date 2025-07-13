import os
from pathlib import Path
import streamlit as st
import pandas as pd
import json

from src.parquet.parquet_storage import ParquetStorage
from src.logger_factory import LoggerFactory
from src.altair_graphs.chart_factory import ConsoiidatedDataChartFactory

class App:
   
  def __init__(self):
        # data storage
        self.data_path = Path(os.getenv("OUTPUT_PATH", "data/"))
        self.storage = ParquetStorage(self.data_path)

        # app configuration
        self.config_path = Path(os.getenv("CONFIG_PATH", "config/"))
        rules_path = self.config_path / "rules.json"
        with rules_path.open("r", encoding="utf-8") as f:
          self.rules = json.load(f)

        # logging
        factory = LoggerFactory()
        self.logger = factory.create_logger(__name__)

        # list of tickers
        self.overview_df = pd.read_parquet(self.data_path / 'OVERVIEW', engine="pyarrow")
        self.tickers = sorted(self.overview_df['symbol'].unique())

        # consolidated data across all tickers
        self.consolidated_df = pd.read_parquet(self.data_path / 'CONSOLIDATED', engine="pyarrow")

        # chart factory
        self.chart_factory = ConsoiidatedDataChartFactory(self.consolidated_df, self.logger)

  
  def rules_display(self):
    
    ticker = st.sidebar.selectbox("Select Ticker", self.tickers)
    #df_ticker = self.storage.read_df("consolidated", ticker).set_index('qtr_end_date')
    #co_ticker = self.storage.read_df("overview", ticker)

    # build the list of heads
    heads = [r["head"] for r in self.rules]
    # select a head (string)
    selected_head = st.sidebar.selectbox("Select Rule", heads)
    # find the rule dict that matches
    rule = next(r for r in self.rules if r["head"] == selected_head)

    # Use factory to render the appropriate Altair chart
    self.chart_factory.create_chart(rule["head"], rule["subhead"], ticker=ticker)


  def startup_sidebar(self):      
    sb_menu_items = ["Rules", "Top Buys",  "Rule Timeline", "data table"]

    view = st.sidebar.radio("View", sb_menu_items)
    if view == sb_menu_items[0]:  
      self.rules_display()

    elif view == sb_menu_items[1]:
      st.write("Top buys tbd")

    elif view == sb_menu_items[2]:
      st.write("Rule timeline tbd")

    elif view == sb_menu_items[3]:   
      st.write("data table tbd")

  def startup(self):
    # page configuration
    st.set_page_config(
    page_title="Dividend-Focused Portfolio Dashboard",
    layout="wide",              
    initial_sidebar_state="auto",
    page_icon=":strawberry:",
    menu_items={
        'Get Help': 'https://www.extremelycoolapp.com/help',
        'Report a bug': "https://www.extremelycoolapp.com/bug",
        'About': "# This is a header. This is an *extremely* cool app!"
    })

    # sidebar configuration
    self.startup_sidebar()

App().startup()

