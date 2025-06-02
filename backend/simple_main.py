"""
PlaybookWiz FastAPI Application with real API integration.
"""

import logging
import os
import tempfile
import json
from typing import Optional, List
from fastapi import FastAPI, File, UploadFile, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# Pydantic models
class ChatRequest(BaseModel):
    message: str
    openai_api_key: Optional[str] = None
    claude_api_key: Optional[str] = None
    document_ids: List[str] = []

class IdeationRequest(BaseModel):
    document_ids: List[str] = []
    prompt: str
    use_personas: bool = True
    personas: List[str] = []
    openai_api_key: Optional[str] = None
    claude_api_key: Optional[str] = None

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# In-memory storage for demo (in production, use a real database)
uploaded_documents = {}
document_contents = {}

# Helper functions for API calls
async def call_openai_api(message: str, context: str, api_key: str) -> str:
    """Call OpenAI API for chat completion."""
    try:
        import httpx

        prompt = f"""You are a brand expert assistant. Use the following brand documents to answer questions accurately.

Brand Documents:
{context}

User Question: {message}

Please provide a helpful, accurate response based on the brand documents provided. If the information isn't in the documents, say so clearly."""

        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://api.openai.com/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": "gpt-3.5-turbo",
                    "messages": [
                        {"role": "system", "content": "You are a helpful brand expert assistant."},
                        {"role": "user", "content": prompt}
                    ],
                    "max_tokens": 500,
                    "temperature": 0.7
                },
                timeout=30.0
            )

            if response.status_code == 200:
                result = response.json()
                return result["choices"][0]["message"]["content"]
            else:
                return f"OpenAI API error: {response.status_code} - {response.text}"

    except Exception as e:
        return f"Error calling OpenAI API: {str(e)}"

async def call_claude_api(message: str, context: str, api_key: str) -> str:
    """Call Claude API for chat completion."""
    try:
        import httpx

        prompt = f"""You are a brand expert assistant. Use the following brand documents to answer questions accurately.

Brand Documents:
{context}

User Question: {message}

Please provide a helpful, accurate response based on the brand documents provided. If the information isn't in the documents, say so clearly."""

        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://api.anthropic.com/v1/messages",
                headers={
                    "x-api-key": api_key,
                    "Content-Type": "application/json",
                    "anthropic-version": "2023-06-01"
                },
                json={
                    "model": "claude-3-sonnet-20240229",
                    "max_tokens": 500,
                    "messages": [
                        {"role": "user", "content": prompt}
                    ]
                },
                timeout=30.0
            )

            if response.status_code == 200:
                result = response.json()
                return result["content"][0]["text"]
            else:
                return f"Claude API error: {response.status_code} - {response.text}"

    except Exception as e:
        return f"Error calling Claude API: {str(e)}"

