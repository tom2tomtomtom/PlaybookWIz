"""
Health check endpoints.
"""

import asyncio
import time
from typing import Dict, Any

from fastapi import APIRouter, HTTPException, status
from sqlalchemy import text

from app.core.config import settings
from app.core.database import engine, mongodb, redis_db

router = APIRouter()


async def check_postgres() -> Dict[str, Any]:
    """Check PostgreSQL database connectivity."""
    try:
        start_time = time.time()
        async with engine.begin() as conn:
            await conn.execute(text("SELECT 1"))
        response_time = time.time() - start_time
        return {
            "status": "healthy",
            "response_time_ms": round(response_time * 1000, 2)
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e)
        }


async def check_mongodb() -> Dict[str, Any]:
    """Check MongoDB connectivity."""
    try:
        start_time = time.time()
        if not mongodb.client:
            await mongodb.connect()
        await mongodb.client.admin.command('ping')
        response_time = time.time() - start_time
        return {
            "status": "healthy",
            "response_time_ms": round(response_time * 1000, 2)
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e)
        }


async def check_redis() -> Dict[str, Any]:
    """Check Redis connectivity."""
    try:
        start_time = time.time()
        if not redis_db.redis:
            await redis_db.connect()
        await redis_db.redis.ping()
        response_time = time.time() - start_time
        return {
            "status": "healthy",
            "response_time_ms": round(response_time * 1000, 2)
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e)
        }


async def check_anthropic() -> Dict[str, Any]:
    """Check Anthropic API connectivity."""
    try:
        if not settings.ANTHROPIC_API_KEY:
            return {
                "status": "not_configured",
                "error": "API key not configured"
            }

        # For production health checks, we'll just verify the API key is set
        # and return a simple status without making actual API calls
        # to avoid unnecessary costs and rate limiting
        return {
            "status": "configured",
            "model": settings.ANTHROPIC_MODEL,
            "note": "API key configured, actual connectivity not tested in health check"
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e)
        }


@router.get("/")
async def health_check():
    """Basic health check endpoint."""
    return {
        "status": "healthy",
        "service": "PlaybookWiz API",
        "version": settings.APP_VERSION,
        "environment": settings.ENVIRONMENT,
        "timestamp": time.time()
    }


@router.get("/detailed")
async def detailed_health_check():
    """Detailed health check with service status."""
    start_time = time.time()

    # Run all health checks concurrently
    postgres_check, mongodb_check, redis_check, anthropic_check = await asyncio.gather(
        check_postgres(),
        check_mongodb(),
        check_redis(),
        check_anthropic(),
        return_exceptions=True
    )

    # Handle exceptions from gather
    def safe_result(result):
        if isinstance(result, Exception):
            return {"status": "unhealthy", "error": str(result)}
        return result

    postgres_status = safe_result(postgres_check)
    mongodb_status = safe_result(mongodb_check)
    redis_status = safe_result(redis_check)
    anthropic_status = safe_result(anthropic_check)

    # Determine overall status
    all_healthy = all(
        component["status"] == "healthy"
        for component in [postgres_status, mongodb_status, redis_status]
    )

    overall_status = "healthy" if all_healthy else "degraded"

    # If critical services are down, mark as unhealthy
    critical_services = [postgres_status, redis_status]
    if any(service["status"] == "unhealthy" for service in critical_services):
        overall_status = "unhealthy"

    total_time = time.time() - start_time

    result = {
        "status": overall_status,
        "service": "PlaybookWiz API",
        "version": settings.APP_VERSION,
        "environment": settings.ENVIRONMENT,
        "timestamp": time.time(),
        "response_time_ms": round(total_time * 1000, 2),
        "components": {
            "api": {"status": "healthy"},
            "postgres": postgres_status,
            "mongodb": mongodb_status,
            "redis": redis_status,
            "anthropic": anthropic_status
        }
    }

    # Return appropriate HTTP status code
    if overall_status == "unhealthy":
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=result
        )

    return result


@router.get("/readiness")
async def readiness_check():
    """Kubernetes readiness probe endpoint."""
    try:
        # Check critical services only
        postgres_check, redis_check = await asyncio.gather(
            check_postgres(),
            check_redis(),
            return_exceptions=True
        )

        def safe_result(result):
            if isinstance(result, Exception):
                return {"status": "unhealthy", "error": str(result)}
            return result

        postgres_status = safe_result(postgres_check)
        redis_status = safe_result(redis_check)

        if postgres_status["status"] != "healthy" or redis_status["status"] != "healthy":
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail={
                    "status": "not_ready",
                    "postgres": postgres_status,
                    "redis": redis_status
                }
            )

        return {
            "status": "ready",
            "postgres": postgres_status,
            "redis": redis_status
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail={
                "status": "not_ready",
                "error": str(e)
            }
        )


@router.get("/liveness")
async def liveness_check():
    """Kubernetes liveness probe endpoint."""
    return {
        "status": "alive",
        "service": "PlaybookWiz API",
        "timestamp": time.time()
    }
