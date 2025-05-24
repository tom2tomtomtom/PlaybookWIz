"""
Health check endpoints.
"""

from fastapi import APIRouter

router = APIRouter()


@router.get("/")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": "PlaybookWiz API",
        "version": "1.0.0"
    }


@router.get("/detailed")
async def detailed_health_check():
    """Detailed health check with service status."""
    return {
        "status": "healthy",
        "service": "PlaybookWiz API",
        "version": "1.0.0",
        "components": {
            "api": "healthy",
            "database": "not_configured",
            "ai_service": "not_configured"
        }
    }
