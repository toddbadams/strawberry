from dataclasses import dataclass
from typing import Optional


@dataclass
class ChartConfig:
    title: str
    metrics: list[str]
    metric_labels: list[str]
    y_label: str
    y_axis_format: str
    y_axis_min: Optional[float] = None
    y_axis_max: Optional[float] = None
    x_axis_range: Optional[int] = 10  # years