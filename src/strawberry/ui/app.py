from numpy import place
import streamlit as st
from pathlib import Path

from strawberry.config.config_loader import ConfigLoader
from strawberry.repository.storage import ParquetStorage
from strawberry.acquisition.acquire import Acquire
from strawberry.ui.app_srv import AppServices
from strawberry.ui.views import data_view
from strawberry.ui.views.data_view import DataView
from strawberry.ui.views.placeholder import PlaceholderView
from strawberry.validation.validate import Validate
from strawberry.logging.logger_factory import LoggerFactory
from strawberry.ui.views.stock_view import StockView
from strawberry.dimensions.dim_stocks import DimStocks


class DataApp:
    # Class-level constants
    PAGES = ["Screener", "Stock View", "Data Viewer"]
    URLs = ["screener", "stock-view", "data-viewer"]
    PAGE_TITLE = "Strawberry Equities"

    def __init__(self):
        # Initialize logger
        self.logger = LoggerFactory().create_logger(self.__class__.__name__)

        self.srv = self.get_services()
        placeholder = PlaceholderView(self.srv)
        stock_view = StockView(self.srv)
        data_view = DataView(self.srv)

        # Define pages
        self.st_pages = [
            st.Page(
                placeholder.render,
                title=self.PAGES[0],
                url_path=self.URLs[0],
            ),
            st.Page(
                stock_view.render,
                title=self.PAGES[1],
                url_path=self.URLs[1],
            ),
            st.Page(
                data_view.render,
                title=self.PAGES[2],
                url_path=self.URLs[2],
            ),
        ]

    def get_services(self) -> AppServices:
        if "app_services" not in st.session_state:
            st.session_state["app_services"] = AppServices(self.__class__.__name__)
        return st.session_state["app_services"]

    def render(self):
        self.logger.info(f"Running {self.PAGE_TITLE} Application")
        st.set_page_config(page_title=self.PAGE_TITLE, layout="wide")

        # Create navigation in the sidebar
        sel_page = st.navigation(self.st_pages, position="sidebar")
        sel_page.run()


if __name__ == "__main__":
    app = DataApp()
    app.render()
