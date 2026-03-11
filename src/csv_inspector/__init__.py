"""
csv_inspector - A tool for analyzing CSV DataFrames.

This package provides utilities to assess column quality, detect likely
data types, and propose Pydantic-based schemas from raw CSV data.
"""

from csv_inspector.analyzer import analyze_dataframe
from csv_inspector.schema import propose_schema

__all__ = ["analyze_dataframe", "propose_schema"]
