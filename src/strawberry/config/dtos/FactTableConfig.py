from dataclasses import dataclass
from datetime import date
import json


@dataclass(frozen=True)
class FactColConfig:
    data_col_name: str  # column table name
    display_name: str  # column display name
    type: str  # type format of the column following printf format
    format: str  # plain, bold, italic
    indent: int  # 0 to 2, the number of spaces to indent
    isMetric: bool  # true if this is a metric column, false if it's a dimension
    tooltip: str  # a tooltip help message when overing over column head

    @classmethod
    def from_dict(cls, d: dict) -> "FactColConfig":
        return cls(**d)


@dataclass(frozen=True)
class FactTableConfig:
    val_table_name: str
    fact_table_name: str
    display_name: str
    date_col_name: str
    columns: list[FactColConfig]

    def data_col_names(self) -> list[str]:
        return [col.data_col_name for col in self.columns]

    def metric_col_names(self) -> list[str]:
        return [col.display_name for col in self.columns if col.isMetric]

    def get_metric_cols(self) -> list[FactColConfig]:
        return [col for col in self.columns if col.isMetric]

    def get_data_col_by_display_name(self, display_name: str) -> str:
        for col in self.columns:
            if col.display_name == display_name:
                return col.data_col_name
        raise ValueError(f"Column with display name '{display_name}' not found.")

    @classmethod
    def load_from_file(cls, path: str) -> "FactTableConfig":
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
            result = FactTableConfig(
                val_table_name=data["val_table_name"],
                fact_table_name=data["fact_table_name"],
                display_name=data["display_name"],
                date_col_name=data["date_col_name"],
                columns=[FactColConfig.from_dict(col) for col in data["columns"]],
            )
        return result
