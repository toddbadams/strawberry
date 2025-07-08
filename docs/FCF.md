Alright, here's the deal:

You’ve got **quarterly returns** for the past 20 years — that's *performance data*, not actual financials. But to calculate **Free Cash Flow (FCF)** and **Levered Free Cash Flow (LFCF)**, you need **fundamental accounting data**, not just returns.

---

### 🚨 Problem:

Returns alone (price-based data) **don’t contain operating cash flows, CapEx, interest, or debt repayments** — all of which are essential for FCF and LFCF calculations.

---

### ✅ Solution: What You Actually Need

To compute **FCF and LFCF quarterly**, gather the following **per quarter** from financial statements (cash flow and income statement):

#### 📊 Required Inputs (per quarter):

| Metric                       | Needed For      | Source                                  |
| ---------------------------- | --------------- | --------------------------------------- |
| Operating Cash Flow (OCF)    | Both FCF & LFCF | Cash Flow Statement                     |
| Capital Expenditures (CapEx) | Both            | Cash Flow Statement                     |
| Interest Payments            | LFCF only       | Income Statement / Notes                |
| Debt Repayments              | LFCF only       | Cash Flow Statement (Financing section) |

---

### 🧮 FCF Formula (per quarter):

```
FCF = Operating Cash Flow – Capital Expenditures
```

### 🧮 LFCF Formula (per quarter):

```
LFCF = Operating Cash Flow – Capital Expenditures – Interest – Mandatory Debt Repayments
```

---

### 🛠️ Step-by-Step (assuming you can get the data):

1. **Download financial statements** for each quarter (ideally from a data provider like Bloomberg, Capital IQ, or even EDGAR/10-Qs).
2. Extract the required fields.
3. Use the formulas above.
4. Repeat for each quarter across the 20 years.

---

### 🔁 Bonus: Automate It (Optional)

If you’re working with Python and, say, `pandas`, you can automate this with a dataset containing:

* `quarter`, `OCF`, `CapEx`, `Interest`, `DebtRepayments`

```python
df['FCF'] = df['OperatingCashFlow'] - df['CapEx']
df['LFCF'] = df['FCF'] - df['Interest'] - df['DebtRepayments']
```

---

### 👉 Bottom Line:

You **can’t calculate FCF or LFCF from returns alone** — you need **quarterly cash flow and income data**. Once you’ve got that, it’s simple arithmetic.

Want help structuring the data source or automating the calculations? I can walk you through that too.
