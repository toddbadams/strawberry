from src.consolidators.dividend_consolidator import DividendConsolidator
from src.consolidators.earnings_consolidator import EarningsConsolidator
from src.consolidators.income_statement_consolidator import IncomeStatementConsolidator
from src.consolidators.insiders_consolidator import InsiderConsolidator
from src.consolidators.stock_price_consolidator import StockPriceConsolidator
from src.consolidators.balance_sheet_consolidator import BalanceSheetConsolidator
from src.consolidators.cashflow_consolidator import CashflowConsolidator
from src.rules.dividend_rules import DividendRules
from src.rules.value_rules import ValueRules
from src.data.parquet_storage import ParquetStorage

class DataConsolidator:
    def __init__(self, data_path: str):
        self.storage = ParquetStorage(data_path)

    def consolidate(self, ticker: str):

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

        # apply rules
        dv_rules = DividendRules()
        df = dv_rules.dividend_yield_rule(df)
        df = dv_rules.dividend_growth_rule(df)
        v_rules = ValueRules()
        df = v_rules.dcf_ddm_value_rule(df) # todo:  find a way to introduce growth rates
        df = v_rules.pe_value_rule(df) # todo:   P/E v Peers and PEG

        # tidy and store
        df["symbol"] = ticker
        df.sort_values('qtr_end_date')
        self.storage.write_df(df, "CONSOLIDATED", partition_cols=["symbol"], index=False)

        print(df.columns)
        print(df.info())