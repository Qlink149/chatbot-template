"""[HYBRID] Webhook handler and message routing.

Boilerplate parts: webhook receiving, duplicate checking, session management.
Client-specific parts: intent routing, tool calling.
"""
import asyncio
import json

from fastapi import APIRouter, BackgroundTasks, Request
from fastapi.responses import Response

from src.precheck.webhook_parser import extract_gupshup_message, is_media_only
from src.precheck.duplicate_check import mark_message_processed
from src.precheck.session_handler import (
    get_or_create_session,
    save_message_to_history,
)
from src.ai.llm_orchestrator import chat_agent
from src.response.message_dispatcher import dispatch_whatsapp
from src.utils.logger_config import logger

try:
    from config.client import CLIENT_CONFIG
except ImportError:
    CLIENT_CONFIG = {
        "prompts": {
            "system": "You are a helpful chatbot assistant."
        },
        "tools": [],
        "responses": {
            "media_not_supported": "I can't process media yet. Please describe what you need."
        }
    }

router = APIRouter()


@router.post("/gupshup/message/hc")
async def webhook_handler(data: Request, background_tasks: BackgroundTasks):
    """[BOILERPLATE] Gupshup webhook — fast return, background processing."""
    request_data = await data.json()
    logger.info("Webhook received", extra={"data": request_data})

    background_tasks.add_task(_process_message_bg, request_data)
    return Response(status_code=200)


async def _process_message_bg(request_data: dict):
    """[BOILERPLATE + CLIENT-SPECIFIC] Background message processing pipeline."""
    phone_number = ""
    try:
        # [BOILERPLATE] Parse
        gupshup_msg = extract_gupshup_message(request_data)
        if not gupshup_msg:
            logger.info("Invalid message format")
            return

        phone_number = gupshup_msg["from"]
        user_text = gupshup_msg["text"]
        user_name = gupshup_msg["name"]
        message_id = gupshup_msg["message_id"]

        # [BOILERPLATE] Duplicate check
        if not mark_message_processed(message_id, phone_number, user_text):
            logger.info("Duplicate message", extra={"phone": phone_number})
            return

        # [BOILERPLATE] Media check
        if is_media_only(user_text):
            dispatch_whatsapp(
                phone_number,
                [{"type": "text", "text": CLIENT_CONFIG["responses"]["media_not_supported"]}],
            )
            return

        # [BOILERPLATE] Get or create session
        session = get_or_create_session(phone_number, user_name)
        save_message_to_history(phone_number, "user", user_text)

        # [CLIENT-SPECIFIC] Route message and get response
        bot_response = await _route_message(
            user_text, phone_number, session.get("chat_history", [])
        )

        # [BOILERPLATE] Save + send
        save_message_to_history(phone_number, "assistant", bot_response)
        responses = _build_responses(bot_response)
        dispatch_whatsapp(phone_number, responses)

    except Exception as e:
        logger.exception(
            "Message processing failed",
            extra={"phone": phone_number, "error": str(e)},
        )
        if phone_number:
            dispatch_whatsapp(
                phone_number,
                [{"type": "text", "text": "Unexpected error. Please try again."}],
            )


async def _route_message(user_text: str, session_id: str, chat_history: list) -> str:
    """[CLIENT-SPECIFIC] Route message based on configured intents.

    This is where you customize per client. Override with client-specific logic.
    """
    return await chat_agent(
        user_message=user_text,
        chat_history=chat_history,
        session_id=session_id,
        system_prompt=CLIENT_CONFIG["prompts"]["system"],
        tools=CLIENT_CONFIG["tools"],
    )


def _build_responses(text: str) -> list[dict]:
    """[BOILERPLATE] Convert text to WhatsApp message list.

    Args:
        text: Response text from LLM.

    Returns:
        List of message dicts for WhatsApp.
    """
    if not text:
        return [{"type": "text", "text": "Sorry, I couldn't generate a response."}]
    return [{"type": "text", "text": text}]
