
# Dividend Growth Stock Modeling

**Problem:** Long-term, sustainable income growth through dividends can be hard to plan and track over decades.
**Solution:** Develop a software system that selects, builds, and manages a 15-stock, dividend-focused portfolio—leveraging historical data analysis and predictive modeling—to hold and compound returns over a 20-year horizon.

## User Stories

| Category  | Icon | Description       |
|-----------|------|-------------------|
| Status    | 🔴   | Not started       |
| Status    | 🟡   | In progress       |
| Status    | ✅   | Done              |

-  🟡 [Epic: Data Ingestion & Storage](/docs/data_ingestion/README.md)
-  🔴 [Epic: Pipeline Orchestration](/docs/orchestration/README.md)
-  🟡 [Epic: Metric Computation ](/docs/metric_computation/README.md)
-  🔴 [Epic: Rule-Based Filtering & Scoring](/docs/rules/READ.ME)
-  🔴 [Epic: ML Labeling & Modeling](/docs/ml_modeling/README.md)
-  🔴 [Epic: Moat Analysis](/docs/moat_analysis/README.md)
-  🔴 [Epic: Sentiment Analysis](/docs/sentiment_analysis/README.md)
-  🟡 [Epic: Dashboard & Reporting](/docs/dashboard/README.md)
-  🔴 [Epic: Alerts & Notifications](/docs/alerts/README.md)
  

## Tools
- **Financials Source**: [Alpha Vantage API](https://www.alphavantage.co/)
- **Moat Analysis**: [OpenAI API](https://openai.com/api/)
- **Data Storage**: [Parquet](https://parquet.apache.org/)
- **Visualization**: [Streamlit](https://streamlit.io/), [Vega-Altair](https://altair-viz.github.io/)
- **Export**: [Pandas ExcelWriter](https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.ExcelWriter.html)

