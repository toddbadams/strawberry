import logging
import sys

class LoggerFactory:
    def __init__(self, e: str = 'DEV', default_level: int = logging.INFO):
        self.default_level = default_level
        self.env = e

    def create_logger(self, name: str, level: int = None) -> logging.Logger:
        lvl = level or self.default_level

        # 1. Grab (or create) your logger
        logger = logging.getLogger(name)
        logger.setLevel(lvl)

        # 2. Create a console handler that writes to stdout
        console = logging.StreamHandler(sys.stdout)
        console.setLevel(lvl)

        # 3. Define a nice format
        fmt = "%(asctime)s | %(levelname)-5s | %(name)s | %(message)s"
        formatter = logging.Formatter(fmt)
        console.setFormatter(formatter)

        # 4. Attach the handler if it's not already there
        if not any(isinstance(h, logging.StreamHandler) for h in logger.handlers):
            logger.addHandler(console)

        return logger
