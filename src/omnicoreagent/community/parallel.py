import json
from os import getenv
from typing import Any, Dict, List, Optional

from omnicoreagent.core.tools.local_tools_registry import Tool
from omnicoreagent.core.utils import log_error

try:
    from parallel import Parallel as ParallelClient
except ImportError:
    ParallelClient = None



class CustomJSONEncoder(json.JSONEncoder):
    """Custom JSON encoder that handles non-serializable types by converting them to strings."""

    def default(self, obj):
        try:
            return super().default(obj)
        except TypeError:
            return str(obj)


class ParallelTools:
    def __init__(
        self,
        api_key: Optional[str] = None,
        max_results: int = 10,
        max_chars_per_result: int = 10000,
        beta_version: str = "search-extract-2025-10-10",
        mode: Optional[str] = None,
        include_domains: Optional[List[str]] = None,
        exclude_domains: Optional[List[str]] = None,
        max_age_seconds: Optional[int] = None,
        disable_cache_fallback: Optional[bool] = None,
    ):
        self.api_key = api_key or getenv("PARALLEL_API_KEY")
        if not self.api_key:
            log_error("PARALLEL_API_KEY not set.")
        self.max_results = max_results
        self.max_chars_per_result = max_chars_per_result
        self.beta_version = beta_version
        self.mode = mode
        self.include_domains = include_domains
        self.exclude_domains = exclude_domains
        self.max_age_seconds = max_age_seconds
        self.disable_cache_fallback = disable_cache_fallback
        self.parallel_client = ParallelClient(
            api_key=self.api_key, default_headers={"parallel-beta": self.beta_version}
        )

    def _build_policies(self) -> Dict[str, Any]:
        policies: Dict[str, Any] = {}
        source_policy: Dict[str, Any] = {}
        if self.include_domains:
            source_policy["include_domains"] = self.include_domains
        if self.exclude_domains:
            source_policy["exclude_domains"] = self.exclude_domains
        if source_policy:
            policies["source_policy"] = source_policy

        fetch_policy: Dict[str, Any] = {}
        if self.max_age_seconds is not None:
            fetch_policy["max_age_seconds"] = self.max_age_seconds
        if self.disable_cache_fallback is not None:
            fetch_policy["disable_cache_fallback"] = self.disable_cache_fallback
        if fetch_policy:
            policies["fetch_policy"] = fetch_policy
        return policies

    def _format_search_result(self, search_result: Any) -> Dict[str, Any]:
        try:
            if hasattr(search_result, "model_dump"):
                return search_result.model_dump()
        except Exception:
            pass

        formatted: Dict[str, Any] = {"search_id": getattr(search_result, "search_id", ""), "results": []}
        if hasattr(search_result, "results") and search_result.results:
            for r in search_result.results:
                formatted["results"].append({
                    "title": getattr(r, "title", ""),
                    "url": getattr(r, "url", ""),
                    "publish_date": getattr(r, "publish_date", ""),
                    "excerpt": getattr(r, "excerpt", ""),
                })
        return formatted

    def get_tool(self) -> Tool:
        return Tool(
            name="parallel_search",
            description="Search the web using Parallel's AI-optimized Search API.",
            inputSchema={
                "type": "object",
                "properties": {
                    "objective": {"type": "string", "description": "Natural-language search objective"},
                    "search_queries": {"type": "array", "items": {"type": "string"}, "description": "Keyword queries"},
                    "max_results": {"type": "integer", "default": 10},
                },
            },
            function=self._search,
        )

    async def _search(
        self,
        objective: Optional[str] = None,
        search_queries: Optional[List[str]] = None,
        max_results: Optional[int] = None,
    ) -> Dict[str, Any]:
        try:
            if not objective and not search_queries:
                return {"status": "error", "data": None, "message": "Provide at least objective or search_queries"}

            params: Dict[str, Any] = {"max_results": max_results or self.max_results}
            if objective:
                params["objective"] = objective
            if search_queries:
                params["search_queries"] = search_queries
            if self.mode:
                params["mode"] = self.mode

            excerpts_config: Dict[str, Any] = {"max_chars_per_result": self.max_chars_per_result}
            params["excerpts"] = excerpts_config
            params.update(self._build_policies())

            result = self.parallel_client.beta.search(**params)
            data = self._format_search_result(result)
            return {"status": "success", "data": data, "message": f"Found {len(data.get('results', []))} results"}
        except Exception as e:
            log_error(f"Parallel search failed: {e}")
            return {"status": "error", "data": None, "message": str(e)}


class ParallelExtract(ParallelTools):
    def get_tool(self) -> Tool:
        return Tool(
            name="parallel_extract",
            description="Extract content from URLs using Parallel's Extract API.",
            inputSchema={
                "type": "object",
                "properties": {
                    "urls": {"type": "array", "items": {"type": "string"}},
                    "objective": {"type": "string"},
                    "excerpts": {"type": "boolean", "default": True},
                    "full_content": {"type": "boolean", "default": False},
                },
                "required": ["urls"],
            },
            function=self._extract,
        )

    async def _extract(
        self,
        urls: List[str],
        objective: Optional[str] = None,
        excerpts: bool = True,
        full_content: bool = False,
    ) -> Dict[str, Any]:
        try:
            if not urls:
                return {"status": "error", "data": None, "message": "Provide at least one URL"}

            params: Dict[str, Any] = {"urls": urls, "excerpts": excerpts, "full_content": full_content}
            if objective:
                params["objective"] = objective
            params.update(self._build_policies())

            result = self.parallel_client.beta.extract(**params)

            try:
                if hasattr(result, "model_dump"):
                    data = result.model_dump()
                    return {"status": "success", "data": data, "message": f"Extracted {len(urls)} URLs"}
            except Exception:
                pass

            formatted: Dict[str, Any] = {"extract_id": getattr(result, "extract_id", ""), "results": []}
            if hasattr(result, "results") and result.results:
                for r in result.results:
                    entry: Dict[str, Any] = {
                        "url": getattr(r, "url", ""),
                        "title": getattr(r, "title", ""),
                    }
                    if excerpts and hasattr(r, "excerpts"):
                        entry["excerpts"] = r.excerpts
                    if full_content and hasattr(r, "full_content"):
                        entry["full_content"] = r.full_content
                    formatted["results"].append(entry)
            return {"status": "success", "data": formatted, "message": f"Extracted {len(urls)} URLs"}
        except Exception as e:
            log_error(f"Parallel extract failed: {e}")
            return {"status": "error", "data": None, "message": str(e)}
