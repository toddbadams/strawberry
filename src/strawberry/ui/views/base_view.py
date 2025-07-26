from abc import ABC, abstractmethod
from pathlib import Path

from strawberry.logging.logger_factory import LoggerFactory
from strawberry.config.config_loader import ConfigLoader
from strawberry.repository.storage import ParquetStorage
from strawberry.acquisition.acquire import Acquire
from strawberry.ui.app_srv import AppServices
from strawberry.validation.validate import Validate
from strawberry.dimensions.dim_stocks import DimStocks


class BaseView(ABC):

    def __init__(self, service: AppServices):
        # Initialize logger
        self.logger = LoggerFactory().create_logger(self.__class__.__name__)
        self.srv = service

    @abstractmethod
    def render(self, ticker: str = None):
        pass
