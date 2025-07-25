import pandas as pd
import streamlit as st

from strawberry.repository.storage import ParquetStorage
from strawberry.config.config_loader import ConfigLoader
from strawberry.ui.views.financial_views import FinancialView
from strawberry.dimensions.dim_stocks import DimStocks
from strawberry.config.dtos.FactTableConfig import FactTableConfig
from strawberry.ui.views.placeholder import PlaceholderView


class StockView:
    def __init__(self):
        self.config = ConfigLoader()
        self.env = self.config.environment()
        self.dim_store = ParquetStorage(self.env.dim_stocks_folder)
        self.dim_stock_srv = DimStocks()
        self.tickers = sorted(self.dim_stock_srv.tickers_dimensioned())

        # Load full stock table once (no ticker filter)
        self.full_df = self.dim_store.read_df("DIM_STOCKS")

        self.subpages = {
            "Summary": PlaceholderView(),
            "Income Statement": FinancialView(self.config.fact_qtr_income),
            "Balance Sheet": FinancialView(self.config.fact_qtr_balance),
            "Cash Flow": PlaceholderView(),
            "Earnings": PlaceholderView(),
            "Dividends": PlaceholderView(),
            "Insider Transactions": PlaceholderView(),
            "Charting": PlaceholderView(),
        }

    def _filder_by_ticker(self, ticker) -> pd.DataFrame:
        df = (
            self.full_df[self.full_df["symbol"] == ticker]
            if self.full_df is not None
            else None
        )
        return df if df is not None and not df.empty else None

    def render(self):
        ticker = st.sidebar.selectbox("Select Ticker", self.tickers)

        # Filter the stock row from full_df based on selected ticker
        df = self._filder_by_ticker(ticker)

        if df is not None and not df.empty:
            stock = df.iloc[0]
            st.header(
                f"{stock['name']} ({stock['exchange']}: {stock['symbol']} {stock['currency']})"
            )
        else:
            st.warning("No stock information available.")
            return

        tab = st.tabs(list(self.subpages.keys()))

        for i, (name, page) in enumerate(self.subpages.items()):
            with tab[i]:
                page.render(ticker)

        return df
