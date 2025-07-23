import pandas as pd


from strawberry.config.config_loader import ConfigLoader
from strawberry.config.dtos import  ConsolidationTableConfig, ConsolidateColumnConfig
from strawberry.data_utilities.series_conversion import SeriesConversion
from strawberry.repository.storage import ParquetStorage
from strawberry.logging.logger_factory import LoggerFactory


class DimStocks:
    
    def __init__(self):
        self.logger = LoggerFactory().create_logger(__name__)
        self.config = ConfigLoader()
        self.env = self.config.environment()
        self.cfg = self.config.dim_stock()

        self.dim_store = ParquetStorage(self.env.dim_stocks_folder) # we write to the transformed folder
        self.val_store = ParquetStorage(self.env.validated_folder) # we read from the validated folder        
        
        # get a set of tickers from the validation folder
        self.tickers = self.val_store.get_tickers(self.cfg.name)
        self.tickers = sorted(self.tickers)

        self.clean = SeriesConversion()        
    
    def _transform_column(self, log_prefix: str, series: pd.Series, col: ConsolidateColumnConfig) -> pd.Series:
        try:
            if col.type == "date":
                new_series = self.clean.to_datetime(series)
            elif col.type == "float":
                new_series = self.clean.to_float(series)
            elif col.type == "integer":
                new_series = self.clean.to_integer(series)
            else:
                new_series = series
            return new_series
        except (TypeError, ValueError) as e:
            self.logger.warning(f"{log_prefix} {col.out_name}  | {col.type} | {str(e)}")
            raise

    def _transform_table(self, table: ConsolidationTableConfig, ticker: str) -> pd.DataFrame:    
        log_prefix = f"{ticker} | {table.name} | "   
        df = self.val_store.read_df(table.name, ticker)

         # get required columns
        df = df[table.in_names()]        

        # rename columns
        df.rename(columns=table.in_to_out_map(), inplace=True)

        # convert and clean the columns
        for col in table.columns:
            df[col.out_name] = self._transform_column(log_prefix, df[col.out_name], col)

        # save the file in the transformed folder
        self.dim_store.write_df(df, "DIM_STOCKS")
        self.logger.info(f"{ticker} | consolidated and saved to transformed folder")


    def transform_table2(self) -> pd.DataFrame:   
        table = self.cfg 
        log_prefix = f" {table.name} | "   
        df = self.val_store.read_df(table.name)

         # get required columns
        df = df[table.in_names()]        

        # rename columns
        df.rename(columns=table.in_to_out_map(), inplace=True)

        # convert and clean the columns
        for col in table.columns:
            df[col.out_name] = self._transform_column(log_prefix, df[col.out_name], col)

        # save the file in the transformed folder
        self.dim_store.write_df(df, "DIM_STOCKS")
        self.logger.info(f"{log_prefix} | consolidated and saved to transformed folder")

    def transform_ticker(self, ticker: str):
        self.logger.info("do stuff")


    def main(self):
        for ticker in self.tickers:
            self._transform_table(self.cfg, ticker)

        
if __name__ == "__main__":
   t = DimStocks()
   t.transform_table2()   