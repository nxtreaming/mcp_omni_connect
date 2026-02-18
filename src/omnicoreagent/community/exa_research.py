import os
from typing import Any, Dict, Optional

from omnicoreagent.core.tools.local_tools_registry import Tool

try:
    from exa_py import Exa
except ImportError:
    Exa = None


class ExaResearch:
    """Exa Research Tool - Search and retrieve content using the Exa API."""

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.environ.get("EXA_API_KEY")
        if not self.api_key:
            raise ValueError("Exa API key not found. Please set EXA_API_KEY environment variable.")
        if Exa is None:
            raise ImportError(
                "Could not import `exa_py` python package. "
                "Please install it using `pip install exa_py`."
            )
        self.client = Exa(api_key=self.api_key)

    def get_tool(self) -> Tool:
        return Tool(
            name="exa_search",
            description="Search the web using Exa's neural search engine.",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "Search query"},
                    "num_results": {"type": "integer", "default": 10},
                    "use_autoprompt": {"type": "boolean", "default": True},
                },
                "required": ["query"],
            },
            function=self._search,
        )

    async def _search(
        self, query: str, num_results: int = 10, use_autoprompt: bool = True
    ) -> Dict[str, Any]:
        try:
            results = self.client.search(
                query, num_results=num_results, use_autoprompt=use_autoprompt
            )
            data = []
            for r in results.results:
                data.append({
                    "title": getattr(r, "title", ""),
                    "url": getattr(r, "url", ""),
                    "score": getattr(r, "score", None),
                    "published_date": getattr(r, "published_date", None),
                })
            return {"status": "success", "data": data, "message": f"Found {len(data)} results"}
        except Exception as e:
            return {"status": "error", "data": None, "message": str(e)}


class ExaSearchContents(ExaResearch):
    def get_tool(self) -> Tool:
        return Tool(
            name="exa_search_with_contents",
            description="Search the web and retrieve full page contents using Exa.",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {"type": "string"},
                    "num_results": {"type": "integer", "default": 5},
                },
                "required": ["query"],
            },
            function=self._search_with_contents,
        )

    async def _search_with_contents(self, query: str, num_results: int = 5) -> Dict[str, Any]:
        try:
            results = self.client.search_and_contents(query, num_results=num_results)
            data = []
            for r in results.results:
                data.append({
                    "title": getattr(r, "title", ""),
                    "url": getattr(r, "url", ""),
                    "text": getattr(r, "text", ""),
                })
            return {"status": "success", "data": data, "message": f"Found {len(data)} results with contents"}
        except Exception as e:
            return {"status": "error", "data": None, "message": str(e)}
