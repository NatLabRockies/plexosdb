# Benchmark Tests

This folder contains `pytest-benchmark` performance tests for hot paths.

Run all benchmark tests:

```bash
uv run pytest benchmarks --benchmark-only --no-cov
```

Run only membership bulk insert benchmark:

```bash
uv run pytest benchmarks/test_add_memberships_from_records.py --benchmark-only --no-cov
```

Run the `300k` case only:

```bash
uv run pytest benchmarks/test_add_memberships_from_records.py -k xlarge_300k --benchmark-only --no-cov
```
