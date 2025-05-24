"""
PlaybookWiz FastAPI Application

Main application entry point for the Brand Playbook Intelligence API.
"""

import logging
import time
from contextlib import asynccontextmanager
from typing import Any

from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api.api_v1.api import api_router

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    # Startup
    logger.info("Starting up PlaybookWiz API...")
    logger.info("PlaybookWiz API startup complete")

    yield

    # Shutdown
    logger.info("Shutting down PlaybookWiz API...")
    logger.info("PlaybookWiz API shutdown complete")


# Create FastAPI application
app = FastAPI(
    title="PlaybookWiz API",
    version="1.0.0",
    description="Intelligent brand playbook processing and analysis platform",
    openapi_url="/api/v1/openapi.json",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)


@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    """Add processing time header to responses."""
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    return response


@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Log all requests for monitoring."""
    start_time = time.time()

    # Log request
    logger.info(
        "Request started",
        extra={
            "method": request.method,
            "url": str(request.url),
            "client_ip": request.client.host if request.client else None,
            "user_agent": request.headers.get("user-agent"),
        }
    )

    response = await call_next(request)

    # Log response
    process_time = time.time() - start_time
    logger.info(
        "Request completed",
        extra={
            "method": request.method,
            "url": str(request.url),
            "status_code": response.status_code,
            "process_time": process_time,
        }
    )

    return response


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler."""
    logger.error(
        "Unhandled exception",
        extra={
            "method": request.method,
            "url": str(request.url),
            "error": str(exc),
        },
        exc_info=True,
    )

    return JSONResponse(
        status_code=500,
        content={
            "detail": "Internal server error",
            "error_id": getattr(exc, "error_id", None),
        },
    )


# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "app_name": "PlaybookWiz API",
        "version": "1.0.0",
        "environment": "development",
    }


# Root endpoint
@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "Welcome to PlaybookWiz API",
        "version": "1.0.0",
        "docs": "/docs",
    }


# Include API router
app.include_router(api_router, prefix="/api/v1")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info",
    )
