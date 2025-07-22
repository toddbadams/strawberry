from datetime import datetime
from pathlib import Path
import pandas as pd
import logging
import numpy as np
import re

from strawberry.config.config_loader import ConfigLoader
from strawberry.config.dtos import AcquisitionTableConfig, ColumnConfig
from strawberry.repository.storage import ParquetStorage
from strawberry.logging.logger_factory import LoggerFactory


class Validate:
    NONE_TOKENS=("None", "none", "NULL", "", "-")
    DATE_RE = re.compile(r'((?:00|19|20)\d{2}-\d{2}-\d{2})')  # first ISO date

    def __init__(self):
        self.logger = LoggerFactory().create_logger(__name__)
        self.config = ConfigLoader()
        self.env = self.config.environment()
        self.tickers = self.config.tickers()
        self.acq_cfg = self.config.acquisition()

        self.acq_store = ParquetStorage(self.env.acquisition_folder) # we read from acquisition folder
        self.val_store = ParquetStorage(self.env.validated_folder) # we write to the validation folder

    
    def _to_datetime(self, series: pd.Series, col: ColumnConfig) -> pd.Series:
        # Normalize to string and Drop HTML/XML-ish tags and collapse whitespace
        clean = (series.astype(str)
                    .str.replace(r"<[^>]*>", "", regex=True)
                    .str.replace(r"\s+", " ", regex=True)
                    .str.strip())

        # Extract the first ISO date anywhere in the string
        clean = clean.str.extract(self.DATE_RE, expand=False)

        # Fix years that start with '00' -> assume 2000s (e.g. 0012 -> 2012)
        clean = clean.str.replace(r"^00(\d{2})", r"20\1", regex=True)

        # if not nullable and we have a null action, take it
        if not col.nullable and not col.null_action:
            mask_none = clean.str.strip().isin(self.NONE_TOKENS)
            clean = clean.where(~mask_none, pd.NA)

            # Parse to datetime (NaT for missing/bad)
            dt = pd.to_datetime(clean, format=col.format)

            # Fill ONLY the rows that were NONE_TOKENS with the previous value
            dt_filled = dt.where(~mask_none, dt.ffill())
            return dt_filled
        
        # Handle Python None automatically; handle string forms manually
        mask = clean.astype(str).str.strip().isin(self.NONE_TOKENS)
        clean[mask] = pd.NA
        clean = pd.to_datetime(clean, format=col.format)
        return clean   
    
    def _to_float(self, series: pd.Series) -> pd.Series:
        clean = series.copy()
        # Handle Python None automatically; handle string forms manually
        mask = clean.astype(str).str.strip().isin(self.NONE_TOKENS)
        clean[mask] = pd.NA
        clean = pd.to_numeric(clean)
        return clean.astype("float64", copy=False)    
    
    def _to_integer(self, series: pd.Series) -> pd.Series:
        clean = series.copy()
        # Handle Python None automatically; handle string forms manually
        mask = clean.astype(str).str.strip().isin(self.NONE_TOKENS)
        clean[mask] = pd.NA
        clean = pd.to_numeric(clean, downcast="integer")
        return clean.astype("Int64", copy=False)


    def validate_column(self, log_prefix: str, series: pd.Series, col: ColumnConfig) -> pd.Series:
        try:
            if col.type == "date":
                new_series = self._to_datetime(series, col)
            elif col.type == "float":
                new_series = self._to_float(series)
            elif col.type == "integer":
                new_series = self._to_integer(series)
            else:
                new_series = series
            return new_series
        except (TypeError, ValueError) as e:
            self.logger.warning(f"{log_prefix} {col.name}  | {col.type} | {str(e)}")
            raise
    

    def validate_table(self, log_prefix: str, table: AcquisitionTableConfig, ticker: str):   
        df = self.acq_store.read_df(table.name, ticker)
        for col in table.columns:
            df[col.name] = self.validate_column(log_prefix, df[col.name], col)
        
        # add a symbol column and store in validation directory
        df['symbol'] = ticker
        self.val_store.write_df(df, table.name, ["symbol"])
        self.logger.info(f"{log_prefix} validated")
    
    def validate(self):
        exceptions =[]

        for table in self.acq_cfg.tables:
            for ticker in self.tickers:
                log_prefix = f"{ticker} | {table.name} | "
                try:
                    # if NOT exists as an acquired table, skip
                    if not self.acq_store.exists(table.name, ticker):
                        self.logger.info(f"{log_prefix} not acquired, skipping")
                        continue
                    
                    # if exists as a validated table, skip
                    if self.val_store.exists(table.name, ticker):
                        self.logger.info(f"{log_prefix} alreaded validated, skipping")
                        continue

                    # validate the table
                    self.validate_table(log_prefix, table, ticker)


                except (TypeError, ValueError) as e:
                    exceptions = np.append(exceptions, [table.name, ticker, str(e)])
                    self.logger.warning(f"{log_prefix} {str(e)}")

        e_df = pd.DataFrame(exceptions, ['table', 'ticker', 'error'])
        self.val_store.write_df(e_df, "EXCEPTIONS")

if __name__ == "__main__":
   validator = Validate()
   validator.validate()