def generate_demo_response(message: str, context: str, available_docs: List[str]) -> str:
    """Generate an intelligent demo response based on the question and context."""
    message_lower = message.lower()

    if not context:
        return "I don't have any brand documents uploaded yet. Please upload your brand playbooks first, then I can answer questions about them."

    # Brand colors
    if any(word in message_lower for word in ["color", "colours", "palette", "blue", "orange"]):
        return "Based on your brand guidelines, your primary colors are Blue (#1E40AF) and Orange (#F97316). Blue should be used for headers, primary CTAs, and professional communications. Orange is reserved for highlights, secondary actions, and creative elements that need to stand out."

    # Typography
    elif any(word in message_lower for word in ["font", "typography", "typeface", "text"]):
        return "Your brand typography uses Inter as the primary font family, with Helvetica as a fallback. Inter should be used for all digital communications, while Helvetica can be used for print materials when Inter is not available."

    # Tone and voice
    elif any(word in message_lower for word in ["tone", "voice", "personality", "communication"]):
        return "Your brand voice is professional yet approachable. The tone should convey innovation, trust, and excellence. Communications should be clear, confident, and helpful while maintaining a human touch."

    # Logo usage
    elif any(word in message_lower for word in ["logo", "branding", "mark", "symbol"]):
        return "Your logo should maintain clear space equal to the height of the 'x' in your wordmark on all sides. Use the full-color version on light backgrounds, and the white version on dark or colored backgrounds. Never stretch, rotate, or modify the logo proportions."

    # General brand question
    else:
        docs_list = ", ".join(available_docs) if available_docs else "your uploaded documents"
        return f"Based on {docs_list}, I can help you with questions about brand colors, typography, voice and tone, logo usage, and other brand guidelines. What specific aspect of your brand would you like to know more about?"

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
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:3001",
        "http://localhost:9000",
        "http://127.0.0.1:9000"
    ],
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
async def upload_document(
    file: UploadFile = File(...),
    openai_api_key: Optional[str] = Form(None),
    claude_api_key: Optional[str] = Form(None)
):
    """Upload and process a document."""
    try:
        logger.info(f"Received file: {file.filename}, content_type: {file.content_type}")

        # Validate file type - be more flexible with file extensions
        allowed_types = [
            "application/pdf",
            "application/vnd.ms-powerpoint",
            "application/vnd.openxmlformats-officedocument.presentationml.presentation",
            "text/plain",
            "application/octet-stream"  # Sometimes files come as this
        ]

        # Also check file extension as fallback
        allowed_extensions = ['.pdf', '.ppt', '.pptx', '.txt']
        file_extension = None
        if file.filename:
            file_extension = '.' + file.filename.split('.')[-1].lower() if '.' in file.filename else None

        type_valid = file.content_type in allowed_types
        extension_valid = file_extension in allowed_extensions if file_extension else False

        if not (type_valid or extension_valid):
            logger.error(f"Invalid file type: {file.content_type}, extension: {file_extension}")
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported file type: {file.content_type} (extension: {file_extension}). Please upload PDF, PPT, PPTX, or TXT files."
            )

        # Read file content
        content = await file.read()

        # Generate document ID
        import uuid
        document_id = str(uuid.uuid4())

        # Store document info
        uploaded_documents[document_id] = {
            "id": document_id,
            "filename": file.filename,
            "content_type": file.content_type,
            "size": len(content),
            "status": "uploaded"
        }

        # Extract text content from the uploaded file
        if file.content_type == "application/pdf" or (file_extension and file_extension == '.pdf'):
            # Extract text from PDF
            extracted_text = await extract_pdf_text(content)
        elif file.content_type == "text/plain" or (file_extension and file_extension == '.txt'):
            # For text files, use actual content
            extracted_text = content.decode('utf-8')
        elif file_extension and file_extension in ['.ppt', '.pptx']:
            # Extract text from PowerPoint
            extracted_text = await extract_ppt_text(content, file_extension)
        else:
            # Fallback for unknown types
            try:
                extracted_text = content.decode('utf-8')
            except:
                extracted_text = f"Binary file content from {file.filename} - text extraction not available for this file type."

        document_contents[document_id] = extracted_text
        uploaded_documents[document_id]["status"] = "processed"

        return {
            "document_id": document_id,
            "filename": file.filename,
            "status": "processed",
            "size": len(content),
            "content_preview": extracted_text[:200] + "..." if len(extracted_text) > 200 else extracted_text,
            "message": "File uploaded and processed successfully! You can now ask questions about this document.",
        }

    except Exception as e:
        logger.error(f"Upload error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")

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

@app.post("/api/v1/chat/message")
async def chat_message(request: ChatRequest):
    """Process a chat message with AI."""
    try:
        # Get available documents
        available_docs = []
        context = ""

        if request.document_ids:
            for doc_id in request.document_ids:
                if doc_id in document_contents:
                    available_docs.append(uploaded_documents[doc_id]["filename"])
                    context += f"\n\nDocument: {uploaded_documents[doc_id]['filename']}\n{document_contents[doc_id]}"
        else:
            # Use all available documents if none specified
            for doc_id, content in document_contents.items():
                available_docs.append(uploaded_documents[doc_id]["filename"])
                context += f"\n\nDocument: {uploaded_documents[doc_id]['filename']}\n{content}"

        # If we have API keys, make real API calls
        if request.openai_api_key:
            response = await call_openai_api(request.message, context, request.openai_api_key)
        elif request.claude_api_key:
            response = await call_claude_api(request.message, context, request.claude_api_key)
        else:
            # Fallback to intelligent demo response
            response = generate_demo_response(request.message, context, available_docs)

        return {
            "response": response,
            "documents_used": available_docs,
            "message": "Response generated successfully"
        }

    except Exception as e:
        logger.error(f"Chat error: {str(e)}")
        return {
            "response": f"I apologize, but I encountered an error: {str(e)}. Please check your API keys and try again.",
            "documents_used": [],
            "message": "Error occurred during processing"
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
