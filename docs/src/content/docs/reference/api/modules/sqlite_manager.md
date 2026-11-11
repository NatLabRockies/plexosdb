---
title: "SQLite Manager"
---

<!-- Generated API reference -->

## Public module members

### plexosdb.db_manager

#### SQLiteConfig

[Source](https://github.com/NatLabRockies/plexosdb/blob/36b632a1a0dd1fd24258b2fad2ec11ebd7e6a207/src/plexosdb/db_manager.py#L14)

SQLite database configuration.

##### Methods and properties

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

[Source](https://github.com/NatLabRockies/plexosdb/blob/36b632a1a0dd1fd24258b2fad2ec11ebd7e6a207/src/plexosdb/db_manager.py#L49)

SQLite database manager with optimized transaction support.

##### Methods and properties

###### connection

```text
connection: sqlite3.Connection
```

SQLite connection.

###### config

```text
config: SQLiteConfig
```

SQLite configuration.

###### sqlite_version

```text
sqlite_version: str
```

SQLite version.

###### tables

```text
tables: list[str]
```

List of table names.

###### add_collation

```text
add_collation(self, name: str, callable_func: Callable[[str, str], int]) -> bool
```

Register a collation function.

**Parameters**

- `name : str`
  Name of the collation
- `callable_func : callable`
  Function implementing the collation

**Returns**

- `bool`
  True if creation succeeded, False if it failed

###### backup

```text
backup(self, target_path: str | Path) -> bool
```

Backup the database to a file.

**Parameters**

- `target_path : str or Path`
  Path to save the database backup

**Returns**

- `bool`
  True if backup succeeded, False if it failed

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

Each execution is its own transaction unless used within a transaction context.

**Parameters**

- `query : str`
  SQL statement to execute
- `params : tuple or dict, optional`
  Parameters to bind to the statement

**Returns**

- `bool`
  True if execution succeeded, False if it failed

**Raises**

- `sqlite3.Error`
  If a database error occurs within a transaction

###### executemany

```text
executemany(self, query: str, params_seq: list[tuple[Any, ...]] | list[dict[str, Any]]) -> bool
```

Execute a SQL statement with multiple parameter sets.

**Parameters**

- `query : str`
  SQL statement to execute
- `params_seq : list of tuples or dicts`
  Sequence of parameter sets to bind

**Returns**

- `bool`
  True if execution succeeded, False if it failed

**Raises**

- `sqlite3.Error`
  If a database error occurs within a transaction

###### executescript

```text
executescript(self, script: str) -> bool
```

Execute a SQL script containing multiple statements.

**Parameters**

- `script : str`
  SQL script to execute

**Returns**

- `bool`
  True if execution succeeded, False if it failed

###### iter_query

```text
iter_query(self, query: str, params: tuple[Any, ...] | dict[str, Any] | None=None, batch_size: int=1000) -> Iterator[tuple[Any, ...]]
```

Execute a read-only query and return an iterator of results.

This is memory-efficient for large result sets. Use only for SELECT statements.

**Parameters**

- `query : str`
  SQL query to execute (SELECT statements only)
- `params : tuple or dict, optional`
  Parameters to bind to the query
- `batch_size : int, default=1000`
  Number of records to fetch in each batch

**Yields**

- `tuple`
  One database row at a time

**Raises**

- `sqlite3.Error`
  If a database error occurs

###### last_insert_rowid

```text
last_insert_rowid(self) -> int
```

Get the ID of the last inserted row.

**Returns**

- `int`
  ID of the last inserted row

**Raises**

- `sqlite3.Error`
  If a database error occurs

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

VACUUM can't run inside a transaction, so this method may commit
any pending changes before optimizing the database.

**Returns**

- `bool`
  True if optimization succeeded, False if it failed

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

Note: This method should ONLY be used for SELECT statements.
For INSERT/UPDATE/DELETE, use execute() instead.

**Parameters**

- `query : str`
  SQL query to execute (SELECT statements only)
- `params : tuple or dict, optional`
  Parameters to bind to the query

**Returns**

- `list`
  Query results (tuples or named tuples based on initialization)

**Raises**

- `sqlite3.Error`
  If a database error occurs

###### fetchall

```text
fetchall(self, query: str, params: tuple[Any, ...] | dict[str, Any] | None=None) -> list[tuple[Any, ...]]
```

Execute a query and return all results as a list of rows.

This method is a standard DB-API style alias for query().

**Parameters**

- `query : str`
  SQL query to execute (SELECT statements only)
- `params : tuple or dict, optional`
  Parameters to bind to the query

**Returns**

- `list`
  All rows (as tuples or named tuples based on row_factory setting)

**Raises**

- `sqlite3.Error`
  If a database error occurs

**See Also**

- `query` : Equivalent method with PlexosDB-specific naming
- `fetchone` : Get only the first row of results
- `fetchall_dict` : Return results as dictionaries

**Examples**

```python
>>> db = SQLiteManager()
>>> db.execute("CREATE TABLE test (id INTEGER, name TEXT)")
>>> db.execute("INSERT INTO test VALUES (1, 'Alice')")
>>> db.fetchall("SELECT * FROM test")
[(1, 'Alice')]
```

###### fetchall_dict

```text
fetchall_dict(self, query: str, params: tuple[Any, ...] | dict[str, Any] | None=None) -> list[dict[str, Any]]
```

Execute a query and return all results as a list of dictionaries.

**Parameters**

- `query : str`
  SQL query to execute (SELECT statements only)
- `params : tuple or dict, optional`
  Parameters to bind to the query

**Returns**

- `list[dict[str, Any]]`
  All rows as dictionaries with column names as keys

**Raises**

- `sqlite3.Error`
  If a database error occurs

**See Also**

- `query` : Return results as tuples
- `iter_dicts` : Memory-efficient iterator over dictionaries

**Examples**

```python
>>> db = SQLiteManager()
>>> db.execute("CREATE TABLE users (id INTEGER, name TEXT)")
>>> db.execute("INSERT INTO users VALUES (1, 'Alice')")
>>> db.fetchall_dict("SELECT * FROM users")
[{'id': 1, 'name': 'Alice'}]
>>> user = db.fetchall_dict("SELECT * FROM users")[0]
>>> print(f"User {user['id']}: {user['name']}")
User 1: Alice
```

###### fetchmany

```text
fetchmany(self, query: str, size: int=1000, params: tuple[Any, ...] | dict[str, Any] | None=None) -> list[tuple[Any, ...]]
```

Execute a query and return a specified number of rows.

**Parameters**

- `query : str`
  SQL query to execute (SELECT statements only)
- `size : int, default=1000`
  Maximum number of rows to return
- `params : tuple or dict, optional`
  Parameters to bind to the query

**Returns**

- `list`
  Up to 'size' rows from the query result

**Raises**

- `sqlite3.Error`
  If a database error occurs

**See Also**

- `fetchall` : Get all rows
- `fetchone` : Get only one row
- `iter_query` : Iterator over results

**Examples**

```python
>>> db = SQLiteManager()
>>> db.execute("CREATE TABLE items (id INTEGER, name TEXT)")
>>> db.executemany("INSERT INTO items VALUES (?, ?)", [(i, f"Item {i}") for i in range(1, 101)])
>>> # Get first 10 items
>>> first_batch = db.fetchmany("SELECT * FROM items", size=10)
>>> len(first_batch)
10
```

###### fetchone

```text
fetchone(self, query: str, params: tuple[Any, ...] | dict[str, Any] | None=None) -> Any | None
```

Execute a query and return only the first result row.

**Parameters**

- `query : str`
  SQL query to execute (SELECT statements only)
- `params : tuple or dict, optional`
  Parameters to bind to the query

**Returns**

- `tuple or namedtuple or None`
  First row of results or None if no results

**Raises**

- `sqlite3.Error`
  If a database error occurs

**See Also**

- `fetchall` : Get all rows
- `fetchone_dict` : Get first row as dictionary

**Examples**

```python
>>> db = SQLiteManager()
>>> db.execute("CREATE TABLE users (id INTEGER, name TEXT)")
>>> db.execute("INSERT INTO users VALUES (1, 'Alice')")
>>> user = db.fetchone("SELECT * FROM users WHERE id = ?", (1,))
>>> user
(1, 'Alice')
>>> user = db.fetchone("SELECT * FROM users WHERE id = ?", (999,))
>>> user is None
True
```

###### fetchone_dict

```text
fetchone_dict(self, query: str, params: tuple[Any, ...] | dict[str, Any] | None=None) -> dict[str, Any] | None
```

Execute a query and return only the first result row as a dictionary.

**Parameters**

- `query : str`
  SQL query to execute (SELECT statements only)
- `params : tuple or dict, optional`
  Parameters to bind to the query

**Returns**

- `dict[str, Any] or None`
  First row as dictionary with column names as keys, or None if no results

**Raises**

- `sqlite3.Error`
  If a database error occurs

**See Also**

- `fetchone` : Get first row as tuple
- `fetchall_dict` : Get all rows as dictionaries

**Examples**

```python
>>> db = SQLiteManager()
>>> db.execute("CREATE TABLE users (id INTEGER, name TEXT, email TEXT)")
>>> db.execute("INSERT INTO users VALUES (1, 'Alice', 'alice@example.com')")
>>> user = db.fetchone_dict("SELECT * FROM users WHERE id = ?", (1,))
>>> print(f"{user['name']}'s email is {user['email']}")
Alice's email is alice@example.com
```

###### iter_dicts

```text
iter_dicts(self, query: str, params: tuple[Any, ...] | dict[str, Any] | None=None, batch_size: int=1000) -> Iterator[dict[str, Any]]
```

Execute a read-only query and yield results as dictionaries.

This is memory-efficient for large result sets. Each row is returned
as a dictionary with column names as keys.

**Parameters**

- `query : str`
  SQL query to execute (SELECT statements only)
- `params : tuple or dict, optional`
  Parameters to bind to the query
- `batch_size : int, default=1000`
  Number of records to fetch in each batch

**Yields**

- `dict[str, Any]`
  One database row at a time as a dictionary

**Raises**

- `sqlite3.Error`
  If a database error occurs

**See Also**

- `iter_query` : Iterator over tuples or named tuples
- `fetchall_dict` : Get all results as dictionaries at once

**Examples**

```python
>>> db = SQLiteManager()
>>> db.execute("CREATE TABLE users (id INTEGER, name TEXT)")
>>> db.executemany("INSERT INTO users VALUES (?, ?)", [(i, f"User {i}") for i in range(1, 1001)])
>>> # Process users efficiently one at a time
>>> for user in db.iter_dicts("SELECT * FROM users"):
...     print(f"Processing user {user['name']}")
```

###### transaction

```text
transaction(self) -> Generator['SQLiteManager', None, None]
```

Begin a transaction that can span multiple operations.

This provides explicit transaction control for grouping multiple operations
into a single atomic unit that either all succeed or all fail.

**Returns**

- `context manager`
  A context manager for the transaction

**Examples**

```python
>>> with db.transaction():
>>>     db.execute("INSERT INTO table1 VALUES (1, 'a')")
>>>     db.execute("INSERT INTO table2 VALUES (1, 'b')")
```

**Raises**

- `Exception`
  Re-raises any exception from the transaction after rolling back

###### insert_records

```text
insert_records(self, table_name: str, records: dict[str, Any] | list[dict[str, Any]]) -> bool
```

Insert records into a table using dictionaries with column names as keys.

Fails if duplicate records exist (uses INSERT without OR REPLACE).

**Parameters**

- `table_name : str`
  Name of the table to insert records into
- `records : dict or list of dicts`
  Dictionary or list of dictionaries with column names as keys

**Returns**

- `bool`
  True if insertion succeeded, False if it failed

**Raises**

- `ValueError`
  If table doesn't exist, records are empty, or have inconsistent keys
- `sqlite3.Error`
  If a database error occurs within a transaction or duplicate records exist

<!-- End generated API reference -->
