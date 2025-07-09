
import pandas as pd
import altair as alt
from src.altair_graphs.altair_grapher import AltairGrapher


class DividendYieldGrapher(AltairGrapher):

    def high_relative_yield_plot(self, df: pd.DataFrame) -> alt.Chart:
        cols = ['dividend_yield', 'yield_historical_mean_5y']
        title = "Dividend yield vs historical average"
        date_col = "qtr_end_date"
        df_plot = df[cols].reset_index().melt(date_col, var_name='metric', value_name='value')
        rule_years = self.__year_start_rules(df_plot)

        # line graph for dividend yield and historical average
        line = (
            alt.Chart(df_plot)
                .mark_line()
                .encode(x=super().__QuarterEndX(),
                        y=alt.Y('value:Q', 
                                title='Percentage', 
                                axis=alt.Axis(format='.2%')),
                        color=alt.Color('metric:N', 
                                        legend=None, 
                                        scale=alt.Scale(domain=cols, range=self.line_palette))
                    )
                )

        return alt.layer(rule_years, line).properties(height=500, title=title)

        # st.altair_chart(chart, use_container_width=True)
    
    def yield_z_score_plot(self, df: pd.DataFrame):
        cols = ['yield_zscore']
        title = "Dividend Yield Z-Score"
        df_plot = (
            df[cols]
            .reset_index()
            .melt('fiscalDateEnding', var_name='metric', value_name='value')
        )

        rule_years = self.__year_start_rules(df_plot)
        buy_line = self.__horizontal_line(1, self.buy_sell_palette[3])
        strong_buy_line = self.__horizontal_line(2, self.buy_sell_palette[2])
        sell_line = self.__horizontal_line(-1, self.buy_sell_palette[1])
        strong_sell_line = self.__horizontal_line(-2, self.buy_sell_palette[0])

        # Z-score line
        line = (
            alt.Chart(df_plot)
            .mark_point(filled=True, size=150)
            .encode(
                x=alt.X('fiscalDateEnding:T', 
                        title='Date', 
                        axis=alt.Axis(format='%Y', tickCount='year', labelAngle=0)),
                y=alt.Y('value:Q', 
                        title='Z Score', 
                        axis=alt.Axis(format='.2')),
                    color=alt.Color('metric:N', 
                                    legend=None, 
                                    scale=alt.Scale(domain=cols, range=self.line_palette)),
                tooltip=[
                    alt.Tooltip('fiscalDateEnding:T', title='Date'),
                    alt.Tooltip('value:N', title='Z-Score', format='.2')
                ]
            )
        )
        
        return = (alt.layer(strong_buy_line, buy_line, strong_sell_line, sell_line, rule_years, line)
                .properties(height=500, title=title)
                .configure_legend(disable=True))
        
        # st.altair_chart(chart, use_container_width=True)