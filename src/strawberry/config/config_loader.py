import json
import logging
import os
from pathlib import Path
import csv

from . import dtos as dto
from strawberry.logging.logger_factory import LoggerFactory


class ConfigLoader:

    def __init__(self):
        self.logger = LoggerFactory().create_logger(__name__)
        self.env = dto.Environment.load()
        # cache to avoid reloading
        self._acquisition_config = None

    def acquisition(self) -> dto.AcquisitionConfig:
        p = os.path.join(self.env.config_path, "acquisition.json")
        if self._acquisition_config is not None:
            return self._acquisition_config
        self._acquisition_config = dto.AcquisitionConfig.load_from_file(p)
        self.logger.info(
            f"Loaded {len(self._acquisition_config.tables)} acquisition table configs from {p}"
        )
        return self._acquisition_config

    def fact_qtr_financials(self) -> list[dto.ValTableConfig]:
        path = os.path.join(self.env.config_path, "fact_qtr_financials.json")
        tables = dto.ValTableConfig.load_from_file(path)
        self.logger.info(f"Loaded -Fact Qtrly Financials- table configs from {path}")
        return tables

    def dim_stock(self) -> dto.ValTableConfig:
        path = os.path.join(self.env.config_path, "dim_stocks.json")
        table = dto.ValTableConfig.load_from_file(path)[0]
        self.logger.info(f"Loaded -Dim Stocks- table configs from {path}")
        return table

    def fact_qtr_income(self) -> dto.FactTableConfig:
        path = os.path.join(self.env.config_path, "fact_qtr_income_statement.json")
        table = dto.FactTableConfig.load_from_file(path)
        self.logger.info(f"Loaded -FACT Qrt Income Statement- config from {path}")
        return table

    def fact_qtr_balance(self) -> dto.FactTableConfig:
        path = os.path.join(self.env.config_path, "fact_qtr_balance_sheet.json")
        table = dto.FactTableConfig.load_from_file(path)
        self.logger.info(f"Loaded -FACT Qrt Balance Statment- config from {path}")
        return table

    def tickers(self) -> list[str]:
        tickers: list[str] = []
        path = os.path.join(self.env.config_path, "tickers.csv")

        with open(path, newline="") as csvfile:
            reader = csv.reader(csvfile)
            for row in reader:
                if row:  # skip empty rows
                    tickers.append(row[0])

        self.logger.info(f"Loaded {len(tickers)} tickers from {path}")
        return sorted(tickers)

    def load_dividend_params(self) -> list[dto.DividendScoreParameter]:
        path = os.path.join(self.env.config_path, "dividend_score.json")
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)

        params = []

        for item in data:
            chart = dto.ChartConfig(
                title=item["chart"]["title"],
                metrics=item["chart"]["metrics"],
                metric_labels=item["chart"]["metric_labels"],
                y_label=item["chart"]["y_label"],
                y_axis_format=item["chart"]["y_axis_format"],
                y_axis_min=item["chart"]["y_axis_min"],
                y_axis_max=item["chart"]["y_axis_max"],
                x_axis_range=item["chart"]["x_axis_range"],
            )
            params.append(
                dto.DividendScoreParameter(
                    name=item["name"],
                    description=item["description"],
                    raw_column_name=item["raw_column_name"],
                    raw_value=0,
                    score_column_name=item["score_column_name"],
                    score_value=0,
                    weight=item["weight"],
                    chart=chart,
                )
            )

        self.logger.info(f"Loaded {len(params)} dividend parameters from {path}")
        return params

    def load_dividend_score_rules(self) -> list[dto.RuleConfig]:
        path = os.path.join(self.env.config_path, "dividend_score_rules.json")
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)

        rules = []

        for item in data:
            charts = []
            rule_card = dto.RuleConfig(
                head=item["head"], subhead=item["subhead"], charts=charts
            )
            rules.append(rule_card)

        self.logger.info(f"Loaded {len(rules)} rules from {path}")
        return rules

    def environment(self) -> dto.Environment:
        return self.env
