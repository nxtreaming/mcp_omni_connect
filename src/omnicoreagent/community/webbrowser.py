import webbrowser
from typing import Any, Dict

from omnicoreagent.core.tools.local_tools_registry import Tool


class WebBrowserTools:
    def get_tool(self) -> Tool:
        return Tool(
            name="open_web_page",
            description="Open a URL in the default web browser.",
            inputSchema={
                "type": "object",
                "properties": {
                    "url": {"type": "string"},
                    "new_window": {"type": "boolean", "default": False, "description": "Open in a new window instead of a new tab"},
                },
                "required": ["url"],
            },
            function=self._open_page,
        )

    async def _open_page(self, url: str, new_window: bool = False) -> Dict[str, Any]:
        try:
            if new_window:
                webbrowser.open_new(url)
            else:
                webbrowser.open_new_tab(url)
            return {"status": "success", "data": None, "message": f"Opened {url}"}
        except Exception as e:
            return {"status": "error", "data": None, "message": str(e)}
