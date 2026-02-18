import os
from typing import Any, Dict, List, Optional
try:
    import httpx
except ImportError:
    httpx = None
from omnicoreagent.core.tools.local_tools_registry import Tool

class ExaSearch:
    """
    Exa Search Tool Wrapper.
    """

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.environ.get("EXA_API_KEY")
        if not self.api_key:
            raise ValueError("Exa API key not found. Please set EXA_API_KEY environment variable or pass it to the constructor.")
        if httpx is None:
            raise ImportError(
                "Could not import `httpx` python package. "
                "Please install it with `pip install httpx`."
            )
        self.base_url = "https://api.exa.ai"

    async def _search(
        self,
        query: str,
        num_results: int = 5,
        use_autoprompt: bool = True,
        category: Optional[str] = None,
        include_domains: Optional[List[str]] = None,
        exclude_domains: Optional[List[str]] = None,
        start_published_date: Optional[str] = None,
        end_published_date: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Search using Exa API.
        """
        async with httpx.AsyncClient() as client:
            try:
                headers = {
                    "x-api-key": self.api_key,
                    "Content-Type": "application/json",
                }
                payload = {
                    "query": query,
                    "numResults": num_results,
                    "useAutoprompt": use_autoprompt,
                }
                
                # Add optional parameters if provided
                if category:
                    payload["category"] = category
                if include_domains:
                    payload["includeDomains"] = include_domains
                if exclude_domains:
                    payload["excludeDomains"] = exclude_domains
                if start_published_date:
                    payload["startPublishedDate"] = start_published_date
                if end_published_date:
                    payload["endPublishedDate"] = end_published_date

                response = await client.post(
                    f"{self.base_url}/search",
                    headers=headers,
                    json=payload,
                    timeout=30.0
                )
                response.raise_for_status()
                data = response.json()
                
                results = data.get("results", [])
                formatted_results = []
                for result in results:
                    formatted_results.append(
                        f"Title: {result.get('title')}\nURL: {result.get('url')}\nID: {result.get('id')}\n"
                    )
                
                return {
                    "status": "success",
                    "data": data,
                    "message": "\n---\n".join(formatted_results) if formatted_results else "No results found."
                }

            except Exception as e:
                return {
                    "status": "error",
                    "data": None,
                    "message": f"Error searching Exa: {str(e)}"
                }

    def get_tool(self) -> Tool:
        return Tool(
            name="exa_search",
            description="Search the web using Exa (formerly Metaphor). Optimized for LLMs to find accurate and relevant content.",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "The search query.",
                    },
                    "num_results": {
                        "type": "integer",
                        "description": "Number of results to return.",
                        "default": 5,
                    },
                    "use_autoprompt": {
                        "type": "boolean",
                        "description": "Whether to use Exa's autoprompt feature to improve the query.",
                        "default": True,
                    },
                    "category": {
                        "type": "string",
                        "description": "The category to filter search results.",
                        "enum": ["company", "research paper", "news", "pdf", "github", "tweet", "personal site", "linkedin profile", "financial report"],
                    },
                    "include_domains": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "List of domains to include in the search.",
                    },
                    "exclude_domains": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "List of domains to exclude from the search.",
                    },
                    "start_published_date": {
                        "type": "string",
                        "description": "Start date for published content (YYYY-MM-DD).",
                    },
                    "end_published_date": {
                        "type": "string",
                        "description": "End date for published content (YYYY-MM-DD).",
                    },
                },
                "required": ["query"],
            },
            function=self._search,
        )
