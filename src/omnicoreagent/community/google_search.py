
import os
try:
    import httpx
except ImportError:
    httpx = None
from typing import Any, Dict, Optional
from omnicoreagent.core.tools.local_tools_registry import Tool


class GoogleSearch:
    """Google Custom Search Tool integration."""

    def __init__(self, api_key: Optional[str] = None, cse_id: Optional[str] = None):
        """
        Initialize the Google Search tool.

        Args:
            api_key: Google API key. If not provided, it will be read from GOOGLE_API_KEY environment variable.
            cse_id: Google Custom Search Engine ID. If not provided, it will be read from GOOGLE_CSE_ID environment variable.
        """
        self.api_key = api_key or os.environ.get("GOOGLE_API_KEY")
        self.cse_id = cse_id or os.environ.get("GOOGLE_CSE_ID")
        
        if httpx is None:
            raise ImportError(
                "Could not import `httpx` python package. "
                "Please install it with `pip install httpx`."
            )

        if not self.api_key:
            raise ValueError(
                "Google API key is required. Set GOOGLE_API_KEY environment variable or pass it to constructor."
            )
        if not self.cse_id:
            raise ValueError(
                "Google CSE ID is required. Set GOOGLE_CSE_ID environment variable or pass it to constructor."
            )

    def get_tool(self) -> Tool:
        """Return the configured Tool object."""
        return Tool(
            name="google_search",
            description="Search the web using Google. Reliable and comprehensive search results.",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "The search query.",
                    },
                    "num_results": {
                        "type": "integer",
                        "description": "Number of results to return (max 10).",
                        "default": 5,
                    },
                },
                "required": ["query"],
            },
            function=self._search,
        )

    async def _search(self, query: str, num_results: int = 5) -> Dict[str, Any]:
        """Execute the search request."""
        url = "https://www.googleapis.com/customsearch/v1"

        params = {
            "key": self.api_key,
            "cx": self.cse_id,
            "q": query,
            "num": min(num_results, 10),
        }

        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(url, params=params, timeout=30.0)
                response.raise_for_status()
                data = response.json()
                return {
                    "status": "success",
                    "data": data,
                    "message": f"Found {len(data.get('items', []))} results for '{query}'"
                }
            except httpx.HTTPStatusError as e:
                return {
                    "status": "error",
                    "data": None,
                    "message": f"HTTP error: {e.response.status_code} - {e.response.text}",
                }
            except Exception as e:
                return {
                    "status": "error",
                    "data": None,
                    "message": f"Search failed: {str(e)}"
                }
