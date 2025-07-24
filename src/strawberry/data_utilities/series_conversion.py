import re
import pandas as pd
import logging
from typing import Sequence, Optional

from strawberry.config.dtos.AcquisitionTableConfig import ColumnConfig


class SeriesConversion:
    """Utilities to coerce pandas Series to datetime/float/integer with consistent cleaning rules."""

    NONE_TOKENS: Sequence[str] = ("None", "none", "NULL", "", "-")
    DATE_RE = re.compile(
        r"((?:00|19|20)\d{2}-\d{2}-\d{2})"
    )  # first ISO-like date in string

    def __init__(self):
        # set up logger and type-to-function mapping
        self.logger = logging.getLogger(__name__)
        self._validators = {
            "date": self._validate_date,
            "float": self._validate_float,
            "integer": self._validate_integer,
        }

    def _validate_date(self, series: pd.Series, col: ColumnConfig) -> pd.Series:
        return self.to_datetime(
            series,
            fmt=col.format,
            nullable=col.nullable,
            null_action=col.null_action,
        )

    def _validate_float(self, series: pd.Series, col: ColumnConfig) -> pd.Series:
        return self.to_float(series)

    def _validate_integer(self, series: pd.Series, col: ColumnConfig) -> pd.Series:
        return self.to_integer(series)

    def validate_column(
        self,
        log_prefix: str,
        series: pd.Series,
        col: ColumnConfig,
    ) -> pd.Series:
        """
        Dispatch conversion based on column configuration type, with logging on errors.
        """
        try:
            validator = self._validators.get(col.type, lambda s, c: s)
            return validator(series, col)
        except (TypeError, ValueError) as e:
            self.logger.warning(f"{log_prefix} {col.name} | {col.type} | {e}")
            raise

    def to_datetime(
        self,
        series: pd.Series,
        fmt: Optional[str] = "%Y-%m-%d",
        *,
        nullable: bool = True,
        null_action: Optional[str] = None,
    ) -> pd.Series:
        """
        Convert a Series to datetime.
        - Strips tags/extra whitespace.
        - Extracts the first ISO date substring.
        - Fixes years starting '00' -> 2000s.
        - Respects NONE_TOKENS as nulls.
        - If nullable is False and no null_action provided, forward-fills rows that were NONE_TOKENS.
        """
        # Normalize to string, drop HTML-ish tags, collapse whitespace
        clean = (
            series.astype(str)
            .str.replace(r"<[^>]*>", "", regex=True)
            .str.replace(r"\s+", " ", regex=True)
            .str.strip()
        )

        # Extract first date-like token
        clean = clean.str.extract(self.DATE_RE, expand=False)

        # Fix '00YY' -> '20YY'
        clean = clean.str.replace(r"^00(\d{2})", r"20\1", regex=True)

        mask_none = clean.astype(str).str.strip().isin(self.NONE_TOKENS)

        if not nullable and not null_action:
            # mark NONE_TOKENS as NA
            clean = clean.where(~mask_none, pd.NA)
            dt = pd.to_datetime(clean, format=fmt, errors="coerce")
            # forward-fill only those rows that were NONE_TOKENS
            return dt.where(~mask_none, dt.ffill())

        # default path (nullable or has explicit null_action you’ll handle elsewhere)
        clean[mask_none] = pd.NA
        return pd.to_datetime(clean, format=fmt, errors="coerce")

    def to_float(self, series: pd.Series) -> pd.Series:
        """
        Convert Series to float64, honoring NONE_TOKENS as nulls.
        """
        clean = series.copy()
        mask = clean.astype(str).str.strip().isin(self.NONE_TOKENS)
        clean[mask] = pd.NA
        clean = pd.to_numeric(clean, errors="coerce")
        return clean.astype("float64", copy=False)

    def to_integer(self, series: pd.Series) -> pd.Series:
        """
        Convert Series to nullable pandas Int64, honoring NONE_TOKENS as nulls.
        """
        clean = series.copy()
        mask = clean.astype(str).str.strip().isin(self.NONE_TOKENS)
        clean[mask] = pd.NA
        clean = pd.to_numeric(clean, errors="coerce", downcast="integer")
        return clean.astype("Int64", copy=False)
