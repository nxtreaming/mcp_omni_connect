import os
try:
    import httpx
except ImportError:
    httpx = None
from typing import Any, Dict, Optional, Union
from omnicoreagent.core.tools.local_tools_registry import Tool

class TelegramSendMessage:
    """Telegram Send Message Tool."""

    def __init__(self, chat_id: Union[str, int, None] = None, token: Optional[str] = None):
        if httpx is None:
            raise ImportError("`httpx` not installed. Please install using `pip install httpx`")
        self.token = token or os.getenv("TELEGRAM_TOKEN")
        self.chat_id = chat_id 
        self.base_url = "https://api.telegram.org"

    def get_tool(self) -> Tool:
        return Tool(
            name="telegram_send_message",
            description="Send a message to a Telegram chat.",
            inputSchema={
                "type": "object",
                "properties": {
                    "message": {"type": "string", "description": "The message to send."},
                    "chat_id": {"type": "string", "description": "The chat ID (optional if set in init)."},
                },
                "required": ["message"],
            },
            function=self._send_message,
        )

    async def _send_message(self, message: str, chat_id: Optional[str] = None) -> Dict[str, Any]:
        target_chat_id = chat_id or self.chat_id
        if not self.token or not target_chat_id:
             return {
                "status": "error",
                "data": None,
                "message": "Telegram token and chat_id are required."
            }

        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(
                    f"{self.base_url}/bot{self.token}/sendMessage",
                    json={"chat_id": target_chat_id, "text": message}
                )
                response.raise_for_status()
                return {
                    "status": "success",
                    "data": response.json(),
                    "message": "Message sent successfully."
                }
            except Exception as e:
                return {
                    "status": "error",
                    "data": None,
                    "message": f"Error sending Telegram message: {str(e)}"
                }
