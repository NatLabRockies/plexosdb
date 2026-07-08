# plexosdb-mcp

Thin MCP adapter package for plexosdb. Provides the `plexosdb-mcp` executable
and exposes the full PlexosDB MCP server over stdio.

## Install

```console
uv add plexosdb-mcp
```

## Run

Happy path:

```console
uvx plexosdb-mcp
```

Safe path (read-only):

```console
uvx plexosdb-mcp --read-only
```

Smoke checks:

```console
uvx plexosdb-mcp health
uvx plexosdb-mcp version
uvx plexosdb-mcp doctor
uvx plexosdb-mcp capabilities
uvx plexosdb-mcp --version
uvx plexosdb-mcp --help
```

All diagnostic subcommands output JSON to stdout. Pass `--json` to make the
contract explicit in agent scripts (e.g. `uvx plexosdb-mcp doctor --json`).
Errors write `{"ok": false, "error": "…"}` to stderr and exit with code 1.

## Local development

From this repository, use the nested project path:

```console
uv run --project src/plexosdb-mcp plexosdb-mcp health
uv run --project src/plexosdb-mcp plexosdb-mcp --read-only
```

This package provides the MCP server implementation for plexosdb
(`plexosdb_mcp.server`).
