# CI Workflow Security Hardening (zizmor findings)

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Resolve all 75 zizmor findings (36 high, 11 medium, 9 low, 1 info) across 6 workflow files.

**Architecture:** Apply defense-in-depth to GitHub Actions: pin all actions to commit SHAs with version comments, set explicit least-privilege permissions at workflow and job level, disable credential persistence on every checkout, and migrate publish_pypi.yaml to trusted publishing.

**Tech Stack:** GitHub Actions, zizmor 1.23.1

---

## Findings Summary

| Audit | Severity | Count | Affected Workflows |
|-------|----------|-------|--------------------|
| `unpinned-uses` | error (high) | 31 | all 6 |
| `excessive-permissions` | error+warning | 11 | CI, commit, docs, publish_pypi, release |
| `artipacked` | help (low) | 9 | all 6 |
| `dangerous-triggers` | error (medium) | 1 | labeler |
| `secrets-outside-env` | warning (high) | 3 | CI, publish_pypi |
| `use-trusted-publishing` | info | 1 | publish_pypi |

## SHA Pin Reference

Use these exact SHAs (resolved 2026-03-15):

| Action | Version | SHA |
|--------|---------|-----|
| `actions/checkout` | v6 | `de0fac2e4500dabe0009e67214ff5f5447ce83dd` |
| `actions/setup-python` | v6 | `a309ff8b426b58ec0e2a45f0f869d46889d02405` |
| `astral-sh/setup-uv` | v7 | `b75dde52aef63a238519e7aecbbe79a4a52e4315` |
| `codecov/codecov-action` | v5 | `671740ac38dd9b0130fbe1cec585b89eea48d3de` |
| `actions/cache` | v5 | `cdf6c1fa76f9f475f3d7449005a359c84ca0f306` |
| `benchmark-action/github-action-benchmark` | v1.21.0 | `a7bc2366eda11037936ea57d811a43b3418d3073` |
| `peaceiris/actions-gh-pages` | v4 | `e9c66a37f080288a11235e32cbe2dc5fb3a679cc` |
| `amannn/action-semantic-pull-request` | v6.1.1 | `48f256284bd46cdaab1048c3721360e808335d50` |
| `googleapis/release-please-action` | v4 | `c3fc4de07084f75a2b61a5b933069bda6edf3d5c` |
| `actions/upload-artifact` | v7 | `bbbca2ddaa5d8feaa63e36b76fdaad77386f024f` |
| `actions/download-artifact` | v8 | `3e5f45b2cfb9172054b4087a40e8e0b5a5461e7c` |
| `pypa/gh-action-pypi-publish` | v1.13.0 | `106e0b0b7c337fa67ed433972f777c6357f78598` |
| `actions/labeler` | v6.0.1 | `634933edcd8ababfe52f92936142cc22ac488b1b` |

---

## Task 1: CI.yaml — permissions, pins, and persist-credentials

**Files:**
- Modify: `.github/workflows/CI.yaml`

**Step 1: Add top-level permissions block**

Add after `env:` block (line 11):

```yaml
permissions: {}
```

This sets default to no permissions. The `benchmarks` job already has its own block.

**Step 2: Add job-level permissions to `pre-commit` and `package` jobs**

Both need only `contents: read`:

```yaml
  pre-commit:
    permissions:
      contents: read
    ...

  package:
    permissions:
      contents: read
    ...
```

**Step 3: Add job-level permissions to `pytest` job**

Needs `contents: read` (checkout) only. Codecov uses its own token so no extra permission needed:

```yaml
  pytest:
    permissions:
      contents: read
    ...
```

**Step 4: Pin all actions to SHAs**

Replace every `uses:` line with SHA-pinned version (keep version as comment):

