from prefect import flow, task

from strawberry.acquisition.acquire import Acquire
from strawberry.config.config_loader import ConfigLoader
from strawberry.dimensions.fact_qtr_financials import FactQrtFinancials
from strawberry.validation.validate import Validate
from strawberry.dimensions.dim_stocks import DimStocks
from strawberry.logging.logger_factory import LoggerFactory


class PrefectPipeline:

    def __init__(self):
        self.logger = LoggerFactory().create_logger(__name__)
        self.config = ConfigLoader()
        self.tickers = self.config.tickers()  # full list
        self.acquire_srv = Acquire()
        self.validate_srv = Validate()
        self.dim_stock_srv = DimStocks()
        self.fact_q_fin_srv = FactQrtFinancials()

    @task
    def read_tickers_to_acquire(self) -> list[str]:
        # given the full list of tickers reduce to only those not yet acquired
        return self.acquire_srv.tickers_not_acquired(self.tickers)

    @task
    def read_tickers_to_validate(self) -> list[str]:
        return self.validate_srv.tickers_not_validated(self.tickers)

    @task
    def acquire_stock(self, ticker: str) -> bool:
        return self.acquire_srv.acquire_ticker(ticker=ticker)

    @task
    def validate_stock(self, ticker: str) -> bool:
        return self.validate_srv.validate_ticker(ticker=ticker)

    @task
    def dimension_stock(self) -> bool:
        return self.dim_stock_srv.dimension_ticker()

    @task
    def fact_qtr_financials(self, ticker: str) -> bool:
        return self.fact_q_fin_srv.fact_ticker(ticker)

    @task
    def fact_qtr_ratios(self, ticker: str) -> bool:
        return True

    @task
    def fact_qtr_dividend_scores(self, ticker: str) -> bool:
        return True

    @task
    def fact_qtr_alpha_scores(self, ticker: str) -> bool:
        return True

    @flow
    def pipeline(self):
        # get a list of tickers to acquire
        tickers = self.read_tickers_to_acquire()
        for t in tickers:
            success = self.acquire_stock(t)
            if not success:
                # skip to validation
                break

        # validate any files that have been acquired but not yet validated
        tickers = self.read_tickers_to_validate()
        for t in tickers:
            self.validate_stock(t)

        # Dimensions are run across all validated tables
        self.dimension_stock()
        tickers = self.dim_stock_srv.tickers_dimensioned()
        for t in tickers:
            self.fact_qtr_financials(t)
        """
            for t in self.dim_stock_srv.tickers_dimensioned():
            if not self.dimension_stock.submit(ticker):
                return
            if not self.fact_qtr_financials.submit(ticker):
                return
            if not self.fact_qtr_ratios.submit(ticker):
                return
            if not self.fact_qtr_dividend_scores.submit(ticker):
                return
            if not self.fact_qtr_alpha_scores.submit(ticker):
                return
        """


if __name__ == "__main__":
    p = PrefectPipeline()
    p.pipeline()
