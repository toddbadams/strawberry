

### 3. **Payout Ratio (Sustainability)**

> Is the dividend actually safe?

* Measured as a % of earnings (or FFO for REITs, DCF for pipelines).
* Sweet spot: **40–60% for most sectors**, lower is safer.
* If the ratio is too high, it raises a red flag that dividends might be cut.


### 5. **Dividend Safety Score (Optional, via Tools)**

Sites like **Simply Safe Dividends** give dividend safety ratings (0-100 scale) based on:

* Cash flow
* Debt levels
* Payout ratio
* Earnings consistency
* Recession performance

---

### 6. **Total Return Potential (Yield + Growth)**

> Think long-term compounding.

* Dividendologists care about **total return** but emphasize **income first**.
* A stock yielding 4% with 6% annual dividend growth is attractive for compounding—even if the share price stays flat.



### Summary: Key Filters Dividendologists Use

| Metric                 | Target                        |
| ---------------------- | ----------------------------- |
| Dividend Yield         | Above historical average      |
| Dividend Growth        | 5–10% per year                |
| Payout Ratio           | <60% (unless sector-specific) |
| Dividend Streak        | 10+ years ideally             |
| Safety Score (if used) | 70+                           |
| Chowder Rule           | Yield + Growth > 12%          |




| Column Name                      | Description                                                                 |
| -------------------------------- | --------------------------------------------------------------------------- |
| `rule_healthy_cash_conversion`   | 🟢 True if (net income / free cash flow) between 0.4 and 0.6                |
| `rule_growth_adjusted_valuation` | 🟢 True if PEG ratio < 1                                                    |
| `rule_earnings_premium`          | 🟢 True if projected earnings yield (1/price) ≥ (10-yr bond yield + 2 %)    |
| `rule_debt_cushion`              | 🟢 True if total debt ≤ 50 % of fair-value equity                           |
| `rule_skin_in_game`              | 🟢 True if insiders own ≥ 5 % of outstanding shares                         |
| `rule_wide_economic_moat`        | 🟢 True if moat score ≥ 4/5 on your brand/network/switching-costs/IP rubric |


| Column Name                  | Description                                                                  |
| ---------------------------- | ---------------------------------------------------------------------------- |
| **Cash Conversion**          |                                                                              |
| `net_income`                 | Reported net income for the period                                           |
| `free_cash_flow`             | Operating cash flow – capital expenditures                                   |
| `earnings_to_fcf_ratio`      | net\_income ÷ free\_cash\_flow                                               |
| **Earnings Premium**         |                                                                              |
| `earnings_yield`             | Earnings yield: EPS ÷ share\_price  (or 1 ÷ pe\_ratio) × 100                 |
| `bond_yield_10yr`            | Current 10-year government bond yield                                        |
| `earnings_premium_pct`       | earnings\_yield – bond\_yield\_10yr                                          |
| **Debt Cushion**             |                                                                              |
| `total_debt`                 | Sum of short-term + long-term interest-bearing debt                          |
| `fair_value_equity_total`    | fair\_value\_blended × sharesOutstanding                                     |
| `debt_to_fair_equity_pct`    | total\_debt ÷ fair\_value\_equity\_total × 100                               |
| **Insider & Moat**           |                                                                              |
| `insider_ownership_pct`      | Total shares held by insiders ÷ sharesOutstanding × 100                      |
| `moat_score`                 | Composite moat rating (1–5) from your qualitative rubric                     |

