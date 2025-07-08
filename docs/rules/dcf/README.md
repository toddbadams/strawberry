Here are some **benchmark ranges** and considerations you can use when setting up your DCF model. Of course, you’ll want to tailor each input to the company’s industry, lifecycle stage, and risk profile—these are just common starting points.

| Parameter                | Typical Range    | Rationale & Tips                                                                                                                                                 |
| ------------------------ | ---------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **High Growth Rate**     | 10 % – 25 % p.a. | Applies to the initial “super-normal” growth phase.  • High-tech or small-cap companies might use 20 %–25 %.  • Mature, stable sectors might be closer to 10 %.  |
| **High Growth Years**    | 5 – 10 years     | How long you expect that elevated growth to persist.  • Use 5 – 7 years for most companies.  • Up to 10 years if you have a long runway (e.g. emerging markets). |
| **Discount Rate (WACC)** | 8 % – 12 %       | Your weighted average cost of capital.  • Lower‐risk, large-cap firms often mid-8 %s. • Higher-beta firms or cyclical industries can approach 12 %.              |
| **Terminal Growth Rate** | 2 % – 4 %        | Long-term sustainable growth, typically near GDP+inflation.  • 2 %–3 % is common in developed markets.  • Up to 4 % for faster-growing economies or niches.      |

---

### How to Pick the Right Inputs for Your Company

1. **High Growth Rate**

   * **Bottom-up check:** Compare to 5-year historical revenue/EPS CAGR.
   * **Peer benchmark:** See consensus analyst forecasts (e.g. 10–15 % next 2 years, then taper).

2. **High Growth Period**

   * **Product lifecycle:** How long before growth normalizes (e.g. new‐tech hype vs. consumer staples)?
   * **Competitive dynamics:** Once moat builds, growth may slow—so lean toward the shorter end if competition is fierce.

3. **Discount Rate**

   * **Cost of debt:** Use your after-tax borrowing rate.
   * **Cost of equity:** CAPM: `r_e = r_f + β·(r_m – r_f)`.  • `r_f` = 10-yr government yield.  • `β` from regression or a peer-group average.
   * **WACC blend:** Weight debt/equity by market values and after-tax costs.

4. **Terminal Growth**

   * **Macro anchor:** Should not exceed long‐run GDP + inflation.
   * **Conservatism:** Many practitioners cap at 3 % in the U.S. to avoid overstating perpetual growth.

---

#### Example Inputs

| Scenario                    | High Growth Rate | High Growth Years | WACC  | Terminal Growth |
| --------------------------- | ---------------- | ----------------- | ----- | --------------- |
| **Big Tech**                | 20 %             | 8 years           | 9 %   | 3 %             |
| **Consumer Staples**        | 8 %              | 5 years           | 7.5 % | 2 %             |
| **Emerging-Market Telecom** | 15 %             | 10 years          | 11 %  | 4 %             |

Use these as a starting point, then stress-test your valuation by running sensitivity tables (e.g. +/- 1 % on WACC and terminal growth) to see how your fair value shifts under different market conditions.
