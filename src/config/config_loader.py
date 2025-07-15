import json
import logging
import os
from dataclasses import dataclass, field
from typing import Optional
from pathlib import Path

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

@dataclass
class ColumnConfig:
    in_name: str
    out_name: str
    type: str

@dataclass
class Environment:
    alpha_vantage_api_key: str
    alpha_vantage_url: str
    output_path: Path
    config_path: Path
    openapi_api_key: str
    env: str

@dataclass
class ConsolidationTableConfig:
    name: str
    columns: list[ColumnConfig]

    def in_names(self) -> list[str]:
        return [col.in_name for col in self.columns]

    def in_to_out_map(self) -> dict[str, str]:
         return {col.in_name: col.out_name for col in self.columns}
    
    def date_out_names(self) -> list[str]:
        return [col.out_name for col in self.columns if col.type == "date"]
    
    def number_out_names(self) -> list[str]:
        return [col.out_name for col in self.columns if col.type == "number"]
    
class ConfigLoader:

    def __init__(self, logger: logging.Logger):
        self.logger = logger
        self.env = Environment(
            alpha_vantage_api_key = self._get_env_var('ALPHA_VANTAGE_API_KEY'),
            alpha_vantage_url       = self._get_env_var('ALPHA_VANTAGE_URL'),
            output_path             = Path(self._get_env_var('OUTPUT_PATH')),
            config_path             = Path(self._get_env_var('CONFIG_PATH')),
            openapi_api_key         = self._get_env_var('OPENAPI_API_KEY'),
            env                     = self._get_env_var('ENV')
        )

    def load_rules(self) -> list[RuleConfig]:
        p = os.path.join(self.env.config_path, "rules.json")
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
    
    def load_table_consolidation_config(self) -> list[ConsolidationTableConfig]:
        p = os.path.join(self.env.config_path, "consolidation.json")
        with open(p, "r", encoding="utf-8") as f:
            data = json.load(f)

        tables = []

        for item in data:
            tables.append(ConsolidationTableConfig(name=item["name"], 
                                                   columns=[ColumnConfig(**column) for column in item["columns"]]))

        return tables

    # Helper to fetch required vars and raise if missing
    def _get_env_var(self, name: str) -> str:
        value = os.getenv(name)
        if value is None:
            raise KeyError(f"Required environment variable '{name}' not set")
        return value
            
    def environment(self) -> Environment:
        return self.env
