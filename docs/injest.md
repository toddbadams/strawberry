
# Data Ingestion

Alpha Vantage is a widely used financial data provider offering free and paid APIs for real-time and historical equity, forex, and cryptocurrency data. For equities, it provides endpoints for balance sheets, cash flows, dividends, earnings, insider trading, company overviews, and time series price data, making it suitable for automated financial analysis and research pipelines.

✅ **As a Data Engineer**, I want to fetch quarterly financials, dividends, and share counts from Alpha Vantage so that raw data for all tickers is available in Parquet.

**Acceptance**: Raw JSON → Parquet files exist in the data lake for a sample list of tickers.

**Recommended Parquet Folder Structure (partitioned by symbol):**

```
parquet/
  balance_sheet/
    symbol=MSFT/
      part-00000.parquet
      ...
  cash_flow/
    symbol=MSFT/
      part-00000.parquet
      ...
  dividends/
    symbol=MSFT/
      part-00000.parquet
      ...
  earnings/
    symbol=MSFT/
      part-00000.parquet
      ...
  income_statements/
    symbol=MSFT/
      part-00000.parquet
      ...
  insider_trading/
    symbol=MSFT/
      part-00000.parquet
      ...
  overview/
    symbol=MSFT/
      part-00000.parquet
      ...
  time_series_monthly_adjusted/
    symbol=MSFT/
      part-00000.parquet
      ...
```

- Each top-level folder corresponds to an Alpha Vantage endpoint.
- Each subfolder is partitioned by symbol (e.g., symbol=MSFT).
- Each partition contains one or more Parquet files for that symbol and endpoint.
  
# Data Conslidation

✅ **As a Data Engineer**,  I want to: **consolidate raw financial data** from Alpha Vantage so that all downstream rules operate on a consistent, clean dataset.

**Acceptance:**  
      - Raw data is loaded, mapped to standardized column names, and missing values are handled according to business logic.
      - All numeric fields are converted to the correct types and units (e.g., millions, percentages as decimals).
      - Data is timestamped and versioned for traceability.

| Final Column Name          | Alpha Vantage Column Name(s)               | Alpha Vantage Table Name                | Description                                                      |
|----------------------------|--------------------------------------------|-----------------------------------------|------------------------------------------------------------------|
| qtr_end_date               | fiscalDateEnding                           | balance_sheet                           | last fiscal day in quarter, used to join all tables              |
| shares_outstanding         | SharesOutstanding                          | balance_sheet                           | Number of shares outstanding                                     |
| capital_expenditures       | capitalExpenditures                        | cash_flow                               | Capital expenditures (for FCF calculation)                       |
| operating_cashflow         | operatingCashflow                          | cash_flow                               | Operating cash flow (for FCF calculation)                        |
| free_cashflow              | **calculated**                             | cash_flow                               | operating_cashflow - capital_expenditures                        |
| free_cashflow_TTM          | **calculated**                             | cash_flow                               | rolling sum last 4 quarters                                      |
| free_cashflow__ps_TTM      | **calculated**                             | cash_flow                               | free_cashflow__ps_TTM / shares_outstanding                       |
| share_price                | 05. price                                  | time_series_monthly_adjusted            | Current share price                                              |
| dividend                   | amount                                     | dividends                               | dividend per share (for growth calculations)                     |
| eps                        | reportedEPS                                | earnings                                | Earnings per share (trailing 12 months)                          |
| estimated_eps              | estimatedEPS                               | earnings                                | Estimated earnings per share (trailing 12 months)                |
| surprise_eps_pct           | surprisePercentage                         | earnings                                | EPS surprise percentage                                          |
| net_income                 | netIncome                                  | income_statements                       | net income                                                       |
| ebit                       | ebit                                       | income_statements                       | Earnings before interest, taxes                                  |
| ebitda                     | ebitda                                     | income_statements                       | Earnings before interest, taxes, depreciation, and amortization  |



The following are to be determined 


