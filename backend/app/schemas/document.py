"""Pydantic schemas for document objects."""

from __future__ import annotations

from datetime import datetime
from typing import Optional, Dict, Any
from uuid import UUID

from pydantic import BaseModel, Field
from enum import Enum


class ProcessingStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class DocumentBase(BaseModel):
    filename: str
    file_path: str
    file_size: int
    file_type: str
    user_id: UUID
    status: ProcessingStatus = ProcessingStatus.PENDING
    error_message: Optional[str] = None
    page_count: Optional[int] = None
    word_count: Optional[int] = None
    metadata: Optional[Dict[str, Any]] = None


class DocumentCreate(DocumentBase):
    pass


class DocumentUpdate(BaseModel):
    status: Optional[ProcessingStatus] = None
    error_message: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


class DocumentResponse(DocumentBase):
    id: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True
