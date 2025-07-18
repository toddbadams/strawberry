import pandas as pd
import alpha_vantage as av

# define your new exceptions
class DataNotFoundError(Exception):
    """Raised when the API returns no data for a given ticker."""
    pass

class APILimitReachedError(Exception):
    """Raised when the AlphaVantage API limit is reached."""
    pass

class Injestor():
    def __init__(self, alpha_vantage: av.AlphaVantageAPI):
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
        df = super().injest(name, attr, ticker)                
        df = df.rename(columns={'index': 'date'}, inplace=True)
        return df