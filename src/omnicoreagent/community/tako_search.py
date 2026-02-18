import os
from typing import Any, Dict, Optional
try:
    import httpx
except ImportError:
    httpx = None
from omnicoreagent.core.tools.local_tools_registry import Tool

class TakoSearch:
    """
    Tako Search Tool Wrapper.
    Search for data visualizations and analytics.
    """

    def __init__(self, api_key: Optional[str] = None):
        if httpx is None:
            raise ImportError("`httpx` not installed. Please install using `pip install httpx`")
        self.api_key = api_key or os.environ.get("TAKO_API_KEY")
        if not self.api_key:
            raise ValueError("Tako API key not found. Please set TAKO_API_KEY environment variable or pass it to the constructor.")
        self.base_url = "https://api.tako.ai/v1" # Hypothetical URL, check API docs if available

    async def _search(self, query: str) -> Dict[str, Any]:
        """
        Search using Tako API.
        """
        async with httpx.AsyncClient() as client:
            try:
                headers = {
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json",
                }
                payload = {
                    "query": query,
                }
                response = await client.post(
                    f"{self.base_url}/search",
                    headers=headers,
                    json=payload,
                    timeout=30.0
                )
                response.raise_for_status()
                data = response.json()
                
                # Assuming standard response structure, adjust based on actual API
                results = data.get("results", [])
                formatted_results = []
                for result in results:
                    formatted_results.append(
                        f"Title: {result.get('title')}\nDescription: {result.get('description')}\nURL: {result.get('url')}\n"
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
                    "message": f"Error searching Tako: {str(e)}"
                }

    def get_tool(self) -> Tool:
        return Tool(
            name="tako_search",
            description="Search for data visualizations and analytics using Tako.",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "The search query for data or visualizations.",
                    },
                },
                "required": ["query"],
            },
            function=self._search,
        )
