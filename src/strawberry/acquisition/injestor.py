import pandas as pd
from .alpha_vantage_api import AlphaVantageAPI

# define your new exceptions
class DataNotFoundError(Exception):
    """Raised when the API returns no data for a given ticker."""
    pass

class APILimitReachedError(Exception):
    """Raised when the AlphaVantage API limit is reached."""
    pass

class Injestor():
    def __init__(self, alpha_vantage: AlphaVantageAPI):
        self.alpha_vantage = alpha_vantage
  
    def injest(self, name: str, attr: str, ticker: str):        
        data = self.alpha_vantage.fetch(name, ticker)
                
        # ensure we have data to proceed
        if data is None:
            raise DataNotFoundError("No data found.") 
        
        # ensure we have not reached API limit
        if 'Information' in data:
            raise APILimitReachedError(" API limit reached.")
                
        # create data frame 
        df = pd.DataFrame([data]) if attr is None else pd.DataFrame(data[attr])
        df['symbol'] = ticker

        return df
    

class PriceInjestor(Injestor):
  
    def injest(self, name: str, attr: str, ticker: str):
        """
        API Shape:
                                2025-07-18 2025-06-30   ...  1999-12-31 symbol
            1. open              289.1900   294.7300   ...    53.0600     CB
            2. high              290.5000   300.2700   ...    57.0000     CB
            3. low               273.2300   281.3900   ...    51.2500     CB
            4. close             274.1300   289.7200   ...    56.3100     CB
            5. adjusted close    274.1300   289.7200   ...    12.9761     CB
            6. volume            23197339   32291378   ...    9427500     CB
            7. dividend amount     0.0000     0.9700   ...     0.0000     CB
        Transposed (and returned shape):

        """
        df = super().injest(name, attr, ticker)                
        df.rename(columns={'index': 'date'}, inplace=True)
        return df
