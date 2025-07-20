from typing import Optional
from .ChartConfig import ChartConfig


from dataclasses import dataclass


@dataclass
class DividendScoreParameter:
    name: str
    description: str
    raw_column_name: str
    raw_value: float
    score_column_name: str
    score_value: float
    weight: int
    chart: Optional[ChartConfig] = None