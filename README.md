
# Long-Term Dividend Investment Strategy and Modeling

## Goal
Build a 15-stock dividend-focused portfolio to hold and accumulate over 20 years, using historical data and predictive modeling.

## User Stories

| Category  | Icon | Description       |
|-----------|------|-------------------|
| Status    | 🔴   | Not started       |
| Status    | 🟡   | In progress       |
| Status    | ✅   | Done              |
| Priority  | 🔴   | High Priority     |
| Priority  | 🟢   | Low Priority      |

-  🟡 [Epic: Data Ingestion & Storage](/docs/data_ingestion/README.md)
-  [Epic: Pipeline Orchestration](/docs/orchestration/README.md)
-  🟡 [Epic: Metric Computation ](/docs/metric_computation/README.md)
-  [Epic: Rule-Based Filtering & Scoring](/docs/rules/READ.ME)
-  [Epic: ML Labeling & Modeling](/docs/ml_modeling/README.md)
-  [Epic: Moat Analysis](/docs/moat_analysis/README.md)
-  [Epic: Sentiment Analysis](/docs/sentiment_analysis/README.md)
-  🟡 [Epic: Dashboard & Reporting](/docs/dashboard/README.md)
-  [Epic: Alerts & Notifications](/docs/alerts/README.md)
  

## Tools
- **Financials Source**: Alpha Vantage API
- **Moat Soource**: OpenAI
- **Data Storage**: Parquet
- **Visualization**: matplotlib, seaborn, notebook (?)
- **Export**: Excel using pandas + ExcelWriter



## Enhancements to Consider

### 1. Dividend Growth Rate (CAGR)
- Use 5â€“10 year historical CAGR
- Forecast using growth scenarios

### 2. Payout Ratio
- Use net income or free cash flow-based payout
- Add limits or warning flags > 80%

### 3. Earnings & Revenue Trends
- EPS and revenue growth support sustainable dividends

### 4. Volatility / Drawdown
- Understand risk of price collapse or dividend cut

### 5. Dividend Cut Probability
- Use historical behavior or red flags like high debt, declining earnings

### 6. Valuation Metrics
- PE, PB, Yield vs 5Y avg
- Avoid buying overvalued dividend traps

### 7. Sector Diversification
- Prevent overexposure to utilities, REITs, etc.

### 8. DRIP Impact
- Include reinvestment in projections

### 9. Total Return View
- Blend dividend yield + projected capital gains

### 10. Rebalancing Rules
- DCA assumptions
- Rebalance annually
- Drop stocks that cut dividends

---

## Advanced Considerations

| Metric | Why It Matters |
|--------|----------------|
| ROE | Efficiency and profitability |
| FCF | Sustainability of dividends |
| Insider Ownership | Alignment with shareholders |
| Debt/Equity | Financial flexibility |
| Moat | Long-term competitive edge |

