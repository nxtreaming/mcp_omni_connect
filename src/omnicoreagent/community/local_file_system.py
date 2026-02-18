from pathlib import Path
from typing import Any, Dict, Optional
from uuid import uuid4

from omnicoreagent.core.tools.local_tools_registry import Tool
from omnicoreagent.core.utils import log_debug, logger


class FileSystemWriteFile:
    def __init__(
        self,
        target_directory: Optional[str] = None,
        default_extension: str = "txt",
    ):
        self.target_directory = target_directory or str(Path.cwd())
        self.default_extension = default_extension.lstrip(".")

        target_path = Path(self.target_directory)
        target_path.mkdir(parents=True, exist_ok=True)

    def get_tool(self) -> Tool:
        return Tool(
            name="file_system_write_file",
            description="Write content to a local file.",
            inputSchema={
                "type": "object",
                "properties": {
                    "content": {"type": "string", "description": "Content to write to the file"},
                    "filename": {"type": "string", "description": "Name of the file. Defaults to UUID"},
                    "directory": {"type": "string", "description": "Directory to write file to"},
                    "extension": {"type": "string", "description": "File extension"},
                },
                "required": ["content"],
            },
            function=self._write_file,
        )

    async def _write_file(
        self,
        content: str,
        filename: Optional[str] = None,
        directory: Optional[str] = None,
        extension: Optional[str] = None,
        overwrite: bool = True,
    ) -> Dict[str, Any]:
        try:
            filename = filename or str(uuid4())
            directory = directory or self.target_directory
            if filename and "." in filename:
                path_obj = Path(filename)
                filename = path_obj.stem
                extension = extension or path_obj.suffix.lstrip(".")

            log_debug(f"Writing file to local system: {filename}")

            extension = (extension or self.default_extension).lstrip(".")

            dir_path = Path(directory)
            dir_path.mkdir(parents=True, exist_ok=True)

            full_filename = f"{filename}.{extension}"
            file_path = dir_path / full_filename

            if file_path.exists() and not overwrite:
                return {"status": "error", "data": None, "message": f"File '{file_path}' already exists"}

            file_path.write_text(content)
            return {"status": "success", "data": str(file_path), "message": f"Written to {file_path}"}
        except Exception as e:
            logger.error(f"Failed to write file: {e}")
            return {"status": "error", "data": None, "message": str(e)}


class FileSystemReadFile:
    def __init__(self, target_directory: Optional[str] = None):
        self.target_directory = target_directory or str(Path.cwd())

    def get_tool(self) -> Tool:
        return Tool(
            name="file_system_read_file",
            description="Read content from a local file.",
            inputSchema={
                "type": "object",
                "properties": {
                    "filename": {"type": "string", "description": "Name of the file to read"},
                    "directory": {"type": "string", "description": "Directory to read file from"},
                    "start_line": {"type": "integer", "description": "Line to start reading from (1-based)"},
                    "end_line": {"type": "integer", "description": "Line to end reading at (1-based, inclusive)"},
                },
                "required": ["filename"],
            },
            function=self._read_file,
        )

    async def _read_file(
        self,
        filename: str,
        directory: Optional[str] = None,
        start_line: Optional[int] = None,
        end_line: Optional[int] = None,
    ) -> Dict[str, Any]:
        try:
            file_path = Path(directory or self.target_directory) / filename
            if not file_path.exists():
                return {"status": "error", "data": None, "message": f"File not found: {file_path}"}

            content = file_path.read_text()

            if start_line is not None or end_line is not None:
                lines = content.splitlines()
                start_index = (start_line - 1) if start_line else 0
                end_index = end_line if end_line else len(lines)
                start_index = max(0, start_index)
                end_index = min(len(lines), end_index)
                content = "\n".join(lines[start_index:end_index])

            return {"status": "success", "data": content, "message": f"Read {file_path}"}
        except Exception as e:
            return {"status": "error", "data": None, "message": str(e)}


class FileSystemListFiles:
    def __init__(self, target_directory: Optional[str] = None):
        self.target_directory = target_directory or str(Path.cwd())

    def get_tool(self) -> Tool:
        return Tool(
            name="file_system_list_files",
            description="List files in a directory.",
            inputSchema={
                "type": "object",
                "properties": {
                    "directory": {"type": "string", "description": "Directory to list files from"},
                },
            },
            function=self._list_files,
        )

    async def _list_files(self, directory: Optional[str] = None) -> Dict[str, Any]:
        try:
            target_dir = Path(directory or self.target_directory)
            if not target_dir.exists() or not target_dir.is_dir():
                return {"status": "error", "data": None, "message": f"Directory not found: {target_dir}"}

            files = [str(p.name) for p in target_dir.iterdir()]
            return {"status": "success", "data": files, "message": f"Listed {len(files)} items in {target_dir}"}
        except Exception as e:
            return {"status": "error", "data": None, "message": str(e)}
