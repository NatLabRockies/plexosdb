"""CLI entrypoint for the standalone mcp-server-plexosdb package."""

from __future__ import annotations

import sys

from mcp_server_plexosdb import main as _main


def main() -> None:
    """Delegate execution to the MCP server implementation."""
    _main(sys.argv[1:])


if __name__ == "__main__":
    main()
