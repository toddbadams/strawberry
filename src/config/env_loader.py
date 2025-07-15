from dataclasses import dataclass
from pathlib import Path
from dotenv import load_dotenv
import os

@dataclass
class Environment:
    alpha_vantage_api_key: str
    alpha_vantage_url: str
    output_path: Path
    config_path: Path
    openapi_api_key: str
    env: str

class EnvLoader:
    def __init__(self, env_file: str = '.env'):
        # Load variables from .env into environment
        load_dotenv(env_file)

    def load(self) -> Environment:
        # Helper to fetch required vars and raise if missing
        def get_var(name: str) -> str:
            value = os.getenv(name)
            if value is None:
                raise KeyError(f"Required environment variable '{name}' not set")
            return value

        return Environment(
            alpha_vantage_api_key = get_var('ALPHA_VANTAGE_API_KEY'),
            alpha_vantage_url       = get_var('ALPHA_VANTAGE_URL'),
            output_path             = Path(os.getenv('OUTPUT_PATH', 'data/')),
            config_path             = Path(os.getenv('CONFIG_PATH', 'config/')),
            openapi_api_key         = get_var('OPENAPI_API_KEY'),
            env                     = os.getenv('ENV', 'DEV')
        )


