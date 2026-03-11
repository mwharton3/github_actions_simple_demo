"""
Schema proposal engine for CSV DataFrames.

Given analysis results from the analyzer module, this module generates
a Pydantic model class (as source code) that represents the proposed
typed schema for each row of the CSV.
"""

from __future__ import annotations

from pydantic import BaseModel, Field

from csv_inspector.analyzer import ColumnReport

# ---------------------------------------------------------------------------
# Pydantic models that describe the *proposed* schema
# ---------------------------------------------------------------------------


class ColumnSchema(BaseModel):
    """
    Schema proposal for a single column.

    Attributes:
        name: Column name.
        python_type: The Python type string (e.g. ``int``, ``Optional[float]``).
        nullable: Whether the column contains any nulls.
        detected_type: Raw detected type from the analyzer.
        cast_error: Maximum absolute error from numeric casting.
    """

    name: str
    python_type: str
    nullable: bool
    detected_type: str
    cast_error: float = Field(default=0.0, description="Max absolute cast error for numeric cols")


class DataFrameSchema(BaseModel):
    """
    Full schema proposal for a DataFrame.

    Attributes:
        columns: Ordered list of column schemas.
        pydantic_code: Generated Pydantic model source code.
    """

    columns: list[ColumnSchema]
    pydantic_code: str


# ---------------------------------------------------------------------------
# Type-mapping helpers
# ---------------------------------------------------------------------------

_TYPE_MAP: dict[str, str] = {
    "int": "int",
    "float": "float",
    "bool": "bool",
    "datetime": "datetime",
    "str": "str",
}


def _python_type(detected: str, nullable: bool) -> str:
    """
    Map a detected type name to a Python type annotation string.

    Wraps in ``Optional[...]`` when the column contains nulls.
    """
    base = _TYPE_MAP.get(detected, "str")
    if nullable:
        return f"Optional[{base}]"
    return base


# ---------------------------------------------------------------------------
# Code generation
# ---------------------------------------------------------------------------


def _generate_pydantic_code(columns: list[ColumnSchema]) -> str:
    """
    Generate Pydantic model source code from a list of ColumnSchema objects.

    The resulting code defines a ``RowModel`` class that can validate one row
    of the original CSV.
    """
    lines: list[str] = [
        "from __future__ import annotations",
        "",
        "from datetime import datetime",
        "from typing import Optional",
        "",
        "from pydantic import BaseModel",
        "",
        "",
        "class RowModel(BaseModel):",
        '    """Auto-generated Pydantic model for one CSV row."""',
        "",
    ]
    for col in columns:
        field_name = col.name.replace(" ", "_").replace("-", "_")
        lines.append(f"    {field_name}: {col.python_type}")
    return "\n".join(lines) + "\n"


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def propose_schema(reports: list[ColumnReport]) -> DataFrameSchema:
    """
    Propose a typed schema from analyzer reports.

    Args:
        reports: List of ColumnReport objects (one per column).

    Returns:
        A DataFrameSchema containing per-column schemas and generated code.
    """
    columns: list[ColumnSchema] = []
    for r in reports:
        nullable = r.null_count > 0
        columns.append(
            ColumnSchema(
                name=r.name,
                python_type=_python_type(r.detected_type, nullable),
                nullable=nullable,
                detected_type=r.detected_type,
                cast_error=r.cast_error,
            )
        )
    code = _generate_pydantic_code(columns)
    return DataFrameSchema(columns=columns, pydantic_code=code)
