---
title: "DatabaseValidationError"
editUrl: false
---

[Source](https://github.com/NatLabRockies/plexosdb/blob/36b632a1a0dd1fd24258b2fad2ec11ebd7e6a207/src/plexosdb/exceptions.py#L43)

Raised when database validation finds integrity or consistency issues.

WARN labels are yellow when stderr is a terminal, unless NO_COLOR is set.
Redirected output remains plain text.

## Import

```python
from plexosdb import DatabaseValidationError
```

## Constructor

```text
__init__(self, findings: Iterable[DatabaseValidationFinding]) -> None
```

Create an error carrying typed findings.

## Declared methods and properties
