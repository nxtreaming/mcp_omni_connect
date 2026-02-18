from os import getenv
from typing import Any, Dict, List, Optional

try:
    import httpx
except ImportError:
    httpx = None
from omnicoreagent.core.tools.local_tools_registry import Tool
from omnicoreagent.core.utils import log_debug, logger


class WhatsAppBase:
    base_url = "https://graph.facebook.com"

    def __init__(
        self,
        access_token: Optional[str] = None,
        phone_number_id: Optional[str] = None,
        version: Optional[str] = None,
        recipient_waid: Optional[str] = None,
    ):
        if httpx is None:
            raise ImportError(
                "Could not import `httpx` python package. "
                "Please install it with `pip install httpx`."
            )
        self.access_token = access_token or getenv("WHATSAPP_ACCESS_TOKEN")
        if not self.access_token:
            logger.error("WHATSAPP_ACCESS_TOKEN not set. Please set the WHATSAPP_ACCESS_TOKEN environment variable.")

        self.phone_number_id = phone_number_id or getenv("WHATSAPP_PHONE_NUMBER_ID")
        if not self.phone_number_id:
            logger.error(
                "WHATSAPP_PHONE_NUMBER_ID not set. Please set the WHATSAPP_PHONE_NUMBER_ID environment variable."
            )

        self.default_recipient = recipient_waid or getenv("WHATSAPP_RECIPIENT_WAID")
        self.version = version or getenv("WHATSAPP_VERSION", "v22.0")

    def _get_headers(self) -> Dict[str, str]:
        return {"Authorization": f"Bearer {self.access_token}", "Content-Type": "application/json"}

    def _get_messages_url(self) -> str:
        return f"{self.base_url}/{self.version}/{self.phone_number_id}/messages"

    async def _send_request(self, data: Dict[str, Any]) -> Dict[str, Any]:
        url = self._get_messages_url()
        headers = self._get_headers()
        
        log_debug(f"Sending WhatsApp request to URL: {url}")
        
        async with httpx.AsyncClient() as client:
            response = await client.post(url, headers=headers, json=data)
            response.raise_for_status()
            return response.json()


class WhatsAppSendMessage(WhatsAppBase):
    def get_tool(self) -> Tool:
        return Tool(
            name="whatsapp_send_message",
            description="Send a text or template message via WhatsApp.",
            inputSchema={
                "type": "object",
                "properties": {
                    "recipient": {"type": "string", "description": "Recipient phone number or WAID. Defaults to env var."},
                    "message_type": {"type": "string", "enum": ["text", "template"], "default": "text"},
                    "text": {"type": "string", "description": "Content for text messages."},
                    "template_name": {"type": "string", "description": "Name of the template for template messages."},
                    "template_language": {"type": "string", "default": "en_US"},
                    "template_components": {"type": "array", "items": {"type": "object"}},
                    "preview_url": {"type": "boolean", "default": False},
                },
                "required": ["message_type"],
            },
            function=self._send_message,
        )

    async def _send_message(
        self,
        recipient: Optional[str] = None,
        message_type: str = "text",
        text: Optional[str] = None,
        template_name: Optional[str] = None,
        template_language: str = "en_US",
        template_components: Optional[List[Dict[str, Any]]] = None,
        preview_url: bool = False,
    ) -> Dict[str, Any]:
        target_recipient = recipient or self.default_recipient
        if not target_recipient:
            return {"status": "error", "data": None, "message": "No recipient provided"}

        data: Dict[str, Any] = {
            "messaging_product": "whatsapp",
            "to": target_recipient,
            "type": message_type,
        }

        if message_type == "text":
            if not text:
                return {"status": "error", "data": None, "message": "Text content required for text messages"}
            data["text"] = {"preview_url": preview_url, "body": text}
        elif message_type == "template":
            if not template_name:
                return {"status": "error", "data": None, "message": "Template name required for template messages"}
            data["template"] = {"name": template_name, "language": {"code": template_language}}
            if template_components:
                data["template"]["components"] = template_components

        try:
            response = await self._send_request(data)
            message_id = response.get("messages", [{}])[0].get("id", "unknown")
            return {
                "status": "success",
                "data": response,
                "message": f"Message sent successfully. ID: {message_id}"
            }
        except httpx.HTTPStatusError as e:
            msg = e.response.text if hasattr(e, 'response') else str(e)
            return {"status": "error", "data": None, "message": f"WhatsApp API Error: {msg}"}
        except Exception as e:
            return {"status": "error", "data": None, "message": str(e)}
