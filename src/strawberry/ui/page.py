from src.config.config_loader import ConfigLoader
from logging.logger_factory import LoggerFactory
import pandas as pd
from abc import ABC, abstractmethod


class Page(ABC):
    def __init__(self,
                 config: ConfigLoader,
                 overview_df: pd.DataFrame,
                 consolidated_df: pd.DataFrame,
                 tickers: list[str],
                 selected_ticker: str,
                 unique_year_quarters: list[str],
                 selected_year_quarter: str,
                 logger: LoggerFactory):
        # assign constructor args to instance attrs
        self.config = config
        self.overview_df = overview_df
        self.consolidated_df = consolidated_df        
        self.tickers = tickers
        self.selected_ticker = selected_ticker
        self.unique_year_quarters = unique_year_quarters
        self.selected_year_quarter = selected_year_quarter
        self.logger = logger

    @abstractmethod
    def render(self):
        """Called to draw the page content in the main area."""
        pass