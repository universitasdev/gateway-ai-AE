"""
Web chat endpoint — generic REST API for browser / frontend clients.
Analytics 360: message_id, user_context logging, feedback endpoint.
"""

import logging
import time
import uuid

from fastapi import APIRouter, HTTPException

from app.schemas.messages import (
    FeedbackRequest,
    FeedbackResponse,
    TokenUsage,
    WebChatRequest,
    WebChatResponse,
)
from app.services import agent_service
from app.services.analytics_log import log_chat_event, log_feedback_event

logger = logging.getLogger(__name__)

router = APIRouter(tags=["Web"])


@router.post(
    "/api/chat",
    response_model=WebChatResponse,
    summary="Send a message to the AI agent",
    description="Generic REST endpoint for web frontends (WP Tutor IA).",
)
async def web_chat(payload: WebChatRequest) -> WebChatResponse:
    """
    Receive a JSON message from the web client, forward it to the
    Reasoning Engine, and return the agent's reply with message_id.
    """
    message_id = str(uuid.uuid4())
    started = time.perf_counter()

    try:
        reply = agent_service.query_agent(
            message=payload.message,
            session_id=payload.session_id,
        )
        latency_ms = int((time.perf_counter() - started) * 1000)

        usage_model = None
        usage_dict = reply.usage
        if usage_dict:
            usage_model = TokenUsage(**usage_dict)

        ctx_dict = None
        if payload.user_context is not None:
            ctx_dict = payload.user_context.model_dump()

        log_chat_event(
            message_id=message_id,
            session_id=payload.session_id,
            question=payload.message,
            answer=reply.text,
            user_context=ctx_dict,
            usage=usage_dict,
            latency_ms=latency_ms,
            model=None,
        )

        return WebChatResponse(
            response=reply.text,
            session_id=payload.session_id,
            message_id=message_id,
            usage=usage_model,
        )

    except RuntimeError as exc:
        logger.error("Agent service error: %s", exc)
        raise HTTPException(status_code=503, detail="AI agent unavailable") from exc

    except Exception as exc:
        logger.exception("Unexpected error in /api/chat")
        raise HTTPException(
            status_code=500,
            detail="Internal server error",
        ) from exc


@router.post(
    "/api/feedback",
    response_model=FeedbackResponse,
    summary="Submit thumbs up/down for a bot message",
    description="Analytics 360 feedback event (correlated by message_id).",
)
async def web_feedback(payload: FeedbackRequest) -> FeedbackResponse:
    """Record a feedback event via structured logging (sink → BigQuery later)."""
    try:
        log_feedback_event(
            message_id=payload.message_id,
            session_id=payload.session_id,
            feedback_score=payload.feedback_score,
            user_id=payload.user_id,
        )
        return FeedbackResponse(ok=True, message_id=payload.message_id)
    except Exception as exc:
        logger.exception("Unexpected error in /api/feedback")
        raise HTTPException(
            status_code=500,
            detail="Internal server error",
        ) from exc
