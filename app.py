import os
from pathlib import Path
import streamlit as st
import pandas as pd

from src.parquet.parquet_storage import ParquetStorage
from src.logger_factory import LoggerFactory
from src.ui.menu_factory import MenuFactory
from src.config.config_loader import ConfigLoader

class App:

  def __init__(self):
    # logging
    factory = LoggerFactory()
    self.logger = factory.create_logger(__name__)

    # configuration
    self.config_loader = ConfigLoader(self.logger)

    # data storage
    self.storage = ParquetStorage(self.config_loader.env.output_path)

    # list of tickers
    self.overview_df = pd.read_parquet(self.config_loader.env.output_path / 'OVERVIEW', engine="pyarrow")
    self.tickers = sorted(self.overview_df['symbol'].unique())

    # consolidated data across all tickers
    self.consolidated_df = pd.read_parquet(self.config_loader.env.output_path / 'CONSOLIDATED', engine="pyarrow")

    # sidebar menu
    self.menu = MenuFactory(tickers=self.tickers,
                          consolidated_df=self.consolidated_df,
                          overview_df=self.overview_df,
                          config_loader=self.config_loader,
                          logger=self.logger)

  def startup(self):
    # page configuration
    st.set_page_config(page_title="Dividend-Focused Portfolio Dashboard",
                      layout="wide",              
                      initial_sidebar_state="auto",
                      page_icon=":strawberry:")

    # sidebar configuration
    self.menu.run()

App().startup()

