import os
from typing import Any, Dict, Optional
try:
    import httpx
except ImportError:
    httpx = None
from omnicoreagent.core.tools.local_tools_registry import Tool

class PerplexitySearch:
    """
    Perplexity Search Tool Wrapper.
    """

    def __init__(self, api_key: Optional[str] = None):
        if httpx is None:
            raise ImportError("`httpx` not installed. Please install using `pip install httpx`")
        self.api_key = api_key or os.environ.get("PERPLEXITY_API_KEY")
        if not self.api_key:
            raise ValueError("Perplexity API key not found. Please set PERPLEXITY_API_KEY environment variable or pass it to the constructor.")
        self.base_url = "https://api.perplexity.ai"

    async def _search(self, query: str, model: str = "llama-3.1-sonar-small-128k-online") -> Dict[str, Any]:
        """
        Search using Perplexity API.
        """
        async with httpx.AsyncClient() as client:
            try:
                headers = {
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json",
                }
                payload = {
                    "model": model,
                    "messages": [
                        {"role": "system", "content": "Be precise and concise."},
                        {"role": "user", "content": query}
                    ]
                }
                response = await client.post(
                    f"{self.base_url}/chat/completions",
                    headers=headers,
                    json=payload,
                    timeout=60.0
                )
                response.raise_for_status()
                data = response.json()
                
                content = data["choices"][0]["message"]["content"]
                citations = data.get("citations", [])
                
                result = f"Answer: {content}\n\nCitations:\n"
                for i, citation in enumerate(citations, 1):
                    result += f"[{i}] {citation}\n"
                
                return {
                    "status": "success",
                    "data": data,
                    "message": result
                }

            except Exception as e:
                return {
                    "status": "error",
                    "data": None,
                    "message": f"Error searching Perplexity: {str(e)}"
                }

    def get_tool(self) -> Tool:
        return Tool(
            name="perplexity_search",
            description="Search the web using Perplexity. Provides concise answers with citations. Best for complex questions requiring synthesis.",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "The search query.",
                    },
                    "model": {
                        "type": "string",
                        "description": "The model to use.",
                        "default": "llama-3.1-sonar-small-128k-online",
                    },
                },
                "required": ["query"],
            },
            function=self._search,
        )
