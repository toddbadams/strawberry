import streamlit as st
import pandas as pd

from src.ui.screener_page import ScreenerPage
from src.ui.dividend_score_page import DividendScorePage
from parquet.storage import ParquetStorage
from src.logger_factory import LoggerFactory
from src.config.config_loader import ConfigLoader

class DashboardApp:
    def __init__(self):
        # logging
        factory = LoggerFactory()
        self.logger = factory.create_logger(__name__)

        # configuration
        self.config_loader = ConfigLoader(self.logger)

        # data storage
        self.storage = ParquetStorage(self.config_loader.env.output_path)

        # load data
        self.overview_df = pd.read_parquet( self.config_loader.env.output_path / 'OVERVIEW',engine="pyarrow")
        self.tickers = sorted(self.overview_df['symbol'].unique())
        self.selected_ticker = self.tickers[0]

        # consolidated data includes all tickers and columns
        self.consolidated_df = pd.read_parquet(self.config_loader.env.output_path / 'CONSOLIDATED', engine="pyarrow")
        self.consolidated_df['qtr_end_date'] = pd.to_datetime(self.consolidated_df['qtr_end_date'])
        self.consolidated_df['year'] = self.consolidated_df['qtr_end_date'].dt.year
        self.consolidated_df['quarter'] = self.consolidated_df['qtr_end_date'].dt.quarter
        self.consolidated_df['year_quarter'] = self.consolidated_df['year'].astype(str) + ' Q' + self.consolidated_df['quarter'].astype(str)

        # unique date labels  (last 8 quarters)
        self.unique_year_quarters = sorted(self.consolidated_df['year_quarter'].unique(), reverse=True)[:8]
        self.selected_year_quarter = self.unique_year_quarters[0]

        # instantiate page objects
        self.screener_page = ScreenerPage(self.config_loader, self.overview_df, self.consolidated_df,
            self.tickers, self.selected_ticker, self.unique_year_quarters, self.selected_year_quarter, self.logger)
        self.dividend_page = DividendScorePage(self.config_loader, self.overview_df, self.consolidated_df,
            self.tickers, self.selected_ticker, self.unique_year_quarters, self.selected_year_quarter,  self.logger)



    def main(self):
        # page config
        st.set_page_config(page_title="Strawberry", layout="wide",
            initial_sidebar_state="expanded", page_icon=":strawberry:")
        st.sidebar.title("Navigation")

        # initialize session state
        if 'page' not in st.session_state:
            st.session_state.page = 'Screener'

        # map page names to render methods
        pages: dict[str, callable] = {
            'Screener': self.screener_page.render,
            'Dividend Score': self.dividend_page.render
        }

        # navigation buttons (interlocked)
        for name, r_fn in pages.items():
            is_active = (st.session_state.page == name)
            btn_type = 'secondary' if is_active else 'primary'
            if is_active: 
                st.session_state.page = name
            st.sidebar.button(label=name, type=btn_type, use_container_width=True, on_click=r_fn)

if __name__ == "__main__":
    DashboardApp().main()
