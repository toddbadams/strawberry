## Epic: Dashboard & Reporting

1. 🔴 **As a Portfolio Manager**, I want a Streamlit dashboard showing the ranked “buy” candidates with their composite score, fair value gap, and moat rating so that I can filter and export them.

   * **Acceptance**: Interactive table with sorting, filters, and CSV download.
   * **Docs**: 
   * **Status**: 🔴 
   * **Priority**: 🔴

2. 🔴 **As a Portfolio Manager**, I want time-series plots of dividend yield vs. historical mean for any ticker so that I can visually confirm the Z-score.

   * **Acceptance**: Plot displays in the dashboard on ticker selection.
   * **Docs**: 
   * **Status**: 🔴 
   * **Priority**: 🔴

3. 🔴 **As a Portfolio Manager**, I want a 20-year line chart of any raw metric (e.g. dividend\_yield, yield\_zscore, fair\_value\_gap\_pct) for a selected ticker so that I can inspect long-term trends.

   * **Acceptance**:

     * Dashboard offers a dropdown of all raw‐metric columns.
     * Selecting a metric and ticker renders an interactive Plotly/Matplotlib line chart spanning the last 20 years (or full available history).
     * Chart includes tooltips on hover showing date and value.

4. 🔴 **As a Portfolio Manager**, I want a 20-year “rule-pass” timeline chart for a selected ticker so that I can see which screening rules it met each quarter over time.

   * **Acceptance**:

     * Dashboard shows a multi-series plot (one series per `rule_…` boolean) over the last 20 years.
     * Each rule’s pass/fail is rendered as 1/0 or as color bands for easy reading.
     * Legend identifies each rule and toggling series on/off is supported.
