from datetime import datetime
from pathlib import Path
import shutil
import pandas as pd
from typing import Optional

from strawberry.logging.logger_factory import LoggerFactory
from strawberry.config.config_loader import ConfigLoader

class ParquetStorage:

    def __init__(self, folder: Path):
        self.logger = LoggerFactory().create_logger(__name__)
        self.config = ConfigLoader()
        self.env = self.config.environment()
        self.engine: str = "pyarrow"
        self.folder = folder

    def _table_path(self, table_name: str) -> Path:
        return self.env.data_root / self.folder / f"{table_name}"
    
    def _partition_path(self, table_name: str, partition_name: str) -> Path:
        return self._table_path(table_name) / Path(f"symbol={partition_name}")
    
    def last_update(self, table_name: str, partition_name: str = None) -> datetime:
        """
        Return the most recent modification datetime of parquet files
        for a given table, optionally scoped to a symbol partition.
        """
        # Determine search directory: either table root or specific partition
        if partition_name:
            search_path = self._partition_path(table_name, partition_name)
        else:
            search_path = self._table_path(table_name)

        # If path doesn't exist, nothing to update
        if not search_path.exists():
            return None

        # Gather parquet files
        files = []
        # If a single parquet file at the root
        if search_path.is_file() and search_path.suffix == ".parquet":
            files = [search_path]
        else:
            files = list(search_path.glob("**/*.parquet"))

        if not files:
            return None

        # Select most recent modification time
        latest_mtime = max(f.stat().st_mtime for f in files)
        return datetime.fromtimestamp(latest_mtime)

    def exists(self, table_name: str, ticker: str = None) -> bool:
        # If a ticker was provided, look in its partition sub‑dir
        p = self._partition_path(table_name, ticker) if ticker is not None else self._table_path(table_name)

        if not p.is_dir():
            return False

        # Any .parquet files present?
        return any(p.glob("*.parquet"))

    def all_exist(self, table_names: list[str], ticker: str | None = None) -> bool:
        """
        Return True only if *all* given tables exist (optionally within the same ticker partition).
        Empty iterable returns False by default.
        """
        table_names = list(table_names)
        if not table_names:
            return False
        return all(self.exists(t, ticker) for t in table_names)

    def write_df(self, df: pd.DataFrame, table_name: str, partition_cols: list[str] = None, index: bool = False):
        path = self._table_path(table_name)
        path.parent.mkdir(parents=True, exist_ok=True)
        df.to_parquet(str(path), engine=self.engine, partition_cols=partition_cols, index=index)

    def read_df(self, table_name: str, ticker: Optional[str] = None) -> pd.DataFrame:        # Base directory for this table
        table_dir = self._table_path(table_name)

        # If a ticker was provided, look in its partition sub‑dir
        partition_dir = table_dir / Path(f"symbol={ticker}") if ticker is not None else table_dir

        # If the directory (or file) doesn’t exist, bail out with None
        if not partition_dir.exists():
            return None

        # Otherwise attempt to read; guard against any parquet errors too
        try:
            return pd.read_parquet(str(partition_dir), engine=self.engine)
        except (FileNotFoundError, OSError, pd.errors.EmptyDataError):
            return None
        
    def remove_partition_by_symbol(self, table_name: str, ticker: str) -> bool:
        """
        Permanently delete the partition directory for a given symbol.
        Returns True if the directory was found and removed, False otherwise.
        """
        partition_dir = self._table_path(table_name) / f"symbol={ticker}"
        if not partition_dir.is_dir():
            return False

        # Recursively delete the partition folder and its contents
        try:
            shutil.rmtree(partition_dir)
            return True
        except Exception:
            return False
        
    def get_tickers(self, table_name: str) -> list[str]:
        """
        Given a path like 'BALANCE_SHEET', find all subdirectories named
        'symbol=XXX' and return ['XXX', ...].
        """
        base_path = self._table_path(table_name)

        if not base_path.is_dir():
            raise ValueError(f"{table_name!r} is not a valid directory")

        symbols: list[str] = []
        for sub in base_path.iterdir():
            name = sub.name
            if sub.is_dir() and name.startswith("symbol="):
                # split on the first '=' and take the right side
                symbol = name.split("=", 1)[1]
                symbols.append(symbol)

        return symbols