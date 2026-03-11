# Pre-commit Hooks

Pre-commit hooks run checks **before** each `git commit` lands. This catches
formatting issues locally so they never reach CI.

## Setup (one-time)

```bash
uv run pre-commit install
```

This registers the hooks defined in `.pre-commit-config.yaml` with your
local git repository.

## What Happens on Commit

1. You run `git commit`.
2. Pre-commit intercepts and runs **black** on staged files.
3. If black reformats anything, the commit is **aborted** — review the
   changes, `git add` them, and commit again.
4. If everything is already formatted, the commit proceeds normally.

## Running Manually

```bash
# Check all files (not just staged)
uv run pre-commit run --all-files
```

## Why Black?

Black is an opinionated formatter — it removes style debates from code
review. Combined with pre-commit, it guarantees that every commit in the
repository is consistently formatted.
