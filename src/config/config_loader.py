import json
import logging
import os
from dataclasses import dataclass, field
from typing import Optional
from pathlib import Path
import csv

@dataclass
class AcquisitionTableConfig:
    name: str
    attribute: str

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

@dataclass
class DividendScoreParameter:
    name: str
    description: str
    raw_column_name: str
    raw_value: float
    score_column_name: str
    score_value: float
    weight: int

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
           
    def load_acquisition_config(self) -> list[AcquisitionTableConfig]:
        p = os.path.join(self.env.config_path, "acquisition.json")
        with open(p, "r", encoding="utf-8") as f:
            data = json.load(f)

        tables = []

        for item in data:
            tables.append(AcquisitionTableConfig(name=item["name"], attribute=item["attribute"]))

        return tables
    
    def load_table_consolidation_config(self) -> list[ConsolidationTableConfig]:
        p = os.path.join(self.env.config_path, "consolidation.json")
        with open(p, "r", encoding="utf-8") as f:
            data = json.load(f)

        tables = []

        for item in data:
            tables.append(ConsolidationTableConfig(name=item["name"], 
                                                   columns=[ColumnConfig(**column) for column in item["columns"]]))

        return tables

    def load_tickers(self) -> list[str]:
        tickers: list[str] = []
        path = os.path.join(self.env.config_path, "tickers.csv")
        
        self.logger.info(f"Loading tickers from {path}.")
        with open(path, newline="") as csvfile:
            reader = csv.reader(csvfile)
            for row in reader:
                if row:  # skip empty rows
                    tickers.append(row[0])
        
        self.logger.info(f"Loaded {len(tickers)} tickers from {path}")
        return tickers
    
    def load_dividend_params(self) -> list[DividendScoreParameter]:
        p = os.path.join(self.env.config_path, "dividend_score.json")
        with open(p, "r", encoding="utf-8") as f:
            data = json.load(f)

        params = []

        for item in data:
            params.append(DividendScoreParameter(name=item["name"],
                                                 description=item["description"],
                                                 raw_column_name=item["raw_column_name"],
                                                 raw_value=0,
                                                 score_column_name=item["score_column_name"],
                                                 score_value=0,
                                                 weight=item["weight"]))

        return params

    def load_dividend_score_rules(self) -> list[RuleConfig]:
        p = os.path.join(self.env.config_path, "dividend_score_rules.json")
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
    # Helper to fetch required vars and raise if missing
    def _get_env_var(self, name: str) -> str:
        value = os.getenv(name)
        if value is None:
            raise KeyError(f"Required environment variable '{name}' not set")
        return value
            
    def environment(self) -> Environment:
        return self.env
