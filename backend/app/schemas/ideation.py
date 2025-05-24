"""Schemas for creative ideation."""

from datetime import datetime
from typing import List, Optional, Dict, Any
from uuid import UUID

from pydantic import BaseModel


class IdeationRequest(BaseModel):
    document_ids: List[UUID]
    prompt: Optional[str] = None
    objectives: Optional[List[str]] = None
    use_personas: bool = False
    personas: Optional[List[str]] = None


class IdeationResponse(BaseModel):
    session_id: UUID
    ideas: List[Dict[str, Any]]
    request: IdeationRequest
    created_at: datetime

    class Config:
        orm_mode = True


class CreativeSession(IdeationResponse):
    pass


class IdeaEvaluation(BaseModel):
    idea_index: int
    score: float
    notes: Optional[str] = None


class PersonaRequest(BaseModel):
    topic: str
    personas: List[str]
    context: Optional[str] = None

