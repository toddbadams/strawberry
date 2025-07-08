

| Column Name                      | Description                                                                 |
| -------------------------------- | --------------------------------------------------------------------------- |
| `rule_high_relative_yield`       | 🟢 True if dividend yield ≥ 1 σ above its 5-year historical average         |
| `rule_undervalued_stock`         | 🟢 True if current price ≤ 80 % of blended DCF/DDM fair-value               |
| `rule_moderate_dividend_growth`  | 🟢 True if 5-10 yr annual dividend growth rate is between 0.5 % and 10 %    |
| `rule_dividend_return_threshold` | 🟢 True if (current yield) + (5-10 yr avg dividend growth) > 12 %           |
| `rule_healthy_cash_conversion`   | 🟢 True if (net income / free cash flow) between 0.4 and 0.6                |
| `rule_attractive_valuation`      | 🟢 True if P/E ratio < median P/E of peer group                             |
| `rule_growth_adjusted_valuation` | 🟢 True if PEG ratio < 1                                                    |
| `rule_earnings_premium`          | 🟢 True if projected earnings yield (1/price) ≥ (10-yr bond yield + 2 %)    |
| `rule_debt_cushion`              | 🟢 True if total debt ≤ 50 % of fair-value equity                           |
| `rule_skin_in_game`              | 🟢 True if insiders own ≥ 5 % of outstanding shares                         |
| `rule_wide_economic_moat`        | 🟢 True if moat score ≥ 4/5 on your brand/network/switching-costs/IP rubric |



Here’s a suggested set of raw-metric columns to accompany your boolean rule flags. You can drop these into your consolidated table so you have both the underlying values and the pass/fail for each screen.

| Column Name                  | Description                                                                  |
| ---------------------------- | ---------------------------------------------------------------------------- |
| **Dividend Yield & Z-Score** |                                                                              |
| `dividend_yield`             | Annual dividend per share ÷ share price                                      |
| `yield_historical_mean_5y`   | 5-year historical average dividend yield                                     |
| `yield_historical_std_5y`    | 5-year historical standard deviation of dividend yield                       |
| `yield_zscore`               | (dividend\_yield – yield\_historical\_mean\_5y) ÷ yield\_historical\_std\_5y |
| **Fair-Value & Valuation**   |                                                                              |
| `fair_value_dcf`             | Intrinsic value per share from your DCF model                                |
| `fair_value_ddm`             | Intrinsic value per share from your DDM model                                |
| `fair_value_blended`         | (fair\_value\_dcf + fair\_value\_ddm) ÷ 2                                    |
| `fair_value_gap_pct`         | (fair\_value\_blended – share\_price) ÷ fair\_value\_blended × 100           |
| **Dividend Growth**          |                                                                              |
| `dividend_growth_rate_5y`    | Compound annual dividend growth rate over the past 5 years                   |
| **Dividend Return**          |                                                                              |
| `dividend_yield_plus_growth` | dividend\_yield + dividend\_growth\_rate\_5y                                 |
| **Cash Conversion**          |                                                                              |
| `net_income`                 | Reported net income for the period                                           |
| `free_cash_flow`             | Operating cash flow – capital expenditures                                   |
| `earnings_to_fcf_ratio`      | net\_income ÷ free\_cash\_flow                                               |
| **Valuation Ratios**         |                                                                              |
| `pe_ratio`                   | Price/Earnings: share\_price ÷ EPS                                           |
| `peer_group_pe_median`       | Median P/E of the defined peer group                                         |
| `pe_vs_peer_delta_pct`       | (peer\_group\_pe\_median – pe\_ratio) ÷ peer\_group\_pe\_median × 100        |
| `peg_ratio`                  | PEG: pe\_ratio ÷ projected\_EPS\_growth\_rate                                |
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

You can compute each of these alongside your existing joins, then derive your `rule_…` booleans directly from them.

