from pathlib import Path
import streamlit as st
import pandas as pd
from functools import partial

from strawberry.repository.storage import ParquetStorage
from strawberry.logging.logger_factory import LoggerFactory
from strawberry.config.config_loader import ConfigLoader

class App:

    def __init__(self):
        # logging
        factory = LoggerFactory()
        self.logger = factory.create_logger(__name__)

        # configuration
        self.config = ConfigLoader()

        # repositories
        self.acq_store = ParquetStorage(self.config.env.acquisition_folder)
        self.val_store = ParquetStorage(self.config.env.validated_folder)
        self.trn_store = ParquetStorage(self.config.env.transformed_folder)

        # acquisition tables
        self.acq_tables = self.config.acquisition()

        # table name /  tickers / data frame
        self.selected_table = None
        self.tickers = None
        self.selected_ticker = None
        self.df = None

    def render(self):
        # header area
        header_cols = st.columns([3, 1, 1])
        with header_cols[0]:
            st.header(self.selected_table)

        # ticker selection box
        with header_cols[1]:
            self.selected_year_quarter = st.selectbox("Select ticker", options=self.tickers, 
                                                        index=0, key="selected_ticker",
                                                        on_change=lambda: self.ticker_event_handler(st.session_state.selected_ticker))
        
        # Next ticker button
        with header_cols[2]:
            st.button("Next ▶", on_click=self.next_ticker)

        st.dataframe(self.df, use_container_width=True, height=1000)

    def next_ticker(self):
        """Advance to the next ticker in the list (wraps around)."""
        if not self.tickers:
            return
        curr = st.session_state.selected_ticker
        try:
            idx = self.tickers.index(curr)
        except ValueError:
            idx = 0
        next_idx = (idx + 1) % len(self.tickers)
        next_tkr = self.tickers[next_idx]
        # fire your existing flow for loading a ticker
        st.session_state.selected_ticker = next_tkr
        self.ticker_event_handler(next_tkr)

    def table_event_handler(self, table_name: str):    
        self.selected_table = table_name
        self.tickers = self.get_tickers(table_name)
        st.session_state.selected_ticker = self.tickers[0]
        self.ticker_event_handler(self.tickers[0])    

    def ticker_event_handler(self, ticker: str):
        self.selected_ticker = ticker
        self.df = self.acq_store.read_df(self.selected_table, self.selected_ticker)
        self.render()

    def _table_path(self, table_name: str) -> Path:
        return self.config.env.data_root / self.config.env.acquisition_folder / Path(table_name)
    
    def get_tickers(self, table_name: str) -> list[str]:
        """
        Given a path like 'BALANCE_SHEET', find all subdirectories named
        'symbol=XXX' and return ['XXX', ...].
        """
        base_path = self._table_path(table_name)

        if not base_path.is_dir():
            raise ValueError(f"{table_name!r} is not a valid directory")

        symbols: list[str] = []
        for sub in base_path.iterdir():
            name = sub.name
            if sub.is_dir() and name.startswith("symbol="):
                # split on the first '=' and take the right side
                symbol = name.split("=", 1)[1]
                symbols.append(symbol)

        return symbols

    def validation_button(self):
        v = self.val_store.read_df("validation")
        st.dataframe(v, use_container_width=True, height=1000)

        t = self.val_store.read_df("TICKERS_TO_TRANSFORM")
        st.dataframe(t, use_container_width=True, height=1000)

    def dim_stocks_button(self):
        v = self.trn_store.read_df("DIM_STOCKS")
        st.dataframe(v, use_container_width=True, height=1000)


    def startup(self):
        # page configuration
        st.set_page_config(page_title="Acquisition Data Viewer",
                            layout="wide",              
                            initial_sidebar_state="expanded",
                            page_icon=":strawberry:")
        st.sidebar.title("Navigation")

        # build pages dict: name -> render(name)
        pages: dict[str, callable] = {
                cfg.name: partial(self.table_event_handler, cfg.name)
                for cfg in self.acq_tables.tables
            }

        # add the special handler for your monthly-adjusted time series
        pages['TIME_SERIES_MONTHLY_ADJUSTED'] = partial(
            self.table_event_handler,  # or whatever custom fn you want
            'TIME_SERIES_MONTHLY_ADJUSTED'
        )

        # initialize session state
        if 'page' not in st.session_state:
            st.session_state.page = next(iter(pages))
            self.table_event_handler(st.session_state.page)

        # navigation buttons (interlocked)
        for name, r_fn in pages.items():
            is_active = (st.session_state.page == name)
            btn_type = "secondary" if is_active else "primary"
            if is_active:
                st.session_state.page = name
            st.sidebar.button(
                label=name,
                type=btn_type,
                use_container_width=True,
                on_click=r_fn
            )
        st.sidebar.button(label="validation", type="primary", use_container_width=True, on_click=self.validation_button)
        st.sidebar.button(label="dim stocks", type="primary", use_container_width=True, on_click=self.dim_stocks_button)


if __name__ == "__main__":   
    App().startup()

