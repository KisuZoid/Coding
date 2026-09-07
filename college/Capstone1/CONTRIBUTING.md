# Contributing to AutoInspect-X

## Before you start

Read `init.md`, `CLAUDE.md`, and `AGENTS.md`. They define how work is done here
and take precedence over personal preference.

## Working agreement

1. **Inspect before coding.** Search the repository for an existing helper,
   component, schema, or service before adding a new one.
2. **Smallest coherent change.** Do not refactor unrelated modules because they
   could look cleaner.
3. **No speculative abstraction.** Build for the requirement in front of you.
4. **No dead code.** Remove unused imports, variables, functions, components,
   commented-out production code, unreachable logic, and obsolete configuration
   before opening a pull request.
5. **No fake production logic.** Placeholders, mock outputs, and hard-coded
   predictions are acceptable only when the task explicitly asks for scaffolding
   and the code says so plainly.
6. **Justify dependencies.** Check existing dependencies and the standard library
   first. State whether the dependency is needed at runtime, during development,
   or for research, and record why it was added.

## Quality gates

```
format → lint → type check → unit tests → integration / E2E when applicable
```

Python:

```bash
uv run ruff format .
uv run ruff check .
uv run mypy .
uv run pytest
```

GPU training never runs in CI. ML evaluation belongs to explicit experiment
runs, not the normal test suite.

## Commits

Use Conventional Commits: `feat:`, `fix:`, `docs:`, `refactor:`, `test:`,
`chore:`, `ci:`.

Write the subject line in the imperative mood, under 72 characters.

## Architecture decisions

Record any material architectural or research decision as an ADR in
`docs/decisions/`, numbered sequentially, using the format of the existing
records.

## Research and data

- Never fabricate results, datasets, citations, or ground truth.
- Keep these categories distinct: REAL GROUND TRUTH, WEAK LABEL, SYNTHETIC
  LABEL, DERIVED FEATURE, MODEL PREDICTION, ASSUMPTION.
- Never commit datasets or model checkpoints. Commit their documentation instead.
- When combining datasets, document source, licence, preprocessing, class label
  mapping, filtering, deduplication, and split policy.

## Session bookkeeping

Update `TASKS.md` and `MEMORY.md` at the end of a working session, and `LOGIC.md`
whenever workflow or automation logic changes.
