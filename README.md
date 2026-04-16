# mcp-server-sqlite

A community-maintained MCP server for SQLite, forked from the official MCP organization repo (no longer maintained).

## Usage with Claude Code

```bash
claude mcp add sqlite -- uv run --directory /path/to/mcp-server-sqlite mcp-server-sqlite --db-path /path/to/your.db
```

## Usage with Claude Desktop

Add to your `claude_desktop_config.json`:

```json
"mcpServers": {
  "sqlite": {
    "command": "uv",
    "args": [
      "--directory",
      "/path/to/mcp-server-sqlite",
      "run",
      "mcp-server-sqlite",
      "--db-path",
      "/path/to/your.db"
    ]
  }
}
```

## Available Tools

| Tool | Description |
|---|---|
| `read_query` | Execute SELECT queries |
| `write_query` | Execute INSERT, UPDATE, DELETE queries |
| `create_table` | Create new tables |
| `list_tables` | List all tables |
| `describe_table` | Show schema for a table |
| `append_insight` | Append a note to the in-memory insights memo |

## Development

Install dependencies:

```bash
uv sync
```

Run MCP Inspector (requires a machine with a browser):

```bash
uv run mcp dev src/mcp_server_sqlite/server.py:wrapper
```

## License

MIT
