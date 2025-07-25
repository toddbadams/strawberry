import streamlit as st
from streamlit_echarts import st_echarts
import pandas as pd
from strawberry.config.dtos.FactTableConfig import FactTableConfig


class FinancialChart:

    OFFSETS = {
        "3Y": pd.DateOffset(years=3),
        "5Y": pd.DateOffset(years=5),
        "10Y": pd.DateOffset(years=10),
    }

    RANGES = ["3Y", "5Y", "10Y", "MAX"]

    def _build_chart_options(self, x_data, series):
        return {
            "backgroundColor": "#0E1117",
            "tooltip": {"trigger": "axis"},
            "legend": {"top": "bottom", "textStyle": {"color": "#CCCCCC"}},
            "xAxis": {
                "type": "category",
                "data": x_data,
                "axisLabel": {"rotate": 45, "color": "#CCCCCC"},
                "axisLine": {"lineStyle": {"color": "#444"}},
            },
            "yAxis": {
                "type": "value",
                "axisLabel": {"formatter": "${value}M", "color": "#CCCCCC"},
                "axisLine": {"lineStyle": {"color": "#444"}},
                "splitLine": {"lineStyle": {"color": "#333"}},
            },
            "series": series,
            "grid": {"bottom": 80},
        }

    def _map_x_labels(self, date_range: str, x: pd.Timestamp) -> str:
        if date_range == "3Y":
            return f"{x.year}-Q{((x.month - 1) // 3 + 1)}"
        elif date_range == "5Y":
            return f"{x.year} H1" if x.month <= 6 else f"{x.year} H2"
        elif date_range in ["10Y", "MAX"]:
            return str(x.year)
        return x.strftime("%Y-%m-%d") if isinstance(x, pd.Timestamp) else str(x)

    def _build_line(self, y_data: list[float], name: str) -> dict:
        return {
            "data": y_data,
            "type": "line",
            "smooth": True,
            "name": name,
            "showSymbol": False,
            "lineStyle": {"width": 2},
        }

    def _to_millions(self, m: list[str]) -> list[float]:
        return [v / 1_000_000 if pd.notna(v) else None for v in m]

    def render(self, df: pd.DataFrame, config: FactTableConfig, date_range: str):
        df = df.sort_values(by=config.date_col_name)

        # Apply date range filter (only 3Y, 5Y, 10Y, MAX supported)
        if date_range != "MAX" and date_range in self.OFFSETS:
            latest_date = df[config.date_col_name].max()
            if date_range in self.OFFSETS:
                df = df[
                    df[config.date_col_name] >= (latest_date - self.OFFSETS[date_range])
                ]

        x_data = [self._map_x_labels(date_range, x) for x in df[config.date_col_name]]

        series = []
        for col in config.get_metric_cols():
            y_data = self._to_millions(df[col.data_col_name].tolist())
            series.append(self._build_line(y_data, col.display_name))

        options = self._build_chart_options(x_data, series)
        st_echarts(options=options, height="600px")
