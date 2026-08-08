"""
Telegram Bot webhook endpoint.

Receives Update objects from the Telegram Bot API, extracts the
user message, queries the Reasoning Engine, and sends the reply
back via the sendMessage API.
"""

import logging

import httpx
from fastapi import APIRouter, Request, Response

from app.core.config import get_settings
from app.services import agent_service

logger = logging.getLogger(__name__)

router = APIRouter(tags=["Telegram"])

TELEGRAM_API_BASE = "https://api.telegram.org"


async def _send_telegram_message(
    chat_id: int | str,
    text: str,
    http_client: httpx.AsyncClient,
) -> None:
    """Send a text message to a Telegram chat."""
    settings = get_settings()
    url = f"{TELEGRAM_API_BASE}/bot{settings.telegram_bot_token}/sendMessage"

    payload = {
        "chat_id": chat_id,
        "text": text,
        "parse_mode": "Markdown",
    }

    resp = await http_client.post(url, json=payload)

    if resp.status_code != 200:
        logger.error(
            "Telegram sendMessage failed — status=%d body=%s",
            resp.status_code,
            resp.text,
        )


@router.post(
    "/webhook/telegram",
    summary="Telegram Bot webhook",
    description="Receives Telegram Update objects and replies via Bot API.",
)
async def telegram_webhook(request: Request) -> Response:
    """
    Process an incoming Telegram update.

    Returns 200 immediately to prevent Telegram from retrying.
    """
    body = await request.json()

    # Telegram sends many update types; we only care about text messages.
    message = body.get("message")
    if not message:
        return Response(status_code=200)

    text = message.get("text", "")
    chat = message.get("chat", {})
    chat_id = chat.get("id")

    if not text or not chat_id:
        return Response(status_code=200)

    # Skip bot commands like /start for now (can be extended later)
    if text.startswith("/start"):
        async with httpx.AsyncClient(timeout=30) as client:
            await _send_telegram_message(
                chat_id=chat_id,
                text="¡Hola! Soy tu asistente de IA. Envíame tu consulta y te responderé.",
                http_client=client,
            )
        return Response(status_code=200)

    # ── Query the AI agent ──────────────────────────────────────
    try:
        session_id = str(chat_id)
        agent_reply = agent_service.query_agent(
            message=text,
            session_id=session_id,
        )
    except Exception:
        logger.exception("Agent query failed for Telegram chat_id=%s", chat_id)
        agent_reply = "Lo siento, hubo un error procesando tu mensaje. Intenta de nuevo."

    # ── Send reply back to Telegram ─────────────────────────────
    async with httpx.AsyncClient(timeout=30) as client:
        await _send_telegram_message(
            chat_id=chat_id,
            text=agent_reply,
            http_client=client,
        )

    return Response(status_code=200)
