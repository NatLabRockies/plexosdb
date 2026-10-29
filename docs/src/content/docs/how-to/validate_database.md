---
title: "Validating a Database"
---

Use `PlexosDB.validate_database()` after importing a model or modifying its
data. It returns `True` when all checks pass and raises
`DatabaseValidationError` when issues are found. Validation does not modify the
database by default.

```python
from plexosdb import DatabaseValidationError, PlexosDB

db = PlexosDB.from_xml("/path/to/model.xml")

try:
    db.validate_database()
except DatabaseValidationError as error:
    for finding in error.findings:
        print(f"[{finding.category.value}] {finding.message}")
    raise
```

## Checks and findings

Validation checks SQLite integrity, required schema tables and columns, foreign
keys, and model consistency. If required tables or columns are missing, later
checks are skipped to avoid querying an incomplete schema.

If SQLite cannot run its foreign-key check, for example because a referenced
parent key is missing a PRIMARY KEY or UNIQUE constraint, the SQLite error is
included as a `foreign_keys` finding. It raises `DatabaseValidationError` and
can be written to the same text report as other findings.

Model checks cover:

- Object/category, attribute/object, property/collection, and custom-column
  class consistency.
- Unsupported artifacts on static properties, duplicate static data, identical
  data graphs, duplicate non-NULL UIDs, and orphaned child rows.
- Missing System memberships and collection membership-count limits.
- Valid tag classes and actions restricted to Variable tags and texts.
- Property band limits, property and attribute validation rules, integer
  attributes, and case-insensitive object-name collisions within a class.

Each `DatabaseValidationFinding` has a `category` and a `message` describing the
issue and, where available, suggested corrective action. Categories are
`sqlite`, `schema`, `foreign_keys`, `objects`, `memberships`, `attributes`,
`properties`, and `types`. The exception retains all findings in its `findings`
tuple; reports can therefore be generated without parsing the exception text.

Property band limits are enforced only for nonnegative `max_band_id` values.
NULL and negative limits, including the v12 unlimited value `-1`, are not
treated as upper bounds.

Scenario and Data File tags are valid contexts for static property values and
are not reported as artifacts. Static duplicate detection includes the complete
tag/action and text/action sets, band, date bounds, and memo in the data-row
context; it reports multiple values only when they share that context. Different
Scenario or Data File assignments are kept distinct and are not flagged as
duplicates. Unsupported tag classes and static text, date, or memo artifacts
continue to be reported.

Property and attribute rules support inclusive `Between X And Y`, `In (X,Y,Z)`,
and `>=`, `<=`, `<`, and `>` comparisons. NULL attribute values are skipped.
Selected Transmission, Production, and Performance floating-point attributes
have class/name-scoped bounds that take precedence over incorrect integer
metadata; their database validation rules still apply. Transmission's Loss
Function Precision is excluded from the integer check only.

The exception display starts with `Database validation results:` and prefixes
each finding with `WARN:`. Only `WARN` is yellow when stderr is a terminal;
redirected output is plain text. Set `NO_COLOR` to disable coloring. The display
and failure text reports end with `Validation found N errors.`, where `N` is the
number of findings, not the number of affected database rows.

:::note
Findings still raise an exception even though their display uses `WARN`.
The suggested fixes are guidance, not actions performed automatically.
:::

## Writing a text report

Use the following pattern to write every finding to `validation_issues.txt`. The
report is UTF-8 plain text and does not contain terminal color codes. An
existing report is overwritten on each run.

```python
from pathlib import Path

from plexosdb import DatabaseValidationError, PlexosDB

db = PlexosDB.from_xml("/path/to/model.xml")

try:
    db.validate_database()
except DatabaseValidationError as error:
    issues = "\n".join(
        f"- [{finding.category.value}] {finding.message}"
        for finding in error.findings
    )
    Path("validation_issues.txt").write_text(
        f"Database validation results:\n{issues}\n"
        f"Validation found {len(error.findings)} errors.\n",
        encoding="utf-8",
    )
    raise
else:
    Path("validation_issues.txt").write_text(
        "No validation issues found.\n",
        encoding="utf-8",
    )
```

### Running the example script

From a source checkout, run:

```console
uv run python examples/validate_database.py "/path/to/model.xml"
uv run python examples/validate_database.py "/path/to/model.xml" --output model_validation.txt
```

The script closes its database connection after validation. It writes the report
before re-raising validation errors, giving a nonzero exit status when findings
exist. XML import errors and report-writing errors propagate normally; a
successful validation report is not written for those failures.

Download the script:
{download}`validate_database.py <../../../examples/validate_database.py>`.

## Limited automatic repairs

`db.validate_database(fix_issues=True)` only repairs membership class IDs when
the referenced object and collection agree and membership findings are the only
category of findings. Repairs run in a savepoint and are retained only if
revalidation passes; otherwise only the repairs are rolled back and an exception
is raised. If a caller transaction is already open, validation leaves it open
without committing or rolling back unrelated edits. The caller decides whether
to commit or roll back the successful repairs along with its other changes.
Without an existing transaction, successful repairs are committed.

It does not create missing memberships, remove excess memberships or duplicate
rows, delete artifacts or orphans, change values or UIDs, rename objects, or
update class or band-limit metadata. The example script intentionally uses
read-only validation, without automatic repairs.
