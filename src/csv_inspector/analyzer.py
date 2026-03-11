"""
Column quality analyzer for CSV DataFrames.

This module inspects each column of a pandas DataFrame and produces a
quality report containing null rates, unique counts, and detected types
based on typecasting attempts.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd


@dataclass
class ColumnReport:
    """
    Quality report for a single DataFrame column.

    Attributes:
        name: Column name.
        total_rows: Number of rows in the column.
        null_count: Number of null / NaN values.
        null_rate: Fraction of values that are null.
        unique_count: Number of distinct non-null values.
        detected_type: The narrowest type the column can be safely cast to.
        cast_success: Whether the column was successfully cast to detected_type.
        cast_error: Maximum absolute error introduced by the cast (for numeric types).
    """

    name: str
    total_rows: int
    null_count: int
    null_rate: float
    unique_count: int
    detected_type: str
    cast_success: bool
    cast_error: float = 0.0


def _try_cast_int(series: pd.Series) -> tuple[bool, float]:
    """
    Attempt to cast a Series to integer dtype.

    Returns a tuple of (success, max_absolute_error).  The cast is
    considered successful only when every non-null value round-trips
    within a tolerance of 1e-5.
    """
    try:
        numeric = pd.to_numeric(series, errors="coerce")
        non_null = numeric.dropna()
        original_non_null = series.dropna()
        # If coercion dropped values (non-numeric strings), reject
        if len(non_null) < len(original_non_null):
            return False, float("inf")
        if non_null.empty:
            return True, 0.0
        as_int = np.round(non_null).astype(np.int64)
        errors = np.abs(non_null.values - as_int.values)
        max_err = float(np.max(errors))
        if np.all(np.isclose(non_null.values, as_int.values, rtol=0, atol=1e-5)):
            return True, max_err
        return False, max_err
    except (ValueError, TypeError, OverflowError):
        return False, float("inf")


def _try_cast_float(series: pd.Series) -> bool:
    """
    Attempt to cast a Series to float dtype.

    Returns True if every non-null value can be interpreted as a float.
    """
    try:
        numeric = pd.to_numeric(series, errors="coerce")
        original_non_null = series.dropna()
        coerced_nulls = numeric.isna().sum() - series.isna().sum()
        return int(coerced_nulls) == 0 and not original_non_null.empty
    except (ValueError, TypeError):
        return False


def _try_cast_bool(series: pd.Series) -> bool:
    """
    Attempt to interpret a Series as boolean.

    Recognises common boolean representations: true/false, yes/no, 1/0, t/f.
    """
    non_null = series.dropna().astype(str).str.strip().str.lower()
    if non_null.empty:
        return False
    bool_values = {"true", "false", "yes", "no", "1", "0", "t", "f"}
    return set(non_null.unique()).issubset(bool_values)


def _try_cast_datetime(series: pd.Series) -> bool:
    """
    Attempt to parse a Series as datetime values.

    Returns True when at least 90% of non-null values parse successfully.
    """
    try:
        non_null = series.dropna()
        if non_null.empty:
            return False
        parsed = pd.to_datetime(non_null, errors="coerce", format="mixed")
        success_rate = parsed.notna().sum() / len(non_null)
        return success_rate >= 0.9
    except Exception:
        return False


def _detect_type(series: pd.Series) -> tuple[str, bool, float]:
    """
    Detect the narrowest safe type for a column.

    Tries, in order: bool -> int -> float -> datetime -> str.
    Returns (type_name, cast_success, cast_error).
    """
    if _try_cast_bool(series):
        return "bool", True, 0.0

    success, err = _try_cast_int(series)
    if success:
        return "int", True, err

    if _try_cast_float(series):
        return "float", True, 0.0

    if _try_cast_datetime(series):
        return "datetime", True, 0.0

    return "str", True, 0.0


def analyze_column(series: pd.Series) -> ColumnReport:
    """
    Produce a quality report for a single pandas Series.

    Args:
        series: The column to analyze.

    Returns:
        A ColumnReport with quality metrics and detected type.
    """
    total = len(series)
    null_count = int(series.isna().sum())
    null_rate = null_count / total if total > 0 else 0.0
    unique_count = int(series.nunique(dropna=True))
    detected_type, cast_success, cast_error = _detect_type(series)

    return ColumnReport(
        name=series.name or "",
        total_rows=total,
        null_count=null_count,
        null_rate=null_rate,
        unique_count=unique_count,
        detected_type=detected_type,
        cast_success=cast_success,
        cast_error=cast_error,
    )


def analyze_dataframe(df: pd.DataFrame) -> list[ColumnReport]:
    """
    Analyze every column in a DataFrame and return quality reports.

    Args:
        df: The DataFrame to inspect.

    Returns:
        A list of ColumnReport objects, one per column.
    """
    return [analyze_column(df[col]) for col in df.columns]
