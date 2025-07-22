from dataclasses import dataclass


@dataclass
class ConsolidateColumnConfig:
    in_name: str
    out_name: str
    type: str