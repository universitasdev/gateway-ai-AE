"""
WhatsApp Cloud API webhook endpoint.

Handles both:
  - GET  /webhook/whatsapp  → Meta verification (hub.challenge)
  - POST /webhook/whatsapp  → Incoming messages from users
"""

import logging

import httpx
from fastapi import APIRouter, HTTPException, Query, Request, Response
from fastapi.responses import PlainTextResponse

from app.core.config import get_settings
from app.services import agent_service

logger = logging.getLogger(__name__)

router = APIRouter(tags=["WhatsApp"])

GRAPH_API_BASE = "https://graph.facebook.com/v21.0"


# ── Verification (GET) ─────────────────────────────────────────

@router.get(
    "/webhook/whatsapp",
    response_class=PlainTextResponse,
    summary="WhatsApp webhook verification",
    description="Meta sends a GET with hub.challenge to verify the endpoint.",
)
async def verify_whatsapp_webhook(
    hub_mode: str | None = Query(None, alias="hub.mode"),
    hub_challenge: str | None = Query(None, alias="hub.challenge"),
    hub_verify_token: str | None = Query(None, alias="hub.verify_token"),
) -> str:
    """
    Return hub.challenge if the verify token matches.
    Meta calls this once when you register the webhook URL.
    """
    settings = get_settings()

    if hub_mode == "subscribe" and hub_verify_token == settings.whatsapp_verify_token:
        logger.info("WhatsApp webhook verified ✓")
        return hub_challenge or ""

    logger.warning("WhatsApp webhook verification failed — token mismatch")
    raise HTTPException(status_code=403, detail="Verification failed")


# ── Incoming messages (POST) ────────────────────────────────────

async def _send_whatsapp_message(
    to: str,
    text: str,
    http_client: httpx.AsyncClient,
) -> None:
    """Send a text reply via the WhatsApp Cloud API."""
    settings = get_settings()
    url = f"{GRAPH_API_BASE}/{settings.whatsapp_phone_number_id}/messages"

    headers = {
        "Authorization": f"Bearer {settings.whatsapp_access_token}",
        "Content-Type": "application/json",
    }

    payload = {
        "messaging_product": "whatsapp",
        "recipient_type": "individual",
        "to": to,
        "type": "text",
        "text": {"preview_url": False, "body": text},
    }

    resp = await http_client.post(url, json=payload, headers=headers)

    if resp.status_code != 200:
        logger.error(
            "WhatsApp sendMessage failed — status=%d body=%s",
            resp.status_code,
            resp.text,
        )


def _extract_message(body: dict) -> tuple[str, str] | None:
    """
    Parse the deeply-nested Meta webhook payload.

    Returns (phone_number, message_text) or None if the payload
    doesn't contain a user text message.
    """
    try:
        entry = body.get("entry", [])
        if not entry:
            return None

        changes = entry[0].get("changes", [])
        if not changes:
            return None

        value = changes[0].get("value", {})

        # Skip status updates (delivered, read, etc.)
        if "messages" not in value:
            return None

        messages = value["messages"]
        if not messages:
            return None

        msg = messages[0]

        # Only handle text messages for now
        if msg.get("type") != "text":
            return None

        phone = msg.get("from", "")
        text = msg.get("text", {}).get("body", "")

        if not phone or not text:
            return None

        return phone, text

    except (IndexError, KeyError, TypeError):
        logger.exception("Failed to parse WhatsApp webhook payload")
        return None


@router.post(
    "/webhook/whatsapp",
    summary="WhatsApp incoming messages",
    description="Receives messages from the Meta Cloud API webhook.",
)
async def whatsapp_webhook(request: Request) -> Response:
    """
    Process an incoming WhatsApp message.

    Returns 200 immediately — Meta will retry on non-2xx.
    """
    body = await request.json()

    extracted = _extract_message(body)
    if not extracted:
        # Status update or unsupported message type — acknowledge
        return Response(status_code=200)

    phone_number, user_text = extracted

    # ── Query the AI agent ──────────────────────────────────────
    try:
        agent_reply = agent_service.query_agent(
            message=user_text,
            session_id=phone_number,
        )
    except Exception:
        logger.exception(
            "Agent query failed for WhatsApp phone=%s", phone_number
        )
        agent_reply = "Lo siento, hubo un error procesando tu mensaje. Intenta de nuevo."

    # ── Send reply back via WhatsApp ────────────────────────────
    async with httpx.AsyncClient(timeout=30) as client:
        await _send_whatsapp_message(
            to=phone_number,
            text=agent_reply,
            http_client=client,
        )

    return Response(status_code=200)
