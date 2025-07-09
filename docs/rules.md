# Dividend Rules

## **Dividend Yield**

> **Rule of Thumb:** "Buy when the yield is high vs. historical average."
> * If a stock typically yields 2.5%, but now yields 3.2%, that may indicate **undervaluation**.
> * Tools like FastGraphs, Simply Safe Dividends, or YieldChart can show **historical yield bands**.

**Formula:** 
 - `Dividend Yield = Annual Dividend / Current Share Price`
 - `Dividend yield at least 1 σ (standard deviation) above its 5-year historical average.`

   
✅ **As a Quant Analyst**, I want to calculate each company’s current yield and its 5-year historical mean and standard deviation so that we can flag yields ≥ 1 σ above the mean.

   **Acceptance**: 

| Column Name                  | Description                                                                  |
| ---------------------------- | ---------------------------------------------------------------------------- |
| **Dividend Yield & Z-Score** |                                                                              |
| `dividend_yield`             | Annual dividend per share ÷ share price                                      |
| `yield_historical_mean_5y`   | 5-year historical average dividend yield                                     |
| `yield_historical_std_5y`    | 5-year historical standard deviation of dividend yield                       |
| `yield_zscore`               | (dividend\_yield – yield\_historical\_mean\_5y) ÷ yield\_historical\_std\_5y |
| `rule_dividend_yield`        | 🟢 True if dividend yield ≥ 1 σ above its 5-year historical average         |

## **Dividend Growth**

> **Why it matters:** A growing dividend = rising income and often signals financial health.
> * Most want at least **5-10% annual dividend growth**.
> * Some are OK with slower growth if the **yield is high** (think utilities, REITs).
> * They use the **Chowder Rule** to combine growth + yield.

**Chowder Rule:** `Dividend Yield + 5-Year Dividend Growth Rate > 12%`  (Thresholds vary slightly depending on the investor.)
   
✅ **As a Quant Analyst**, I want to calculate each company’s annual dividend growth over the past 5–10 years so that we can flag those with at least 0.5 % growth per year.

   **Acceptance**: 

| Column Name                  | Description                                                                  |
| ---------------------------- | ---------------------------------------------------------------------------- |
| `dividend_growth_rate_5y`    | Compound annual dividend growth rate over the past 5 years                   |
| `rule_dividend_growth`  | 🟢 True if 5-10 yr annual dividend growth rate > 5%    |
| `rule_dividend_chowder` | 🟢 True if (current yield) + (5-10 yr avg dividend growth) > 12 %           |



# Value Rules

## **DCF/DDM Value**
   – Current share price at least 20 % below your blended DCF / DDM fair-value estimate.

   ✅  **As a Quant Analyst**, I want to compute DCF and DDM fair-value estimates provide a current intrinsic value for each company.

   * **Acceptance**:   
  
| Column Name                  | Description                                                                  |
| ---------------------------- | ---------------------------------------------------------------------------- |
| `fair_value_dcf`             | Intrinsic value per share from your DCF model                                |
| `fair_value_ddm`             | Intrinsic value per share from your DDM model                                |
| `fair_value_blended`         | (fair\_value\_dcf + fair\_value\_ddm) ÷ 2                                    |
| `fair_value_gap_pct`         | (fair\_value\_blended – share\_price) ÷ fair\_value\_blended           |
| `rule_undervalued_stock`     | 🟢 True if current price ≤ 80 % of blended DCF/DDM fair-value               |


### DCF Valuation 

 A DCF valuation projects the business’s future free cash flows, discounts each one back to present value at your required rate of return, and sums them (plus a terminal value) to arrive at its intrinsic value.

**Formula:** 
```
free_cashflow_ps_TTM = (cperating_cashflow_ – capital_expenditures) / shares_outstanding

DCF_2stage = ∑[t=1 to high_growth_rate] { free_cashflow_ps_TTM · (1+high_growth_rate)ᵗ / (1+discount_rate)ᵗ } * 
    { FCFPS₀ · (1+high_growth_rate)ⁿ · (1+terminal_growth_rate) / \[ (discount_rate − terminal_growth_rate) · (1+discount_rate)ⁿ ] }
```

| Variable                     | Description                                                                           |
| ---------------------------- | ------------------------------------------------------------------------------------- |
| `free_cashflow_ps_TTM` FCFPS | Trailing-12-month free cash flow **per share**                                        |
| `high_growth_rate`     g\_h  | Assumed annual growth rate during the high-growth stage (decimal, e.g. 0.15 = 15 %)   |
| `high_growth_years`    n     | Number of years of high growth (integer)                                              |
| `terminal_growth_rate` g\_t  | Perpetual growth rate after the high-growth stage (decimal, must be < discount\_rate) |
| `discount_rate`        r     | Required rate of return / WACC (decimal, e.g. 0.10 = 10 %)                            |


