"""Schemas for question and answer functionality."""

from datetime import datetime
from typing import List, Optional, Dict, Any
from uuid import UUID

from pydantic import BaseModel


class QuestionRequest(BaseModel):
    question: str
    document_ids: List[UUID]
    conversation_id: Optional[UUID] = None
    preferences: Optional[Dict[str, Any]] = None


class QuestionResponse(BaseModel):
    id: UUID
    question: str
    answer: str
    confidence: float
    sources: List[Dict[str, Any]]
    conversation_id: Optional[UUID] = None
    created_at: datetime

    class Config:
        orm_mode = True


class QuestionHistory(QuestionResponse):
    pass


class ConversationContext(BaseModel):
    id: UUID
    title: str
    document_ids: List[UUID]
    created_at: datetime

    class Config:
        orm_mode = True
