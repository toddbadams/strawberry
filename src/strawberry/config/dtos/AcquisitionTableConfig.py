from dataclasses import dataclass


@dataclass
class AcquisitionTableConfig:
    name: str
    attribute: str
    columns: list[str]
    release_time: str  # e.g. "08:30"
    timezone: str      # e.g. "US/Eastern"
    frequency: str     # daily, monthly, quarterly
    date_column: str
    injestor: str = "Injestor"  # which injestor class to use (Injestor, PriceInjestor, etc.)