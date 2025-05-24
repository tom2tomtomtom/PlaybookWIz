"""
Creative ideation endpoints.

This module handles brand-aligned creative ideation using Claude's
advanced reasoning capabilities and creative personas.
"""

import logging
from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models.user import User
from app.schemas.ideation import (
    IdeationRequest,
    IdeationResponse,
    CreativeSession,
    IdeaEvaluation,
    PersonaRequest,
)
from app.services.ideation_service import IdeationService
from app.api.deps import get_current_user

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/generate", response_model=IdeationResponse)
async def generate_ideas(
    request: IdeationRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Generate brand-aligned creative ideas using AI personas.
    
    Uses Claude's advanced reasoning to generate creative ideas that
    align with brand guidelines and target specific objectives.
    """
    try:
        ideation_service = IdeationService(db)
        
        # Validate document access
        accessible_docs = await ideation_service.validate_document_access(
            user_id=current_user.id,
            document_ids=request.document_ids,
        )
        
        if not accessible_docs:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="No accessible documents found"
            )
        
        # Generate ideas using the specified approach
        if request.use_personas:
            ideas = await ideation_service.generate_ideas_with_personas(
                request=request,
                document_ids=accessible_docs,
                user_id=current_user.id,
            )
        else:
            ideas = await ideation_service.generate_ideas_direct(
                request=request,
                document_ids=accessible_docs,
                user_id=current_user.id,
            )
        
        # Save ideation session
        session = await ideation_service.save_ideation_session(
            user_id=current_user.id,
            request=request,
            ideas=ideas,
            document_ids=accessible_docs,
        )
        
        response = IdeationResponse(
            session_id=session.id,
            ideas=ideas,
            request=request,
            created_at=session.created_at,
        )
        
        logger.info(f"Generated {len(ideas)} ideas for user {current_user.id}")
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating ideas: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error generating creative ideas"
        )


@router.post("/personas/dialogue", response_model=dict)
async def persona_dialogue(
    request: PersonaRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Engage in a philosophical dialogue between personas to prime creativity.
    
    This implements the Tom-Aiden dialogue framework for enhanced creative output.
    """
    try:
        ideation_service = IdeationService(db)
        
        # Generate philosophical dialogue
        dialogue = await ideation_service.generate_persona_dialogue(
            topic=request.topic,
            personas=request.personas,
            context=request.context,
            user_id=current_user.id,
        )
        
        return {
            "dialogue": dialogue,
            "topic": request.topic,
            "personas": request.personas,
        }
        
    except Exception as e:
        logger.error(f"Error generating persona dialogue: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error generating persona dialogue"
        )


@router.post("/enhance")
async def enhance_creativity(
    session_id: UUID,
    enhancement_type: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Apply creativity enhancement techniques to existing ideas.
    
    Available enhancement types:
    - emotional_depth: Add emotional resonance
    - pattern_breaking: Subvert expectations
    - philosophical: Add philosophical depth
    - cultural_relevance: Enhance cultural connections
    """
    try:
        ideation_service = IdeationService(db)
        
        # Get existing session
        session = await ideation_service.get_session(
            session_id=session_id,
            user_id=current_user.id,
        )
        
        if not session:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Ideation session not found"
            )
        
        # Apply enhancement
        enhanced_ideas = await ideation_service.enhance_ideas(
            session=session,
            enhancement_type=enhancement_type,
        )
        
        # Update session with enhanced ideas
        await ideation_service.update_session_ideas(
            session_id=session_id,
            enhanced_ideas=enhanced_ideas,
        )
        
        return {
            "enhanced_ideas": enhanced_ideas,
            "enhancement_type": enhancement_type,
            "session_id": session_id,
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error enhancing creativity: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error enhancing creativity"
        )


@router.get("/sessions", response_model=List[CreativeSession])
async def get_ideation_sessions(
    skip: int = 0,
    limit: int = 20,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Get user's ideation sessions.
    """
    try:
        ideation_service = IdeationService(db)
        sessions = await ideation_service.get_user_sessions(
            user_id=current_user.id,
            skip=skip,
            limit=limit,
        )
        
        return sessions
        
    except Exception as e:
        logger.error(f"Error retrieving ideation sessions: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error retrieving ideation sessions"
        )


@router.get("/sessions/{session_id}", response_model=CreativeSession)
async def get_ideation_session(
    session_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Get a specific ideation session.
    """
    try:
        ideation_service = IdeationService(db)
        session = await ideation_service.get_session(
            session_id=session_id,
            user_id=current_user.id,
        )
        
        if not session:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Ideation session not found"
            )
        
        return session
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving ideation session: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error retrieving ideation session"
        )


@router.post("/evaluate")
async def evaluate_ideas(
    session_id: UUID,
    criteria: List[str],
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Evaluate generated ideas against specific criteria.
    
    Common criteria:
    - brand_alignment: How well does it align with brand guidelines?
    - feasibility: How practical is implementation?
    - innovation: How novel and creative is the idea?
    - impact: What's the potential business impact?
    - audience_appeal: How appealing is it to the target audience?
    """
    try:
        ideation_service = IdeationService(db)
        
        # Get session
        session = await ideation_service.get_session(
            session_id=session_id,
            user_id=current_user.id,
        )
        
        if not session:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Ideation session not found"
            )
        
        # Evaluate ideas
        evaluations = await ideation_service.evaluate_ideas(
            session=session,
            criteria=criteria,
        )
        
        return {
            "evaluations": evaluations,
            "criteria": criteria,
            "session_id": session_id,
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error evaluating ideas: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error evaluating ideas"
        )


@router.post("/refine")
async def refine_ideas(
    session_id: UUID,
    selected_ideas: List[int],
    refinement_direction: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Refine selected ideas in a specific direction.
    
    Refinement directions:
    - more_specific: Make ideas more concrete and actionable
    - broader_scope: Expand the scope and applications
    - different_angle: Explore from a different perspective
    - combine: Combine multiple ideas into hybrid concepts
    """
    try:
        ideation_service = IdeationService(db)
        
        # Get session
        session = await ideation_service.get_session(
            session_id=session_id,
            user_id=current_user.id,
        )
        
        if not session:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Ideation session not found"
            )
        
        # Refine ideas
        refined_ideas = await ideation_service.refine_ideas(
            session=session,
            selected_ideas=selected_ideas,
            refinement_direction=refinement_direction,
        )
        
        return {
            "refined_ideas": refined_ideas,
            "refinement_direction": refinement_direction,
            "session_id": session_id,
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error refining ideas: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error refining ideas"
        )


@router.delete("/sessions/{session_id}")
async def delete_ideation_session(
    session_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Delete an ideation session.
    """
    try:
        ideation_service = IdeationService(db)
        success = await ideation_service.delete_session(
            session_id=session_id,
            user_id=current_user.id,
        )
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Ideation session not found"
            )
        
        return {"message": "Ideation session deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting ideation session: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error deleting ideation session"
        )
