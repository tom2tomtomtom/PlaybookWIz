"""
API v1 router configuration.

This module defines all API routes for version 1 of the PlaybookWiz API.
"""

from fastapi import APIRouter

from app.api.api_v1.endpoints import (
    auth,
    documents,
    questions,
    ideation,
    analysis,
    users,
    health,
)

api_router = APIRouter()

# Include all endpoint routers
api_router.include_router(health.router, prefix="/health", tags=["health"])
api_router.include_router(auth.router, prefix="/auth", tags=["authentication"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(documents.router, prefix="/documents", tags=["documents"])
api_router.include_router(questions.router, prefix="/questions", tags=["questions"])
api_router.include_router(ideation.router, prefix="/ideation", tags=["ideation"])
api_router.include_router(analysis.router, prefix="/analysis", tags=["analysis"])
