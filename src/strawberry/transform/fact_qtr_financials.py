import pandas as pd


from strawberry.config.config_loader import ConfigLoader
from strawberry.config.dtos import ConsolidationTableConfig
from strawberry.repository.storage import ParquetStorage
from strawberry.logging.logger_factory import LoggerFactory


class FactQrtFinancials:
  
    def __init__(self):
        self.logger = LoggerFactory().create_logger(__name__)
        self.config = ConfigLoader()
        self.env = self.config.environment()
        self.cfg = self.config.fact_qtr_financials()
        tables = [x.name for x in self.cfg]

        self.trn_store = ParquetStorage(self.env.transformed_folder) # we write to the transformed folder
        self.val_store = ParquetStorage(self.env.validated_folder) # we read from the validated folder        
        
        # get a common set of tickers from the validation folder
        self.tickers = {t: set(self.val_store.get_tickers(t)) for t in tables}
        self.tickers = set.intersection(*self.tickers.values()) if self.tickers else set()
        self.tickers = sorted(self.tickers)

    def _insider_transform(self, df: pd.DataFrame, date_col: str) -> pd.DataFrame:
        df = df.copy()

        # make shares negative when disposing and positive when acquired
        df.loc[df["acquisition_or_disposal"] == "D", "insider_shares"] *= -1

        # setup datetime index
        df[date_col] = pd.to_datetime(df[date_col])
        df.set_index(date_col, inplace=True)

        # Resample by quarter and sum
        quarterly = df['insider_shares'].resample('Q').sum()

        # Build result: quarter‐end dates and summed shares
        result = (quarterly
            .reset_index()
            .rename(columns={'date': 'quarter_end', 'insider_shares': 'insider_shares'}))

        return result

    def _dividen_transform(self, df: pd.DataFrame, date_col: str) -> pd.DataFrame:      
        # calc the fiscal date ending of each quarter 
        df[date_col] = (df[date_col] + pd.offsets.QuarterEnd(0)) - pd.offsets.QuarterEnd()
        return df
    
    def _pricing_transform(self, df: pd.DataFrame, date_col: str) -> pd.DataFrame:
        df = df.copy()
        df[date_col] = pd.to_datetime(df[date_col])
        df.set_index(date_col, inplace=True)

        # Resample to quarter-end, taking the last available record
        quarterly_last = df['share_price'].resample('QE').last()

        # Build result DataFrame
        df = (
            quarterly_last
            .reset_index()
            .rename(columns={date_col: 'qtr_end_date', 'share_price': 'share_price'})
        )
        return df


    def _consolidate_table(self, table: ConsolidationTableConfig, ticker: str) -> pd.DataFrame:       
        df = self.val_store.read_df(table.name, ticker)

        # get required columns
        df = df[table.in_names()]        

        # rename columns
        df.rename(columns=table.in_to_out_map(), inplace=True)

        # convert date
        dates = table.date_out_names()
        for item in dates:
            df[item] = pd.to_datetime(df[item], errors='coerce')  
        
        # convert to number
        for item in table.number_out_names():
            df[item] = pd.to_numeric(df[item], errors='coerce')

        # SPECIAL CASES:
        if table.name == 'INSIDER_TRANSACTIONS':
            df = self._insider_transform(df, dates[0])

        if table.name == 'DIVIDENDS':
            df = self._dividen_transform(df, dates[0])

        if table.name == 'TIME_SERIES_MONTHLY_ADJUSTED':
            df = self._pricing_transform(df, dates[0])
              
        self.logger.info(f"Table {table.name} consolidated for {ticker}.")
        return df if df.empty else df.merge(df, on=dates[0], how="left")
    

    def _consoliate_ticker(self, ticker: str):
        df = pd.DataFrame()
        df['symbol'] = ticker
        for table in self.cfg:
            df = df.merge(self._consolidate_table(table, ticker))
            
        # save the file in the transformed folder
        self.trn_store.write_df(df, "CONSOLIDATED", ["symbol"])
        self.logger.info(f"{ticker} | consolidated and saved to transformed folder")
       

    def run(self):
        for ticker in self.tickers:
            self._consoliate_ticker(ticker)

if __name__ == "__main__":
   t = FactQrtFinancials()
   t.run()   