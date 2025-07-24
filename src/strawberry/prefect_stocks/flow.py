from prefect import flow, task

from strawberry.acquisition.acquire import Acquire
from strawberry.config.config_loader import ConfigLoader
from strawberry.validation.validate import Validate
from strawberry.dimensions.dim_stocks import DimStocks
from strawberry.logging.logger_factory import LoggerFactory


class PrefectPipeline:

    def __init__(self):
        self.logger = LoggerFactory().create_logger(__name__)
        self.config = ConfigLoader()
        self.tickers = self.config.tickers()
        self.acquire = Acquire()
        self.validate = Validate()
        self.dim_stock = DimStocks()

    @task
    def read_tickers_to_acquire(self) -> list[str]:
        # given the full list of tickers reduce to only those not yet acquired
        tickers = self.acquire.tickers_not_acquired(self.tickers)
        # limit to the first two for now
        tickers = tickers[:2]
        return tickers

    @task
    def read_tickers_to_validate(self) -> list[str]:
        return self.validate.tickers_not_acquired(self.tickers)

    @task
    def acquire_stock(self, ticker: str) -> bool:
        return self.acquire.acquire_ticker(ticker=ticker)

    @task
    def validate_stock(self, ticker: str) -> bool:
        return self.validate.validate_ticker(ticker=ticker)

    @task
    def dimension_stock(self, ticker: str) -> bool:
        return self.dim_stock.transform_ticker(ticker=ticker)

    @task
    def fact_qtr_financials(self, ticker: str) -> bool:
        return True

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
        tickers = self.read_tickers_to_acquire()
        for t in tickers:
            self.acquire_ticker_pipeline(ticker=t)
        self.validate_pipeline()

    @flow
    def validate_pipeline(self):
        """
        In this flow we validate any files that have been acquired but not yet validated
        """
        tickers = self.read_tickers_to_validate()
        for t in tickers:
            self.validate_ticker_pipeline(ticker=t)

    @flow
    def acquire_ticker_pipeline(self, ticker: str):
        if not self.acquire_stock.submit(ticker):
            return
        if not self.validate_stock.submit(ticker):
            return
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

    @flow
    def validate_ticker_pipeline(self, ticker: str):
        if not self.validate_stock.submit(ticker):
            return
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


if __name__ == "__main__":
    p = PrefectPipeline()
    p.pipeline()
