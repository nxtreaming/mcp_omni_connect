
import os
try:
    import httpx
except ImportError:
    httpx = None
from typing import Any, Dict, Optional
from omnicoreagent.core.tools.local_tools_registry import Tool


class TavilySearch:
    """Tavily Search Tool integration."""

    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the Tavily Search tool.

        Args:
            api_key: Tavily API key. If not provided, it will be read from TAVILY_API_KEY environment variable.
        """
        if httpx is None:
            raise ImportError(
                "Could not import `httpx` python package. "
                "Please install it with `pip install httpx`."
            )
        self.api_key = api_key or os.environ.get("TAVILY_API_KEY")
        if not self.api_key:
            raise ValueError(
                "Tavily API key is required. Set TAVILY_API_KEY environment variable or pass it to constructor."
            )

    def get_tool(self) -> Tool:
        """Return the configured Tool object."""
        return Tool(
            name="tavily_search",
            description="Search the web using Tavily. Get comprehensive, accurate, and up-to-date information. Best for general knowledge, current events, and factual queries.",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "The search query to look up.",
                    },
                    "search_depth": {
                        "type": "string",
                        "enum": ["basic", "advanced"],
                        "description": "The depth of the search. 'basic' is faster, 'advanced' is more thorough.",
                        "default": "basic",
                    },
                    "include_answer": {
                        "type": "boolean",
                        "description": "Include a short answer in the response.",
                        "default": False,
                    },
                    "max_results": {
                        "type": "integer",
                        "description": "Maximum number of results to return.",
                        "default": 5,
                    },
                },
                "required": ["query"],
            },
            function=self._search,
        )

    async def _search(
        self,
        query: str,
        search_depth: str = "basic",
        include_answer: bool = False,
        max_results: int = 5,
    ) -> Dict[str, Any]:
        """Execute the search request."""
        url = "https://api.tavily.com/search"
        
        payload = {
            "api_key": self.api_key,
            "query": query,
            "search_depth": search_depth,
            "include_answer": include_answer,
            "max_results": max_results,
        }

        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(url, json=payload, timeout=30.0)
                response.raise_for_status()
                data = response.json()
                
                results = data.get("results", [])
                formatted_results = []
                for result in results:
                    formatted_results.append(
                        f"Title: {result.get('title')}\nURL: {result.get('url')}\nContent: {result.get('content')}\n"
                    )

                if include_answer and data.get("answer"):
                    formatted_results.insert(0, f"Answer: {data.get('answer')}\n")

                return {
                    "status": "success",
                    "data": data,
                    "message": "\n---\n".join(formatted_results) if formatted_results else "No results found."
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
