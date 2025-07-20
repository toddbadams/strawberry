from dataclasses import dataclass
from pathlib import Path


@dataclass
class Environment:
    alpha_vantage_api_key: str
    alpha_vantage_url: str
    acquisition_path: Path
    output_path: Path
    config_path: Path
    openapi_api_key: str
    env: str