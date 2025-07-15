import logging
from turtle import st
import pandas as pd
import altair as alt

from src.config.config_loader import RuleChartConfig

class YearChart:

    CHART_HEIGHT = 450

    LINE_PALETTE = [
             "#006d9f", # blue
             "#ffa600", # gold
             "#7f6fbf", # purple
             "#ff6d69", # salmon
        ]
    
    BUY_SELL_PALLETTE = [
            "#fb1f07",   # strong sell = red
            "#ff7f0e",   # sell = orange
            "#2ca02c",   # buy = green
            "#06fb43"    # strong buy = bright green
        ]
    
    VIEW_PALLETTE = {
            "platinum":        "#ccdbdc",
            "non_photo_blue":  "#9ad1d4",
            "cerulean":        "#007ea7",
            "prussian_blue":   "#003249",
        }
    
    ERROR_COLOR = "#fb1f07"

    def __init__(self, df: pd.DataFrame, logger: logging.Logger):
        self.df = df
        self.logger = logger
      
    def _year_start_rules(self, df_plot: pd.DataFrame) -> alt.Chart:
        # Create year-start lines
        years = pd.DatetimeIndex(df_plot['qtr_end_date']).year.unique()
        year_starts = pd.DataFrame({
            'year_start': pd.to_datetime([f"{y}-01-01" for y in years])
        })
                
        return (
            alt.Chart(year_starts)
            .mark_rule(color='lightgray', strokeDash=[2,2], opacity=0.3)
            .encode(x='year_start:T')
        )
    
    def _alternate_year_shade(self, df_plot: pd.DataFrame) -> alt.Chart:
        # Build shading periods for every other year
        years = sorted(pd.DatetimeIndex(df_plot['qtr_end_date']).year.unique())
        periods = []
        for idx, yr in enumerate(years):
            # shade every even-indexed year block
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
                # span full vertical extent
                y=alt.value(0),
                y2=alt.value(self.CHART_HEIGHT)
            )
        )
    
    def blank(self, title: str) -> alt.Chart:
        return alt.Chart().mark_text(text=title, color='red').properties(title=title)
    
    def horizontal_line(self, y_value: float, color: str):
        zero_line = alt.Chart(pd.DataFrame({'y': [y_value]})).mark_rule(
            color=color, strokeWidth=2
        ).encode( y=alt.Y('y:Q') )
        return zero_line
    
    def plot(self, ticker: str, config: RuleChartConfig, 
             range_years: int | None = None  # 1, 3, 5, 10; None for all
             ) -> alt.LayerChart:
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
            m = f"{config.title}: Missing column for {ticker} for melt: {e}"
            self.logger.error(m)
            # Return an empty chart with a message
            return self.blank(m)

        if df_plot.empty:
            m = f"{config.title}: No data available for {ticker}."
            self.logger.warning(m)
            return self.blank(m)

        # Apply range filter if specified
        if range_years is not None:
            max_date = df_plot[date_col].max()
            min_date = max_date - pd.DateOffset(years=range_years)
            df_plot = df_plot[df_plot[date_col] >= min_date]

            if df_plot.empty:
                msg = f"{config.title}: No data in the last {range_years} years for {ticker}."
                self.logger.warning(msg)
                return self.blank(msg)
            
        # Generate year boundary rules
        shade_layer = self._alternate_year_shade(df_plot)
        rule_layer = self._year_start_rules(df_plot)

        # Build main line layer
        line_layer = (
            alt.Chart(df_plot)
            .mark_line()
            .encode(
                x=alt.X(f'{date_col}:T', axis=alt.Axis(format='%Y-Q%q', title='Quarter')),
                y=alt.Y('value:Q', title=config.y_label, axis=alt.Axis(format='.2')),
                color=alt.Color('metric:N', title='Metric', scale=alt.Scale(range=self.LINE_PALETTE),
                                legend=alt.Legend(
                                    orient='bottom',       # 📌 move legend to the bottom
                                    columns= len(config.metrics), # 📌 force a single-row legend
                                    labelLimit=150         # 📌 truncate labels at 150px
                                )),
                tooltip=[
                    alt.Tooltip(f'{date_col}:T', title='Date'),
                    alt.Tooltip('value:Q', format=config.y_axis_format, title=config.y_label),
                    alt.Tooltip('metric:N', title='Metric')
                ]
            )
            .interactive()
        )

        # Layer and finalize chart
        chart = alt.layer(shade_layer, rule_layer, line_layer)
        chart = chart.properties(height=450, title=config.title)
        chart = chart.configure_title(
            fontSize=20,
            anchor='start',
            color="#ccdbdc"
        )
        chart = chart.configure_view(
            continuousHeight=200,
            continuousWidth=200,
            strokeWidth=1,
            stroke="#ccdbdc",
        )
        self.logger.info(f"{config.title} Rendered for {ticker}.")
        return chart
    

    