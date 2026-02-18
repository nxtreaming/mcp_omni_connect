from pathlib import Path
from typing import List, Optional, Union
import subprocess

from omnicoreagent.core.tools.local_tools_registry import Tool
from omnicoreagent.core.utils import log_debug, log_info, logger


class ShellRunCommand:
    def __init__(self, base_dir: Optional[Union[Path, str]] = None):
        self.base_dir: Optional[Path] = None
        if base_dir is not None:
            self.base_dir = Path(base_dir) if isinstance(base_dir, str) else base_dir

    def get_tool(self) -> Tool:
        return Tool(
            name="shell_run_command",
            description="Runs a shell command and returns the output or error.",
            inputSchema={
                "type": "object",
                "properties": {
                    "args": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "The command to run as a list of strings.",
                    },
                    "tail": {
                        "type": "integer",
                        "description": "The number of lines to return from the output.",
                        "default": 100,
                    },
                },
                "required": ["args"],
            },
            function=self._run_shell_command,
        )

    def _run_shell_command(self, args: List[str], tail: int = 100) -> str:
        """Runs a shell command and returns the output or error.

        Args:
            args (List[str]): The command to run as a list of strings.
            tail (int): The number of lines to return from the output.

        Returns:
            str: The output of the command.
        """
        try:
            log_info(f"Running shell command: {args}")
            result = subprocess.run(
                args,
                capture_output=True,
                text=True,
                cwd=str(self.base_dir) if self.base_dir else None,
            )
            log_debug(f"Result: {result}")
            log_debug(f"Return code: {result.returncode}")
            if result.returncode != 0:
                return f"Error: {result.stderr}"
            return "\n".join(result.stdout.split("\n")[-tail:])
        except Exception as e:
            logger.warning(f"Failed to run shell command: {e}")
            return f"Error: {e}"
