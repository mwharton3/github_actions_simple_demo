# Testing Strategy

This document explains how the test suite is organized and what it covers.

## Test Structure

```
tests/
├── __init__.py          # Package docstring
├── test_analyzer.py     # Column analysis & type detection tests
└── test_schema.py       # Schema proposal & code generation tests
```

## What We Test

### Analyzer (`test_analyzer.py`)

| Category | What it verifies |
|----------|-----------------|
| **Quality metrics** | Null counts, null rates, unique counts |
| **Type detection** | int, float, bool, datetime, str detection |
| **Typecasting tolerance** | Integer casting uses `np.isclose(atol=1e-5)` |
| **Edge cases** | All-null columns, empty DataFrames, mixed types |

### Schema (`test_schema.py`)

| Category | What it verifies |
|----------|-----------------|
| **Schema generation** | Correct `ColumnSchema` objects from reports |
| **Nullable handling** | `Optional[...]` wrapping for columns with nulls |
| **Code generation** | Valid Python, correct field names, sanitised names |
| **End-to-end** | CSV → DataFrame → analysis → schema round-trip |

## The Tolerance Test

The project spec requires a tolerance threshold of `1e-5` for integer
typecasting. The `TestCastTolerance` class in `test_analyzer.py` verifies:

- `5.000001` (error ~1e-6) → **passes** as int
- `5.0001`   (error ~1e-4) → **fails** as int
- `5.00001`  (error = 1e-5) → **passes** (boundary)
- `5.00002`  (error = 2e-5) → **fails** (just over boundary)

Under the hood, the tolerance check uses `numpy.isclose(atol=1e-5)`.

## Running Tests

```bash
# Run all tests with verbose output
uv run pytest -v

# Run a specific test class
uv run pytest tests/test_analyzer.py::TestCastTolerance -v

# Run with coverage (if installed)
uv run pytest --cov=csv_inspector
```
