"""
Simplified PlaybookWiz FastAPI Application for demo purposes.
"""

import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Create FastAPI application
app = FastAPI(
    title="PlaybookWiz API",
    version="1.0.0",
    description="Intelligent brand playbook processing and analysis platform",
    docs_url="/docs",
    redoc_url="/redoc",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
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
        "status": "Demo version - simplified for quick start"
    }

# Demo endpoints
@app.get("/api/v1/health")
async def api_health():
    """API health check."""
    return {"status": "healthy", "service": "PlaybookWiz API"}

@app.post("/api/v1/auth/login")
async def demo_login():
    """Demo login endpoint."""
    return {
        "access_token": "demo-token-123",
        "token_type": "bearer",
        "expires_in": 3600,
        "message": "Demo login successful"
    }

@app.get("/api/v1/users/me")
async def demo_user():
    """Demo user endpoint."""
    return {
        "id": "demo-user-123",
        "email": "demo@playbookwiz.com",
        "name": "Demo User",
        "role": "brand_manager"
    }

@app.get("/api/v1/documents")
async def demo_documents():
    """Demo documents endpoint."""
    return {
        "documents": [],
        "message": "Document processing feature coming soon! Add your Anthropic API key to enable full functionality."
    }

@app.post("/api/v1/documents/upload")
async def demo_upload():
    """Demo upload endpoint."""
    return {
        "message": "Upload feature coming soon! This is a demo version.",
        "next_steps": [
            "Add your Anthropic API key to backend/.env",
            "Install additional dependencies",
            "Configure databases"
        ]
    }

@app.post("/api/v1/questions/ask")
async def demo_question():
    """Demo question endpoint."""
    return {
        "answer": "This is a demo response. To enable AI-powered question answering, please add your Anthropic API key to the backend/.env file.",
        "confidence": 1.0,
        "sources": [],
        "message": "Demo mode - full AI functionality requires API key configuration"
    }

@app.post("/api/v1/ideation/generate")
async def demo_ideation():
    """Demo ideation endpoint."""
    return {
        "ideas": [
            {
                "title": "Demo Creative Idea",
                "description": "This is a sample creative idea. Real AI-powered ideation will be available once you configure your Anthropic API key.",
                "persona": "demo",
                "brand_alignment_score": 0.9
            }
        ],
        "message": "Demo mode - full creative ideation requires API key configuration"
    }

if __name__ == "__main__":
    import uvicorn
    
    logger.info("Starting PlaybookWiz API in demo mode...")
    logger.info("To enable full functionality:")
    logger.info("1. Add ANTHROPIC_API_KEY to backend/.env")
    logger.info("2. Install remaining dependencies")
    logger.info("3. Configure databases")
    
    uvicorn.run(
        "simple_main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info",
    )
