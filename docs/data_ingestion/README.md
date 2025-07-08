
## Epic: Data Ingestion & Storage

1. ✅ **As a Data Engineer**, I want to fetch quarterly financials, dividends, and share counts from Alpha Vantage so that raw data for all tickers is available in Parquet.

   * **Acceptance**: Raw JSON → Parquet files exist in the data lake for a sample list of tickers.
   *  **Docs**: 
   * **Status**: 🔴
   * **Priority**: 🔴

2. 🔴 **As a Data Engineer**, I want to validate schema consistency on each Parquet file so that any missing fields or format changes trigger alerts.

   * **Acceptance**: Schema check job flags anomalies and notifies Slack.
   *  **Docs**: [Readme](/validate_schema/README.md)
   * **Status**: 🔴 -  on hold as low priority
   * **Priority**: 🟢
   * 

3. 🔴 **As a Data Engineer**, I want to partition Parquet files by quarter and symbol so that downstream jobs only read what’s needed.

   * **Acceptance**: Parquet folder structure organized as `year=YYYY/quarter=QX/symbol=AAA.parquet`.
   *  **Docs**: [Readme](/docs/data_partition/README.md)
   * **Status**: 🟡 - abandoned for now, not sure this is necessary
   * **Priority**: 🔴

4. 🔴 **As an Infrastructure Engineer**, I want to build a Raspberry Pi 5 (16 GB Starter Kit, 256 GB storage) running OS Bookworm, install and configure Docker, and deploy the data ingestion container so that our pipeline can run on a low-cost, always-on device.

   * **Acceptance**:

     * Raspberry Pi boots into Bookworm, fully updated.
     * Docker engine is installed and running.
     * Data ingestion image is pulled or built locally and successfully writes sample Parquet output when run.
   *  **Docs**: 
   * **Status**: 🔴 - waiting on parts
   * **Priority**: 🔴

5. 🔴 **As a DevOps Engineer**, I want to schedule the data ingestion container to run nightly—ingesting up to 25 tickers per run loaded from a configurable tickers list—so that we stay within Alpha Vantage’s rate limits.

   * **Acceptance**:

     * Cron or systemd-timer is configured to launch the ingestion container at a fixed time each night.
     * The ingestion script reads tickers from a flat file (e.g. `tickers.txt`).
     * The script stops after 25 API calls (tracking counts) and writes completed tickers’ data to Parquet.
     * Logs indicate successful runs and any rate-limit hits.
   *  **Docs**: 
   * **Status**: 🔴 - waiting on raspberry PI
   * **Priority**: 🔴