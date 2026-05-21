# plexosdb Agent Guide

Quick operating contract for humans and agents working in this repository. This
is a README-level guide, not full system documentation.

## North Star

- Think a lot before changing code. Understand the system, then act.
- Collaborate in the open. Explain intent, tradeoffs, and risks.
- Prefer correct-by-construction designs over patch-on-patch fixes.
- Prioritize performance when selecting designs, algorithms, and data
  structures.
- This is a model-processing and SQLite-focused application: watch query and
  transform costs, measure behavior on representative fixtures, and avoid
  unnecessary memory churn.
- Leave the codebase simpler than you found it.

## Team Collaboration Rules

- Assume concurrent work by other agents or humans.
- Treat `git status` and `git diff` as read-only context.
- Never revert or overwrite work you did not author.
- If a command hangs for more than 5 minutes, stop, capture context, and report.
- Prefer these repository-standard commands:
  - `uv sync --all-groups` for a complete local dev environment
  - `uv run prek run --show-diff-on-failure --color=always --all-files --hook-stage pre-push`
    for CI-equivalent pre-push hooks
  - `uv run ty check --output-format github ./src/plexosdb` for type checks
  - `uv run pytest --cov --cov-report=xml` for test + coverage checks
  - `uv run pytest benchmarks/ -k "not xlarge_300k" --benchmark-only --benchmark-json=benchmark-results.json --no-cov`
    for benchmark runs
  - `uv run sphinx-build docs/source/ docs/_build/` for docs build verification
- Before pushing, run the relevant CI-equivalent checks locally for changed
  areas to catch failures early.

## Engineering Workflow

Use red-green-refactor for all non-trivial changes:

1. Red: write or update a failing test that proves the behavior gap.
2. Green: implement the smallest correct change to pass.
3. Refactor: simplify while preserving behavior and keeping tests green.

Additional expectations:

- Start from first principles, not bandaids.
- No breadcrumbs. If you delete or move code, do not leave a comment in the old
  place. No "moved to X", no "relocated". Just remove it.
- Research official docs before introducing new patterns or dependencies.
- Keep modules focused, remove dead code, and avoid unnecessary abstraction.
- Leave each area better than how you found it.

## Testing Standards

- Test a lot. If behavior changes, tests must prove it.
- Prefer deterministic unit and integration tests over brittle ad hoc checks.
- Avoid mocking internal/domain behavior when feasible; use boundary doubles
  only when required (filesystem, network, time, subprocess, external services).
- Prefer fixture files under `tests/fixtures` and `tests/data` over large inline
  literals.
- Add regression coverage for every bug fix.
- Unless the user asks otherwise, run only tests you added or modified.
- Run broader suites when risk is high or before major integration points.

## Documentation Contract

- Document everything that affects users, operators, or contributors.
- If the documentation does not exist, the feature does not exist.
- Documentation is a live document and must ship with code changes.
- Update README, docs pages, examples, and migration notes as needed.
- New APIs and behavior changes require updated docs in the same change.

## Python Best Practices

- Use `uv` with `pyproject.toml` for dependency management and command
  execution.
- Run Python commands via `uv run`.
- Require explicit type hints and structured return types.
- Prefer dataclasses, TypedDicts, and focused domain objects over loose
  dictionaries.
- Keep signatures clear and avoid overly wide positional-argument APIs.
- Name functions so the action and target object are explicit.
- Avoid broad `try/except` blocks and catch-all exception handling.
- Let errors surface with clear types and fail fast at boundaries.
- Keep hot paths and repeated DB operations efficient.

## Python Testing

- Use `pytest` with function-based tests and fixtures.
- Avoid class-based test organization unless there is a compelling reason.
- Keep tests readable and focused on a single behavior per test.

## Commit Style

- Use Conventional Commits (for example, `feat:`, `fix:`, `docs:`, `test:`).

## Dependency Policy

- Add dependencies only when necessary.
- Choose actively maintained libraries with strong ecosystem adoption.
- Validate maintenance, API quality, and long-term fit before adding.

## Final Handoff

Before marking work complete:

1. List what changed and why.
2. List commands/tests run and their result.
3. List documentation updates made.
4. Call out follow-ups, risks, or open questions.
