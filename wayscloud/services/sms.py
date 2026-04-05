"""SMS service -- send and track SMS messages."""

from __future__ import annotations

from typing import Optional


class SMSService:
    """Send SMS messages and track delivery.

    All methods use the public API at /v1/sms (API key auth).
    """

    def __init__(self, client):
        self._client = client

    def send(
        self,
        to: str,
        message: str,
        sender_id: Optional[str] = None,
    ) -> dict:
        """Send an SMS message.

        Args:
            to: Recipient phone number (E.164 format).
            message: Message text.
            sender_id: Optional sender ID / alphanumeric sender.
        """
        body: dict = {"to": to, "message": message}
        if sender_id:
            body["sender_id"] = sender_id
        return self._client.post("/v1/sms/send", json=body)

    def list(self) -> list[dict]:
        """List sent SMS messages."""
        data = self._client.get("/v1/sms/messages")
        return data.get("messages", data) if isinstance(data, dict) else data

    # Alias
    messages = list

    def get(self, message_id: str) -> dict:
        """Get details and delivery status of a specific message."""
        return self._client.get(f"/v1/sms/messages/{message_id}")

    # Alias
    get_message = get
