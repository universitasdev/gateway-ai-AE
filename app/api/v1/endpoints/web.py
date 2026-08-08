"""
Web chat endpoint — generic REST API for browser / frontend clients.
"""

import logging

from fastapi import APIRouter, HTTPException

from app.schemas.messages import WebChatRequest, WebChatResponse
from app.services import agent_service

logger = logging.getLogger(__name__)

router = APIRouter(tags=["Web"])


@router.post(
    "/api/chat",
    response_model=WebChatResponse,
    summary="Send a message to the AI agent",
    description="Generic REST endpoint for web frontends.",
)
async def web_chat(payload: WebChatRequest) -> WebChatResponse:
    """
    Receive a JSON message from the web client, forward it to the
    Reasoning Engine, and return the agent's reply.
    """
    try:
        reply = agent_service.query_agent(
            message=payload.message,
            session_id=payload.session_id,
        )
        return WebChatResponse(response=reply, session_id=payload.session_id)

    except RuntimeError as exc:
        logger.error("Agent service error: %s", exc)
        raise HTTPException(status_code=503, detail="AI agent unavailable") from exc

    except Exception as exc:
        logger.exception("Unexpected error in /api/chat")
        raise HTTPException(
            status_code=500,
            detail="Internal server error",
        ) from exc
