import pandas as pd
from src.alpha_vantage.alpha_vantage_api import AlphaVantageAPI
from src.parquet.parquet_storage import ParquetStorage


class FinancialDataInjestor:
    """
    High-level extractor of financial data via AlphaVantageAPI and storing to ParquetStorage.
    """

    def __init__(
        self,
        api_key: str,
        data_path: str,
        symbol: str,
        base_url: str,
    ):
        self.api = AlphaVantageAPI(api_key, base_url)
        self.storage = ParquetStorage(data_path)
        self.symbol = symbol

    def __parse_dates(self, df: pd.DataFrame, parse_dates: dict[str, dict]):
        """
        Parse date columns in the DataFrame based on provided options.
        """
        for col, opts in parse_dates.items():
            df[col] = df[col].replace(opts.get('none', "None"), None)
            df[col] = pd.to_datetime(df[col], errors=opts.get('errors', 'coerce'))
        return df
    
    def __extract(self, raw: dict | list, table_name: str):
        df = pd.DataFrame(raw) if isinstance(raw, list) else pd.DataFrame([raw])
        df['symbol'] = self.symbol
        self.storage.write_df(df, table_name, partition_cols=['symbol'], index=False)

    def __fetch_historical_dividends(self) -> bool:
        """
        Fetches historical dividend data for the symbol and stores it in Parquet format.
        """
        name = "DIVIDENDS"
        
        # Check if data already exists to avoid unnecessary API calls
        # Note: The storage.exists method checks for the existence of data for the given symbol.
        if self.storage.exists(name, self.symbol):
            print(f"Dividenss already exist: {self.symbol}")
            return True
        
        data = self.api.fetch(name, self.symbol)
        # ensure we have data to proceed
        if data == None or 'Information' in data:
            return False

        data = data['data']
        self.__extract(data, name)
        return True

    def read_historical_dividends(self) -> pd.DataFrame:
        return self.storage.read_df("DIVIDENDS", filters=[('symbol', '=', self.symbol)])

    def __fetch_monthly_adjusted_time_series(self) -> bool:
        """
        This API returns monthly adjusted time series (last trading day of each month, monthly open, monthly high, monthly low, 
        monthly close, monthly adjusted close, monthly volume, monthly dividend) of the equity specified, covering 20+ years of 
        historical data.
        """
        name = "TIME_SERIES_MONTHLY_ADJUSTED"
        
        # Check if data already exists to avoid unnecessary API calls
        # Note: The storage.exists method checks for the existence of data for the given symbol.
        if self.storage.exists(name, self.symbol):
            print(f"Time series already exist: {self.symbol}")
            return True
        
        data = self.api.fetch(name, self.symbol)
        # ensure we have data to proceed
        if data == None or 'Information' in data:
            return False
        
        data = data['Monthly Adjusted Time Series']
        df = pd.DataFrame.from_dict(data, orient="index")
        df = df.reset_index()
        df.rename(columns={'index': 'date'}, inplace=True)
        df['symbol'] = self.symbol
        self.storage.write_df(df, name, partition_cols=['symbol'], index=False)
        return True

    def read_monthly_adjusted_time_series(self) -> pd.DataFrame:
        return self.storage.read_df("TIME_SERIES_MONTHLY_ADJUSTED", filters=[('symbol', '=', self.symbol)])

    def __fetch_insider_transactions(self) -> bool:
        """
        This API returns the latest and historical insider transactions made by key stakeholders 
        (e.g., founders, executives, board members, etc.) of a specific company.
        """
        name = "INSIDER_TRANSACTIONS"
        
        # Check if data already exists to avoid unnecessary API calls
        # Note: The storage.exists method checks for the existence of data for the given symbol.
        if self.storage.exists(name, self.symbol):
            print(f"Insider transactions already exist: {self.symbol}")
            return True
        
        data = self.api.fetch(name, self.symbol)
        # ensure we have data to proceed
        if data == None or 'Information' in data:
            return False
        
        self.__extract(data['data'], name)
        return True

    def read_insider_transactions(self) -> pd.DataFrame:
        return self.storage.read_df("INSIDER_TRANSACTIONS", filters=[('symbol', '=', self.symbol)])

    def __fetch_company_overview(self) -> bool:
        """
        This API returns the company information, financial ratios, and other key metrics for the 
        equity specified. Data is generally refreshed on the same day a company reports its latest 
        earnings and financials.
        """
        name = "OVERVIEW"
        
        # Check if data already exists to avoid unnecessary API calls
        # Note: The storage.exists method checks for the existence of data for the given symbol.
        if self.storage.exists(name, self.symbol):
            print(f"Overview already exist: {self.symbol}")
            return True
        
        data = self.api.fetch(name, self.symbol)
        # ensure we have data to proceed
        if data == None or 'Information' in data:
            return False
        
        self.__extract(data, name)
        return True

    def read_company_overview(self) -> pd.DataFrame:
        return self.storage.read_df("OVERVIEW", filters=[('symbol', '=', self.symbol)])

    def __fetch_income_statements(self) -> bool:
        """
        This API returns the annual and quarterly income statements for the company of interest, with 
        normalized fields mapped to GAAP and IFRS taxonomies of the SEC. Data is generally refreshed on 
        the same day a company reports its latest earnings and financials.
        """
        name = "INCOME_STATEMENT"
        
        # Check if data already exists to avoid unnecessary API calls
        # Note: The storage.exists method checks for the existence of data for the given symbol.
        if self.storage.exists(name, self.symbol):
            print(f"Income statement already exist: {self.symbol}")
            return True
        
        data = self.api.fetch(name, self.symbol)
        # ensure we have data to proceed
        if data == None or 'Information' in data:
            return False
        
        self.__extract(data['quarterlyReports'], name)
        return True

    def read_income_statements(self) -> pd.DataFrame:
        return self.storage.read_df("INCOME_STATEMENT", filters=[('symbol', '=', self.symbol)])

    def __fetch_balance_sheets(self) -> bool:
        """
        This API returns the annual and quarterly balance sheets for the company of interest, with normalized 
        fields mapped to GAAP and IFRS taxonomies of the SEC. Data is generally refreshed on the same day a 
        company reports its latest earnings and financials.
        """
        name = "BALANCE_SHEET"
        
        # Check if data already exists to avoid unnecessary API calls
        # Note: The storage.exists method checks for the existence of data for the given symbol.
        if self.storage.exists(name, self.symbol):
            print(f"Balance sheet already exist: {self.symbol}")
            return True
        
        data = self.api.fetch(name, self.symbol)
        # ensure we have data to proceed
        if data == None or 'Information' in data:
            return False
        
        self.__extract(data['quarterlyReports'], name)
        return True

    def read_balance_sheets(self) -> pd.DataFrame:
        return self.storage.read_df("BALANCE_SHEET", filters=[('symbol', '=', self.symbol)])

    def __fetch_cash_flow_statements(self) -> bool:
        """
        This API returns the annual and quarterly cash flow for the company of interest, with normalized fields mapped 
        to GAAP and IFRS taxonomies of the SEC. Data is generally refreshed on the same day a company reports its 
        latest earnings and financials.
        """
        name = "CASH_FLOW"
        
        # Check if data already exists to avoid unnecessary API calls
        # Note: The storage.exists method checks for the existence of data for the given symbol.
        if self.storage.exists(name, self.symbol):
            print(f"Cashflow already exist: {self.symbol}")
            return True
        
        data = self.api.fetch(name, self.symbol)
        # ensure we have data to proceed
        if data == None or 'Information' in data:
            return False
        
        self.__extract(data['quarterlyReports'], name)
        return True

    def read_cash_flow_statements(self) -> pd.DataFrame:
        return self.storage.read_df("CASH_FLOW", filters=[('symbol', '=', self.symbol)])     

    def __fetch_earnings(self) -> bool:
        """
        This API returns the annual and quarterly earnings (EPS) for the company of interest. 
        Quarterly data also includes analyst estimates and surprise metrics.
        """
        name = "EARNINGS"
        
        # Check if data already exists to avoid unnecessary API calls
        # Note: The storage.exists method checks for the existence of data for the given symbol.
        if self.storage.exists(name, self.symbol):
            print(f"Earnings already exist: {self.symbol}")
            return True
        
        data = self.api.fetch(name, self.symbol)
        # ensure we have data to proceed
        if data == None or 'Information' in data:
            return False
        
        self.__extract(data['quarterlyEarnings'], name)
        return True

    def read_earnings(self) -> pd.DataFrame:
        return self.storage.read_df("EARNINGS", filters=[('symbol', '=', self.symbol)])     
           
    def extract(self):
        """
        Extracts all financial data for the symbol.
        """
        if not self.__fetch_historical_dividends():
            return False
        if not self.__fetch_monthly_adjusted_time_series():
            return False
        if not self.__fetch_insider_transactions():
            return False
        if not self.__fetch_company_overview():
            return False
        if not self.__fetch_income_statements():
            return False
        if not self.__fetch_balance_sheets():
            return False
        if not self.__fetch_cash_flow_statements():
            return False
        if not self.__fetch_earnings():
            return False
        return True