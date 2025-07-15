import os
import csv
import logging
from typing import List

class TickerLoader:

    def __init__(self, data_path: str, logger: logging.Logger):
        self.data_path = data_path
        self.logger = logger

    def run(self) -> List[str]:
        tickers: List[str] = []
        path = os.path.join(self.data_path, "tickers.csv")
        
        self.logger.info(f"Loading tickers from {path}.")
        with open(path, newline="") as csvfile:
            reader = csv.reader(csvfile)
            for row in reader:
                if row:  # skip empty rows
                    tickers.append(row[0])
        
        self.logger.info(f"Loaded {len(tickers)} tickers from {path}")
        return tickers
