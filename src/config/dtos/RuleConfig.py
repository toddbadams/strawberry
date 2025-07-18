from .ChartConfig import ChartConfig


from dataclasses import dataclass, field


@dataclass
class RuleConfig:
    head: str
    subhead: str
    charts: list[ChartConfig] = field(default_factory=list)