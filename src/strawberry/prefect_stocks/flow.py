from prefect import flow, task 

from strawberry.acquisition.acquire import Acquire
from strawberry.acquisition.alpha_vantage_api import APILimitReachedError, DataNotFoundError
from strawberry.config.config_loader import ConfigLoader
from strawberry.validation.validate import Validate
from strawberry.dimensions.dim_stocks import DimStocks

@task
def read_tickers_to_acquire() -> list[str]:
    tickers = ConfigLoader().tickers()
    # given the full list of tickers reduce to only those not yet acquired
    tickers = Acquire().tickers_not_acquired(tickers)
    # limit to the first two for now
    tickers = tickers[:2]
    return tickers

@task
def acquire_stock(ticker: str) -> str:
    return Acquire().acquire_ticker(ticker=ticker)

@task
def validate_stock(ticker: str) -> str:
    return Validate().validate_ticker(ticker=ticker)

@task
def dimension_stock(ticker: str) -> str:
    return DimStocks().transform_ticker(ticker=ticker)


@task
def fact_qtr_financials(ticker: str) -> str:
    return None

@task
def fact_qtr_ratios(ticker: str) -> str:
    return None

@task
def fact_qtr_dividend_scores(ticker: str) -> str:
    return None

@task
def fact_qtr_alpha_scores(ticker: str) -> str:
    return None


@flow  # (task_runner=ConcurrentTaskRunner())
def stock_pipeline_flow():
    tickers = read_tickers_to_acquire()

    # Fan-out: launch per-ticker sub-graph
    results = []
    for t in tickers:
        res = per_ticker_chain(ticker=t)
        results.append(res)

    return results

@flow
def per_ticker_chain(ticker: str):
    try:
        act = acquire_stock.submit(ticker)
    except (APILimitReachedError, DataNotFoundError) as e:
        return
    
    val = validate_stock.submit(ticker)
    dim = dimension_stock.submit(ticker)
    fin = fact_qtr_financials.submit(ticker)
    ratios = fact_qtr_ratios.submit(ticker)
    div = fact_qtr_dividend_scores.submit(ticker)
    alpha = fact_qtr_alpha_scores.submit(ticker)
    return {"ticker": ticker, "acquire": act, "validate": val,
            "dim": dim, "financials": fin, "ratios": ratios,
            "dividends": div, "alpha": alpha}

if __name__ == "__main__":
   results = stock_pipeline_flow()
   print(results)