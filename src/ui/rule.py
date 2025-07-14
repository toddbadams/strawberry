from dataclasses import dataclass, field

@dataclass
class RuleChartConfig:
    title: str
    metrics: list[str]
    metric_labels: list[str]
    y_label: str
    y_axis_format: str

@dataclass
class RuleConfig:
    head: str
    subhead: str
    charts: list[RuleChartConfig] = field(default_factory=list)
