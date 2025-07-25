import streamlit as st
from pathlib import Path

from strawberry.config.config_loader import ConfigLoader
from strawberry.repository.storage import ParquetStorage
from strawberry.acquisition.acquire import Acquire
from strawberry.validation.validate import Validate
from strawberry.logging.logger_factory import LoggerFactory
from strawberry.ui.stock_view_app import StockView


class DataApp:
    # Class-level constants
    PAGES = ["Screener", "Stock View", "Data Viewer"]
    SECTIONS = ["Acquired", "Validated", "Dimensions"]
    DIMENSIONS = ["DIM_STOCKS"]

    def __init__(self):
        # Initialize logger
        self.logger = LoggerFactory().create_logger(self.__class__.__name__)
        self.logger.info("Initializing DataApp")

        # Load configuration and environment
        self.config = ConfigLoader()
        self.env = self.config.environment()
        self.logger.debug(
            f"Environment: acquisition_folder={self.env.acquisition_folder}, validated_folder={self.env.validated_folder}"
        )

        # Initialize storage backends
        self.acq_store = ParquetStorage(Path(self.env.acquisition_folder))
        self.val_store = ParquetStorage(Path(self.env.validated_folder))
        self.dim_store = ParquetStorage(Path(self.env.dim_stocks_folder))
        self.logger.info("Parquet storage backends initialized")

        # Data loaders
        self.acquire = Acquire()
        self.validate = Validate()
        self.logger.info("Data loaders initialized")

        # Pre-load table list (same for Acquired & Validated)
        self.table_loader = self.config.acquisition()
        self.tables = self.table_loader.table_names()
        self.logger.debug(f"Tables: {self.tables}")

    def run(self):
        """Entrypoint using Streamlit's multipage navigation API"""
        self.logger.info("Running DataApp with st.navigation")
        # Common page config
        st.set_page_config(page_title="Data App", layout="wide")

        # Define pages
        pages = [
            st.Page(self.screener_page, title="Screener", url_path="screener"),
            st.Page(StockView().render, title="Stock View", url_path="stock-view"),
            st.Page(self.data_viewer_page, title="Data Viewer", url_path="data-viewer"),
        ]

        # Create navigation in the sidebar
        sel_page = st.navigation(pages, position="sidebar")
        sel_page.run()

    def screener_page(self):
        self.logger.info("Displaying Screener page")
        st.title("Screener")
        st.info("Coming soon – stay tuned for the full screener design!")

    def data_viewer_page(self):
        self.logger.info("Displaying Data Viewer page")
        st.title("Data Viewer")

        # Section selection
        section = st.sidebar.radio("Data layer", self.SECTIONS)
        self.logger.debug(f"Selected section: {section}")

        if section in ["Acquired", "Validated"]:
            self._display_acq_valid(section)
        else:
            self._display_dimensions()

    def _display_acq_valid(self, section: str):
        """Handles the Acquired and Validated sections"""
        # Determine tickers first
        if section == "Acquired":
            all_tickers = self.acquire.tickers
            tickers = self.acquire.tickers_acquired(all_tickers)
        else:
            all_tickers = self.validate.tickers
            tickers = self.validate.tickers_validated(all_tickers)
        # Sort tickers in ascending order
        tickers = sorted(tickers)
        self.logger.debug(f"Available tickers for {section}: {tickers}")
        ticker = st.sidebar.selectbox("Select ticker", tickers)
        self.logger.info(f"Selected ticker: {ticker}")

        # Then choose table via radio
        self.logger.debug(f"Available tables: {self.tables}")
        table = st.sidebar.radio("Select table", self.tables)
        self.logger.info(f"Selected table: {table}")

        # Read and display DataFrame
        df = (
            self.acq_store.read_df(table, ticker)
            if section == "Acquired"
            else self.val_store.read_df(table, ticker)
        )
        rows = len(df) if df is not None else 0
        self.logger.info(f"Loaded DataFrame with {rows} rows")
        st.dataframe(df, height=1000)

    def _display_dimensions(self):
        """Handles the Dimensions section"""
        self.logger.debug(f"Available dimensions: {self.DIMENSIONS}")
        table = st.sidebar.selectbox("Select dimension", self.DIMENSIONS)
        self.logger.info(f"Selected dimension: {table}")

        df = self.dim_store.read_df(table)
        rows = len(df) if df is not None else 0
        self.logger.info(f"Loaded dimension DataFrame with {rows} rows")
        st.dataframe(df, height=1000)


if __name__ == "__main__":
    app = DataApp()
    app.run()