```yaml
# In pre-commit job:
- uses: actions/checkout@de0fac2e4500dabe0009e67214ff5f5447ce83dd # v6
- uses: actions/setup-python@a309ff8b426b58ec0e2a45f0f869d46889d02405 # v6
- uses: astral-sh/setup-uv@b75dde52aef63a238519e7aecbbe79a4a52e4315 # v7

# In pytest job:
- uses: actions/checkout@de0fac2e4500dabe0009e67214ff5f5447ce83dd # v6
- uses: astral-sh/setup-uv@b75dde52aef63a238519e7aecbbe79a4a52e4315 # v7
- uses: codecov/codecov-action@671740ac38dd9b0130fbe1cec585b89eea48d3de # v5

# In benchmarks job:
- uses: actions/checkout@de0fac2e4500dabe0009e67214ff5f5447ce83dd # v6
- uses: astral-sh/setup-uv@b75dde52aef63a238519e7aecbbe79a4a52e4315 # v7
- uses: actions/cache@cdf6c1fa76f9f475f3d7449005a359c84ca0f306 # v5
- uses: benchmark-action/github-action-benchmark@a7bc2366eda11037936ea57d811a43b3418d3073 # v1

# In package job:
- uses: actions/checkout@de0fac2e4500dabe0009e67214ff5f5447ce83dd # v6
- uses: actions/setup-python@a309ff8b426b58ec0e2a45f0f869d46889d02405 # v6
- uses: astral-sh/setup-uv@b75dde52aef63a238519e7aecbbe79a4a52e4315 # v7
```

**Step 5: Add `persist-credentials: false` to every checkout**

All 4 checkout steps need:

```yaml
- uses: actions/checkout@de0fac2e4500dabe0009e67214ff5f5447ce83dd # v6
  with:
    persist-credentials: false
```

For the `pre-commit` checkout that already has `with: fetch-depth: 0`, just add `persist-credentials: false` alongside it.

**Step 6: Run zizmor on CI.yaml to verify**

Run: `zizmor .github/workflows/CI.yaml`
Expected: Only `secrets-outside-env` for `CODECOV_TOKEN` remains (acceptable, see Decision Notes below).

**Step 7: Commit**

```
git add .github/workflows/CI.yaml
git commit -m "fix(ci): harden CI.yaml — pin actions, scope permissions, disable credential persistence"
```

---

## Task 2: commit.yaml — permissions, pins, and persist-credentials

**Files:**
- Modify: `.github/workflows/commit.yaml`

**Step 1: Add top-level permissions block**

```yaml
permissions: {}
```

**Step 2: Add permissions to `lint-commit-messages` job**

Only needs to read the repo:

```yaml
  lint-commit-messages:
    permissions:
      contents: read
    ...
```

The `lint-pr-title` job already has `permissions: pull-requests: read`.

**Step 3: Pin all actions to SHAs**

```yaml
- uses: actions/checkout@de0fac2e4500dabe0009e67214ff5f5447ce83dd # v6
- uses: astral-sh/setup-uv@b75dde52aef63a238519e7aecbbe79a4a52e4315 # v7
- uses: amannn/action-semantic-pull-request@48f256284bd46cdaab1048c3721360e808335d50 # v6.1.1
```

**Step 4: Add `persist-credentials: false` to checkout**

```yaml
- uses: actions/checkout@de0fac2e4500dabe0009e67214ff5f5447ce83dd # v6
  with:
    ref: ${{ github.event.pull_request.head.sha }}
    fetch-depth: 0
    persist-credentials: false
```

**Step 5: Run zizmor on commit.yaml to verify**

Run: `zizmor .github/workflows/commit.yaml`
Expected: 0 findings.

**Step 6: Commit**

```
git add .github/workflows/commit.yaml
git commit -m "fix(ci): harden commit.yaml — pin actions, scope permissions, disable credential persistence"
```

---

## Task 3: docs.yaml — permissions, pins, and persist-credentials

**Files:**
- Modify: `.github/workflows/docs.yaml`

**Step 1: Add top-level permissions block**

The `build` job needs `contents: write` only for the gh-pages deploy step (on push to main). However, the deploy step uses `github_token` explicitly, so we can use a more targeted approach:

```yaml
permissions:
  contents: write
```

Note: `peaceiris/actions-gh-pages` needs `contents: write` to push to the gh-pages branch. This is a workflow-level permission because there's only one job.

**Step 2: Pin all actions to SHAs**

```yaml
- uses: actions/checkout@de0fac2e4500dabe0009e67214ff5f5447ce83dd # v6
- uses: astral-sh/setup-uv@b75dde52aef63a238519e7aecbbe79a4a52e4315 # v7
- uses: peaceiris/actions-gh-pages@e9c66a37f080288a11235e32cbe2dc5fb3a679cc # v4
```

