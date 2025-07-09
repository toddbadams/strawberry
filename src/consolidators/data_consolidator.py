import pandas as pd
from src.consolidators.dividend_consolidator import DividendConsolidator
from src.consolidators.earnings_consolidator import EarningsConsolidator
from src.consolidators.income_statement_consolidator import IncomeStatementConsolidator
from src.consolidators.insiders_consolidator import InsiderConsolidator
from src.consolidators.stock_price_consolidator import StockPriceConsolidator
from src.consolidators.balance_sheet_consolidator import BalanceSheetConsolidator
from src.consolidators.cashflow_consolidator import CashflowConsolidator
from src.parquet.parquet_storage import ParquetStorage

class DataConsolidator:
    def __init__(self, storage: ParquetStorage):
        self.storage = storage

    def consolidate(self, ticker: str) -> pd.DataFrame:

        # create the consolidator objects
        bs = BalanceSheetConsolidator(self.storage)
        cf = CashflowConsolidator(self.storage)
        ps = StockPriceConsolidator(self.storage)
        dv = DividendConsolidator(self.storage)
        er = EarningsConsolidator(self.storage)
        inc = IncomeStatementConsolidator(self.storage)
        ins = InsiderConsolidator(self.storage)
        
        # consolidate from data sources
        df = bs.consolidate(ticker)
        df = cf.consolidate(df, ticker)
        df = ps.consolidate(df, ticker)
        df = dv.consolidate(df, ticker)
        df = er.consolidate(df, ticker)
        df = inc.consolidate(df, ticker)
        df = ins.consolidate(df, ticker)

        # tidy 
        df["symbol"] = ticker
        df.sort_values('qtr_end_date')

        return df

