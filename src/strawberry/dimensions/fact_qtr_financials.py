import pandas as pd


from strawberry.config.config_loader import ConfigLoader
from strawberry.config.dtos import ValTableConfig
from strawberry.dimensions.dim_stocks import DimStocks
from strawberry.repository.storage import ParquetStorage
from strawberry.logging.logger_factory import LoggerFactory


class FactQrtFinancials:

    TABLE_NAME = "FACT_QTR_FINANCIALS"

    def __init__(self):
        self.logger = LoggerFactory().create_logger(__name__)
        self.config = ConfigLoader()
        self.env = self.config.environment()
        self.cfg = self.config.fact_qtr_financials()
        tables = [x.name for x in self.cfg]

        self.dim_store = ParquetStorage(self.env.dim_stocks_folder)
        self.val_store = ParquetStorage(self.env.validated_folder)

        # get a common set of tickers from the validation folder
        self.dim_stock_srv = DimStocks()
        self.tickers = sorted(self.dim_stock_srv.tickers_dimensioned())

    def _insider_transform(self, df: pd.DataFrame, date_col: str) -> pd.DataFrame:
        df = df.copy()

        # make shares negative when disposing and positive when acquired
        df.loc[df["acquisition_or_disposal"] == "D", "insider_shares"] *= -1

        # setup datetime index
        df[date_col] = pd.to_datetime(df[date_col])
        df.set_index(date_col, inplace=True)

        # Resample by quarter and sum
        quarterly = df["insider_shares"].resample("Q").sum()

        # Build result: quarter‐end dates and summed shares
        result = quarterly.reset_index().rename(
            columns={"date": "quarter_end", "insider_shares": "insider_shares"}
        )

        return result

    def _dividend_transform(self, df: pd.DataFrame, date_col: str) -> pd.DataFrame:
        # calc the fiscal date ending of each quarter
        df[date_col] = (
            df[date_col] + pd.offsets.QuarterEnd(0)
        ) - pd.offsets.QuarterEnd()
        return df

    def _pricing_transform(self, df: pd.DataFrame, date_col: str) -> pd.DataFrame:
        df = df.copy()
        df[date_col] = pd.to_datetime(df[date_col])
        df.set_index(date_col, inplace=True)

        # Resample to quarter-end, taking the last available record
        quarterly_last = df["share_price"].resample("QE").last()

        # Build result DataFrame
        df = quarterly_last.reset_index().rename(
            columns={date_col: "qtr_end_date", "share_price": "share_price"}
        )
        return df

    def _consolidate_table(self, table: ValTableConfig, ticker: str) -> pd.DataFrame:
        df = self.val_store.read_df(table.name, ticker)

        # get required columns
        df = df[table.in_names()]

        # rename columns
        df.rename(columns=table.in_to_out_map(), inplace=True)

        # get quarterly date column
        dates = table.date_out_names()

        # to do set the dates to the last of the quarter

        # SPECIAL CASES:
        if table.name == "INSIDER_TRANSACTIONS":
            df = self._insider_transform(df, dates[0])

        if table.name == "DIVIDENDS":
            df = self._dividend_transform(df, dates[0])

        if table.name == "TIME_SERIES_MONTHLY_ADJUSTED":
            df = self._pricing_transform(df, dates[0])

        self.logger.info(f"Table {table.name} consolidated for {ticker}.")
        return df if df.empty else df.merge(df, on=dates[0], how="left")

    def fact_ticker(self, ticker: str) -> bool:
        df = pd.DataFrame()
        for table in self.cfg:
            df2 = self._consolidate_table(table, ticker)
            if not df2.empty:
                df = df.merge(df2)
            else:
                self.logger.warning(f"{ticker} | FACT Qtrly Financials FAILED")
                return False

        # save the file in the transformed folder
        df["symbol"] = ticker
        self.dim_store.write_df(df, "CONSOLIDATED", ["symbol"])
        self.logger.info(f"{ticker} | FACT Qtrly Financials successful")
        return True

    def main(self):
        for ticker in self.tickers:
            self.fact_ticker(ticker)


if __name__ == "__main__":
    t = FactQrtFinancials()
    t.main()
