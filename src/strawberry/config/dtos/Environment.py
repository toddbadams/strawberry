# Environment.py
from dataclasses import dataclass, field, fields
from pathlib import Path
import os
from typing import Any, Callable, Mapping

def _cast_value(value: str, target_type: Any):
    if target_type is Path:
        return Path(value)
    return target_type(value)

@dataclass(frozen=True)
class Environment:
    alpha_vantage_api_key: str = field(metadata={"env": "ALPHA_VANTAGE_API_KEY"})
    alpha_vantage_url: str     = field(metadata={"env": "ALPHA_VANTAGE_URL"})
    openapi_api_key: str       = field(metadata={"env": "OPENAPI_API_KEY"})
    env: str                   = field(metadata={"env": "ENV"})
    data_root: Path            = field(metadata={"env": "DATA_ROOT"})
    acquisition_folder: Path   = field(metadata={"env": "ACQUISITION_FOLDER"})
    validated_folder: Path     = field(metadata={"env": "VALIDATED_FOLDER"})
    dim_stocks_folder: Path    = field(metadata={"env": "DIM_STOCKS_FOLDER"})        
    signals_folder: Path       = field(metadata={"env": "SIGNALS_FOLDER"})
    prediction_folder: Path    = field(metadata={"env": "PREDICTION_FOLDER"})
    evaluation_folder: Path    = field(metadata={"env": "EVALUATION_FOLDER"})
    config_path: Path          = field(metadata={"env": "CONFIG_FOLDER"})

    @classmethod
    def load(cls, source: Mapping[str, str] | None = None,
        missing_handler: Callable[[str], None] | None = None) -> "Environment":
        """Create Environment from env vars (or any mapping)."""
        src = source or os.environ

        kwargs: dict[str, Any] = {}
        for f in fields(cls):
            key = f.metadata.get("env", f.name.upper())
            raw = src.get(key)
            if raw is None:
                if missing_handler:
                    missing_handler(key)
                else:
                    raise KeyError(f"Required environment variable '{key}' not set")
            else:
                kwargs[f.name] = _cast_value(raw, f.type)

        return cls(**kwargs)
