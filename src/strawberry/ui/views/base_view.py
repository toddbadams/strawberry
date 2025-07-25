from abc import ABC, abstractmethod


class BasePlaceholderView(ABC):
    @abstractmethod
    def render(self, ticker: str = None):
        pass
