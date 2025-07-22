import os
import json
from pathlib import Path
import re
import shutil
import logging
from datetime import datetime
import pandas as pd

from strawberry.config.config_loader import ConfigLoader
from strawberry.config.dtos import AcquisitionTableConfig
from strawberry.repository.storage import ParquetStorage
from strawberry.logging.logger_factory import LoggerFactory

class ParquetETL:
    def __init__(self):
        
        # logging and configuration
        self.logger = LoggerFactory().create_logger(__name__)
        self.config = ConfigLoader()
        self.env = self.config.environment()
        cfg = self.config.acquisition()
        self.defaults = cfg.defaults
        self.tables = cfg.tables

        # Directories and files
        self.manifest_path = self.env.validated_folder
        self.acquisition_dir = Path(self.env.data_root) / self.env.acquisition_folder
        self.validated_dir = Path(self.env.data_root) / self.env.validated_folder
        self.exceptions_dir = Path(self.env.data_root) / self.env.validated_folder / Path("exceptions")

        self.val_store = ParquetStorage(self.env.validated_folder)
        self.acq_store = ParquetStorage(self.env.acquisition_folder)

        # manifest
        self.manifest_name = "manifest"
        if self.val_store.exists(self.manifest_name):
            self.manifest = self.val_store.read_df(self.manifest_name)
        else:
            cols = ['table', 'pk', 'status', 'last_checked', 'error']
            self.manifest = pd.DataFrame(columns=cols)
            self.logger.info("Initialized empty manifest.")

    def _save_manifest(self):
        self.val_store.write_df(self.manifest, self.manifest_name)

    def _validate_and_clean(self, row: dict, schema: dict):
        errors = []
        cleaned = {}
        for col in schema['columns']:
            name = col['name']
            val = row.get(name)

            # Nullability
            if val is None:
                if not col.get('nullable', True):
                    errors.append(f"{name} is null")
                cleaned[name] = None
                continue

            # Type & format
            t = col['type']
            try:
                if t == 'int':
                    v = int(val)
                elif t == 'float':
                    v = float(val)
                elif t == 'date':
                    fmt = col.get('format', '%Y-%m-%d')
                    v = datetime.strptime(val, fmt)
                else:
                    v = str(val)
            except Exception:
                errors.append(f"{name} failed {t} conversion")
                continue

            # Regex
            regex = col.get('regex')
            if regex and not re.match(regex, str(val)):
                errors.append(f"{name} regex mismatch")

            # Min/Max
            if 'min' in col and isinstance(v, (int, float)) and v < col['min']:
                errors.append(f"{name} < min")
            if 'max' in col and isinstance(v, (int, float)) and v > col['max']:
                errors.append(f"{name} > max")

            cleaned[name] = v

        if errors:
            return False, None, '; '.join(errors)
        return True, cleaned, None

    def _atomic_parquet_write(self, df: pd.DataFrame, path: str):
        """
        Atomically write a DataFrame to Parquet: write to .tmp then move.
        """
        tmp = path + '.tmp'
        df.to_parquet(tmp, index=False)
        shutil.move(tmp, path)

    def process_table(self, table_cfg: AcquisitionTableConfig, ticker):
        """
        Process a partitioned Parquet table for a specific ticker.

        Locates the source file under acquisition_folder/<table>/symbol=<ticker>/, validates and cleans,
        then writes out to validated and exceptions partitions.
        """
        name = table_cfg.name
        pk = table_cfg.primary_key

        # if no primary key, then nothing to clean, go to next
        if not pk:
            self.logger.error(f"No primaryKey defined for table {name}, skipping.")
            return
        
        # if the destination exists, then it's clean, so go to next
        if self.val_store.exists(name, ticker):
            return
        
        self.logger.info(f"Processing table: {name} (ticker={ticker})")

        # Build partitioned paths
        acq_dir = Path(self.acquisition_dir) / name / f"symbol={ticker}"
        val_dir = Path(self.validated_dir) / name / f"symbol={ticker}"
        exc_dir = Path(self.exceptions_dir) / name / f"symbol={ticker}"
        acq_path = acq_dir / f"{name}.parquet"
        val_path = val_dir / f"{name}.parquet"
        exc_path = exc_dir / f"{name}.parquet"

        # Read source
        df = self.acq_store.read_df(name, ticker) # pd.read_parquet(acq_path)

        # Validate and split rows
        good, bad, records = [], [], []
        for _, row in df.iterrows():
            rec = row.to_dict()
            ok, cleaned, err = self._validate_and_clean(rec, table_cfg)
            key = tuple(rec[c] for c in pk)
            base_record = {'table': name, 'ticker': ticker, 'pk': key, 'last_checked': datetime.now()}
            if ok:
                good.append(cleaned)
                records.append({**base_record, 'status':'SUCCESS', 'error': None})
            else:
                rec['error_msg'] = err
                bad.append(rec)
                records.append({**base_record, 'status':'FAILED', 'error': err})

        # Write validated rows
        if good:
            df_good = pd.DataFrame(good)
            if val_path.exists():
                df_good = pd.concat([pd.read_parquet(val_path), df_good], ignore_index=True)
            self._atomic_parquet_write(df_good, str(val_path))
            self.logger.info(f"Wrote {len(good)} valid rows to {val_path}.")

        # Write exception rows
        if bad:
            df_bad = pd.DataFrame(bad)
            if exc_path.exists():
                df_bad = pd.concat([pd.read_parquet(exc_path), df_bad], ignore_index=True)
            self._atomic_parquet_write(df_bad, str(exc_path))
            self.logger.info(f"Wrote {len(bad)} bad rows to {exc_path}.")

        # Update manifest
        self.manifest = pd.concat([self.manifest, pd.DataFrame(records)], ignore_index=True)
        self._save_manifest()


    def run_all(self):
        for tbl in self.tables:
            tickers = self.acq_store.get_tickers(tbl.name)
            for ticker in tickers:
                self.process_table(tbl, ticker)


# Example usage
if __name__ == '__main__':
    etl = ParquetETL( )
    etl.run_all()
