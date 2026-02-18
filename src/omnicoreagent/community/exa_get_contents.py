import os
import httpx
from typing import Any, Dict, Optional, List
from omnicoreagent.core.tools.local_tools_registry import Tool


class ExaGetContents:
    """Exa Get Contents Tool integration."""

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

    async def _get_contents(
        self,
        ids: List[str],
        text: bool = True,
    ) -> Dict[str, Any]:
        """Retrieve contents for specific Exa IDs (which look like URLs or UUIDs)."""
        async with httpx.AsyncClient() as client:
            try:
                headers = {
                    "x-api-key": self.api_key,
                    "Content-Type": "application/json",
                }
                payload = {
                    "ids": ids,
                    "text": text,
                }

                response = await client.post(
                    f"{self.base_url}/contents",
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
                        f"ID: {result.get('id')}\nUrl: {result.get('url')}\nTitle: {result.get('title')}\nText: {result.get('text')}\n"
                    )

                return {
                    "status": "success",
                    "data": data,
                    "message": "\n---\n".join(formatted_results) if formatted_results else "No contents found."
                }
            except Exception as e:
                return {
                    "status": "error",
                    "data": None,
                    "message": f"Error getting contents from Exa: {str(e)}"
                }

    def get_tool(self) -> Tool:
        return Tool(
            name="exa_get_contents",
            description="Retrieve detailed content from specific Exa Result IDs.",
            inputSchema={
                "type": "object",
                "properties": {
                    "ids": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "List of Exa IDs (or URLs) to fetch content for.",
                    },
                    "text": {
                        "type": "boolean",
                        "description": "Whether to return the full text content.",
                        "default": True,
                    }
                },
                "required": ["ids"],
            },
            function=self._get_contents,
        )
