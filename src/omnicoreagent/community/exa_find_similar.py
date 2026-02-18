import os
import httpx
from typing import Any, Dict, Optional, List
from omnicoreagent.core.tools.local_tools_registry import Tool


class ExaFindSimilar:
    """Exa Find Similar Tool integration."""

    def __init__(self, api_key: Optional[str] = None):
        if httpx is None:
             raise ImportError(
                "Could not import `httpx` python package. "
                "Please install it using `pip install httpx`."
            )
        self.api_key = api_key or os.environ.get("EXA_API_KEY")
        if not self.api_key:
            raise ValueError("Exa API key not found. Please set EXA_API_KEY environment variable.")
        self.base_url = "https://api.exa.ai"

    async def _find_similar(
        self,
        url: str,
        num_results: int = 5,
        include_domains: Optional[List[str]] = None,
        exclude_domains: Optional[List[str]] = None,
        start_published_date: Optional[str] = None,
        end_published_date: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Find similar links to a given URL using Exa."""
        async with httpx.AsyncClient() as client:
            try:
                headers = {
                    "x-api-key": self.api_key,
                    "Content-Type": "application/json",
                }
                payload = {
                    "url": url,
                    "numResults": num_results,
                }
                if include_domains:
                    payload["includeDomains"] = include_domains
                if exclude_domains:
                    payload["excludeDomains"] = exclude_domains
                if start_published_date:
                    payload["startPublishedDate"] = start_published_date
                if end_published_date:
                    payload["endPublishedDate"] = end_published_date

                response = await client.post(
                    f"{self.base_url}/findSimilar",
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
                    "message": "\n---\n".join(formatted_results) if formatted_results else "No similar results found."
                }
            except Exception as e:
                return {
                    "status": "error",
                    "data": None,
                    "message": f"Error finding similar in Exa: {str(e)}"
                }

    def get_tool(self) -> Tool:
        return Tool(
            name="exa_find_similar",
            description="Find similar links to a given URL using Exa.",
            inputSchema={
                "type": "object",
                "properties": {
                    "url": {
                        "type": "string",
                        "description": "The URL to find similar links for.",
                    },
                    "num_results": {
                        "type": "integer",
                        "description": "Number of results to return.",
                        "default": 5,
                    },
                    "include_domains": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "List of domains to include.",
                    },
                    "exclude_domains": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "List of domains to exclude.",
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
                "required": ["url"],
            },
            function=self._find_similar,
        )
