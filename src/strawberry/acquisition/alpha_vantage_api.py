import requests

# define your new exceptions
class DataNotFoundError(Exception):
    """Raised when the API returns no data for a given ticker."""
    pass

class APILimitReachedError(Exception):
    """Raised when the AlphaVantage API limit is reached."""
    pass

class AlphaVantageAPI:
    """
    Simple client for Alpha Vantage REST API.
    """

    def __init__(self, api_key: str,
                 base_url: str = "https://www.alphavantage.co/query"):
        self.api_key = api_key
        self.base_url = base_url
        self.api_limit = 25
        self.calls = 0

    def fetch(self, function: str, symbol: str, datatype: str = "json") -> dict:
        # do not exceed api limit
        if self.calls >= self.api_limit:            
            return None
        self.calls += 1

        params = {
            "function": function,
            "symbol": symbol,
            "apikey": self.api_key,
            "datatype": datatype,
        }
        resp = requests.get(self.base_url, params=params) 
        resp.raise_for_status()
        data = resp.json()
        # ensure we have data to proceed
        if data is None:
            raise DataNotFoundError(f"{symbol} | {function} | Alpha Vantage - No data found.") 
        
        # ensure we have not reached API limit
        if 'Information' in data:
            raise APILimitReachedError(f"{symbol} | {function} | Alpha Vantage API limit reached.")
        return data
