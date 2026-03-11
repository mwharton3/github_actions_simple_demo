"""
Tests for csv_inspector.schema.

Covers schema proposal generation, Pydantic model code output, nullable
handling, and round-trip validation of generated code.
"""

import pandas as pd

from csv_inspector.analyzer import ColumnReport, analyze_dataframe
from csv_inspector.schema import DataFrameSchema, propose_schema

# ---------------------------------------------------------------------------
# Schema proposal from reports
# ---------------------------------------------------------------------------


class TestProposeSchema:
    """Tests for the propose_schema function."""

    def test_basic_schema(self):
        """A simple DataFrame should produce a valid DataFrameSchema."""
        reports = [
            ColumnReport(
                name="id",
                total_rows=3,
                null_count=0,
                null_rate=0.0,
                unique_count=3,
                detected_type="int",
                cast_success=True,
            ),
            ColumnReport(
                name="name",
                total_rows=3,
                null_count=0,
                null_rate=0.0,
                unique_count=3,
                detected_type="str",
                cast_success=True,
            ),
        ]
        schema = propose_schema(reports)
        assert isinstance(schema, DataFrameSchema)
        assert len(schema.columns) == 2

    def test_nullable_wrapping(self):
        """Columns with nulls should have Optional[...] types."""
        reports = [
            ColumnReport(
                name="score",
                total_rows=5,
                null_count=2,
                null_rate=0.4,
                unique_count=3,
                detected_type="float",
                cast_success=True,
            ),
        ]
        schema = propose_schema(reports)
        assert schema.columns[0].python_type == "Optional[float]"
        assert schema.columns[0].nullable is True

    def test_non_nullable(self):
        """Columns without nulls should not be wrapped in Optional."""
        reports = [
            ColumnReport(
                name="flag",
                total_rows=4,
                null_count=0,
                null_rate=0.0,
                unique_count=2,
                detected_type="bool",
                cast_success=True,
            ),
        ]
        schema = propose_schema(reports)
        assert schema.columns[0].python_type == "bool"
        assert schema.columns[0].nullable is False


# ---------------------------------------------------------------------------
# Generated Pydantic code
# ---------------------------------------------------------------------------


class TestGeneratedCode:
    """Tests for the Pydantic model code generation."""

    def test_code_contains_class(self):
        """Generated code should define a RowModel class."""
        reports = [
            ColumnReport(
                name="x",
                total_rows=1,
                null_count=0,
                null_rate=0.0,
                unique_count=1,
                detected_type="int",
                cast_success=True,
            ),
        ]
        schema = propose_schema(reports)
        assert "class RowModel(BaseModel):" in schema.pydantic_code

    def test_code_contains_field(self):
        """Generated code should include the column as a typed field."""
        reports = [
            ColumnReport(
                name="age",
                total_rows=10,
                null_count=0,
                null_rate=0.0,
                unique_count=5,
                detected_type="int",
                cast_success=True,
            ),
        ]
        schema = propose_schema(reports)
        assert "age: int" in schema.pydantic_code

    def test_code_is_valid_python(self):
        """Generated code should compile without syntax errors."""
        reports = [
            ColumnReport(
                name="val",
                total_rows=2,
                null_count=1,
                null_rate=0.5,
                unique_count=1,
                detected_type="float",
                cast_success=True,
            ),
        ]
        schema = propose_schema(reports)
        compile(schema.pydantic_code, "<string>", "exec")

    def test_column_name_sanitisation(self):
        """Spaces and hyphens in column names should become underscores."""
        reports = [
            ColumnReport(
                name="my column-name",
                total_rows=1,
                null_count=0,
                null_rate=0.0,
                unique_count=1,
                detected_type="str",
                cast_success=True,
            ),
        ]
        schema = propose_schema(reports)
        assert "my_column_name: str" in schema.pydantic_code


# ---------------------------------------------------------------------------
# Integration: DataFrame -> reports -> schema
# ---------------------------------------------------------------------------


class TestEndToEnd:
    """Integration tests going from raw DataFrame to schema proposal."""

    def test_csv_round_trip(self, tmp_path):
        """Write a CSV, read it back, analyze, and propose a schema."""
        csv_path = tmp_path / "test.csv"
        csv_path.write_text("id,name,score\n1,Alice,95.5\n2,Bob,87.3\n3,Carol,\n")
        df = pd.read_csv(csv_path)
        reports = analyze_dataframe(df)
        schema = propose_schema(reports)
        assert len(schema.columns) == 3
        # score has a null → should be Optional
        score_col = next(c for c in schema.columns if c.name == "score")
        assert score_col.nullable is True
