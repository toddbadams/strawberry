
import altair as alt
import streamlit as st
import pandas as pd
from pandas import DataFrame


class AltairGrapher:

    def __init__(self):
        self.line_palette = [
             "#006d9f", # blue
             "#ffa600", # gold
             "#7f6fbf", # purple
             "#ff6d69", # salmon
        ]
        self.action_order = [
            'strong sell',
            'sell',
            'hold',
            'buy',
            'strong buy'
        ]
        self.buy_sell_palette = [
            "#fb1f07",   # strong sell = red
            "#ff7f0e",   # sell = orange
            "#2ca02c",   # buy = green
            "#06fb43"    # strong buy = bright green
        ]
        self.buy_sell_values = [
            -2,             # strong sell
            -1,             # sell
            1,              # buy
            2               # strong buy
        ]

    def __year_start_rules(self, df_plot: pd.DataFrame):
        # Create year-start lines
        years = pd.DatetimeIndex(df_plot['qtr_end_date']).year.unique()
        year_starts = pd.DataFrame({
            'year_start': pd.to_datetime([f"{y}-01-01" for y in years])
        })

        rule_years = (
            alt.Chart(year_starts)
            .mark_rule(color='lightgray', strokeDash=[2,2], opacity=0.7)
            .encode(x='year_start:T')
        )
        return rule_years

    def __horizontal_line(self, y_value: float, color: str):
        zero_line = alt.Chart(pd.DataFrame({'y': [y_value]})).mark_rule(
            color=color, strokeWidth=2
        ).encode(
            y=alt.Y('y:Q')
        )
        return zero_line

    def __QuarterEndX(self) -> alt.X:
        return alt.X('qtr_end_date:T', 
                            title='Date', 
                            axis=alt.Axis(format='%Y', tickCount='year', labelAngle=0))


    def yield_z_score_plot2(self, df: DataFrame):
        ps = df.copy()
        ps['fiscalDateEnding'] = pd.to_datetime(ps['fiscalDateEnding'])  
        chart = (alt.Chart(ps)
                .mark_circle(filled=True, size=150)
                .encode(
                    x='fiscalDateEnding',
                    y='yield_zscore',
                    color='action_high_relative_yield',
                    tooltip=['fiscalDateEnding', 'yield_zscore', 'action_high_relative_yield']
                ).interactive())

        st.altair_chart(chart, use_container_width=True)
          
    def high_div_yield_buy_sell(self, df: DataFrame):
        cols = ['action_high_relative_yield']
        title = "High dividend yield buy / sell"
        df_plot = (
            df[cols]
            .reset_index()
            .melt('fiscalDateEnding', var_name='metric', value_name='value')
        )

        rule_years = self.__year_start_rules(df_plot)

        # Z-score line
        line = (
            alt.Chart(df_plot)
            .mark_point(filled=True, size=150) 
            .encode(
                x=alt.X('fiscalDateEnding:T', 
                        title='Date', 
                        axis=alt.Axis(format='%Y', tickCount='year', labelAngle=0)),
                y=alt.Y('value:N', 
                        title='Action', 
                        sort=self.action_order, 
                        axis=alt.Axis(labelAngle=0)),
                color=alt.Color('value:N', legend=alt.Legend(title="Action"), 
                                scale=alt.Scale(domain=self.action_order, range=self.buy_sell_palette)),
                tooltip=[
                    alt.Tooltip('fiscalDateEnding:T', title='Date'),
                    alt.Tooltip('value:N', title='Action')
                ]
            )
        )
        
        chart = (alt.layer(rule_years, line)
                .properties(height=500, title=title)
                .configure_legend(disable=True)
        )
        st.altair_chart(chart, use_container_width=True)

    def dividend_return_plot(self, df: DataFrame):
        cols = ['dividend_yield_plus_growth', 'dividend_growth_rate_5y', 'dividend_yield']
        title = "Dividend Yield vs 5-Year Mean"
        date_col = "fiscalDateEnding"
        df_plot = df[cols].reset_index().melt(date_col, var_name='metric', value_name='value')
        rule_years = self.__year_start_rules(df_plot)
        buy_line = self.__horizontal_line(.12, self.buy_sell_palette[2])
        line = (
            alt.Chart(df_plot)
                .mark_line()
                .encode(
                    x=alt.X('fiscalDateEnding:T', title='Date', axis=alt.Axis(format='%Y', tickCount='year', labelAngle=0)),
                    y=alt.Y('value:Q', title='Percentage', axis=alt.Axis(format='.2%')),
                    color=alt.Color('metric:N', 
                                    scale=alt.Scale(domain=cols, range=self.line_palette),
                                    legend=alt.Legend(orient='right', direction='vertical'))
                    )
        )

        chart = (alt.layer(buy_line, rule_years, line)
                .properties(height=500, width=500, title=title)
                .configure_legend(disable=True)
        )
        st.altair_chart(chart, use_container_width=True)

    def dividend_table(self, df: DataFrame):
            st.dataframe(
            df[['dividendTTM', 'dividend_yield', 'yield_historical_mean_5y', 'yield_zscore', 
                'dividend_yield_plus_growth', 'dividend_growth_rate_5y', 'rule_high_relative_yield',
                'action_high_relative_yield']],
          #  column_order = "fiscalDateEnding"
            column_config = {
                "fiscalDateEnding": st.column_config.DateColumn(
                label="Quarter Date Ending",
                help="The last day of the reporting quarter",
                format="iso8601"),
                
                "dividendTTM": st.column_config.NumberColumn(
                label="Dividend TTM (USD)",
                help="The dividends for the last twelve months in USD",
                format="dollar"),
                
                "dividend_yield": st.column_config.NumberColumn(
                label="Dividend Yield",
                help="The dividends yield for the last twelve months",
                format="percent"),
                
                "yield_historical_mean_5y": st.column_config.NumberColumn(
                label="5yr Dividend Yield Average",
                help="The dividends yield average for the last 5 years",
                format="percent"),
                
                "dividend_growth_rate_5y": st.column_config.NumberColumn(
                label="5yr Dividend Growth",
                help="The dividends yield average for the last 5 years",
                format="percent"),
                
                "dividend_yield_plus_growth": st.column_config.NumberColumn(
                label="5yr Dividend Yield plug growth",
                help="The dividends yield average for the last 5 years",
                format="percent"),
                
                "yield_zscore": st.column_config.NumberColumn(
                label="Z Scopre",
                help="Number of standard deviations the current dividend yield is from its 5-year mean. Sell (< –1), Hold (–1 to 1), Buy (> 1).",
                format="%.2f")
                }
            )

    def overview_table(self, df: DataFrame):
        row0 = df.iloc[0]
        col1, col2, col3, col4 = st.columns(4)

        # 
        with col1:
            st.subheader("About")
            st.text(f"{row0['Name']} ({row0['Exchange']}) - {row0['Description']}")
            st.text(f"{row0['OfficialSite']}")
            st.text(f"Sector:  {row0['Sector']}")
            st.text(f"Industry:    {row0['Industry']}")

        with col2: 
            st.subheader("Dividends")
            st.text(f"Ex Div Date: {row0['ExDividendDate']}")
            st.text(f"Dividend Per Share: {row0['DividendPerShare']}")
            st.text(f"Dividend Yield: {row0['DividendYield']}")
            st.text(f"Next Div Date: {row0['DividendDate']}")

        with col3:
            st.subheader("Health")
            st.text(f"Latest Quarter:    {row0['LatestQuarter']}")
            st.text(f"Market Cap:    {row0['MarketCapitalization']}")
            st.text(f"Enterprise Value:    tbd")
            st.text(f"Shares Outstanding:    tbd")
            st.text(f"Net Debt LTM:    tbd")
            st.text(f"Net Deb / EBITDA  LTM:    tbd")

        with col4:
            st.subheader("Value")
            st.text(f"PE:    {row0['PERatio']}")
            st.text(f"PEG:    {row0['PEGRatio']}")
            st.text(f"Book Value:    {row0['BookValue']}")
            st.text(f"Street Fair Value:    {row0['AnalystTargetPrice']}")
            st.text(f"EV/Revenue  (NTM - LTM):    tbd, tbd")
            st.text(f"EV/EBIDTA  (NTM - LTM):    tbd, tbd")
            st.text(f"P/E  (NTM - LTM):    tbd, tbd")
            st.text(f"MC/FCF  (NTM - LTM):    tbd, tbd")

        st.dataframe(df)

        
    def dividend_growth_plot(self, df: DataFrame):
        cols = ['dividend_growth_rate_5y']
        title = "Dividend growth rate 5yr average"
        date_col = "fiscalDateEnding"
        df_plot = df[cols].reset_index().melt(date_col, var_name='metric', value_name='value')
        rule_years = self.__year_start_rules(df_plot)
        buy_line = self.__horizontal_line(0.05, self.buy_sell_palette[3])

        # line graph for dividend yield and historical average
        line = (
            alt.Chart(df_plot)
                .mark_line()
                .encode(
                    x=alt.X('fiscalDateEnding:T', 
                            title='Date', 
                            axis=alt.Axis(format='%Y', tickCount='year', labelAngle=0)),
                    y=alt.Y('value:Q', 
                            title='Percentage', 
                            axis=alt.Axis(format='.2%')),
                    color=alt.Color('metric:N', 
                                    legend=None, 
                                    scale=alt.Scale(domain=cols, range=self.line_palette)),
                    strokeDash=alt.condition(
                        alt.datum.metric == cols[0],
                        alt.value([6, 4]),
                        alt.value([0])
                    )
                )
        )

        chart = (alt.layer(buy_line, rule_years, line)
                .properties(height=500, width=500, title=title)
                .configure_legend(disable=True)
        )
        st.altair_chart(chart, use_container_width=True)
    