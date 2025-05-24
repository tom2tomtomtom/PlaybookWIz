"""
Question answering endpoints.

This module handles intelligent question answering about brand playbooks
using retrieval-augmented generation (RAG) with Claude.
"""

import logging
from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models.user import User
from app.schemas.question import (
    QuestionRequest,
    QuestionResponse,
    QuestionHistory,
    ConversationContext,
)
from app.services.ai_service import AIService
from app.services.question_service import QuestionService
from app.api.deps import get_current_user

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/ask", response_model=QuestionResponse)
async def ask_question(
    question_request: QuestionRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Ask a question about brand playbooks.
    
    Uses retrieval-augmented generation (RAG) to provide accurate answers
    based on the content of uploaded brand playbooks.
    """
    try:
        # Validate that user has access to the specified documents
        question_service = QuestionService(db)
        
        # Check document access
        accessible_docs = await question_service.validate_document_access(
            user_id=current_user.id,
            document_ids=question_request.document_ids,
        )
        
        if not accessible_docs:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="No accessible documents found"
            )
        
        # Initialize AI service
        ai_service = AIService()
        await ai_service.initialize()
        
        # Get conversation context if provided
        context = None
        if question_request.conversation_id:
            context = await question_service.get_conversation_context(
                conversation_id=question_request.conversation_id,
                user_id=current_user.id,
            )
        
        # Answer the question
        answer_result = await ai_service.answer_question(
            question=question_request.question,
            document_ids=accessible_docs,
            user_context={
                "user_id": str(current_user.id),
                "conversation_context": context,
                "preferences": question_request.preferences,
            }
        )
        
        # Save question and answer to history
        question_record = await question_service.save_question_answer(
            user_id=current_user.id,
            question=question_request.question,
            answer=answer_result["answer"],
            document_ids=accessible_docs,
            confidence=answer_result["confidence"],
            sources=answer_result["sources"],
            conversation_id=question_request.conversation_id,
        )
        
        # Prepare response
        response = QuestionResponse(
            id=question_record.id,
            question=question_request.question,
            answer=answer_result["answer"],
            confidence=answer_result["confidence"],
            sources=answer_result["sources"],
            conversation_id=question_record.conversation_id,
            created_at=question_record.created_at,
        )
        
        logger.info(f"Question answered successfully for user {current_user.id}")
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error answering question: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error processing question"
        )


@router.get("/history", response_model=List[QuestionHistory])
async def get_question_history(
    skip: int = 0,
    limit: int = 50,
    conversation_id: Optional[UUID] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Get user's question history with optional filtering by conversation.
    """
    try:
        question_service = QuestionService(db)
        history = await question_service.get_user_question_history(
            user_id=current_user.id,
            skip=skip,
            limit=limit,
            conversation_id=conversation_id,
        )
        
        return history
        
    except Exception as e:
        logger.error(f"Error retrieving question history: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error retrieving question history"
        )


@router.get("/conversations", response_model=List[ConversationContext])
async def get_conversations(
    skip: int = 0,
    limit: int = 20,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Get user's conversation contexts.
    """
    try:
        question_service = QuestionService(db)
        conversations = await question_service.get_user_conversations(
            user_id=current_user.id,
            skip=skip,
            limit=limit,
        )
        
        return conversations
        
    except Exception as e:
        logger.error(f"Error retrieving conversations: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error retrieving conversations"
        )


@router.post("/conversations", response_model=ConversationContext)
async def create_conversation(
    title: str,
    document_ids: List[UUID],
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Create a new conversation context.
    """
    try:
        question_service = QuestionService(db)
        
        # Validate document access
        accessible_docs = await question_service.validate_document_access(
            user_id=current_user.id,
            document_ids=document_ids,
        )
        
        if not accessible_docs:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="No accessible documents found"
            )
        
        conversation = await question_service.create_conversation(
            user_id=current_user.id,
            title=title,
            document_ids=accessible_docs,
        )
        
        return conversation
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating conversation: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error creating conversation"
        )


@router.get("/{question_id}", response_model=QuestionResponse)
async def get_question(
    question_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Get a specific question and answer by ID.
    """
    try:
        question_service = QuestionService(db)
        question = await question_service.get_question(
            question_id=question_id,
            user_id=current_user.id,
        )
        
        if not question:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Question not found"
            )
        
        return question
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving question: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error retrieving question"
        )


@router.delete("/{question_id}")
async def delete_question(
    question_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Delete a question from history.
    """
    try:
        question_service = QuestionService(db)
        success = await question_service.delete_question(
            question_id=question_id,
            user_id=current_user.id,
        )
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Question not found"
            )
        
        return {"message": "Question deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting question: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error deleting question"
        )


@router.post("/{question_id}/feedback")
async def provide_feedback(
    question_id: UUID,
    helpful: bool,
    feedback_text: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Provide feedback on a question answer.
    """
    try:
        question_service = QuestionService(db)
        success = await question_service.save_feedback(
            question_id=question_id,
            user_id=current_user.id,
            helpful=helpful,
            feedback_text=feedback_text,
        )
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Question not found"
            )
        
        return {"message": "Feedback saved successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error saving feedback: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error saving feedback"
        )


@router.post("/suggest")
async def suggest_questions(
    document_ids: List[UUID],
    count: int = 5,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Suggest relevant questions based on document content.
    """
    try:
        question_service = QuestionService(db)
        
        # Validate document access
        accessible_docs = await question_service.validate_document_access(
            user_id=current_user.id,
            document_ids=document_ids,
        )
        
        if not accessible_docs:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="No accessible documents found"
            )
        
        # Generate question suggestions
        ai_service = AIService()
        await ai_service.initialize()
        
        suggestions = await ai_service.suggest_questions(
            document_ids=accessible_docs,
            count=count,
        )
        
        return {"suggestions": suggestions}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating question suggestions: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error generating question suggestions"
        )
