import logging
import sys
from typing import Optional

def _in_prefect_run() -> bool:
    try:
        from prefect.context import get_run_context  # Prefect 3
        get_run_context()
        return True
    except Exception:
        return False

class _NameAdapter(logging.LoggerAdapter):
    """Prefixes messages with the module/name you requested."""
    def __init__(self, logger: logging.Logger, name: str):
        super().__init__(logger, {})
        self._name = name

    def process(self, msg, kwargs):
        return f"{self._name} | {msg}", kwargs

class LoggerFactory:
    def __init__(self, e: str = 'DEV', default_level: int = logging.INFO):
        self.default_level = default_level
        self.env = e

    def create_logger(self, name: str, level: Optional[int] = None) -> logging.Logger:
        lvl = level or self.default_level

        if _in_prefect_run():
            # Use Prefect's logger
            from prefect.logging import get_run_logger
            run_logger = get_run_logger()          # already configured
            run_logger.setLevel(lvl)
            return _NameAdapter(run_logger, name)  # keep your module name in messages

        # Fallback: plain console logger
        logger = logging.getLogger(name)
        logger.setLevel(lvl)

        # Avoid duplicate handlers
        if not any(isinstance(h, logging.StreamHandler) for h in logger.handlers):
            console = logging.StreamHandler(sys.stdout)
            console.setLevel(lvl)
            fmt = "%(asctime)s | %(levelname)-5s | %(name)s | %(message)s"
            console.setFormatter(logging.Formatter(fmt))
            logger.addHandler(console)

        return logger
