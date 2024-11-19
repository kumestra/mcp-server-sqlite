# Simple SQLite Notes Server

A basic MCP server implementation that demonstrates note-taking functionality using the three core MCP primitives: Resources, Prompts, and Tools.

## Core Concepts

### Resources
Resources are how clients access data from the server. In this case, they're notes stored in SQLite.

```python
# Access notes through a custom URI scheme
note:///example_note   # Gets the content of 'example_note'
```

### Prompts
Prompts allow generating text based on server state. Our server has a note summarization prompt that can be styled.

```python
# Example prompt with style argument
{
    "name": "summarize-notes",
    "arguments": {
        "style": "academic"  # Can be any style descriptor
    }
}
```

### Tools
Tools modify server state. We have a simple tool to add new notes.

```python
# Adding a new note
{
    "name": "add-note",
    "arguments": {
        "name": "my_note",
        "content": "This is my note content"
    }
}
```

## Key Implementation Details

### Handler Registration
All decorated handlers must be inside `__init__`:
```python
def __init__(self):
    super().__init__("sqlite")
    
    @self.list_resources()
    async def handle_list_resources():
        # Handler code here

    @self.read_resource()
    async def handle_read_resource():
        # Handler code here
```

### Storage
- Uses SQLite for persistent storage
- Helper methods handle database operations
- Clients are notified of state changes