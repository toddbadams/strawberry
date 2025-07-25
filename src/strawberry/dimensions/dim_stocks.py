import pandas as pd

from strawberry.config.config_loader import ConfigLoader
from strawberry.data_utilities.series_conversion import SeriesConversion
from strawberry.repository.storage import ParquetStorage
from strawberry.logging.logger_factory import LoggerFactory


class DimStocks:

    TABLE_NAME = "DIM_STOCKS"

    def __init__(self):
        self.logger = LoggerFactory().create_logger(__name__)
        self.config = ConfigLoader()
        self.env = self.config.environment()
        self.cfg = self.config.dim_stock()
        self.series = SeriesConversion()

        self.dim_store = ParquetStorage(self.env.dim_stocks_folder)
        self.val_store = ParquetStorage(self.env.validated_folder)

        # get a set of tickers from the validation folder
        self.tickers = self.val_store.get_tickers(self.cfg.name)
        self.tickers = sorted(self.tickers)

        self.clean = SeriesConversion()

    def tickers_dimensioned(self) -> list[str]:
        return self.dim_store.unique_column_list(self.TABLE_NAME, "symbol")

    def tickers_not_dimensioned(self, tickers: list[str]) -> list[str]:
        """
        Return a list of tickers from the input tickers that have not yet been dimensioned.
        """
        # Get already dimensioned tickers from the dimension store
        dimensioned_tickers = self.dim_store.unique_column_list(
            self.TABLE_NAME, "symbol"
        )
        # Filter and return tickers not present in the dimensioned list
        return [ticker for ticker in tickers if ticker not in dimensioned_tickers]

    def dimension_ticker(self):
        log_prefix = f" {self.cfg.name} | "

        # read the table from the validation folder
        df = self.val_store.read_df(self.cfg.name)

        # get required columns
        df = df[self.cfg.in_names()]

        # rename columns
        df.rename(columns=self.cfg.in_to_out_map(), inplace=True)

        self.dim_store.update(self.TABLE_NAME, "symbol", df)
        self.logger.info(f"{log_prefix} | consolidated and saved to transformed folder")

    def main(self):
        self.dimension_ticker()


if __name__ == "__main__":
    t = DimStocks()
    t.main()