**Step 3: Add `persist-credentials: false` to checkout**

```yaml
- uses: actions/checkout@de0fac2e4500dabe0009e67214ff5f5447ce83dd # v6
  with:
    persist-credentials: false
```

**Step 4: Run zizmor on docs.yaml to verify**

Run: `zizmor .github/workflows/docs.yaml`
Expected: 0 findings.

**Step 5: Commit**

```
git add .github/workflows/docs.yaml
git commit -m "fix(ci): harden docs.yaml — pin actions, scope permissions, disable credential persistence"
```

---

## Task 4: labeler.yaml — dangerous trigger, pins, and persist-credentials

**Files:**
- Modify: `.github/workflows/labeler.yaml`

**Step 1: Pin all actions to SHAs**

```yaml
- uses: actions/checkout@de0fac2e4500dabe0009e67214ff5f5447ce83dd # v6
- uses: actions/labeler@634933edcd8ababfe52f92936142cc22ac488b1b # v6.0.1
```

**Step 2: Add `persist-credentials: false` to checkout**

```yaml
- uses: actions/checkout@de0fac2e4500dabe0009e67214ff5f5447ce83dd # v6
  with:
    persist-credentials: false
```

**Step 3: Address `dangerous-triggers` (pull_request_target)**

`pull_request_target` runs in the context of the base branch, which is inherently risky. However, the labeler workflow:
- Does NOT checkout PR code for execution (it only reads labels/file paths)
- Has minimal permissions (contents: read, pull-requests: write, issues: write)
- Uses the trusted `actions/labeler` action

This is the standard, documented use case for `pull_request_target`. The risk is acceptable. To suppress the zizmor warning, add an inline annotation:

```yaml
on:
  pull_request_target: # zizmor: ignore[dangerous-triggers]
    types: [opened, reopened, synchronize]
```

**Step 4: Run zizmor on labeler.yaml to verify**

Run: `zizmor .github/workflows/labeler.yaml`
Expected: 0 findings (dangerous-triggers suppressed by inline annotation).

**Step 5: Commit**

```
git add .github/workflows/labeler.yaml
git commit -m "fix(ci): harden labeler.yaml — pin actions, disable credential persistence, annotate pull_request_target"
```

---

## Task 5: publish_pypi.yaml — trusted publishing, permissions, pins

**Files:**
- Modify: `.github/workflows/publish_pypi.yaml`

This workflow is the most outdated and has the most issues. It uses `twine` with username/password secrets instead of trusted publishing.

**Decision point:** The `release.yaml` workflow already handles publishing via trusted publishing (`pypa/gh-action-pypi-publish@release/v1` with OIDC). This `publish_pypi.yaml` appears to be a legacy duplicate. Check with the team whether it should be deleted entirely or migrated.

**Step 1: If keeping the workflow, migrate to trusted publishing**

Replace the entire file:

```yaml
name: Upload to PyPi

on:
  release:
    types: [published]

permissions: {}

jobs:
  deploy:
    runs-on: ubuntu-latest
    permissions:
      contents: read
      id-token: write
    environment:
      name: pypi
      url: https://pypi.org/p/plexosdb
    steps:
      - uses: actions/checkout@de0fac2e4500dabe0009e67214ff5f5447ce83dd # v6
        with:
          persist-credentials: false
      - name: Set up Python
        uses: actions/setup-python@a309ff8b426b58ec0e2a45f0f869d46889d02405 # v6
        with:
          python-version: 3.11
      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          python -m pip install build
      - name: Build package
        run: python -m build
      - name: Publish to PyPI
        uses: pypa/gh-action-pypi-publish@106e0b0b7c337fa67ed433972f777c6357f78598 # v1.13.0
```

This eliminates:
- `TWINE_USERNAME` / `TWINE_PASSWORD` secrets (no more `secrets-outside-env`)
- `twine` dependency
- Token-based auth in favor of OIDC trusted publishing

**Step 1 (alternative): If deleting the workflow**

