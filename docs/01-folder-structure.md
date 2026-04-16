# Folder Structure

```
mcp-server-sqlite/
├── src/
│   └── mcp_server_sqlite/
│       ├── __init__.py       # Entry point, CLI argument parsing
│       └── server.py         # Main server logic, tools, resources, prompts
├── docs/                     # Project documentation (this folder)
├── .vscode/
│   └── settings.json         # VS Code workspace settings (readonly mode)
├── .gitignore                # Python gitignore template + SQLite db files
├── .python-version           # Pinned Python version for uv
├── Dockerfile                # Container image definition
├── pyproject.toml            # Project metadata and dependencies
├── uv.lock                   # Locked dependency versions
└── README.md                 # Project overview and usage instructions
```

## Key Files

| File | Purpose |
|---|---|
| `src/mcp_server_sqlite/server.py` | Core server — defines all MCP tools, resources, and prompts |
| `src/mcp_server_sqlite/__init__.py` | CLI entry point, parses `--db-path` argument |
| `pyproject.toml` | Project config, dependencies (`mcp[cli]>=1.6.0`), build backend |
| `uv.lock` | Locked dependency tree for reproducible installs |
| `Dockerfile` | For running the server in a container |

## Notes

- The server source lives under `src/` following Python src layout convention.
- `.venv/` is created locally by `uv` and is not committed (excluded by `.gitignore`).
- Database files (`*.db`, `*.sqlite`) are excluded from git — each environment maintains its own database.
