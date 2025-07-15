import json
import logging
import os
from dataclasses import dataclass, field
from typing import Optional

from src.config.table_config import ColumnConfig, TableConfig

@dataclass
class RuleChartConfig:
    title: str
    metrics: list[str]
    metric_labels: list[str]
    y_label: str
    y_axis_format: str
    buy: Optional[float] = None
    sell: Optional[float] = None

@dataclass
class RuleConfig:
    head: str
    subhead: str
    charts: list[RuleChartConfig] = field(default_factory=list)

class RuleConfigLoader:

    def __init__(self, config_path: str, 
                 logger: logging.Logger):
        self.logger = logger
        self.config_path = config_path

    def load_rules(self) -> list[RuleConfig]:
        p = os.path.join(self.config_path, "rules.json")
        with open(p, "r", encoding="utf-8") as f:
            data = json.load(f)

        rules = []

        for item in data:
            charts = [RuleChartConfig(**chart) for chart in item["charts"]]
            rule_card = RuleConfig(
                head=item["head"],
                subhead=item["subhead"],
                charts=charts
            )
            rules.append(rule_card)

        return rules
    
    def load_table_consolidation_config(self) -> list[TableConfig]:
        p = os.path.join(self.config_path, "consolidation.json")
        with open(p, "r", encoding="utf-8") as f:
            data = json.load(f)

        tables = []

        for item in data:
            c = [ColumnConfig(**column) for column in item["columns"]]
            t = TableConfig(
                name=item["name"],
                columns=c
            )
            tables.append(c)

        return tables