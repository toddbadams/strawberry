import pandas as pd

class DDMCalculator:

    def __init__(self, div_gr: float = 0.05,
                discount_rate: float = 0.0775):
        self.dividend_growth_rate = div_gr
        self.discount_rate = discount_rate

    def calc(self, dividend_series: pd.Series) -> list[float]:

        ddm_values = []

        for dividend in dividend_series:
            # Ensure dividend is a valid number
            if pd.isna(dividend) or dividend <= 0:
                ddm_values.append(None)
                continue

            # Gordon Growth Model for DDM
            try:
                ddm_valuation = round(dividend * (1 + self.dividend_growth_rate) / 
                                      (self.discount_rate - self.dividend_growth_rate), 2)
            except ZeroDivisionError:
                ddm_valuation = None

            ddm_values.append(ddm_valuation)
        return ddm_values