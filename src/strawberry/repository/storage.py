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
        p = (
            self._partition_path(table_name, ticker)
            if ticker is not None
            else self._table_path(table_name)
        )

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

    def write_df(
        self,
        df: pd.DataFrame,
        table_name: str,
        partition_cols: list[str] = None,
        index: bool = False,
    ):
        path = self._table_path(table_name)
        path.parent.mkdir(parents=True, exist_ok=True)
        df.to_parquet(
            str(path), engine=self.engine, partition_cols=partition_cols, index=index
        )

    def read_df(self, table_name: str, ticker: Optional[str] = None) -> pd.DataFrame:
        # Base directory for this table
        table_dir = self._table_path(table_name)

        # If a ticker was provided, look in its partition sub‑dir
        partition_dir = (
            table_dir / Path(f"symbol={ticker}") if ticker is not None else table_dir
        )

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

    def column_has_unique_index(
        self, table_name: str, column_name: str, value: str
    ) -> bool:
        """
        Read the specified table, index by the given column, and check if the value exists in the indexed column.
        Returns True if exists, False otherwise.
        """
        # Load the DataFrame for the table
        df = self.read_df(table_name)
        if df is None:
            self.logger.warning(f"Table '{table_name}' does not exist or is empty.")
            return False
        # Ensure the column is present
        if column_name not in df.columns:
            self.logger.warning(
                f"Column '{column_name}' not found in table '{table_name}'."
            )
            return False
        # Attempt to set the index on the column
        try:
            indexed_df = df.set_index(column_name)
        except Exception as e:
            self.logger.error(f"Failed to set index on column '{column_name}': {e}")
            return False
        # Check if the value is present in the index
        return value in indexed_df.index

    def unique_column_list(self, table_name: str, column_name: str) -> list[str]:
        """
        Read the specified table, index by the given column (assumed unique),
        and return a list of all index values as strings.
        Returns an empty list if the table or column is missing or on error.
        """
        # Load the DataFrame for the table
        df = self.read_df(table_name)
        if df is None:
            self.logger.warning(f"Table '{table_name}' does not exist or is empty.")
            return []
        # Ensure the column is present
        if column_name not in df.columns:
            self.logger.warning(
                f"Column '{column_name}' not found in table '{table_name}'."
            )
            return []
        # Attempt to set the index on the column
        try:
            indexed_df = df.set_index(column_name)
        except Exception as e:
            self.logger.error(f"Failed to set index on column '{column_name}': {e}")
            return []
        # Return all unique index values as strings
        return [str(idx) for idx in indexed_df.index.tolist()]

    def update(self, table_name: str, index: str, df: pd.DataFrame) -> None:
        """
        Update a table by merging rows from df based on a unique index column.
        Existing rows with matching index values are replaced; new rows are appended.
        """
        # 1) Load existing table (if any)
        existing = self.read_df(table_name)
        if existing is None or existing.empty:
            # Nothing there yet → just write
            self.write_df(df, table_name, index=False)
            self.logger.info(f"Created new table '{table_name}' with {len(df)} rows.")
            return

        # 2) Sanity checks
        if index not in existing.columns:
            raise KeyError(f"Index column '{index}' not found in table '{table_name}'.")
        missing = set(existing.columns) - set(df.columns)
        extra = set(df.columns) - set(existing.columns)
        if missing or extra:
            raise ValueError(
                f"Column mismatch for '{table_name}'. "
                f"Missing in df: {missing}, extra in df: {extra}."
            )

        # 3) Drop old rows, keep the rest
        old_idx = existing.set_index(index)
        new_idx = df.set_index(index)
        keep = old_idx.drop(new_idx.index, errors="ignore")

        # 4) Concat + reset index
        combined = pd.concat([keep, new_idx]).reset_index()

        # 5) Remove on‑disk data so we don’t leave stale files around
        table_path = self._table_path(table_name)
        if table_path.exists():
            try:
                shutil.rmtree(table_path)
            except Exception as e:
                self.logger.error(f"Failed to clear old table dir: {e}")

        # 6) Write it back
        self.write_df(combined, table_name, index=False)
        self.logger.info(
            f"Updated table '{table_name}': {len(new_idx)} rows upserted, "
            f"{len(combined) - len(new_idx)} rows untouched."
        )
