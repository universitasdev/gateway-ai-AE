"""
Pydantic schemas for request / response validation across all channels.
"""

from pydantic import BaseModel, Field


# ── Web Chat ────────────────────────────────────────────────────

class WebChatRequest(BaseModel):
    """Payload sent by the web frontend."""

    message: str = Field(..., min_length=1, max_length=4096, description="User message text")
    session_id: str = Field(..., min_length=1, max_length=128, description="Client-generated session identifier")


class WebChatResponse(BaseModel):
    """Response returned to the web frontend."""

    response: str = Field(..., description="Agent reply text")
    session_id: str = Field(..., description="Echo of the session identifier")


# ── Health Check ────────────────────────────────────────────────

class HealthResponse(BaseModel):
    """Simple health-check payload."""

    status: str = "ok"
    service: str = "gateway"
