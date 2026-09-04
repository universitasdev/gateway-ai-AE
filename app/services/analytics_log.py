"""
Structured JSON logging for Tutor Analytics 360.

Cloud Logging / Log Router can sink these lines into BigQuery.
One log line per chat turn or feedback event — never the full history.
Cost (USD) is NOT computed here; only tokens when available.
"""

from __future__ import annotations

import json
import logging
from datetime import datetime, timezone
from typing import Any, Dict, Optional

logger = logging.getLogger("tutor.analytics")


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def log_chat_event(
    *,
    message_id: str,
    session_id: str,
    question: str,
    answer: str,
    user_context: Optional[Dict[str, Any]] = None,
    usage: Optional[Dict[str, Any]] = None,
    latency_ms: Optional[int] = None,
    model: Optional[str] = None,
) -> None:
    ctx = user_context or {}
    payload = {
        "event_type": "chat",
        "timestamp": _utc_now_iso(),
        "message_id": message_id,
        "session_id": session_id,
        "user_id": ctx.get("user_id"),
        "display_name": ctx.get("display_name"),
        "course_id": ctx.get("course_id"),
        "course_title": ctx.get("course_title"),
        "post_id": ctx.get("post_id"),
        "post_type": ctx.get("post_type"),
        "post_title": ctx.get("post_title"),
        "lesson_id": ctx.get("lesson_id"),
        "topic_id": ctx.get("topic_id"),
        "quiz_id": ctx.get("quiz_id"),
        "question": question,
        "answer": answer,
        "usage": usage,
        "latency_ms": latency_ms,
        "model": model,
    }
    logger.info(json.dumps(payload, ensure_ascii=False, default=str))


def log_feedback_event(
    *,
    message_id: str,
    session_id: str,
    feedback_score: int,
    user_id: Optional[int] = None,
) -> None:
    payload = {
        "event_type": "feedback",
        "timestamp": _utc_now_iso(),
        "message_id": message_id,
        "session_id": session_id,
        "user_id": user_id,
        "feedback_score": feedback_score,
    }
    logger.info(json.dumps(payload, ensure_ascii=False, default=str))
