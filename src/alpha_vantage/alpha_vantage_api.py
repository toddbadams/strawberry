import requests
import logging

class AlphaVantageAPI:
    """
    Simple client for Alpha Vantage REST API.
    """

    def __init__(self, api_key: str,
                 logger: logging.Logger, 
                 base_url: str = "https://www.alphavantage.co/query"):
        self.api_key = api_key
        self.base_url = base_url
        self.api_limit = 25
        self.calls = 0
        self.logger = logger

    def fetch(self, function: str, symbol: str, datatype: str = "json") -> dict:
        # do not exceed api limit
        if self.calls >= self.api_limit:            
            print(f"daily limit reached: {symbol}")
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
        if not data:
            raise ValueError(f"Empty response from Alpha Vantage: {resp.text}")
        return data
