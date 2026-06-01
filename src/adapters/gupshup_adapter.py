"""[BOILERPLATE] Gupshup WhatsApp API client.

Do not modify per client.
"""
import json
import os

import httpx

from src.utils.logger_config import logger

GUPSHUP_URL = "https://api.gupshup.io/wa/api/v1/msg"


async def send_whatsapp_message(phone: str, message: dict) -> bool:
    """Send message via Gupshup WhatsApp API.

    Args:
        phone: Recipient phone number.
        message: Message dict with type and content.

    Returns:
        True if sent successfully.
    """
    try:
        headers = {
            "Content-Type": "application/x-www-form-urlencoded",
            "apikey": os.getenv("GUPSHUP_API_KEY", ""),
        }

        data = {
            "source": os.getenv("GUPSHUP_SOURCE", ""),
            "destination": phone,
            "message": json.dumps(message),
            "src.name": os.getenv("GUPSHUP_APP_NAME", ""),
        }

        async with httpx.AsyncClient(timeout=10) as client:
            response = await client.post(GUPSHUP_URL, headers=headers, data=data)
            response.raise_for_status()

        logger.info("Message sent", extra={"phone": phone})
        return True

    except Exception as e:
        logger.error(
            "Gupshup send failed", extra={"error": str(e), "phone": phone}
        )
        return False


def send_whatsapp_message_sync(phone: str, message: dict) -> bool:
    """Synchronous wrapper for send_whatsapp_message.

    Args:
        phone: Recipient phone number.
        message: Message dict.

    Returns:
        True if sent successfully.
    """
    import asyncio

    try:
        return asyncio.run(send_whatsapp_message(phone, message))
    except Exception as e:
        logger.error("Sync send failed", extra={"error": str(e)})
        return False
