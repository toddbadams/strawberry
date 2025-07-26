import pandas as pd
import streamlit as st

from strawberry.config.config_loader import ConfigLoader
from strawberry.repository.storage import ParquetStorage
from strawberry.config.dtos.FactTableConfig import FactTableConfig
from strawberry.ui.app_srv import AppServices
from strawberry.ui.charts.financial_charts import FinancialChart
from strawberry.ui.views.base_view import BaseView


class FinancialView(BaseView):
    def __init__(self, service: AppServices, config: FactTableConfig):
        super().__init__(service)
        self.table_cfg: FactTableConfig = config
        self.chart = FinancialChart()
        self.date_ranges = self.chart.RANGES

    def render(self, ticker: str):
        df = self.srv.dim_store.read_df(self.table_cfg.fact_table_name, ticker)
        if df is None or df.empty:
            st.warning("No data found.")
            return

        date_range = st.radio(
            "Date Range",
            self.date_ranges,
            horizontal=True,
            key=f"{self.table_cfg.fact_table_name}_radio",
        )

        with st.container():
            self.chart.render(df, self.table_cfg, date_range)
