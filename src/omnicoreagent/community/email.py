from typing import Any, Dict, Optional

from omnicoreagent.core.tools.local_tools_registry import Tool
from omnicoreagent.core.utils import log_info, logger


class EmailTools:
    def __init__(
        self,
        receiver_email: Optional[str] = None,
        sender_name: Optional[str] = None,
        sender_email: Optional[str] = None,
        sender_passkey: Optional[str] = None,
    ):
        self.receiver_email = receiver_email
        self.sender_name = sender_name
        self.sender_email = sender_email
        self.sender_passkey = sender_passkey

    def get_tool(self) -> Tool:
        return Tool(
            name="email_user",
            description="Send an email to the configured recipient.",
            inputSchema={
                "type": "object",
                "properties": {
                    "subject": {"type": "string", "description": "Email subject"},
                    "body": {"type": "string", "description": "Email body"},
                },
                "required": ["subject", "body"],
            },
            function=self._email_user,
        )

    async def _email_user(self, subject: str, body: str) -> Dict[str, Any]:
        try:
            import smtplib
            from email.message import EmailMessage
        except ImportError:
            return {"status": "error", "data": None, "message": "smtplib not available"}

        if not self.receiver_email:
            return {"status": "error", "data": None, "message": "No receiver email provided"}
        if not self.sender_name:
            return {"status": "error", "data": None, "message": "No sender name provided"}
        if not self.sender_email:
            return {"status": "error", "data": None, "message": "No sender email provided"}
        if not self.sender_passkey:
            return {"status": "error", "data": None, "message": "No sender passkey provided"}

        msg = EmailMessage()
        msg["Subject"] = subject
        msg["From"] = f"{self.sender_name} <{self.sender_email}>"
        msg["To"] = self.receiver_email
        msg.set_content(body)

        log_info(f"Sending Email to {self.receiver_email}")
        try:
            with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
                smtp.login(self.sender_email, self.sender_passkey)
                smtp.send_message(msg)
        except Exception as e:
            logger.error(f"Error sending email: {e}")
            return {"status": "error", "data": None, "message": f"Error sending email: {e}"}

        return {"status": "success", "data": None, "message": "Email sent successfully"}
