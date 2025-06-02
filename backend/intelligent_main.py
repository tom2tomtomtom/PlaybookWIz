"""
PlaybookWiz Intelligent Production API
Complete Brand Playbook Intelligence with Vector Search and Source Attribution
"""

import logging
import os
import uuid
import asyncio
from typing import Optional, List
from fastapi import FastAPI, File, UploadFile, Form, HTTPException, Depends, Header, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from dotenv import load_dotenv
from supabase import create_client, Client
from cryptography.fernet import Fernet
import base64

# Import our intelligence engine
from intelligence_engine import intelligence_engine, IntelligentResponse, SearchResult

# Load environment variables
load_dotenv()

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Supabase client
supabase: Client = create_client(
    os.getenv("SUPABASE_URL"),
    os.getenv("SUPABASE_SERVICE_KEY")
)

# Encryption for API keys
encryption_key = os.getenv("ENCRYPTION_KEY", "playbookwiz-32char-encryption-key")
fernet_key = base64.urlsafe_b64encode(encryption_key.encode().ljust(32, b'0')[:32])
cipher_suite = Fernet(fernet_key)

# Pydantic models
class IntelligentChatRequest(BaseModel):
    message: str
    session_id: Optional[str] = None
    document_ids: List[str] = []

class APIKeyRequest(BaseModel):
    provider: str  # 'openai' or 'claude'
    api_key: str

class AdminAPIKeyRequest(BaseModel):
    user_email: str
    provider: str  # 'openai' or 'claude'
    api_key: str
    admin_secret: str

class DocumentSearchRequest(BaseModel):
    query: str
    document_ids: List[str] = []
    max_results: int = 5

# FastAPI app
app = FastAPI(
    title="PlaybookWiz Intelligence API",
    description="AI-powered brand playbook analysis with vector search and source attribution",
    version="2.0.0"
)

