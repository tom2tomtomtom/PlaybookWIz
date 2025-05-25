"""
Brand analysis endpoints.
"""

import uuid
import logging

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models.user import User
from app.schemas.analysis import (
    CompetitorAnalysisRequest,
    OpportunityAnalysisRequest,
    AnalysisResponse,
)
from app.services.analysis_service import AnalysisService
from app.api.deps import get_current_user

router = APIRouter()


logger = logging.getLogger(__name__)


@router.post("/competitors", response_model=AnalysisResponse)
async def analyze_competitors(
    request: CompetitorAnalysisRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Analyze competitors mentioned in brand documents."""
    try:
        service = AnalysisService(db)
        accessible_docs = await service.validate_document_access(
            user_id=current_user.id,
            document_ids=request.document_ids,
        )

        if not accessible_docs:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="No accessible documents found",
            )

        results = await service.analyze_competitors(
            user_id=current_user.id,
            document_ids=accessible_docs,
            competitors=request.competitors,
            analysis_type=request.analysis_type,
        )

        return AnalysisResponse(
            analysis_id=uuid.uuid4(),
            status="completed",
            results=results,
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error analyzing competitors: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error analyzing competitors",
        )


@router.post("/opportunities", response_model=AnalysisResponse)
async def identify_opportunities(
    request: OpportunityAnalysisRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Identify strategic opportunities from brand documents."""
    try:
        service = AnalysisService(db)
        accessible_docs = await service.validate_document_access(
            user_id=current_user.id,
            document_ids=request.document_ids,
        )

        if not accessible_docs:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="No accessible documents found",
            )

        results = await service.identify_opportunities(
            user_id=current_user.id,
            document_ids=accessible_docs,
            market_context=request.market_context,
            analysis_depth=request.analysis_depth,
        )

        return AnalysisResponse(
            analysis_id=uuid.uuid4(),
            status="completed",
            results=results,
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error identifying opportunities: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error identifying opportunities",
        )
