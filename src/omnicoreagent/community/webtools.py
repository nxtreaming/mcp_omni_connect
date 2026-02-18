try:
    import httpx
except ImportError:
    httpx = None

from omnicoreagent.core.tools.local_tools_registry import Tool
from omnicoreagent.core.utils import logger


class UrlExpand:
    """
    Tool for expanding shortened URLs.
    """
    def __init__(self, retries: int = 3):
        if httpx is None:
            raise ImportError(
                "Could not import `httpx` python package. "
                "Please install it with `pip install httpx`."
            )
        self.retries = retries

    def get_tool(self) -> Tool:
        return Tool(
            name="url_expand",
            description="Expands a shortened URL to its final destination.",
            inputSchema={
                "type": "object",
                "properties": {
                    "url": {
                        "type": "string",
                        "description": "The URL to expand.",
                    }
                },
                "required": ["url"],
            },
            function=self._expand_url,
        )

    def _expand_url(self, url: str) -> str:
        """
        Expands a shortened URL to its final destination using HTTP HEAD requests with retries.
        """
        timeout = 5
        for attempt in range(1, self.retries + 1):
            try:
                response = httpx.head(url, follow_redirects=True, timeout=timeout)
                final_url = response.url
                logger.info(f"expand_url: {url} expanded to {final_url} on attempt {attempt}")
                return str(final_url)
            except Exception as e:
                logger.error(f"Error expanding URL {url} on attempt {attempt}: {e}")

        return url
