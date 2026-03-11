# GitHub Actions — How It Works

This document explains the CI pipeline in this repository step by step.

## What is GitHub Actions?

GitHub Actions is a CI/CD platform built into GitHub. It lets you automate
workflows — like running tests and linters — in response to events such as
pushes and pull requests.

## Key Concepts

| Term | Meaning |
|------|---------|
| **Workflow** | A YAML file in `.github/workflows/` that defines automation |
| **Trigger (`on`)** | The event that starts the workflow (push, PR, schedule, etc.) |
| **Job** | A set of steps that run on the same runner (virtual machine) |
| **Step** | A single command or action within a job |
| **Action** | A reusable unit of code (e.g. `actions/checkout@v4`) |
| **Runner** | The machine that executes the job (GitHub-hosted or self-hosted) |

## Our Workflow: `.github/workflows/ci.yml`

```yaml
on:
  push:
    branches: [main]
  pull_request:
    branches: [main]
```

This means the workflow fires when:

1. Someone **pushes** directly to `main`
2. Someone **opens or updates a pull request** targeting `main`

### Steps Breakdown

1. **Checkout** — Clones the repo onto the runner.
2. **Install uv** — Installs the `uv` package manager.
3. **Set up Python** — Installs Python 3.12 via uv.
4. **Install dependencies** — Runs `uv sync --all-extras` to install all
   project and dev dependencies from `pyproject.toml`.
5. **Lint with ruff** — Static analysis to catch errors and style issues.
6. **Check formatting with black** — Ensures code is consistently formatted.
7. **Run tests** — Executes `pytest -v` to run the full test suite.

If **any** step fails, the workflow fails and the PR gets a red ✗.

## How to Read the Results

1. Go to the **Actions** tab in your GitHub repository.
2. Click on the latest workflow run.
3. Expand any step to see its console output.
4. Green ✓ = passed, Red ✗ = failed.

## Common Gotchas

- **Indentation matters** — YAML is whitespace-sensitive.
- **Branch name must match** — `branches: [main]` won't trigger on `master`.
- **Secrets** — Never hard-code secrets; use GitHub Settings → Secrets.
- **Caching** — For faster builds, consider caching the uv cache directory.