| Final Column Name          | Alpha Vantage Column Name(s)               | Alpha Vantage Table Name                | Description                                                      |
|----------------------------|--------------------------------------------|-----------------------------------------|------------------------------------------------------------------|
| projected_EPS_growth_rate  | *Not available; derived or external*       | *N/A*                                   | Projected annual EPS growth rate (decimal, e.g., 0.12 for 12%)   |
| insider_pct                | *Not available; from insider_trading or external* | insider_trading                  | Percentage of shares owned by insiders (decimal, e.g., 0.06)     |
| total_debt                 | totalDebt                                  | balance_sheet                           | Total debt (short + long term)                                   |
| moat_score                 | *Not available; calculated downstream*     | *N/A*                                   | Score on 5-point economic moat rubric                            |
| peer_group                 | Sector or Industry                         | overview                                | Identifier for peer group/industry classification                |
| bond_yield                 | *Not available; from external source*      | *N/A*                                   | Current 10-year government bond yield (decimal, e.g., 0.045)     |
| yield_history              | *Calculated: dividend/time_series price*   | dividends + time_series_monthly_adjusted | Historical dividend yield (for z-score calculations)             |
| beta                       | Beta                                       | overview                                | Beta coefficient (for WACC calculation)                          |
| sector                     | Sector                                     | overview                                | Sector or industry classification                                |
| data_version               | *Generated during pipeline*                | *N/A*                                   | Version or batch identifier for the

# Data Validation

🔴 **As a Data Engineer**, I want to validate schema consistency on each Parquet file so that any missing fields or format changes trigger alerts.

   * **Acceptance**: Schema check job flags anomalies and notifies Slack.

1. **Define the Expected Schema**

   * Store your master schema in code (as a PyArrow Schema object) or in a simple JSON/YAML file that maps column names → data types.

2. **Read & Extract the Parquet Schema**

   * Use **PyArrow** to open each Parquet file and pull its arrow schema:

     python
     from pyarrow.parquet import ParquetFile

     def load_parquet_schema(path: str) -> pa.Schema:
         pf = ParquetFile(path)
         return pf.schema.to_arrow_schema()
     

3. **Compare Schemas**

   * Iterate your expected fields and types, and check against the actual schema’s fields.
   * Catch three classes of anomalies:

     1. **Missing columns**
     2. **Extra columns**
     3. **Type mismatches**
   * Collect all discrepancies into a list of human-readable error strings.

4. **Notify via Slack**

   * Use a Slack **Incoming Webhook** (URL stored in SLACK_WEBHOOK_URL env var)
   * Post a JSON payload summarizing the anomalies:

     python
     import os, requests

     SLACK_WEBHOOK = os.getenv("SLACK_WEBHOOK_URL")

     def alert_slack(message: str):
         payload = {"text": message}
         resp = requests.post(SLACK_WEBHOOK, json=payload)
         resp.raise_for_status()
     

5. **Glue It Together in a Job**

   * Scan your Parquet folder (or be given a list), run the check on each file, and if any errors are found call alert_slack() once per file (or batch them).
   * Exit with a non-zero code if you want your orchestration tool (Prefect, cron-wrapper) to mark the run as failed.

# Infrastructure

🔴 **As an Infrastructure Engineer**, I want to build a Raspberry Pi 5 (16 GB Starter Kit, 256 GB storage) running OS Bookworm, install and configure Docker, and deploy the data ingestion container so that our pipeline can run on a low-cost, always-on device.

   * **Acceptance**:

     * Raspberry Pi boots into Bookworm, fully updated.
     * Docker engine is installed and running.
     * Data ingestion image is pulled or built locally and successfully writes sample Parquet output when run.


---


🔴 **As a DevOps Engineer**, I want to schedule the data ingestion container to run nightly—ingesting up to 25 tickers per run loaded from a configurable tickers list—so that we stay within Alpha Vantage’s rate limits.

   * **Acceptance**:

     * Cron or systemd-timer is configured to launch the ingestion container at a fixed time each night.
     * The ingestion script reads tickers from a flat file (e.g. tickers.txt).
     * The script stops after 25 API calls (tracking counts) and writes completed tickers’ data to Parquet.
     * Logs indicate successful runs and any rate-limit hits.


