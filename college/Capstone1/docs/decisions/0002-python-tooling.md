# ADR 0002 — Python tooling: uv, Ruff, mypy, pytest

- **Status:** Accepted
- **Date:** 2026-09-07

## Context

The backend and the ML stack are Python. The project needs reproducible
environments, fast feedback, and a quality gate that runs in CI without a GPU.

## Decision

- **uv** for dependency management and virtual environments. Already installed
  (0.11.11).
- **Ruff** for both linting and formatting.
- **mypy** in strict mode for type checking.
- **pytest** for tests.

Configuration lives in `pyproject.toml`. The gate order is
format → lint → type check → unit tests.

## Rationale

- uv resolves and installs fast, and its lock file gives the reproducibility that
  experiment records depend on.
- Ruff replaces flake8, isort, and Black with one tool and one configuration,
  which removes a class of disagreement between tools.
- Strict mypy is cheap to adopt in a repository with no code yet, and expensive
  to retrofit later. Typed boundaries also document the damage-representation
  contract between the ML layer and the API.
- pytest is the default for both application tests and ML utility tests.

## Consequences

- Contributors need uv installed. The alternative — pip plus a hand-maintained
  requirements file — was rejected because it does not lock transitively.
- Strict mypy will need targeted per-module relaxation for untyped ML libraries.
  Relax per module with a stated reason; never disable strictness globally.
- CI skips mypy and pytest until Python sources and tests exist, and picks them
  up automatically when they land.
- No frontend tooling is configured yet, because no frontend code exists. It is
  added with the first frontend task.
