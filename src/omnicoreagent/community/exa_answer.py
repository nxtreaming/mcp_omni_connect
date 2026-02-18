import os
import httpx
from typing import Any, Dict, Optional
from omnicoreagent.core.tools.local_tools_registry import Tool


class ExaAnswer:
    """Exa Answer Tool integration."""

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

    async def _answer(
        self,
        query: str,
        text: bool = False,
    ) -> Dict[str, Any]:
        """Get an LLM answer to a question informed by Exa search results."""
        async with httpx.AsyncClient() as client:
            try:
                headers = {
                    "x-api-key": self.api_key,
                    "Content-Type": "application/json",
                }
                payload = {
                    "query": query,
                    "text": text,
                    # "stream": False # Explicitly not streaming for now
                }

                response = await client.post(
                    f"{self.base_url}/answer",
                    headers=headers,
                    json=payload,
                    timeout=60.0 # Answer generation might take longer
                )
                response.raise_for_status()
                data = response.json()
                
                answer = data.get("answer", "")
                citations = data.get("citations", [])
                
                citation_text = ""
                for c in citations:
                    citation_text += f"[{c.get('id')}] {c.get('title')} ({c.get('url')})\n"

                message = f"Answer: {answer}\n\nCitations:\n{citation_text}"

                return {
                    "status": "success",
                    "data": data,
                    "message": message
                }
            except Exception as e:
                return {
                    "status": "error",
                    "data": None,
                    "message": f"Error getting answer from Exa: {str(e)}"
                }

    def get_tool(self) -> Tool:
        return Tool(
            name="exa_answer",
            description="Get an LLM answer to a question informed by Exa search results.",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "The question or query to answer.",
                    },
                    "text": {
                        "type": "boolean",
                        "description": "Include full text from citation in the data (may be large).",
                        "default": False,
                    }
                },
                "required": ["query"],
            },
            function=self._answer,
        )
