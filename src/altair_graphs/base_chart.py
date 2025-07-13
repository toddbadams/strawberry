import logging
from turtle import st
import pandas as pd
import altair as alt

class YearChart:

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
      
    def year_start_rules(self, df_plot: pd.DataFrame) -> alt.Chart:
        # Create year-start lines
        years = pd.DatetimeIndex(df_plot['qtr_end_date']).year.unique()
        year_starts = pd.DataFrame({
            'year_start': pd.to_datetime([f"{y}-01-01" for y in years])
        })
                
        return (
            alt.Chart(year_starts)
            .mark_rule(color='lightgray', strokeDash=[2,2], opacity=0.7)
            .encode(x='year_start:T')
        )
     
    def blank(self, title: str) -> alt.Chart:
        return alt.Chart().mark_text(text=title, color='red').properties(title=title)
    
    def horizontal_line(self, y_value: float, color: str):
        zero_line = alt.Chart(pd.DataFrame({'y': [y_value]})).mark_rule(
            color=color, strokeWidth=2
        ).encode( y=alt.Y('y:Q') )
        return zero_line
    
    def plot(self, ticker: str, title: str, metrics: list[str], y_label: str = '') -> alt.LayerChart:
        date_col = 'qtr_end_date'

        # Melt DataFrame into long form for Altair
        try:
            df_plot = self.df.melt(
                id_vars=[date_col],
                value_vars=metrics,
                var_name='metric',
                value_name='value'
            )
        except KeyError as e:
            m = f"{title}: Missing column for {ticker} for melt: {e}"
            self.logger.error(m)
            # Return an empty chart with a message
            return self.blank(m)

        if df_plot.empty:
            m = f"{title}: No data available for {ticker}."
            self.logger.warning(m)
            return self.blank(m)

        # Generate year boundary rules
        rule_layer = self.year_start_rules(df_plot)

        # Build main line layer
        line_layer = (
            alt.Chart(df_plot)
            .mark_line()
            .encode(
                x=alt.X(f'{date_col}:T', axis=alt.Axis(format='%Y-Q%q', title='Quarter')),
                y=alt.Y('value:Q', title=y_label, axis=alt.Axis(format='.2')),
                color=alt.Color('metric:N', title='Metric', scale=alt.Scale(range=self.LINE_PALETTE),
                                legend=alt.Legend(
                                    orient='bottom',       # 📌 move legend to the bottom
                                    columns= len(metrics), # 📌 force a single-row legend
                                    labelLimit=150         # 📌 truncate labels at 150px
                                )),
                tooltip=[
                    alt.Tooltip(f'{date_col}:T', title='Date'),
                    alt.Tooltip('value:Q', format='.2', title=y_label),
                    alt.Tooltip('metric:N', title='Metric')
                ]
            )
            .interactive()
        )

        # Layer and finalize chart
        chart = alt.layer(rule_layer, line_layer)
        chart = chart.properties(height=450, title=title)
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
        self.logger.info(f"{title} Rendered for {ticker}.")
        return chart
    

    