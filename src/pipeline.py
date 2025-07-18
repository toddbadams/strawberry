
from pathlib import Path
import pandas as pd
#from prefect import flow, task, get_run_logger

from alpha_vantage.injestor import APILimitReachedError, DataNotFoundError
import scoring as scoring
import transform as transform
import config as config
import alpha_vantage as av
from repository.storage import ParquetStorage

from logger_factory import LoggerFactory

class DataPipeline:
    def __init__(self):
        self.logger = LoggerFactory().create_logger(__name__)
        self.config_loader = config.ConfigLoader(self.logger)
        self.env = self.config_loader.environment()
        self.api = av.AlphaVantageAPI(self.env.alpha_vantage_api_key, self.env.alpha_vantage_url)
        self.storage = ParquetStorage(self.env.output_path)
        self.tickers = self.config_loader.load_tickers()
        self.acq_tables = self.config_loader.load_acquisition_config()
        self.tran_tables = self.config_loader.load_table_consolidation_config()
        #self.logger = get_run_logger() 

    #@task
    def acquisition(self):
        # acquire standard data
        i = av.Injestor(self.api)
        p = av.PriceInjestor(self.api)
        for ticker in self.tickers:
            msg = f"Acquiring ticker: {ticker}"
            self.logger.info(f"{msg}")
            for table in self.acq_tables:
                name = self.env.acquisition_path  / Path(table.name)
                table_msg = f"{msg} | table: {table.name}"
                # Check if data already exists to avoid unnecessary API calls
                if self.storage.exists(name, ticker):
                    self.logger.info(f"{table_msg} | data already exists.") 
                    continue
                try:
                    df = i.injest(table.name, table.attribute, ticker)
                    self.storage.write_df(df, name, partition_cols=['symbol'], index=False)
                except DataNotFoundError  as e:
                    self.logger.warning(f"{table_msg} | {str(e)}")
                    break  # go to next table
                except APILimitReachedError as e:
                    self.logger.warning(f"{table_msg} | {str(e)}")
                    return # end acquisition
                
            # Pricing API is very different shape, so we have a special injector
            table_name = 'TIME_SERIES_MONTHLY_ADJUSTED'
            table_msg = f"{msg} | table: {table_name}"
            path_name = self.env.acquisition_path  / Path(table_name)
            # Check if data already exists to avoid unnecessary API calls
            if self.storage.exists(path_name, ticker):
                self.logger.info(f"{table_msg} | data already exists.") 
                continue
            try:
                df = p.injest('TIME_SERIES_MONTHLY_ADJUSTED', 'Monthly Adjusted Time Series', ticker)
                self.storage.write_df(df, name, partition_cols=['symbol'], index=False)
            except DataNotFoundError  as e:
                self.logger.warning(f"{table_msg} | {str(e)}")
                break  # go to next table
            except APILimitReachedError as e:
                self.logger.warning(f"{table_msg} | {str(e)}")
                return # end acquisition

    def transform(self) -> bool:
        transformer = transform.StockTransformer(self.storage, self.logger)
        table_name = 'TRANSFORMED'
        df = pd.DataFrame()
        for ticker in self.tickers:             
            self.logger.info(f"Transforming ticker: {ticker}")

            for table in self.tran_tables:
                df = transformer.run(df, table, ticker)

            # run colum level calculations to enrich the consolidated dataset
            df = transform.ColumnCalculator(self.logger).run(df, ticker)
            df = scoring.DividendScoring().apply(df)
            df = scoring.AlphaPulseScoring().apply(df)

            # tidy 
            df["symbol"] = ticker
            df.sort_values('qtr_end_date')
            df.reset_index()
            self.storage.write_df(df, table_name, partition_cols=["symbol"], index=False)
            return True

    #@flow
    def run(self):
        self.acquisition()
       # self.transform()

DataPipeline().run()