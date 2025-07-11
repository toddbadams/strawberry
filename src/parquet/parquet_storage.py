
from pathlib import Path
import shutil
import pandas as pd
from typing import Optional

class ParquetStorage:
    """
    Utility for partitioned Parquet read/write.
    """

    def __init__(self, data_path: str):
        self.data_path = Path(data_path)
        self.engine: str = "pyarrow"

    def __table_root(self, table_name: str) -> Path:
        return self.data_path / f"{table_name}"

    def exists(self, table_name: str, symbol: str) -> bool:
        partition_dir = self.__table_root(table_name) / f"symbol={symbol}"
        if not partition_dir.is_dir():
            return False
        return any(partition_dir.glob("*.parquet"))

    def write_df(self, df: pd.DataFrame, table_name: str, partition_cols: list[str] = None, index: bool = False):
        root = self.__table_root(table_name)
        root.parent.mkdir(parents=True, exist_ok=True)
        df.to_parquet(str(root), engine=self.engine, partition_cols=partition_cols, index=index)

    def read_df(self, table_name: str, symbol: Optional[str] = None) -> pd.DataFrame:
        root = self.__table_root(table_name) 
        root = root / f"symbol={symbol}" if symbol else root
        # If the directory (or file) doesn’t exist, bail out with None
        if not root.exists():
            return None

        # Otherwise attempt to read; guard against any parquet errors too
        try:
            return pd.read_parquet(str(root), engine=self.engine)
        except (FileNotFoundError, OSError, pd.errors.EmptyDataError):
            return None
        
    def remove_partition_by_symbol(self, table_name: str, symbol: str) -> bool:
        """
        Permanently delete the partition directory for a given symbol.
        Returns True if the directory was found and removed, False otherwise.
        """
        partition_dir = self.__table_root(table_name) / f"symbol={symbol}"
        if not partition_dir.is_dir():
            return False

        # Recursively delete the partition folder and its contents
        shutil.rmtree(partition_dir)
        return True