"""
Document processing service.

This service handles document upload, processing, and content extraction
for brand playbooks in various formats (PDF, PowerPoint, Word).
"""

import asyncio
import logging
import os
import uuid
from pathlib import Path
from typing import List, Optional, Dict, Any
from uuid import UUID

import aiofiles
from fastapi import UploadFile
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete

from app.core.config import settings
from app.models.document import Document
from app.schemas.document import DocumentCreate, DocumentUpdate, ProcessingStatus
from app.services.processors.pdf_processor import PDFProcessor
from app.services.processors.powerpoint_processor import PowerPointProcessor
from app.services.processors.word_processor import WordProcessor
from app.services.ai_service import AIService

logger = logging.getLogger(__name__)


class DocumentService:
    """Service for document processing and management."""
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self.upload_dir = Path(settings.UPLOAD_DIR)
        self.upload_dir.mkdir(exist_ok=True)
        
        # Initialize processors
        self.pdf_processor = PDFProcessor()
        self.powerpoint_processor = PowerPointProcessor()
        self.word_processor = WordProcessor()
        self.ai_service = AIService()
    
    async def upload_and_process(
        self,
        file: UploadFile,
        user_id: UUID,
        filename: str,
    ) -> Document:
        """Upload and process a document."""
        
        # Generate unique filename
        file_id = str(uuid.uuid4())
        file_extension = filename.split(".")[-1].lower()
        stored_filename = f"{file_id}.{file_extension}"
        file_path = self.upload_dir / stored_filename
        
        try:
            # Save file to disk
            async with aiofiles.open(file_path, 'wb') as f:
                content = await file.read()
                await f.write(content)
            
            # Create document record
            document_data = DocumentCreate(
                filename=filename,
                file_path=str(file_path),
                file_size=len(content),
                file_type=file_extension,
                user_id=user_id,
                status=ProcessingStatus.PENDING,
            )
            
            document = Document(**document_data.dict())
            self.db.add(document)
            await self.db.commit()
            await self.db.refresh(document)
            
            # Start background processing
            asyncio.create_task(self._process_document_async(document.id))
            
            return document
            
        except Exception as e:
            # Clean up file if something went wrong
            if file_path.exists():
                file_path.unlink()
            logger.error(f"Error uploading document: {e}")
            raise
    
    async def _process_document_async(self, document_id: UUID):
        """Process document in background."""
        try:
            # Update status to processing
            await self._update_document_status(document_id, ProcessingStatus.PROCESSING)
            
            # Get document
            result = await self.db.execute(
                select(Document).where(Document.id == document_id)
            )
            document = result.scalar_one_or_none()
            
            if not document:
                logger.error(f"Document not found: {document_id}")
                return
            
            # Process based on file type
            processor = self._get_processor(document.file_type)
            if not processor:
                await self._update_document_status(
                    document_id, 
                    ProcessingStatus.FAILED,
                    error_message="Unsupported file type"
                )
                return
            
            # Extract content
            extracted_content = await processor.process(document.file_path)
            
            # Generate embeddings and store in vector database
            await self.ai_service.process_document_content(
                document_id=document_id,
                content=extracted_content,
            )
            
            # Update document with extracted metadata
            await self._update_document_with_content(document_id, extracted_content)
            
            # Update status to completed
            await self._update_document_status(document_id, ProcessingStatus.COMPLETED)
            
            logger.info(f"Document processed successfully: {document_id}")
            
        except Exception as e:
            logger.error(f"Error processing document {document_id}: {e}")
            await self._update_document_status(
                document_id,
                ProcessingStatus.FAILED,
                error_message=str(e)
            )
    
    def _get_processor(self, file_type: str):
        """Get appropriate processor for file type."""
        processors = {
            "pdf": self.pdf_processor,
            "ppt": self.powerpoint_processor,
            "pptx": self.powerpoint_processor,
            "doc": self.word_processor,
            "docx": self.word_processor,
        }
        return processors.get(file_type.lower())
    
    async def _update_document_status(
        self,
        document_id: UUID,
        status: ProcessingStatus,
        error_message: Optional[str] = None,
    ):
        """Update document processing status."""
        update_data = {"status": status}
        if error_message:
            update_data["error_message"] = error_message
        
        await self.db.execute(
            update(Document)
            .where(Document.id == document_id)
            .values(**update_data)
        )
        await self.db.commit()
    
    async def _update_document_with_content(
        self,
        document_id: UUID,
        content: Dict[str, Any],
    ):
        """Update document with extracted content metadata."""
        update_data = {
            "page_count": content.get("page_count", 0),
            "word_count": content.get("word_count", 0),
            "metadata": content.get("metadata", {}),
        }
        
        await self.db.execute(
            update(Document)
            .where(Document.id == document_id)
            .values(**update_data)
        )
        await self.db.commit()
    
    async def get_user_documents(
        self,
        user_id: UUID,
        skip: int = 0,
        limit: int = 100,
        status_filter: Optional[ProcessingStatus] = None,
    ) -> List[Document]:
        """Get user's documents with optional filtering."""
        query = select(Document).where(Document.user_id == user_id)
        
        if status_filter:
            query = query.where(Document.status == status_filter)
        
        query = query.offset(skip).limit(limit).order_by(Document.created_at.desc())
        
        result = await self.db.execute(query)
        return result.scalars().all()
    
    async def get_document(self, document_id: UUID, user_id: UUID) -> Optional[Document]:
        """Get a specific document."""
        result = await self.db.execute(
            select(Document).where(
                Document.id == document_id,
                Document.user_id == user_id,
            )
        )
        return result.scalar_one_or_none()
    
    async def update_document(
        self,
        document_id: UUID,
        user_id: UUID,
        update_data: DocumentUpdate,
    ) -> Optional[Document]:
        """Update document metadata."""
        # Check if document exists and belongs to user
        document = await self.get_document(document_id, user_id)
        if not document:
            return None
        
        # Update document
        update_dict = update_data.dict(exclude_unset=True)
        if update_dict:
            await self.db.execute(
                update(Document)
                .where(Document.id == document_id)
                .values(**update_dict)
            )
            await self.db.commit()
            await self.db.refresh(document)
        
        return document
    
    async def delete_document(self, document_id: UUID, user_id: UUID) -> bool:
        """Delete a document and all associated data."""
        # Check if document exists and belongs to user
        document = await self.get_document(document_id, user_id)
        if not document:
            return False
        
        try:
            # Delete file from disk
            if os.path.exists(document.file_path):
                os.remove(document.file_path)
            
            # Delete from vector database
            await self.ai_service.delete_document_embeddings(document_id)
            
            # Delete from database
            await self.db.execute(
                delete(Document).where(Document.id == document_id)
            )
            await self.db.commit()
            
            return True
            
        except Exception as e:
            logger.error(f"Error deleting document {document_id}: {e}")
            await self.db.rollback()
            return False
    
    async def reprocess_document(self, document_id: UUID, user_id: UUID) -> Optional[Document]:
        """Reprocess a document."""
        document = await self.get_document(document_id, user_id)
        if not document:
            return None
        
        # Start reprocessing
        asyncio.create_task(self._process_document_async(document_id))
        
        return document
    
    async def get_document_content(
        self,
        document_id: UUID,
        user_id: UUID,
        page: Optional[int] = None,
        section: Optional[str] = None,
    ) -> Optional[Dict[str, Any]]:
        """Get processed content from a document."""
        document = await self.get_document(document_id, user_id)
        if not document or document.status != ProcessingStatus.COMPLETED:
            return None
        
        # Get content from AI service
        return await self.ai_service.get_document_content(
            document_id=document_id,
            page=page,
            section=section,
        )