Here are some **benchmark ranges** when setting up the DCF model. These should be added into the data store on a per ticker basis.

| Parameter                | Typical Range    | Notes                                                                                                                                                 |
| ------------------------ | ---------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **High Growth Rate**     | 10 % – 25 % p.a. | Perform a bottom-up check by comparing your assumed rate to the company’s five-year historical revenue or EPS CAGR. Then benchmark against peers by looking at consensus analyst forecasts—often you’ll see 10–15 % growth projected over the next two years before it tapers off. |
| **High Growth Years**    | 5 – 10 years     | Decide how long the company can sustain that above-average growth by examining its product lifecycle—is it riding a new-tech wave or a mature consumer staples market? Then factor in competitive dynamics: once a moat is established, growth tends to slow, so if competition is fierce you should lean toward a shorter runway. |
| **Discount Rate (WACC)** | 8 % – 12 %       | Calculate the cost of debt using the company’s after-tax borrowing rate. Estimate the cost of equity with the CAPM formula, $r_e = r_f + \beta \, (r_m - r_f)$, where $r_f$ is the 10-year government yield and $\beta$ comes from a regression or peer-group average. Finally, blend debt and equity costs into your WACC by weighting each by its market value.            |
| **Terminal Growth Rate** | 2 % – 4 %        | Tie your terminal growth rate to macro fundamentals—it shouldn’t exceed long-run GDP plus inflation. To stay conservative, many practitioners cap this rate at around 3 % for U.S. companies.    |


| Scenario                    | High Growth Rate | High Growth Years | WACC  | Terminal Growth |
| --------------------------- | ---------------- | ----------------- | ----- | --------------- |
| **Big Tech**                | 20 %             | 8 years           | 9 %   | 3 %             |
| **Consumer Staples**        | 8 %              | 5 years           | 7.5 % | 2 %             |
| **Emerging-Market Telecom** | 15 %             | 10 years          | 11 %  | 4 %             |



## **P/E Value**

When you compare a stock’s price-to-earnings multiple to its closest peers, a lower P/E can spotlight companies that the market might be undervaluing relative to their industry. By screening for stocks trading below the median P/E of their peer group, you can zero in on potential bargains whose earnings power isn’t fully reflected in today’s share price.


> Look at fundamentals, but with a dividend lens.
> * **P/E** (Price to Earnings): Lower P/E can mean undervaluation.
> * **P/FCF** (Price to Free Cash Flow): Especially important for capital-intensive sectors.
> * **PEG**: P/E relative to growth—if PEG < 1, it's usually attractive.

🔴 As a Quant Analyst, I want to calculate the median P/E ratio for each stock’s peer group and flag companies whose P/E falls below that median so that we can identify potentially undervalued opportunities.

   **Acceptance**: 

| Column Name                  | Description                                                                  |
| ---------------------------- | ---------------------------------------------------------------------------- |
| `pe_ratio`                   | Price/Earnings: share_price ÷ EPS                                            |
| `peer_group_pe_median`       | Median P/E of the defined peer group                                         |
| `pe_vs_peer_delta_pct`       | (peer_group_pe_median – pe_ratio) ÷ peer_group_pe_median × 100               |
| `peg_ratio`                  | PEG: pe_ratio ÷ projected_EPS_growth_rate                                    |
| `rule_attractive_valuation`  | 🟢 True if P/E ratio < median P/E of peer group                              |

    **Formula**:


```
pe_ratio                  = share_price / EPS
peer_group_pe_median      = median({ pe_ratio_i | i ∈ peer_group })
pe_vs_peer_delta_pct      = (peer_group_pe_median - pe_ratio) / peer_group_pe_median * 100
peg_ratio                 = pe_ratio / projected_EPS_growth_rate
rule_attractive_valuation = pe_ratio < peer_group_pe_median
```

# Health Rules

## **Healthy Cash Conversion**

> **Rule of Thumb:** "Earnings-to-free-cash-flow ratio between 0.4 and 0.6 signals efficient cash conversion."

- **Formula:**  
  `ebitda_to_fcflow = EBITDA / Free Cash Flow`

✅ **As a Quant Analyst**, I want to compute the earnings-to-free-cash-flow ratio for each company so that we can flag those between 0.4 and 0.6.

**Acceptance**:

| Column Name             | Description                                                      |
|------------------------ |------------------------------------------------------------------|
| `ebitda_to_fcflow`      | EBITDA divided by free cash flow                                 |
| `rule_cash_conversion`  | 🟢 True if `0.4 ≤ ebitda_to_fcflow ≤ 0.6`                        |

