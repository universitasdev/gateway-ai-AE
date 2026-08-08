"""
Gateway Actas de Entrega — FastAPI application entry point.

Connects WhatsApp, Telegram, and Web clients to a Vertex AI
Reasoning Engine (Agent Runtime) deployed on Google Cloud.
"""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.router import router as v1_router
from app.core.config import get_settings
from app.schemas.messages import HealthResponse
from app.services import agent_service

# ── Logging ─────────────────────────────────────────────────────

settings = get_settings()

logging.basicConfig(
    level=getattr(logging, settings.log_level.upper(), logging.INFO),
    format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

logger = logging.getLogger(__name__)


# ── Lifespan ────────────────────────────────────────────────────

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup / shutdown lifecycle hook."""
    logger.info("🚀 Starting Gateway Actas de Entrega…")
    agent_service.init()
    logger.info("✅ Gateway ready — all services initialised")
    yield
    logger.info("🛑 Shutting down Gateway Actas de Entrega…")


# ── App ─────────────────────────────────────────────────────────

app = FastAPI(
    title="Gateway Actas de Entrega",

    description=(
        "BFF que conecta WhatsApp, Telegram y Web "
        "con un Agente de IA en Vertex AI Agent Runtime."
    ),
    version="1.0.0",
    lifespan=lifespan,
)

# CORS — allow web frontends to call the API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Lock down in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Routes ──────────────────────────────────────────────────────

app.include_router(v1_router)


@app.get(
    "/health",
    response_model=HealthResponse,
    tags=["Infrastructure"],
    summary="Health check",
)
async def health_check() -> HealthResponse:
    """Return a simple health check response."""
    return HealthResponse()
