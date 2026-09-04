"""
Pydantic schemas for request / response validation across all channels.
"""

from typing import Literal, Optional

from pydantic import BaseModel, Field


# ── Analytics 360 / Web Chat ─────────────────────────────────────


class UserContext(BaseModel):
    """LearnDash / WordPress context (built server-side in WP)."""

    user_id: Optional[int] = None
    display_name: Optional[str] = None
    course_id: Optional[int] = None
    course_title: Optional[str] = None
    post_id: Optional[int] = None
    post_type: Optional[str] = None
    post_title: Optional[str] = None
    lesson_id: Optional[int] = None
    topic_id: Optional[int] = None
    quiz_id: Optional[int] = None


class TokenUsage(BaseModel):
    """Token counts from the model (cost is computed later in BigQuery)."""

    input_tokens: Optional[int] = None
    output_tokens: Optional[int] = None
    total_tokens: Optional[int] = None


class WebChatRequest(BaseModel):
    """Payload sent by the web frontend (WP pasarela)."""

    message: str = Field(..., min_length=1, max_length=4096, description="User message text")
    session_id: str = Field(
        ..., min_length=1, max_length=128, description="Client-generated session identifier"
    )
    event_type: Literal["chat"] = Field(
        default="chat", description="Analytics event type (chat)"
    )
    user_context: Optional[UserContext] = Field(
        default=None, description="WP/LearnDash context for analytics"
    )


class WebChatResponse(BaseModel):
    """Response returned to the web frontend."""

    response: str = Field(..., description="Agent reply text")
    session_id: str = Field(..., description="Echo of the session identifier")
    message_id: str = Field(..., description="UUID of this turn (for feedback correlation)")
    usage: Optional[TokenUsage] = Field(
        default=None, description="Token usage when available from the agent"
    )


class FeedbackRequest(BaseModel):
    """Thumb up/down for a previous bot message."""

    event_type: Literal["feedback"] = Field(default="feedback")
    message_id: str = Field(..., min_length=1, max_length=128)
    session_id: str = Field(..., min_length=1, max_length=128)
    feedback_score: Literal[1, -1] = Field(..., description="1 = thumbs up, -1 = thumbs down")
    user_id: Optional[int] = None


class FeedbackResponse(BaseModel):
    ok: bool = True
    message_id: str


# ── Health Check ────────────────────────────────────────────────

class HealthResponse(BaseModel):
    """Simple health-check payload."""

    status: str = "ok"
    service: str = "gateway"
