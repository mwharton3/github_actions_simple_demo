# CSV Inspector — GitHub Actions Demo

A minimal Python project that demonstrates how to set up GitHub Actions CI
with linting, formatting, and automated tests.

The tool itself accepts an arbitrary CSV, analyzes column quality and likely
data types, and proposes a Pydantic schema based on typecasting attempts.

## Quick Start

### 1. Clone and install

```bash
git clone <your-repo-url>
cd github_actions_simple_demo

# Install uv if you don't have it
curl -LsSf https://astral.sh/uv/install.sh | sh

# Install project + dev dependencies
uv sync --all-extras
```

### 2. Run the tests locally

```bash
uv run pytest -v
```

### 3. Run the linter and formatter

```bash
uv run ruff check src/ tests/
uv run black --check src/ tests/
```

### 4. Set up pre-commit hooks

```bash
uv run pre-commit install
```

Now `black` will auto-format your code on every commit.

### 5. Try the tool

```python
import pandas as pd
from csv_inspector import analyze_dataframe, propose_schema

df = pd.read_csv("your_data.csv")
reports = analyze_dataframe(df)
schema = propose_schema(reports)

# See the proposed schema
for col in schema.columns:
    print(f"{col.name}: {col.python_type} (nullable={col.nullable})")

# Get generated Pydantic model code
print(schema.pydantic_code)
```

## Setting Up GitHub Actions (UI Guide)

If you're starting from scratch on GitHub, here's how to enable CI:

### Step 1: Push your code

Make sure the `.github/workflows/ci.yml` file is committed and pushed to the
`main` branch.

### Step 2: Verify the Actions tab

1. Go to your repository on GitHub.
2. Click the **Actions** tab at the top.
3. You should see the **CI** workflow listed.

If Actions is disabled:
- Go to **Settings → Actions → General**
- Select **Allow all actions and reusable workflows**
- Click **Save**

### Step 3: Require status checks (recommended)

To prevent merges when tests fail:

1. Go to **Settings → Branches**
2. Click **Add branch protection rule**
3. Set **Branch name pattern** to `main`
4. Check **Require status checks to pass before merging**
5. Search for and select the **lint-and-test** job
6. Click **Create** (or **Save changes**)

Now every PR targeting `main` must pass CI before it can be merged.

### Step 4: Make a PR and watch it run

1. Create a feature branch: `git checkout -b my-feature`
2. Make a change, commit, and push
3. Open a Pull Request on GitHub
4. Watch the **Actions** tab — CI will run automatically
5. Green ✓ means you're good to merge!

## Project Structure

```
├── .github/workflows/ci.yml   # GitHub Actions CI workflow
├── .pre-commit-config.yaml     # Pre-commit hooks (black)
├── pyproject.toml              # Project config (deps, tools)
├── src/csv_inspector/
│   ├── __init__.py             # Package exports
│   ├── analyzer.py             # Column quality analysis & type detection
│   └── schema.py               # Pydantic schema proposal & code generation
├── tests/
│   ├── test_analyzer.py        # Analyzer unit tests (incl. tolerance tests)
│   └── test_schema.py          # Schema generation tests
└── docs/
    ├── github_actions.md       # Deep dive on the CI workflow
    ├── pre_commit.md           # Pre-commit hook setup & usage
    └── testing_strategy.md     # Test organisation & what we cover
```

## Learn More

- [docs/github_actions.md](docs/github_actions.md) — How the CI workflow works
- [docs/pre_commit.md](docs/pre_commit.md) — Pre-commit hooks explained
- [docs/testing_strategy.md](docs/testing_strategy.md) — Testing strategy and the tolerance test
