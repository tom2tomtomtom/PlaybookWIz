"""Schemas for competitor and opportunity analysis."""

from typing import List, Dict, Any, Optional
from uuid import UUID

from pydantic import BaseModel


class CompetitorAnalysisRequest(BaseModel):
    document_ids: List[UUID]
    competitors: List[str]
    analysis_type: Optional[str] = "positioning"


class OpportunityAnalysisRequest(BaseModel):
    document_ids: List[UUID]
    market_context: Optional[str] = None
    analysis_depth: Optional[str] = "basic"


class AnalysisResponse(BaseModel):
    analysis_id: UUID
    status: str
    results: Dict[str, Any]

    class Config:
        orm_mode = True
