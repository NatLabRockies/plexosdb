# AGENTS.md

- Assume concurrent human/agent work; never revert or overwrite changes you did not author.
- This repo processes model data into SQLite; watch query/transform cost, memory churn, and fixture representativeness.
- Prefer minimal, behavior-proven changes; add regression coverage for bug fixes and use existing fixtures under `tests/fixtures` or `tests/data` when practical.
- No breadcrumbs after deleting or moving code; remove the old code/comment instead of leaving relocation notes.
- Use `uv sync --all-groups` for setup. For changed areas, run the narrow relevant check first; before broad handoff use `uv run prek run --show-diff-on-failure --color=always --all-files --hook-stage pre-push` when feasible.
- Type-check package changes with `uv run ty check --output-format github ./src/plexosdb`.
- Test package changes with `uv run pytest --cov --cov-report=xml`; benchmark-sensitive changes may need `uv run pytest benchmarks/ -k "not xlarge_300k" --benchmark-only --benchmark-json=benchmark-results.json --no-cov`.
- Build docs for user/operator-facing documentation changes with `uv run sphinx-build docs/source/ docs/_build/`.
