
## Screening Rules

## Dividend Rules
1. **Dividend Growth**
   – Annual dividend increase of at least 0.5 % over the past 5–10 years.

2. **Dividend Return**
   – (Current yield) + (5 yr average dividend growth rate) > 12 %.

3. **Dividend Yield**

> **Rule of Thumb:** "Buy when the yield is high vs. historical average."
> * If a stock typically yields 2.5%, but now yields 3.2%, that may indicate **undervaluation**.
* Tools like FastGraphs, Simply Safe Dividends, or YieldChart can show **historical yield bands**.

**Formula:**
`Current Dividend Yield = Annual Dividend / Current Share Price`

   – Dividend yield at least 1 σ (standard deviation) above its 5-year historical average.

## Value
4. **DCF/DDM Value**
   – Current share price at least 20 % below your blended DCF / DDM fair-value estimate.
5. **P/E Value**
   – P/E ratio below the median of its peer group.

## Health
5. **Healthy Cash Conversion**
   – Earnings-to-free-cash-flow ratio between 0.4 and 0.6.
7. **Growth-Adjusted Valuation**
   – PEG ratio < 1.
8. **Earnings Premium**
   – Projected earnings yield (1 / P) exceeds the current 10-yr bond yield by at least 2 %.
9. **Debt Cushion**
   – Total debt no more than 50 % of your calculated fair-value equity (i.e., strong margin of safety).
10. **Skin in the Game**
    – Insiders (executives & board) collectively own ≥ 5 % of outstanding shares.
11. **Wide Economic Moat**
    – Company scores ≥ 4 out of 5 on your moat rubric (brand, network effects, switching costs, cost advantage, IP/regulatory barriers).

## Epic: Rule-Based Filtering & Scoring

1. 🔴 **As an Analyst**, I want to apply each of the boolean filters on the metrics table so that we can flag which rules each company passes.

   * **Acceptance**: flag columns (e.g. `rule_dividend_yield_high`) appear and pass unit tests.
   *  **Docs**: [rule columns](/docs/rules/rule_columns/README.md)
   * **Status**: 🟡 
   * **Priority**: 🔴
  
2. 🔴 **As an Analyst**, I want to assign weights to each rule and compute a composite “score” in Python so that we have a ranked list.

    * **Acceptance**: New column `composite_score` sorts as expected when tested with synthetic data.
   *  **Docs**: 
   * **Status**: 🔴 
   * **Priority**: 🔴

3. 🔴 **As an Analyst**, I want to export the top‐50 “buy” and top‐50 “sell” candidates as CSV so that I can review them in Excel.

    * **Acceptance**: CSV files generated and download link provided.
   *  **Docs**: 
   * **Status**: 🔴 
   * **Priority**: 🔴
