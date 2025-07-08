Problem: You need a way to track the evolving risk-adjusted return of a stock using monthly prices (plus quarterly dividends) and quarterly risk-free rates, so you can see your Sharpe Ratio “running” over time.

Solution:  https://www.youtube.com/watch?v=9HD6xo2iO1g

1. **Compute monthly total returns**
   For month *t*, let

   $$
   r_t \;=\;\frac{P_t - P_{t-1} + D_t}{P_{t-1}}
   $$

   where

   * $P_t$ = month-end price
   * $D_t$ = dividends paid in month *t* (from the quarterly payout)

2. **Convert quarterly risk-free to monthly**
   If the risk-free APR for the quarter containing month *t* is $R_{f,Q}$, then approximate the monthly risk-free rate as

   $$
   rf_t \;=\;(1 + R_{f,Q})^{1/3} \;-\; 1
   $$

3. **Define your rolling window**
   Choose a window of $N$ months (e.g. 12 for a 1-year rolling Sharpe).

4. **Rolling Sharpe formula**
   At month *t*, over months $i = t-N+1,\dots,t$:

   * Average excess return

     $$
     \overline{r - rf}_t \;=\;\frac{1}{N}\sum_{i=t-N+1}^t (r_i - rf_i)
     $$
   * Standard deviation of excess returns

     $$
     \sigma_{t} \;=\;\sqrt{\frac{1}{N-1}\sum_{i=t-N+1}^t \bigl((r_i - rf_i) - \overline{r - rf}_t\bigr)^2}
     $$
   * **Rolling Sharpe** (annualized)

     $$
     S_t \;=\;\frac{\overline{r - rf}_t}{\sigma_t}\;\times\;\sqrt{12}
     $$

**Putting it all together:**

$$
S_t \;=\;\frac{
  \displaystyle \frac{1}{N}\sum_{i=t-N+1}^t\bigl(\tfrac{P_i - P_{i-1} + D_i}{P_{i-1}} - \bigl((1 + R_{f,Q(i)})^{1/3} -1\bigr)\bigr)
}{
  \displaystyle \sqrt{\frac{1}{N-1}\sum_{i=t-N+1}^t 
    \Bigl[\bigl(\tfrac{P_i - P_{i-1} + D_i}{P_{i-1}} - rf_i\bigr)
          - \overline{r-rf}_t\Bigr]^2
  }
}\;\times\;\sqrt{12}
$$

* **N** = length of the rolling window in months
* **$R_{f,Q(i)}$** = quarterly APR for the quarter of month *i*
* **Annualization** uses $\sqrt{12}$ for monthly data

With this in your pipeline, you can compute $S_t$ at each month *t* to see how your Sharpe Ratio “runs” over time.

# Todd's Notes

goal is sharp greater than 2
combine stock to create a larger sharp ratio (smoother return) - this hedges risk
leveraging amplifies both returns and volitility, however sharp ratio stays the same.
We can use high sharpe strategies to target even higher returns while maintaining idential sharpe
leverage comes with cost



# sample code

import pandas as pd
import numpy as np

def compute_rolling_sharpe(df: pd.DataFrame,
                           price_col: str = 'price',
                           dividend_col: str = 'dividend',
                           rf_apr_col: str = 'rf_apr',
                           window: int = 12) -> pd.Series:
    """
    Compute a rolling Sharpe ratio from monthly prices, quarterly dividends, and quarterly risk-free APR.

    Parameters:
    - df: DataFrame indexed by date (monthly).
    - price_col: Column name for month-end prices.
    - dividend_col: Column name for dividends paid in that month.
    - rf_apr_col: Column name for the quarterly risk-free APR (repeated for each month in the quarter).
    - window: Rolling window length in months (e.g., 12 for a 1-year Sharpe).

    Returns:
    - A pandas Series of rolling Sharpe ratios, aligned with the input dates.
    """
    # Ensure chronological order
    df = df.sort_index().copy()
    
    # 1. Monthly total return: (P_t - P_{t-1} + D_t) / P_{t-1}
    df['monthly_return'] = (df[price_col] - df[price_col].shift(1) + df[dividend_col]) / df[price_col].shift(1)
    
    # 2. Convert quarterly APR to monthly rate: (1 + APR)^(1/3) - 1
    df['rf_monthly'] = (1 + df[rf_apr_col]) ** (1/3) - 1
    
    # 3. Excess return
    df['excess_return'] = df['monthly_return'] - df['rf_monthly']
    
    # 4. Rolling statistics
    rolling_mean = df['excess_return'].rolling(window=window).mean()
    rolling_std = df['excess_return'].rolling(window=window).std(ddof=1)
    
    # 5. Annualize and compute Sharpe
    sharpe_ratio = rolling_mean / rolling_std * np.sqrt(12)
    
    return sharpe_ratio

# Example usage:
# df = pd.read_csv('historical.csv', parse_dates=['date'], index_col='date')
# sharpe_series = compute_rolling_sharpe(df)
# print(sharpe_series.tail())

