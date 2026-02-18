from os import getenv
from typing import Any, Dict, Literal, Optional

from omnicoreagent.core.tools.local_tools_registry import Tool
from omnicoreagent.core.utils import logger

try:
    from linkup import LinkupClient
except ImportError:
    LinkupClient = None



class LinkupTools:
    def __init__(
        self,
        api_key: Optional[str] = None,
        depth: Literal["standard", "deep"] = "standard",
        output_type: Literal["sourcedAnswer", "searchResults"] = "searchResults",
    ):
        if LinkupClient is None:
             raise ImportError("linkup not installed. Please install it using `pip install linkup-sdk`.")

        self.api_key = api_key or getenv("LINKUP_API_KEY")
        if not self.api_key:
            logger.error("LINKUP_API_KEY not set. Please set the LINKUP_API_KEY environment variable.")

        self.linkup = LinkupClient(api_key=self.api_key)
        self.depth = depth
        self.output_type = output_type

    def get_tool(self) -> Tool:
        return Tool(
            name="linkup_web_search",
            description="Search the web using the Linkup API for realtime online information.",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "Search query"},
                    "depth": {
                        "type": "string",
                        "enum": ["standard", "deep"],
                        "description": "Depth of the search",
                    },
                    "output_type": {
                        "type": "string",
                        "enum": ["sourcedAnswer", "searchResults"],
                        "description": "Type of output",
                    },
                },
                "required": ["query"],
            },
            function=self._web_search,
        )

    async def _web_search(
        self,
        query: str,
        depth: Optional[str] = None,
        output_type: Optional[str] = None,
    ) -> Dict[str, Any]:
        try:
            response = self.linkup.search(
                query=query,
                depth=depth or self.depth,  # type: ignore
                output_type=output_type or self.output_type,  # type: ignore
            )
            return {"status": "success", "data": response, "message": "Search completed"}
        except Exception as e:
            return {"status": "error", "data": None, "message": str(e)}
