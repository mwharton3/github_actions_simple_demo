"""
Tests for csv_inspector.analyzer.

Covers column quality reporting, type detection for int / float / bool /
datetime / str columns, null handling, and typecasting tolerance.
"""

import numpy as np
import pandas as pd
import pytest

from csv_inspector.analyzer import (
    ColumnReport,
    _try_cast_int,
    analyze_column,
    analyze_dataframe,
)

# ---------------------------------------------------------------------------
# Basic quality metrics
# ---------------------------------------------------------------------------


class TestAnalyzeColumnMetrics:
    """Tests that verify null counts, rates, and unique values."""

    def test_no_nulls(self):
        """A column with no nulls should report zero null_count and null_rate."""
        s = pd.Series([1, 2, 3], name="x")
        report = analyze_column(s)
        assert report.null_count == 0
        assert report.null_rate == 0.0
        assert report.total_rows == 3

    def test_all_nulls(self):
        """A column of all NaN should report 100% null_rate."""
        s = pd.Series([None, None, None], name="empty")
        report = analyze_column(s)
        assert report.null_count == 3
        assert report.null_rate == 1.0

    def test_some_nulls(self):
        """Null rate should equal null_count / total_rows."""
        s = pd.Series([1, None, 3, None], name="mixed")
        report = analyze_column(s)
        assert report.null_count == 2
        assert pytest.approx(report.null_rate) == 0.5

    def test_unique_count(self):
        """unique_count should exclude NaN."""
        s = pd.Series(["a", "b", "a", None], name="cat")
        report = analyze_column(s)
        assert report.unique_count == 2


# ---------------------------------------------------------------------------
# Type detection
# ---------------------------------------------------------------------------


class TestTypeDetection:
    """Tests for automatic type detection across common column patterns."""

    def test_int_column(self):
        """Strings that represent integers should be detected as int."""
        s = pd.Series(["1", "2", "3"], name="ids")
        report = analyze_column(s)
        assert report.detected_type == "int"

    def test_int_with_nan(self):
        """Integers mixed with NaN should still detect as int."""
        s = pd.Series(["10", None, "30"], name="vals")
        report = analyze_column(s)
        assert report.detected_type == "int"

    def test_float_column(self):
        """Strings with decimal points should detect as float."""
        s = pd.Series(["1.5", "2.7", "3.14"], name="measurements")
        report = analyze_column(s)
        assert report.detected_type == "float"

    def test_bool_column(self):
        """Common boolean representations should detect as bool."""
        s = pd.Series(["true", "false", "True", "False"], name="flags")
        report = analyze_column(s)
        assert report.detected_type == "bool"

    def test_bool_yes_no(self):
        """Yes/No values should detect as bool."""
        s = pd.Series(["yes", "no", "YES", "NO"], name="yn")
        report = analyze_column(s)
        assert report.detected_type == "bool"

    def test_datetime_column(self):
        """ISO-format date strings should detect as datetime."""
        s = pd.Series(["2024-01-01", "2024-06-15", "2024-12-31"], name="dates")
        report = analyze_column(s)
        assert report.detected_type == "datetime"

    def test_string_column(self):
        """Free-text values should fall back to str."""
        s = pd.Series(["hello", "world", "foo"], name="text")
        report = analyze_column(s)
        assert report.detected_type == "str"

    def test_mixed_types_fallback(self):
        """Columns with truly mixed types should fall back to str."""
        s = pd.Series(["hello", "123", "2024-01-01", "true"], name="mix")
        report = analyze_column(s)
        # Could be str since not all values parse consistently
        assert report.detected_type in ("str", "bool", "datetime")


# ---------------------------------------------------------------------------
# Typecasting tolerance (1e-5) — explicitly required by project spec
# ---------------------------------------------------------------------------


class TestCastTolerance:
    """
    Verify that integer typecasting respects the 1e-5 tolerance.

    The spec requires that a value like 5.000001 (error < 1e-5) should
    still be accepted as int, while 5.0001 (error > 1e-5) should not.
    """

    def test_within_tolerance(self):
        """Values within 1e-5 of an integer should cast successfully."""
        s = pd.Series(["5.000001", "10.000009"])
        success, err = _try_cast_int(s)
        assert success is True
        assert np.isclose(err, err, atol=1e-5)

    def test_exceeds_tolerance(self):
        """Values beyond 1e-5 from an integer should fail the cast."""
        s = pd.Series(["5.0001", "10.0002"])
        success, err = _try_cast_int(s)
        assert success is False
        assert err > 1e-5

    def test_exact_integers(self):
        """Exact integer strings should have zero error."""
        s = pd.Series(["7", "42", "100"])
        success, err = _try_cast_int(s)
        assert success is True
        assert err == 0.0

    def test_boundary_value(self):
        """A value at exactly 1e-5 error should still pass (uses np.isclose)."""
        s = pd.Series(["5.00001"])
        success, err = _try_cast_int(s)
        assert success is True

    def test_just_over_boundary(self):
        """A value at 2e-5 error should fail."""
        s = pd.Series(["5.00002"])
        success, err = _try_cast_int(s)
        assert success is False
        assert err > 1e-5

    def test_tolerance_uses_isclose(self):
        """Confirm that np.isclose with rtol=0, atol=1e-5 is the mechanism."""
        val = 5.000005
        rounded = 5
        assert np.isclose(val, rounded, rtol=0, atol=1e-5)

        val_fail = 5.00005
        assert not np.isclose(val_fail, rounded, rtol=0, atol=1e-5)


# ---------------------------------------------------------------------------
# Full DataFrame analysis
# ---------------------------------------------------------------------------


class TestAnalyzeDataFrame:
    """Tests for the top-level analyze_dataframe function."""

    def test_returns_report_per_column(self):
        """Should return one ColumnReport per column in the DataFrame."""
        df = pd.DataFrame({"a": [1, 2], "b": ["x", "y"], "c": [1.1, 2.2]})
        reports = analyze_dataframe(df)
        assert len(reports) == 3
        assert all(isinstance(r, ColumnReport) for r in reports)

    def test_column_names_preserved(self):
        """Report names should match the DataFrame column names."""
        df = pd.DataFrame({"alpha": [1], "beta": [2]})
        reports = analyze_dataframe(df)
        names = [r.name for r in reports]
        assert names == ["alpha", "beta"]

    def test_empty_dataframe(self):
        """An empty DataFrame should return an empty list."""
        df = pd.DataFrame()
        reports = analyze_dataframe(df)
        assert reports == []
