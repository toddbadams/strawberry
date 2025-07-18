import json
import logging
import os
from pathlib import Path
import csv

from . import dtos as dto


class ConfigLoader:

    def __init__(self, logger: logging.Logger):
        self.logger = logger
        self.env = dto.Environment(
            alpha_vantage_api_key = self._get_env_var('ALPHA_VANTAGE_API_KEY'),
            alpha_vantage_url       = self._get_env_var('ALPHA_VANTAGE_URL'),
            acquisition_path        = self._get_env_var('ACQUISITION_PATH'),
            output_path             = Path(self._get_env_var('OUTPUT_PATH')),
            config_path             = Path(self._get_env_var('CONFIG_PATH')),
            openapi_api_key         = self._get_env_var('OPENAPI_API_KEY'),
            env                     = self._get_env_var('ENV')
        )

    def load_rules(self) -> list[dto.RuleConfig]:
        p = os.path.join(self.env.config_path, "rules.json")
        with open(p, "r", encoding="utf-8") as f:
            data = json.load(f)

        rules = []

        for item in data:
            charts = []
            rule_card = dto.RuleConfig(
                head=item["head"],
                subhead=item["subhead"],
                charts=charts
            )
            rules.append(rule_card)

        return rules
           
    def load_acquisition_config(self) -> list[dto.AcquisitionTableConfig]:
        p = os.path.join(self.env.config_path, "acquisition.json")
        with open(p, "r", encoding="utf-8") as f:
            data = json.load(f)

        tables = []

        for item in data:
            tables.append(dto.AcquisitionTableConfig(name=item["name"], attribute=item["attribute"]))

        return tables
    
    def load_table_consolidation_config(self) -> list[dto.ConsolidationTableConfig]:
        p = os.path.join(self.env.config_path, "consolidation.json")
        with open(p, "r", encoding="utf-8") as f:
            data = json.load(f)

        tables = []

        for item in data:
            tables.append(dto.ConsolidationTableConfig(name=item["name"], 
                                                   columns=[dto.ColumnConfig(**column) for column in item["columns"]]))

        return tables

    def load_tickers(self) -> list[str]:
        tickers: list[str] = []
        path = os.path.join(self.env.config_path, "tickers.csv")
        
        with open(path, newline="") as csvfile:
            reader = csv.reader(csvfile)
            for row in reader:
                if row:  # skip empty rows
                    tickers.append(row[0])
        
        self.logger.info(f"Loaded {len(tickers)} tickers from {path}")
        return tickers
    
    def load_dividend_params(self) -> list[dto.DividendScoreParameter]:
        p = os.path.join(self.env.config_path, "dividend_score.json")
        with open(p, "r", encoding="utf-8") as f:
            data = json.load(f)

        params = []

        for item in data:
            chart = dto.ChartConfig(title=item["chart"]["title"],
                                metrics=item["chart"]["metrics"],
                                metric_labels=item["chart"]["metric_labels"],
                                y_label=item["chart"]["y_label"],
                                y_axis_format=item["chart"]["y_axis_format"],
                                y_axis_min=item["chart"]["y_axis_min"],
                                y_axis_max=item["chart"]["y_axis_max"],
                                x_axis_range=item["chart"]["x_axis_range"])
            params.append(dto.DividendScoreParameter(name=item["name"],
                                                 description=item["description"],
                                                 raw_column_name=item["raw_column_name"],
                                                 raw_value=0,
                                                 score_column_name=item["score_column_name"],
                                                 score_value=0,
                                                 weight=item["weight"],
                                                 chart=chart))

        return params

    def load_dividend_score_rules(self) -> list[dto.RuleConfig]:
        p = os.path.join(self.env.config_path, "dividend_score_rules.json")
        with open(p, "r", encoding="utf-8") as f:
            data = json.load(f)

        rules = []

        for item in data:
            charts = []
            rule_card = dto.RuleConfig(
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
            
    def environment(self) -> dto.Environment:
        return self.env
