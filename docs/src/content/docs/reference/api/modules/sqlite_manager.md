---
title: "SQLite Manager"
---

<!-- Generated API reference -->

## Public module members

### plexosdb.db_manager

#### SQLiteConfig

[Source](https://github.com/NatLabRockies/plexosdb/blob/73e7fabe5e9f951231b6120c139cec1e52d12463/src/plexosdb/db_manager.py#L14)

SQLite database configuration.

##### Methods

###### for_in_memory

```text
for_in_memory(cls) -> 'SQLiteConfig'
```

Create optimized config for in-memory databases.

###### for_file_database

```text
for_file_database(cls) -> 'SQLiteConfig'
```

Create optimized config for file-based databases.

#### SQLiteManager

[Source](https://github.com/NatLabRockies/plexosdb/blob/73e7fabe5e9f951231b6120c139cec1e52d12463/src/plexosdb/db_manager.py#L49)

SQLite database manager with optimized transaction support.

##### Methods

###### connection

```text
connection(self) -> sqlite3.Connection
```

SQLite connection.

###### config

```text
config(self) -> SQLiteConfig
```

SQLite configuration.

###### sqlite_version

```text
sqlite_version(self) -> str
```

SQLite version.

###### tables

```text
tables(self) -> list[str]
```

List of table names.

###### add_collation

```text
add_collation(self, name: str, callable_func: Callable[[str, str], int]) -> bool
```

Register a collation function.

###### backup

```text
backup(self, target_path: str | Path) -> bool
```

Backup the database to a file.

###### close

```text
close(self) -> None
```

Close the database connection and release resources.

###### execute

```text
execute(self, query: str, params: tuple[Any, ...] | dict[str, Any] | None=None) -> bool
```

Execute a SQL statement that doesn't return results.

###### executemany

```text
executemany(self, query: str, params_seq: list[tuple[Any, ...]] | list[dict[str, Any]]) -> bool
```

Execute a SQL statement with multiple parameter sets.

###### executescript

```text
executescript(self, script: str) -> bool
```

Execute a SQL script containing multiple statements.

###### iter_query

```text
iter_query(self, query: str, params: tuple[Any, ...] | dict[str, Any] | None=None, batch_size: int=1000) -> Iterator[tuple[Any, ...]]
```

Execute a read-only query and return an iterator of results.

###### last_insert_rowid

```text
last_insert_rowid(self) -> int
```

Get the ID of the last inserted row.

###### list_table_names

```text
list_table_names(self) -> list[str]
```

Return a list of current table names on the database.

###### optimize

```text
optimize(self) -> bool
```

Run optimization routines on the database.

###### query

```text
query(self, query: str, params: None=None) -> list[tuple[Any, ...]]
```

Read-only queries without parameters use the default binding.

###### query

```text
query(self, query: str, params: tuple[Any, ...] | dict[str, Any]) -> list[tuple[Any, ...]]
```

Read-only queries that bind positional or named parameters.

###### query

```text
query(self, query: str, params: tuple[Any, ...] | dict[str, Any] | None=None) -> list[tuple[Any, ...]]
```

Execute a read-only query and return all results.

###### fetchall

```text
fetchall(self, query: str, params: tuple[Any, ...] | dict[str, Any] | None=None) -> list[tuple[Any, ...]]
```

Execute a query and return all results as a list of rows.

###### fetchall_dict

```text
fetchall_dict(self, query: str, params: tuple[Any, ...] | dict[str, Any] | None=None) -> list[dict[str, Any]]
```

Execute a query and return all results as a list of dictionaries.

###### fetchmany

```text
fetchmany(self, query: str, size: int=1000, params: tuple[Any, ...] | dict[str, Any] | None=None) -> list[tuple[Any, ...]]
```

Execute a query and return a specified number of rows.

###### fetchone

```text
fetchone(self, query: str, params: tuple[Any, ...] | dict[str, Any] | None=None) -> Any | None
```

Execute a query and return only the first result row.

###### fetchone_dict

```text
fetchone_dict(self, query: str, params: tuple[Any, ...] | dict[str, Any] | None=None) -> dict[str, Any] | None
```

Execute a query and return only the first result row as a dictionary.

###### iter_dicts

```text
iter_dicts(self, query: str, params: tuple[Any, ...] | dict[str, Any] | None=None, batch_size: int=1000) -> Iterator[dict[str, Any]]
```

Execute a read-only query and yield results as dictionaries.

###### transaction

```text
transaction(self) -> Generator['SQLiteManager', None, None]
```

Begin a transaction that can span multiple operations.

###### insert_records

```text
insert_records(self, table_name: str, records: dict[str, Any] | list[dict[str, Any]]) -> bool
```

Insert records into a table using dictionaries with column names as keys.

<!-- End generated API reference -->
