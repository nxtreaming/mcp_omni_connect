# Creating New Community Tools

This guide explains how to add new tools to the `omnicoreagent.community` package.

## 1. Structure

Community tools live in `src/omnicoreagent/community/`. Each tool should be in its own file (e.g., `my_new_tool.py`).

## 2. Implementation Pattern

All community tools should follow this pattern:

1.  **Class Structure**: Create a class (e.g., `MyNewTool`).
2.  **Initialization**: Accept configuration (API keys, etc.) in `__init__`.
3.  **Tool Definition**: Implement a `get_tool()` method that returns a `Tool` object.
4.  **Standard Response**: The actual execution method (e.g., `_execute`, `_search`) MUST return a dictionary with `status`, `data`, and `message`.

### Example Template

```python
from typing import Dict, Any, Optional
import os
from omnicoreagent import Tool

class MyNewTool:
    def __init__(self, api_key: Optional[str] = None):
        # Best Practice: Allow passing key explicitly OR reading from env var
        self.api_key = api_key or os.getenv("MY_TOOL_API_KEY")
        if not self.api_key:
            raise ValueError("API key is required. Please pass it to __init__ or set MY_TOOL_API_KEY environment variable.")

    def get_tool(self) -> Tool:
        return Tool(
            name="my_new_tool",
            description="Description of what this tool does",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "Search query"},
                },
                "required": ["query"],
            },
            function=self._execute,
        )

    async def _execute(self, query: str) -> Dict[str, Any]:
        try:
            # Your logic here (e.g., API call)
            # result = await call_api(query)
            result = {"foo": "bar"}

            return {
                "status": "success",
                "data": result,
                "message": f"Successfully processed '{query}'"
            }
        except Exception as e:
            return {
                "status": "error",
                "data": None,
                "message": f"Operation failed: {str(e)}"
            }
```

## 3. Registering the Tool

Add your tool to `src/omnicoreagent/community/__init__.py` to make it easily importable:

```python
# src/omnicoreagent/community/__init__.py
from .my_new_tool import MyNewTool

__all__ = [
    # ... existing tools
    "MyNewTool",
]
```

## 4. Testing

Create a test file in `tests/` (e.g., `tests/test_my_new_tool.py`) and verify:
1.  Initialization (API key handling).
2.  Tool registration (`get_tool` returns a valid `Tool`).
3.  Execution (mock external calls and verify the standard response format).

## Checklist

- [ ] Tool returns `{"status": ..., "data": ..., "message": ...}`
- [ ] Type hints are used (`Dict[str, Any]`)
- [ ] Error handling is robust (try/except blocks)
- [ ] Dependencies are minimized or optional
