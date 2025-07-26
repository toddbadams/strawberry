from numpy import place
import pandas as pd
import streamlit as st

from strawberry.repository.storage import ParquetStorage
from strawberry.config.config_loader import ConfigLoader
from strawberry.ui.app_srv import AppServices
from strawberry.ui.views.stock_finanical_view import FinancialView
from strawberry.dimensions.dim_stocks import DimStocks
from strawberry.config.dtos.FactTableConfig import FactTableConfig
from strawberry.ui.views.placeholder import PlaceholderView
from strawberry.ui.views.base_view import BaseView
from strawberry.acquisition.acquire import Acquire
from strawberry.validation.validate import Validate


class StockView(BaseView):
    def __init__(self, service: AppServices):
        super().__init__(service)

        placeholder = PlaceholderView(service)

        self.subpages = {
            "Summary": placeholder,
            "Income Statement": FinancialView(
                self.srv, self.srv.fact_qtr_income_config
            ),
            "Balance Sheet": FinancialView(self.srv, self.srv.fact_qtr_balance_config),
            "Cash Flow": placeholder,
            "Earnings": placeholder,
            "Dividends": placeholder,
            "Insider Transactions": placeholder,
            "Charting": placeholder,
        }

    def render(self):
        ticker = st.sidebar.selectbox("Select Ticker", self.dim_stock_tickers)

        # Filter the stock row from full_df based on selected ticker
        df = self.srv.filter_dim_stocks_by_ticker(ticker)

        if df is not None and not df.empty:
            st.header(self.srv.stock_header(df.iloc[0]))
        else:
            st.warning("No stock information available.")
            return

        tab = st.tabs(list(self.subpages.keys()))

        for i, (name, page) in enumerate(self.subpages.items()):
            with tab[i]:
                page.render(ticker)

        return df
