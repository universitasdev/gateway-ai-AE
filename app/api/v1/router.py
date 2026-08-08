"""
V1 API router — aggregates all endpoint sub-routers.
"""

from fastapi import APIRouter

from app.api.v1.endpoints import telegram, web, whatsapp

router = APIRouter()

router.include_router(web.router)
router.include_router(telegram.router)
router.include_router(whatsapp.router)