# CORS
allowed_origins = ["http://localhost:9000", "http://localhost:3000", "http://127.0.0.1:9000", "http://127.0.0.1:3000"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# Security
security = HTTPBearer()

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Verify JWT token and get current user"""
    try:
        logger.info(f"Authenticating user with token: {credentials.credentials[:20]}...")
        user = supabase.auth.get_user(credentials.credentials)
        if not user.user:
            logger.error("No user found in token")
            raise HTTPException(status_code=401, detail="Invalid token")
        logger.info(f"User authenticated: {user.user.id}")
        return user.user
    except Exception as e:
        logger.error(f"Auth error: {e}")
        raise HTTPException(status_code=401, detail="Authentication failed")

async def get_user_api_keys(user_id: str) -> dict:
    """Get encrypted API keys for user"""
    try:
        result = supabase.table("user_api_keys").select("*").eq("user_id", user_id).execute()
        keys = {}
        for row in result.data:
            try:
                decrypted_key = cipher_suite.decrypt(row["encrypted_key"].encode()).decode()
                keys[row["provider"]] = decrypted_key
            except Exception as e:
                logger.error(f"Decryption error for {row['provider']}: {e}")
        return keys
    except Exception as e:
        logger.error(f"Error getting API keys: {e}")
        return {}

# OPTIONS handlers for CORS
@app.options("/api/v1/auth/api-keys")
async def options_api_keys():
    return Response(
        content="",
        headers={
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "POST, OPTIONS",
            "Access-Control-Allow-Headers": "*",
        }
    )

@app.options("/api/v1/documents/upload")
async def options_upload():
    return Response(
        content="",
        headers={
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "POST, OPTIONS",
            "Access-Control-Allow-Headers": "*",
        }
    )

@app.options("/api/v1/chat/intelligent")
async def options_chat():
    return Response(
        content="",
        headers={
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "POST, OPTIONS",
            "Access-Control-Allow-Headers": "*",
        }
    )

@app.options("/api/v1/search/passages")
async def options_search():
    return Response(
        content="",
        headers={
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "POST, OPTIONS",
            "Access-Control-Allow-Headers": "*",
        }
    )

# API Routes
@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "PlaybookWiz Intelligence API", "version": "2.0.0"}

@app.post("/api/v1/auth/api-keys")
async def save_api_key(request: APIKeyRequest, user = Depends(get_current_user)):
    """Save encrypted API key for user"""
    try:
        logger.info(f"Saving API key for user {user.id}, provider: {request.provider}")
        encrypted_key = cipher_suite.encrypt(request.api_key.encode()).decode()

        # Upsert API key
        result = supabase.table("user_api_keys").upsert({
            "user_id": user.id,
            "provider": request.provider,
            "encrypted_key": encrypted_key
        }, on_conflict="user_id,provider").execute()

        logger.info(f"API key saved successfully")
        return {"message": f"{request.provider} API key saved successfully"}
    except Exception as e:
        logger.error(f"Error saving API key: {e}")
        raise HTTPException(status_code=500, detail="Failed to save API key")

@app.post("/api/v1/admin/save-user-api-key")
async def admin_save_user_api_key(request: AdminAPIKeyRequest):
    """Admin endpoint to save API key for a user by email"""
    try:
        # Verify admin secret
        admin_secret = os.getenv("ADMIN_SECRET", "playbookwiz-admin-secret-2024")
        if request.admin_secret != admin_secret:
            raise HTTPException(status_code=403, detail="Invalid admin secret")

        # Find user by email
        user_result = supabase.auth.admin.list_users()
        target_user = None
        for user in user_result:
            if user.email == request.user_email:
                target_user = user
                break

        if not target_user:
            raise HTTPException(status_code=404, detail=f"User with email {request.user_email} not found")

        logger.info(f"Admin saving API key for user {target_user.id} ({request.user_email}), provider: {request.provider}")
        encrypted_key = cipher_suite.encrypt(request.api_key.encode()).decode()

        # Upsert API key
        result = supabase.table("user_api_keys").upsert({
            "user_id": target_user.id,
            "provider": request.provider,
            "encrypted_key": encrypted_key
        }, on_conflict="user_id,provider").execute()

        logger.info(f"Admin API key saved successfully for {request.user_email}")
        return {
            "message": f"{request.provider} API key saved successfully for {request.user_email}",
            "user_id": target_user.id
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error saving admin API key: {e}")
        raise HTTPException(status_code=500, detail="Failed to save API key")

@app.post("/api/v1/documents/upload")
async def upload_document(
    file: UploadFile = File(...),
    user = Depends(get_current_user)
):
    """Upload and process document with intelligent chunking"""
    try:
        # Validate file
        allowed_types = [
            "application/pdf", 
            "application/vnd.ms-powerpoint", 
            "application/vnd.openxmlformats-officedocument.presentationml.presentation",
            "application/octet-stream"
        ]
        allowed_extensions = ['.pdf', '.ppt', '.pptx']
        
        file_extension = '.' + file.filename.split('.')[-1].lower() if '.' in file.filename else None
        
        type_valid = file.content_type in allowed_types
        extension_valid = file_extension in allowed_extensions if file_extension else False
        
        if not (type_valid or extension_valid):
            logger.error(f"Invalid file type: {file.content_type}, extension: {file_extension}")
            raise HTTPException(
                status_code=400, 
                detail=f"Unsupported file type: {file.content_type} (extension: {file_extension}). Please upload PDF, PPT, or PPTX files."
            )
        
        # Read file content
        content = await file.read()
        document_id = str(uuid.uuid4())
        
        logger.info(f"Processing document: {file.filename} ({len(content)} bytes)")
        
        # Process with intelligence engine
        success = await intelligence_engine.process_document(
            content, file.filename, document_id, user.id
        )
        
        if not success:
            raise HTTPException(status_code=500, detail="Failed to process document")
        
        # Store metadata in Supabase
        document_data = {
            "id": document_id,
            "user_id": user.id,
            "filename": file.filename,
            "content_type": file.content_type,
            "size_bytes": len(content),
            "status": "processed"
        }
        
        result = supabase.table("documents").insert(document_data).execute()
        
        return {
            "document_id": document_id,
            "filename": file.filename,
            "status": "processed",
            "message": "Document uploaded and processed with intelligent chunking",
            "chunks_created": True
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Upload error: {e}")
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")

@app.get("/api/v1/documents")
async def get_documents(user = Depends(get_current_user)):
    """Get user's documents with processing status"""
    try:
        result = supabase.table("documents").select("id, filename, status, created_at").eq("user_id", user.id).execute()
        
        # Get stats from intelligence engine
        stats = await intelligence_engine.get_user_stats(user.id)
        
        return {
            "documents": result.data,
            "stats": stats
        }
    except Exception as e:
        logger.error(f"Error getting documents: {e}")
        raise HTTPException(status_code=500, detail="Failed to get documents")

@app.post("/api/v1/search/passages")
async def search_passages(request: DocumentSearchRequest, user = Depends(get_current_user)):
    """Search for relevant passages using vector similarity"""
    try:
        logger.info(f"Searching passages for query: {request.query}")
        
        # Search using intelligence engine
        search_results = await intelligence_engine.vector_db.search_similar_passages(
            request.query, 
            user.id, 
            n_results=request.max_results,
            document_ids=request.document_ids if request.document_ids else None
        )
        
        # Convert to response format
        passages = []
        for result in search_results:
            passages.append({
                "passage": result.passage,
                "document_name": result.document_name,
                "page_number": result.page_number,
                "relevance_score": result.relevance_score,
                "document_id": result.document_id
            })
        
        return {
            "query": request.query,
            "passages": passages,
            "total_found": len(passages)
        }

    except Exception as e:
        logger.error(f"Search error: {e}")
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")

@app.post("/api/v1/chat/intelligent")
async def intelligent_chat(request: IntelligentChatRequest, user = Depends(get_current_user)):
    """Intelligent chat with source attribution and confidence scoring"""
    try:
        logger.info(f"Processing intelligent chat for user {user.id}: {request.message}")

        # Get user's API keys
        api_keys = await get_user_api_keys(user.id)

        if not api_keys:
            raise HTTPException(
                status_code=400,
                detail="No API keys configured. Please add your OpenAI or Claude API key in the dashboard."
            )

        # Determine which provider to use
        provider = "openai" if "openai" in api_keys else "claude"
        api_key = api_keys[provider]

        # Generate intelligent response
        response = await intelligence_engine.answer_question(
            query=request.message,
            user_id=user.id,
            api_key=api_key,
            provider=provider,
            document_ids=request.document_ids if request.document_ids else None
        )

        # Convert sources to response format
        sources = []
        for source in response.sources:
            sources.append({
                "passage": source.passage,
                "document_name": source.document_name,
                "page_number": source.page_number,
                "relevance_score": round(source.relevance_score, 3),
                "document_id": source.document_id
            })

        # Store chat session in database
        chat_data = {
            "id": str(uuid.uuid4()),
            "user_id": user.id,
            "session_id": request.session_id or str(uuid.uuid4()),
            "message": request.message,
            "response": response.answer,
            "confidence": round(response.confidence, 3),
            "processing_time": round(response.processing_time, 3),
            "sources_count": len(sources),
            "provider_used": provider
        }

        try:
            supabase.table("chat_sessions").insert(chat_data).execute()
        except Exception as e:
            logger.warning(f"Failed to store chat session: {e}")

        return {
            "response": response.answer,
            "confidence": round(response.confidence, 3),
            "sources": sources,
            "processing_time": round(response.processing_time, 3),
            "provider_used": provider,
            "session_id": chat_data["session_id"]
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Intelligent chat error: {e}")
        raise HTTPException(status_code=500, detail=f"Chat failed: {str(e)}")

@app.get("/api/v1/stats")
async def get_user_stats(user = Depends(get_current_user)):
    """Get user statistics and system status"""
    try:
        # Get intelligence engine stats
        stats = await intelligence_engine.get_user_stats(user.id)

        # Get chat history count
        chat_result = supabase.table("chat_sessions").select("id").eq("user_id", user.id).execute()
        chat_count = len(chat_result.data) if chat_result.data else 0

        # Get document count from database
        doc_result = supabase.table("documents").select("id").eq("user_id", user.id).execute()
        doc_count = len(doc_result.data) if doc_result.data else 0

        return {
            "user_id": user.id,
            "documents_uploaded": doc_count,
            "documents_processed": stats["documents_processed"],
            "chat_sessions": chat_count,
            "vector_database_status": stats["vector_database_status"],
            "embedding_model": stats["embedding_model"],
            "intelligence_engine": "active"
        }

    except Exception as e:
        logger.error(f"Error getting stats: {e}")
        raise HTTPException(status_code=500, detail="Failed to get statistics")

@app.delete("/api/v1/documents/{document_id}")
async def delete_document(document_id: str, user = Depends(get_current_user)):
    """Delete document and its vector chunks"""
    try:
        # Delete from vector database
        await intelligence_engine.vector_db.delete_document_chunks(document_id, user.id)

        # Delete from Supabase
        supabase.table("documents").delete().eq("id", document_id).eq("user_id", user.id).execute()

        return {"message": "Document deleted successfully"}

    except Exception as e:
        logger.error(f"Error deleting document: {e}")
        raise HTTPException(status_code=500, detail="Failed to delete document")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("intelligent_main:app", host="0.0.0.0", port=8000, reload=True)