---

## **Growth-Adjusted Valuation**

> **Rule of Thumb:** "PEG ratio < 1 is usually attractive."

- **Formula:**  
  `peg_ratio = pe_ratio / projected_EPS_growth_rate`

✅ **As a Quant Analyst**, I want to calculate each company’s PEG ratio so that we can flag those with PEG < 1.

**Acceptance**:

| Column Name         | Description                                                      |
|---------------------|------------------------------------------------------------------|
| `peg_ratio`         | P/E ratio divided by projected EPS growth rate                   |
| `rule_peg`          | 🟢 True if `peg_ratio < 1.0`                                     |

---

## **Earnings Premium**

> **Rule of Thumb:** "Earnings yield should exceed the 10-yr bond yield by at least 2%."

- **Formula:**  
  `earnings_yield = EPS / share_price`  
  `rule_earnings_premium = earnings_yield ≥ bond_yield + 0.02`

✅ **As a Quant Analyst**, I want to compare each company’s earnings yield against the current 10-yr bond yield so that we can flag those with an earnings yield ≥ bond_yield + 2%.

**Acceptance**:

| Column Name              | Description                                                      |
|--------------------------|------------------------------------------------------------------|
| `earnings_yield`         | EPS divided by share price                                       |
| `rule_earnings_premium`  | 🟢 True if `earnings_yield ≥ bond_yield + 0.02`                  |

---

## **Debt Cushion**

> **Rule of Thumb:** "Total debt should be no more than 50% of fair-value equity."

- **Formula:**  
  `debt_to_equity_fv = total_debt / fair_value_equity`  
  `rule_debt_cushion = total_debt ≤ 0.5 × fair_value_equity`

✅ **As a Quant Analyst**, I want to compute total debt as a % of fair-value equity so that we can flag companies with debt ≤ 50% of equity.

**Acceptance**:

| Column Name             | Description                                                      |
|-------------------------|------------------------------------------------------------------|
| `debt_to_equity_fv`     | Total debt divided by fair-value equity                          |
| `rule_debt_cushion`     | 🟢 True if `debt_to_equity_fv ≤ 0.5`                             |

---

## **Skin in the Game**

> **Rule of Thumb:** "Insiders (executives & board) collectively own ≥ 5% of outstanding shares."

- **Formula:**  
  `rule_skin_in_game = insider_pct ≥ 0.05`

✅ **As a Quant Analyst**, I want to aggregate insider ownership data so that we can flag companies where insiders own ≥ 5% of shares.

**Acceptance**:

| Column Name             | Description                                                      |
|-------------------------|------------------------------------------------------------------|
| `insider_pct`           | Percentage of shares owned by insiders                           |
| `rule_skin_in_game`     | 🟢 True if `insider_pct ≥ 0.05`                                  |

---

## **Wide Economic Moat**

> **Rule of Thumb:** "Company scores ≥ 4 out of 5 on the moat rubric."

- **Formula:**  
  `rule_wide_moat = moat_score ≥ 4`

✅ **As a Quant Analyst**, I want to score each company on our 5-point moat rubric and flag those scoring ≥ 4.

**Acceptance**:

| Column Name             | Description                                                      |
|-------------------------|------------------------------------------------------------------|
| `moat_score`            | Score on 5-point economic moat rubric                            |
| `rule_wide_moat`        | 🟢 True if `moat_score ≥ 4`                                      |

# Data Engineering & Pipeline

## Data Engineering & Pipeline


- **Join and enrich datasets** to ensure each company record contains all required fields for rule calculations (e.g., EBITDA, free cash flow, EPS, share price, projected growth rates, insider ownership).
    - **Acceptance:**  
      - Each row in the master DataFrame contains all columns referenced in the rules tables.
      - Peer group information is attached for each company where applicable.
      - Derived fields (e.g., ratios, medians) are calculated and available for rule evaluation.

- **Automate rule application** so that all health and value rules are run on the latest data and results are stored for analysis and reporting.
    - **Acceptance:**  
      - A pipeline step applies each rule method to the DataFrame and appends the resulting columns.
      - Results are written to a persistent store (e.g., Parquet, SQL) with metadata on run time and data version.
      - Logs capture any errors or data quality issues for review.

- **Monitor data quality and pipeline health** so that issues are detected early and do not impact downstream analytics.
    - **Acceptance:**  
      - Automated checks for missing or anomalous values in key fields.
      - Alerts or logs are generated if data falls outside expected ranges or if pipeline steps fail.
      - Summary statistics and data quality reports are produced after each

