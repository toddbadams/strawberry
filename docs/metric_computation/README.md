# Epic: Metric Computation 

1. 🔴 **As a Quant Analyst**, I want to compute DCF and DDM fair-value estimates using QuantLib modules so that each company has a current intrinsic value.

   * **Acceptance**: New columns `fair_value_dcf` and `fair_value_ddm` appear in the metrics Parquet.
   *  **Docs**: 
   * **Status**: 🔴 
   * **Priority**: 🔴
  
2. 🔴 **As a Quant Analyst**, I want to calculate rolling mean and standard deviation of historical dividend yield (20 quarters) so that I can derive yield Z-scores.

   * **Acceptance**: Column `yield_zscore` computed and validated against known test data.
   *  **Docs**: 
   * **Status**: 🔴 
   * **Priority**: 🔴
  
3. 🔴 **As a Quant Analyst**, I want to compute key ratios (P/E, PEG, EBIT-to-FCF, debt-to-equity, dividend growth rate) with Pandas so that they’re ready for filtering.

   * **Acceptance**: Ratios match hand-calculated values for a test ticker.
   *  **Docs**: 
   * **Status**: 🔴 
   * **Priority**: 🔴
* Here are three new stories to capture the consolidation and rule‐augmentation steps. You can append these as stories 9–11 under your **Metric Computation** (or a new **Consolidation** ) epic:


4. 🔴 **As a Data Engineer**, I want to read and merge all existing Parquet partitions under `/data/{table_name}/symbol={symbol}/part-*.parquet` for every table (DIVIDENDS, BALANCE\_SHEET, CASH\_FLOW, etc.) into a single DataFrame keyed by `symbol` and `ex_dividend_date`/`fiscalDateEnding` (normalized as year+quarter) so that downstream metrics all draw from one unified source.

   * **Acceptance**:

     * Job reads each table’s partitions, extracts the key date column, normalizes to `year` & `quarter`, and joins on `(symbol, year, quarter)`.
     * Resulting DataFrame contains all source-table columns plus `year` and `quarter`.
   * **Docs**: [table structure](/docs/metric_computation/data_tables/README.md)
   * **Status**: ✅
   * **Priority**: 🔴

5. 🔴 **As a Data Engineer**, I want to evaluate each of our 11 screening rules (high relative yield, undervaluation, dividend growth, etc.) for every `(symbol, year, quarter)` in that consolidated DataFrame, producing boolean flag columns (`rule_high_yield`, `rule_undervalued`, …, `rule_wide_moat`) so that each record carries its pass/fail for each criterion.

* **Acceptance**:

  * For each rule, a new column exists and matches expected output on a test fixture.
  * All 11 boolean flags correctly reflect the logic defined in our rule spec.
* **Docs**: Link to “screening\_rules.md”
* **Status**: 🔴
* **Priority**: 🔴

6. 🔴 **As a Data Engineer**, I want to write out this fully consolidated, rule-flagged table as Parquet partitioned by `year`, `quarter`, and `symbol` under `/data/consolidated/` so downstream reporting and ML jobs can ingest directly.

* **Acceptance**:

  * Parquet files appear under `/data/consolidated/year=YYYY/quarter=QX/symbol=AAA/part-*.parquet`.
  * A sanity-check script can read back a sample partition and see all original columns plus the 11 `rule_…` flags.
* **Docs**: Link to consolidation pipeline README
* **Status**: 🔴
* **Priority**: 🔴
