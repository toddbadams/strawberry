from dataclasses import dataclass


@dataclass
class ColumnConfig:
    in_name: str
    out_name: str
    type: str