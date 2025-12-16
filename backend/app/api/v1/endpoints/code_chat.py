"""
Code Chat API Endpoints
=======================

Provides REST API for semantic code search and analysis.

Endpoints:
- GET  /api/v1/code-chat/stats - Get index statistics
- POST /api/v1/code-chat/query - Query the codebase

Author: Antigravity AI
Date: 2025-12-15
"""

from typing import Annotated, List, Optional
from datetime import datetime
import logging

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field

from app.api.dependencies import require_role
from app.infrastructure.database.models import User
from app.core.code_rag_service import get_code_rag_service

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/code-chat", tags=["Code Chat"])


# ============================================================================
# Request/Response Models
# ============================================================================

class ChatMessage(BaseModel):
    """Chat message model."""
    role: str  # "user" or "assistant"
    content: str
    timestamp: Optional[str] = None


class CodeChatRequest(BaseModel):
    """Request model for code chat queries."""
    message: str = Field(..., min_length=1, description="User's question about the code")
    history: List[ChatMessage] = Field(default_factory=list, description="Conversation history")
    filters: Optional[dict] = Field(default=None, description="Optional filters (language, directory)")


class CodeReference(BaseModel):
    """Code reference model."""
    file: str
    score: float
    content: str
    lines: str


class CodeChatResponse(BaseModel):
    """Response model for code chat queries."""
    response: str
    code_references: List[CodeReference]
    metadata: dict


class IndexStats(BaseModel):
    """Index statistics model."""
    status: str
    total_files: int
    total_functions: int
    total_classes: int
    total_lines: int
    indexed_at: Optional[str]
    languages: List[str]


# ============================================================================
# Endpoints
# ============================================================================

@router.get("/stats", response_model=IndexStats)
async def get_index_stats(
    current_user: Annotated[User, Depends(require_role("admin"))]
):
    """
    Get statistics about the code index.
    
    Returns:
        IndexStats: Statistics about indexed code
    """
    try:
        rag_service = get_code_rag_service()
        stats = rag_service.get_index_stats()
        return stats
        
    except Exception as e:
        logger.error(f"Error getting index stats: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao obter estatísticas do índice: {str(e)}"
        )


@router.post("/query", response_model=CodeChatResponse)
async def query_codebase(
    request: CodeChatRequest,
    current_user: Annotated[User, Depends(require_role("admin"))]
):
    """
    Query the codebase with semantic search.
    
    Args:
        request: CodeChatRequest with message, history, and filters
        current_user: Authenticated user
        
    Returns:
        CodeChatResponse: Response with code references and metadata
    """
    try:
        # Validate message
        if not request.message or not request.message.strip():
            raise HTTPException(
                status_code=400,
                detail="A mensagem não pode estar vazia"
            )
        
        # Get RAG service
        rag_service = get_code_rag_service()
        
        # Convert history to dict format
        history_dicts = [
            {"role": msg.role, "content": msg.content}
            for msg in request.history
        ]
        
        # Query the codebase
        logger.info(f"Code chat query from {current_user.username}: {request.message[:100]}...")
        result = rag_service.query(
            message=request.message,
            history=history_dicts,
            filters=request.filters
        )
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in code chat query: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao processar consulta: {str(e)}"
        )
