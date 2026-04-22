# Use plexosdb as an MCP Server

This guide shows how to run the PlexosDB MCP server and verify it is working.

## What the server provides

The server exposes a small, practical tool set:

- `health`
- `create_empty_session`
- `open_xml_session`
- `close_session`
- `list_objects_by_class`
- `add_object`
- `add_property`
- `add_membership`
- `get_object_properties`
- `save_xml`
- `list_classes`
- `list_collections`
- `list_scenarios`
- `list_valid_properties`
- `list_reports`
- `list_units`
- `query_readonly`

Not every `PlexosDB` method in `db.py` is exposed as an MCP tool. Expose methods in
curated batches so the public MCP interface remains stable and easy to support.

## 1) Install dependencies

From the project root:

```console
uv sync --all-groups
```

## 2) Start the MCP server

Run the server over stdio:

```console
uv run plexosdb-mcp
```

If it starts successfully, it will wait for MCP client requests.

## 2b) Use production CLI mode (no Node.js required)

You can run one-shot CLI commands directly without any MCP client:

```console
uv run plexosdb-mcp --cli-command health
uv run plexosdb-mcp --cli-command create-empty-session
uv run plexosdb-mcp --cli-command open-xml-session --xml-path /path/to/model.xml
```

These commands print JSON output and exit. This mode is useful for production scripts,
automation checks, and environments where you do not want to install Node.js.

## 3) Interact with the server and verify tools

A simple way to test is with the MCP Inspector:

```console
npx @modelcontextprotocol/inspector uv run plexosdb-mcp
```

`npx` is only required for Inspector UI testing. It is not required for production use of
`plexosdb-mcp` itself.

In the Inspector UI:

1. Connect to the server process.
2. Call `health` and confirm `{ "ok": true }` is returned.
3. Call `create_empty_session` and copy the returned `session_id`.
4. Call `add_object` with:
   - `session_id`: `<your-session-id>`
   - `class_name`: `Generator`
   - `name`: `Solar_MCP_01`
5. Call `list_objects_by_class` with:
   - `session_id`: `<your-session-id>`
   - `class_name`: `Generator`
6. Confirm `Solar_MCP_01` appears in the response.
7. Call `close_session` and confirm `{ "closed": true }`.

## 4) Load a real XML and export a modified one

Typical sequence:

1. `open_xml_session` with `xml_path` set to your source model file.
2. `add_object` and optional `add_property` or `add_membership`.
3. `save_xml` with `output_path` set to the target file path.
4. `close_session`.

## 5) Configure an MCP client (example)

Most MCP clients support a JSON server entry with command + args. Use this shape:

```json
{
  "mcpServers": {
    "plexosdb": {
      "command": "uv",
      "args": ["run", "plexosdb-mcp"],
      "cwd": "/absolute/path/to/plexosdb"
    }
  }
}
```

After adding the server entry, reconnect the client and run `health`.

## Notes

- Keep the same `session_id` for all operations in one editing flow.
- Call `close_session` when done to release in-memory DB resources.
- `add_property` requires that the target property is valid for the class/collection in the current model.
