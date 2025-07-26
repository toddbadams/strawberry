import streamlit as st
from pathlib import Path

from strawberry.ui.app_srv import AppServices
from strawberry.ui.views.base_view import BaseView
from strawberry.logging.logger_factory import LoggerFactory
from strawberry.config.config_loader import ConfigLoader
from strawberry.repository.storage import ParquetStorage
from strawberry.acquisition.acquire import Acquire
from strawberry.validation.validate import Validate


class DataView(BaseView):

    SECTIONS = ["Acquired", "Validated", "Dimensions"]
    DIMENSIONS = ["DIM_STOCKS"]
    TABLE_HEIGHT = 1000

    def __init__(self, service: AppServices):
        super().__init__(service)

    def _display_acq_valid(self, section: str):
        """Handles the Acquired and Validated sections"""
        # Determine tickers first
        tickers = (
            self.srv.acq_tickers
            if section == self.SECTIONS[0]
            else self.srv.val_tickers
        )

        # select ticker via sidebar
        ticker = st.sidebar.selectbox("Select ticker", tickers)
        self.logger.info(f"Selected ticker: {ticker}")

        # Then choose table via radio (acquired and validated share same table names))
        table = st.sidebar.radio("Select table", self.srv.acq_tables)
        self.logger.info(f"Selected table: {table}")

        # Read and display DataFrame
        df = (
            self.srv.acq_store.read_df(table, ticker)
            if section == self.SECTIONS[0]
            else self.val_store.read_df(table, ticker)
        )
        rows = len(df) if df is not None else 0
        self.logger.info(f"Loaded DataFrame with {rows} rows")
        if rows == 0:
            st.warning(f"No data available for {ticker} in {table}.")
            return

        st.title(f"{section} {table} ({ticker})")
        st.dataframe(df, height=self.TABLE_HEIGHT)

    def _display_dimensions(self):
        """Handles the Dimensions section"""
        table = st.sidebar.selectbox("Select dimension", self.DIMENSIONS)
        self.logger.info(f"Selected dimension: {table}")

        df = self.dim_store.read_df(table)
        rows = len(df) if df is not None else 0
        self.logger.info(f"Loaded dimension DataFrame with {rows} rows")
        if rows == 0:
            st.warning(f"No data available.")
            return

        st.title("Stock Dimensions")
        st.dataframe(df, height=self.TABLE_HEIGHT)

    def render(self, ticker: str = None):
        self.logger.info("Displaying Data Viewer page")

        # Section selection
        section = st.sidebar.radio("Data layer", self.SECTIONS)
        self.logger.debug(f"Selected section: {section}")

        if section in ["Acquired", "Validated"]:
            self._display_acq_valid(section)
        else:
            self._display_dimensions()
