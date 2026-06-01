"""[BOILERPLATE] WhatsApp message dispatch and formatting.

Do not modify per client.
"""
import asyncio

from src.adapters.gupshup_adapter import send_whatsapp_message
from src.utils.logger_config import logger


async def dispatch_whatsapp(phone: str, responses: list):
    """Send all responses to WhatsApp user.

    Args:
        phone: Recipient phone number.
        responses: List of response dicts.
    """
    try:
        for response in responses:
            msg = _build_gupshup_message(response)
            await send_whatsapp_message(phone, msg)
            await asyncio.sleep(0.2)  # Rate limit
        logger.info(
            f"Dispatched {len(responses)} messages", extra={"phone": phone}
        )
    except Exception as e:
        logger.error("Dispatch failed", extra={"error": str(e), "phone": phone})


def _build_gupshup_message(response: dict) -> dict:
    """[CONFIG-DRIVEN] Convert response dict to Gupshup format.

    Args:
        response: Response dict with type and content.

    Returns:
        Gupshup-formatted message.
    """
    msg_type = response.get("type", "text")

    if msg_type == "text":
        return {"type": "text", "text": response.get("text", "")}

    elif msg_type == "image":
        return {
            "type": "image",
            "originalUrl": response.get("image_url", ""),
            "previewUrl": response.get("image_url", ""),
            "caption": response.get("caption", ""),
        }

    # [CLIENT-SPECIFIC] Add more types as needed (button, list, etc)
    return {"type": "text", "text": str(response)}


def dispatch_whatsapp_sync(phone: str, responses: list):
    """Synchronous wrapper for dispatch_whatsapp.

    Args:
        phone: Recipient phone number.
        responses: List of response dicts.
    """
    asyncio.run(dispatch_whatsapp(phone, responses))
