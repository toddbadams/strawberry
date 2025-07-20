import logging
import pandas as pd
import altair as alt

from config.ChartConfig import ChartConfig

class YearChart:

    CHART_HEIGHT = 450

    LINE_PALETTE = [
        "#006d9f",  # blue
        "#ffa600",  # gold
        "#7f6fbf",  # purple
        "#ff6d69",  # salmon
    ]

    BUY_SELL_PALLETTE = [
        "#fb1f07",  # strong sell = red
        "#ff7f0e",  # sell = orange
        "#2ca02c",  # buy = green
        "#06fb43"   # strong buy = bright green
    ]

    VIEW_PALLETTE = {
        "platinum":       "#ccdbdc",
        "non_photo_blue": "#9ad1d4",
        "cerulean":       "#007ea7",
        "prussian_blue":  "#003249",
    }

    ERROR_COLOR = "#fb1f07"

    def __init__(self, df: pd.DataFrame, logger: logging.Logger, use_area: bool = True):
        """
        :param df: DataFrame containing the data
        :param logger: Logger instance
        :param use_area: If True, render an area chart instead of a line chart
        """
        self.df = df
        self.logger = logger
        self.use_area = use_area

    def _year_start_rules(self, df_plot: pd.DataFrame) -> alt.Chart:
        years = pd.DatetimeIndex(df_plot['qtr_end_date']).year.unique()
        year_starts = pd.DataFrame({
            'year_start': pd.to_datetime([f"{y}-01-01" for y in years])
        })
        return (
            alt.Chart(year_starts)
            .mark_rule(color='lightgray', strokeDash=[2, 2], opacity=0.3)
            .encode(x='year_start:T')
        )

    def _alternate_year_shade(self, df_plot: pd.DataFrame) -> alt.Chart:
        years = sorted(pd.DatetimeIndex(df_plot['qtr_end_date']).year.unique())
        periods = []
        for idx, yr in enumerate(years):
            if idx % 2 == 0:
                start = pd.to_datetime(f"{yr}-01-01")
                end = pd.to_datetime(f"{yr + 1}-01-01")
                periods.append({'start': start, 'end': end})
        shade_df = pd.DataFrame(periods)
        return (
            alt.Chart(shade_df)
            .mark_rect(opacity=0.1, fill='lightgray')
            .encode(
                x=alt.X('start:T'),
                x2='end:T',
                y=alt.value(0),
                y2=alt.value(self.CHART_HEIGHT)
            )
        )

    def _blank(self, title: str) -> alt.Chart:
        return alt.Chart().mark_text(text=title, color='red').properties(title=title)

    def _horizontal_line(self, y_value: float, color: str) -> alt.Chart:
        return (
            alt.Chart(pd.DataFrame({'y': [y_value]}))
            .mark_rule(color=color, strokeWidth=2)
            .encode(y=alt.Y('y:Q'))
        )

    def plot(self, ticker: str, config: ChartConfig) -> alt.LayerChart:
        date_col = 'qtr_end_date'

        # Melt DataFrame into long form for Altair
        try:
            df_plot = self.df.melt(
                id_vars=[date_col],
                value_vars=config.metrics,
                var_name='metric',
                value_name='value'
            )
        except KeyError as e:
            msg = f"{config.title}: Missing column for {ticker} for melt: {e}"
            self.logger.error(msg)
            return self._blank(msg)

        if df_plot.empty:
            msg = f"{config.title}: No data available for {ticker}."
            self.logger.warning(msg)
            return self._blank(msg)

        # Apply range filter if specified
        if config.x_axis_range is not None:
            max_date = df_plot[date_col].max()
            min_date = max_date - pd.DateOffset(years=config.x_axis_range)
            df_plot = df_plot[df_plot[date_col] >= min_date]

            if df_plot.empty:
                msg = f"{config.title}: No data in the last {config.x_axis_range} years for {ticker}."
                self.logger.warning(msg)
                return self._blank(msg)

        # Year boundary and shading layers
        shade_layer = self._alternate_year_shade(df_plot)
        rule_layer = self._year_start_rules(df_plot)

        # Prepare y-axis scale with optional domain limits
        scale_kwargs = {}
        if config.y_axis_min is not None:
            scale_kwargs['domainMin'] = config.y_axis_min
        if config.y_axis_max is not None:
            scale_kwargs['domainMax'] = config.y_axis_max
        y_scale = alt.Scale(**scale_kwargs) if scale_kwargs else None
        y_enc = (
            alt.Y('value:Q', title=config.y_label,
                  axis=alt.Axis(format=config.y_axis_format),
                  scale=y_scale)
            if y_scale else
            alt.Y('value:Q', title=config.y_label, axis=alt.Axis(format=config.y_axis_format))
        )

        # Build main chart layer: area or line
        if self.use_area:
            main_layer = (
                alt.Chart(df_plot)
                .mark_area(opacity=0.3)
                .encode(
                    x=alt.X(f'{date_col}:T', axis=alt.Axis(format='%Y-Q%q', title='Quarter')),
                    y=y_enc,
                    color=alt.Color('metric:N', title='Metric',
                                    scale=alt.Scale(range=self.LINE_PALETTE),
                                    legend=alt.Legend(
                                        orient='bottom', columns=len(config.metrics), labelLimit=150
                                    )),
                    tooltip=[
                        alt.Tooltip(f'{date_col}:T', title='Date'),
                        alt.Tooltip('value:Q', format=config.y_axis_format, title=config.y_label),
                        alt.Tooltip('metric:N', title='Metric')
                    ]
                )
                .interactive()
            )
        else:
            main_layer = (
                alt.Chart(df_plot)
                .mark_line()
                .encode(
                    x=alt.X(f'{date_col}:T', axis=alt.Axis(format='%Y-Q%q', title='Quarter')),
                    y=y_enc,
                    color=alt.Color('metric:N', title='Metric',
                                    scale=alt.Scale(range=self.LINE_PALETTE),
                                    legend=alt.Legend(
                                        orient='bottom', columns=len(config.metrics), labelLimit=150
                                    )),
                    tooltip=[
                        alt.Tooltip(f'{date_col}:T', title='Date'),
                        alt.Tooltip('value:Q', format=config.y_axis_format, title=config.y_label),
                        alt.Tooltip('metric:N', title='Metric')
                    ]
                )
                .interactive()
            )

        # Compose and configure final chart
        chart = alt.layer(shade_layer, rule_layer, main_layer).properties(height=500)
        chart = chart.configure_title(fontSize=20, anchor='start', color="#ccdbdc")
        chart = chart.configure_view(
            continuousHeight=200,
            continuousWidth=200,
            strokeWidth=1,
            stroke="#ccdbdc"
        )
        self.logger.info(f"{config.title} Rendered for {ticker}.")
        return chart
