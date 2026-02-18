import time
from typing import Any, Dict

from omnicoreagent.core.tools.local_tools_registry import Tool
from omnicoreagent.core.utils import log_info


class SleepTools:
    def get_tool(self) -> Tool:
        return Tool(
            name="sleep",
            description="Sleep for a given number of seconds.",
            inputSchema={
                "type": "object",
                "properties": {
                    "seconds": {"type": "integer", "description": "Number of seconds to sleep"},
                },
                "required": ["seconds"],
            },
            function=self._sleep,
        )

    async def _sleep(self, seconds: int) -> Dict[str, Any]:
        log_info(f"Sleeping for {seconds} seconds")
        time.sleep(seconds)
        log_info(f"Awake after {seconds} seconds")
        return {"status": "success", "data": None, "message": f"Slept for {seconds} seconds"}
