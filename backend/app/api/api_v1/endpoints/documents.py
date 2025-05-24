"""
Document processing endpoints.

This module handles document upload, processing, and management.
"""

import logging
from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models.document import Document
from app.schemas.document import (
    DocumentCreate,
    DocumentResponse,
    DocumentUpdate,
    ProcessingStatus,
)
from app.services.document_service import DocumentService
from app.api.deps import get_current_user
from app.models.user import User

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/upload", response_model=DocumentResponse)
async def upload_document(
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Upload and process a brand playbook document.
    
    Supports PDF, PowerPoint (PPT/PPTX), and Word documents.
    """
    try:
        # Validate file
        if not file.filename:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No file provided"
            )
        
        # Check file extension
        file_extension = file.filename.split(".")[-1].lower()
        allowed_extensions = ["pdf", "ppt", "pptx", "doc", "docx"]
        
        if file_extension not in allowed_extensions:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"File type not supported. Allowed: {', '.join(allowed_extensions)}"
            )
        
        # Check file size
        content = await file.read()
        if len(content) > 100 * 1024 * 1024:  # 100MB
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="File size too large. Maximum size is 100MB"
            )
        
        # Reset file pointer
        await file.seek(0)
        
        # Process document
        document_service = DocumentService(db)
        document = await document_service.upload_and_process(
            file=file,
            user_id=current_user.id,
            filename=file.filename,
        )
        
        logger.info(f"Document uploaded successfully: {document.id}")
        return document
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error uploading document: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error processing document"
        )


@router.get("/", response_model=List[DocumentResponse])
async def list_documents(
    skip: int = 0,
    limit: int = 100,
    status_filter: Optional[ProcessingStatus] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    List user's documents with optional filtering.
    """
    try:
        document_service = DocumentService(db)
        documents = await document_service.get_user_documents(
            user_id=current_user.id,
            skip=skip,
            limit=limit,
            status_filter=status_filter,
        )
        return documents
        
    except Exception as e:
        logger.error(f"Error listing documents: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error retrieving documents"
        )


@router.get("/{document_id}", response_model=DocumentResponse)
async def get_document(
    document_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Get a specific document by ID.
    """
    try:
        document_service = DocumentService(db)
        document = await document_service.get_document(
            document_id=document_id,
            user_id=current_user.id,
        )
        
        if not document:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Document not found"
            )
        
        return document
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting document: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error retrieving document"
        )


@router.put("/{document_id}", response_model=DocumentResponse)
async def update_document(
    document_id: UUID,
    document_update: DocumentUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Update document metadata.
    """
    try:
        document_service = DocumentService(db)
        document = await document_service.update_document(
            document_id=document_id,
            user_id=current_user.id,
            update_data=document_update,
        )
        
        if not document:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Document not found"
            )
        
        return document
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating document: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error updating document"
        )


@router.delete("/{document_id}")
async def delete_document(
    document_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Delete a document and all associated data.
    """
    try:
        document_service = DocumentService(db)
        success = await document_service.delete_document(
            document_id=document_id,
            user_id=current_user.id,
        )
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Document not found"
            )
        
        return {"message": "Document deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting document: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error deleting document"
        )


@router.post("/{document_id}/reprocess")
async def reprocess_document(
    document_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Reprocess a document (useful if processing failed or to update with new algorithms).
    """
    try:
        document_service = DocumentService(db)
        document = await document_service.reprocess_document(
            document_id=document_id,
            user_id=current_user.id,
        )
        
        if not document:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Document not found"
            )
        
        return {"message": "Document reprocessing started", "document": document}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error reprocessing document: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error reprocessing document"
        )


@router.get("/{document_id}/content")
async def get_document_content(
    document_id: UUID,
    page: Optional[int] = None,
    section: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Get processed content from a document.
    
    Optional parameters:
    - page: Get content from a specific page
    - section: Get content from a specific section
    """
    try:
        document_service = DocumentService(db)
        content = await document_service.get_document_content(
            document_id=document_id,
            user_id=current_user.id,
            page=page,
            section=section,
        )
        
        if not content:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Document or content not found"
            )
        
        return content
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting document content: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error retrieving document content"
        )