Since `release.yaml` already publishes to both TestPyPI and PyPI with trusted publishing, this workflow is redundant. Delete it:

```
git rm .github/workflows/publish_pypi.yaml
```

**Step 2: Run zizmor to verify**

Run: `zizmor .github/workflows/publish_pypi.yaml` (if kept)
Expected: 0 findings.

**Step 3: Commit**

```
git add .github/workflows/publish_pypi.yaml
git commit -m "fix(ci): harden publish_pypi.yaml — migrate to trusted publishing, pin actions, scope permissions"
```

---

## Task 6: release.yaml — permissions, pins, and persist-credentials

**Files:**
- Modify: `.github/workflows/release.yaml`

**Step 1: Move permissions from workflow-level to job-level**

The current workflow has `contents: write`, `pull-requests: write`, `id-token: write` at the top level. Each job should declare only what it needs:

```yaml
# Remove the top-level permissions block and replace with:
permissions: {}

# release-please job needs:
  release-please:
    permissions:
      contents: write
      pull-requests: write
    ...

# build job needs:
  build:
    permissions:
      contents: read
    ...

# publish-testpypi job needs:
  publish-testpypi:
    permissions:
      id-token: write
    ...

# publish-pypi job needs:
  publish-pypi:
    permissions:
      id-token: write
    ...
```

**Step 2: Pin all actions to SHAs**

```yaml
# release-please job:
- uses: googleapis/release-please-action@c3fc4de07084f75a2b61a5b933069bda6edf3d5c # v4

# build job:
- uses: actions/checkout@de0fac2e4500dabe0009e67214ff5f5447ce83dd # v6
- uses: actions/setup-python@a309ff8b426b58ec0e2a45f0f869d46889d02405 # v6
- uses: astral-sh/setup-uv@b75dde52aef63a238519e7aecbbe79a4a52e4315 # v7
- uses: actions/upload-artifact@bbbca2ddaa5d8feaa63e36b76fdaad77386f024f # v7

# publish-testpypi job:
- uses: actions/download-artifact@3e5f45b2cfb9172054b4087a40e8e0b5a5461e7c # v8
- uses: pypa/gh-action-pypi-publish@106e0b0b7c337fa67ed433972f777c6357f78598 # v1.13.0

# publish-pypi job:
- uses: actions/download-artifact@3e5f45b2cfb9172054b4087a40e8e0b5a5461e7c # v8
- uses: pypa/gh-action-pypi-publish@106e0b0b7c337fa67ed433972f777c6357f78598 # v1.13.0
```

**Step 3: Add `persist-credentials: false` to checkout**

```yaml
- uses: actions/checkout@de0fac2e4500dabe0009e67214ff5f5447ce83dd # v6
  with:
    ref: ${{ needs.release-please.outputs.release_tag }}
    fetch-depth: 0
    persist-credentials: false
```

**Step 4: Run zizmor on release.yaml to verify**

Run: `zizmor .github/workflows/release.yaml`
Expected: 0 findings.

**Step 5: Commit**

```
git add .github/workflows/release.yaml
git commit -m "fix(ci): harden release.yaml — scope permissions per job, pin actions, disable credential persistence"
```

---

## Decision Notes

### `secrets-outside-env` for CODECOV_TOKEN (CI.yaml)

zizmor flags `secrets.CODECOV_TOKEN` because it's not accessed within a GitHub environment. Creating a dedicated environment just for codecov adds friction with no real security gain (the token is already scoped to codecov uploads). This finding is acceptable to leave as-is or suppress with `# zizmor: ignore[secrets-outside-env]`.

### `dangerous-triggers` for labeler.yaml

`pull_request_target` is the correct trigger for the labeler use case. The workflow does not execute untrusted PR code. Suppressed with inline annotation.

### publish_pypi.yaml vs release.yaml

These two workflows appear to overlap. `release.yaml` is the modern one (trusted publishing, TestPyPI + PyPI). `publish_pypi.yaml` is legacy (twine + secrets). Recommend deleting `publish_pypi.yaml` if `release.yaml` is the active publish path.

---

## Verification

After all tasks, run full scan:

```bash
zizmor .github/workflows/
```

Expected: 0 errors, 0 warnings. Only acceptable suppressions remain.
