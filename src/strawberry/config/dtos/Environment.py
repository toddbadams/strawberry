from dataclasses import dataclass
from pathlib import Path


@dataclass
class Environment:
    alpha_vantage_api_key: str
    alpha_vantage_url: str
    openapi_api_key: str
    env: str
    data_root: Path
    acquisition_folder: Path
    validated_folder: Path
    transformed_folder: Path
    scored_folder: Path
    signals_folder: Path
    prediction_folder: Path
    evaluation_folder: Path
    config_path: Path