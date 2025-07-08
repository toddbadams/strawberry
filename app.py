import os
import streamlit as st
import pandas as pd
import altair as alt

from src.data.parquet_storage import ParquetStorage
import src.streamlit.streamlit_plots as plots

def raw_metrics(tickers):
    ticker = st.sidebar.selectbox("Select Ticker", tickers)
    metrics = ['Company', 
               'Dividend Growth', 'Dividend Return', 'Dividend Yield', 
               'DCF/DDM Value', 'P/E Value',
               'Health', 'Moat']
    metric = st.sidebar.selectbox("Select Rule", metrics)
    df_ticker = ps.read_df("consolidated", ticker).set_index('fiscalDateEnding')
    co_ticker = ps.read_df("overview", ticker)

    if metric == metrics[0]:
        sl_plotter.overview_table(co_ticker)

    elif metric == metrics[1]:
        st.header("Dividend Growth")
        st.text("Annual dividend increase of at least 0.5 percent over the past 5–10 years.")
        sl_plotter.dividend_growth_plot(df_ticker)
        sl_plotter.dividend_table(df_ticker)

    elif metric == metrics[2]:
        st.header("Dividend Return")
        st.text("(Current yield) + (5 yr average dividend growth rate) > 12 %.")
        sl_plotter.dividend_return_plot(df_ticker)
        sl_plotter.dividend_table(df_ticker)

    elif metric == metrics[3]:
        st.header("Dividend Yield")
        st.text("Dividend yield at least 1 σ (standard deviation) above its 5-year historical average.")
        sl_plotter.yield_z_score_plot(df_ticker)
        sl_plotter.high_relative_yield_plot(df_ticker)
        sl_plotter.dividend_table(df_ticker)


def load_overview_data():
    return pd.read_parquet("data/overview/", engine="pyarrow")


ov = load_overview_data()
tickers = sorted(ov['symbol'].unique())
data_path = os.getenv("OUTPUT_PATH", "data/")
ps = ParquetStorage(data_path)
sl_plotter = plots.StreamLitPlotter()

st.set_page_config(
    page_title="Dividend-Focused Portfolio Dashboard",
    layout="wide",              
    initial_sidebar_state="auto",
    page_icon=":strawberry:",
    menu_items={
        'Get Help': 'https://www.extremelycoolapp.com/help',
        'Report a bug': "https://www.extremelycoolapp.com/bug",
        'About': "# This is a header. This is an *extremely* cool app!"
    }
)

menu_items = ["Metrics", "Top Buys",  "Rule Timeline", "data table"]
view = st.sidebar.radio("View", menu_items)


if view == menu_items[1]:
    # Assuming you have a column 'composite_score'
  #  top = df.groupby('symbol')['composite_score'].last().nlargest(20).index
  #  display_df = df[df['symbol'].isin(top)][['symbol','composite_score']].drop_duplicates()
  #  st.dataframe(display_df)
  st.write("Top buys tbd")

elif view == menu_items[0]:    
   raw_metrics(tickers)

elif view == menu_items[2]:
  #  rules = [c for c in df.columns if c.startswith('rule_')]
  #  selected = st.sidebar.multiselect("Rules to plot", rules, default=rules[:3])
  #  sub = df[df['symbol']==ticker].set_index('fiscalDateEnding')[selected]
  #  # Convert bool→int for plotting
  #  sub = sub.astype(int)
  #  st.area_chart(sub)
  st.write("Rule timeline tbd")

elif view == menu_items[3]:   
  #  ticker = st.sidebar.selectbox("Select Ticker", tickers)
  #  df_ticker = df[df['symbol'] == ticker].set_index('fiscalDateEnding')
  #  df_ticker = df_ticker.sort_values('fiscalDateEnding', ascending=False)
  #  st.dataframe(df_ticker)
  st.write("data table tbd")

# CSV download for the filtered DataFrame
# csv = df[df['symbol']==ticker].to_csv(index=False).encode('utf-8')
# st.download_button("Download Full History (CSV)", csv, f"{ticker}_history.csv")

