import sqlite3
from contextlib import closing
import textwrap
from mcp.server.models import InitializationOptions
import mcp.types as types
from mcp.server import NotificationOptions, Server
from pydantic import AnyUrl
import mcp.server.stdio


class McpServer(Server):
    """
    Example MCP server using SQLite for persistent storage instead of an in-memory dictionary.
    """

    def _init_database(self):
        """Initialize the SQLite database with the notes table"""
        with closing(sqlite3.connect(self.db_path)) as conn:
            with closing(conn.cursor()) as cursor:
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS notes (
                        name TEXT PRIMARY KEY,
                        content TEXT NOT NULL
                    )
                """)
                # Add example note if table is empty
                cursor.execute("SELECT COUNT(*) FROM notes")
                if cursor.fetchone()[0] == 0:
                    cursor.execute(
                        "INSERT INTO notes (name, content) VALUES (?, ?)",
                        ("example", "This is an example note."),
                    )
            conn.commit()

    def _get_notes(self) -> dict[str, str]:
        """Helper method to get all notes from the database"""
        with closing(sqlite3.connect(self.db_path)) as conn:
            with closing(conn.cursor()) as cursor:
                cursor.execute("SELECT name, content FROM notes")
                return dict(cursor.fetchall())

    def _get_note(self, name: str) -> str:
        """Helper method to get a single note from the database"""
        with closing(sqlite3.connect(self.db_path)) as conn:
            with closing(conn.cursor()) as cursor:
                cursor.execute("SELECT content FROM notes WHERE name = ?", (name,))
                result = cursor.fetchone()
                if result is None:
                    raise ValueError(f"Note not found: {name}")
                return result[0]

    def _add_note(self, name: str, content: str):
        """Helper method to add or update a note in the database"""
        with closing(sqlite3.connect(self.db_path)) as conn:
            with closing(conn.cursor()) as cursor:
                cursor.execute(
                    "INSERT OR REPLACE INTO notes (name, content) VALUES (?, ?)",
                    (name, content),
                )
            conn.commit()

    def __init__(self):
        super().__init__("sqlite")

        # Initialize SQLite database
        self.db_path = "notes.db"
        self._init_database()

        # RESOURCE HANDLERS
        @self.list_resources()
        async def handle_list_resources() -> list[types.Resource]:
            """List available note resources from the SQLite database"""
            notes = self._get_notes()
            return [
                types.Resource(
                    uri=AnyUrl(f"note:///{name}"),
                    name=f"Note: {name}",
                    description=f"A simple note named {name}",
                    mimeType="text/plain",
                )
                for name in notes
            ]

        @self.read_resource()
        async def handle_read_resource(uri: AnyUrl) -> str:
            """Read a specific note's content by its URI from the SQLite database"""
            if uri.scheme != "note":
                raise ValueError(f"Unsupported URI scheme: {uri.scheme}")

            name = uri.path
            if name is not None:
                name = name.lstrip("/")
                return self._get_note(name)
            raise ValueError(f"Note not found: {name}")

        # PROMPT HANDLERS
        @self.list_prompts()
        async def handle_list_prompts() -> list[types.Prompt]:
            """List available prompts"""
            return [
                types.Prompt(
                    name="summarize-notes",
                    description="Creates a summary of all notes",
                    arguments=[
                        types.PromptArgument(
                            name="style",
                            description="Style of the summary (brief/detailed)",
                            required=False,
                        )
                    ],
                )
            ]

        @self.get_prompt()
        async def handle_get_prompt(
            name: str, arguments: dict[str, str] | None
        ) -> types.GetPromptResult:
            """Generate a prompt using notes from the database"""
            if name != "summarize-notes":
                raise ValueError(f"Unknown prompt: {name}")
            notes = (
                "<notes>\n"
                + "\n".join(
                    f"<note name='{name}'>\n{content}\n</note>"
                    for name, content in self._get_notes().items()
                )
                + "\n</notes>"
            )
            style = (arguments or {}).get("style", "simple")
            prompt = """
            Your task is to provide a summary of the notes provided below.
            {notes}
            Ensure that the summary is in {style} style.
            """.format(notes=notes, style=style)
            return types.GetPromptResult(
                description="Summarize the current notes",
                messages=[
                    types.PromptMessage(
                        role="user",
                        content=types.TextContent(
                            type="text",
                            text=textwrap.dedent(prompt).strip(),
                        ),
                    )
                ],
            )

        # TOOL HANDLERS
        @self.list_tools()
        async def handle_list_tools() -> list[types.Tool]:
            """List available tools"""
            return [
                types.Tool(
                    name="add-note-to-local-db",
                    description="This tool is used to add a note to the local SQLite database, the SQLite database is stored locally. Only use this tool if the user specifically asks to store a note.",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "name": {"type": "string"},
                            "content": {"type": "string"},
                        },
                        "required": ["name", "content"],
                    },
                )
            ]

        @self.call_tool()
        async def handle_call_tool(
            name: str, arguments: dict | None
        ) -> list[types.TextContent | types.ImageContent | types.EmbeddedResource]:
            """Handle tool execution requests using the SQLite database"""
            if name != "add-note":
                raise ValueError(f"Unknown tool: {name}")

            if not arguments:
                raise ValueError("Missing arguments")

            note_name = arguments.get("name")
            content = arguments.get("content")

            if not note_name or not content:
                raise ValueError("Missing name or content")

            # Update database
            self._add_note(note_name, content)

            # Notify clients that resources have changed
            await self.request_context.session.send_resource_list_changed()

            return [
                types.TextContent(
                    type="text",
                    text=f"Added note '{note_name}' with content: {content}",
                )
            ]


async def main():
    server = McpServer()

    # Run the server using stdin/stdout streams
    async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="sqlite",
                server_version="0.1.0",
                capabilities=server.get_capabilities(
                    notification_options=NotificationOptions(),
                    experimental_capabilities={},
                ),
            ),
        )
