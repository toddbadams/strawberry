

class RulesViewer:


    def view(tickers):
        ticker = st.sidebar.selectbox("Select Ticker", tickers)
        metrics = ['Company', 
                'Dividend Growth', 'Dividend Return', 'Dividend Yield', 
                'DCF/DDM Value', 'P/E Value',
                'Health', 'Moat']
        metric = st.sidebar.selectbox("Select Rule", metrics)
        df_ticker = ps.read_df("consolidated", ticker).set_index('qtr_end_date')
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