import os
from pathlib import Path
import streamlit as st
import pandas as pd
import json

from src.parquet.parquet_storage import ParquetStorage
from src.logger_factory import LoggerFactory
from src.ui.menu_factory import MenuFactory

class App:

  
   
  def __init__(self):
    # data storage
    self.data_path = Path(os.getenv("OUTPUT_PATH", "data/"))
    self.storage = ParquetStorage(self.data_path)

    # app configuration
    self.config_path = Path(os.getenv("CONFIG_PATH", "config/"))

    # logging
    factory = LoggerFactory()
    self.logger = factory.create_logger(__name__)

    # list of tickers
    self.overview_df = pd.read_parquet(self.data_path / 'OVERVIEW', engine="pyarrow")
    self.tickers = sorted(self.overview_df['symbol'].unique())

    # consolidated data across all tickers
    self.consolidated_df = pd.read_parquet(self.data_path / 'CONSOLIDATED', engine="pyarrow")

    # sidebar menu
    self.menu = MenuFactory(
      tickers=self.tickers,
      consolidated_df=self.consolidated_df,
      overview_df=self.overview_df,
      config_path=self.config_path,
      logger=self.logger
    )

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
    self.menu.run()

App().startup()

