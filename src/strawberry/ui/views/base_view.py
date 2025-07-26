from abc import ABC, abstractmethod

from strawberry.logging.logger_factory import LoggerFactory
from strawberry.ui.app_srv import AppServices


class BaseView(ABC):

    def __init__(self, service: AppServices):
        # Initialize logger
        self.logger = LoggerFactory().create_logger(self.__class__.__name__)
        self.srv = service

    @abstractmethod
    def render(self, ticker: str = None):
        pass
