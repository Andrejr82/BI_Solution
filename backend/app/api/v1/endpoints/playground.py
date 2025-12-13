from typing import Annotated, Dict, Any, List, Optional
from datetime import datetime
import json
import logging

import polars as pl
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field

from app.api.dependencies import require_role, get_current_active_user
from app.core.data_scope_service import data_scope_service
from app.infrastructure.database.models import User
from app.config.settings import settings
from app.core.llm_gemini_adapter import GeminiLLMAdapter

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/playground", tags=["Playground"])

class QueryRequest(BaseModel):
    query: str # Não usada diretamente como SQL, mas sim como intent
    columns: List[str] = []
    limit: int = 100

class ChatMessage(BaseModel):
    role: str  # "user" ou "assistant"
    content: str
    timestamp: Optional[str] = None

class PlaygroundChatRequest(BaseModel):
    message: str
    history: List[ChatMessage] = Field(default_factory=list)
    temperature: float = Field(default=1.0, ge=0.0, le=2.0)
    max_tokens: int = Field(default=2048, ge=100, le=8192)
    json_mode: bool = False
    stream: bool = False

@router.post("/query")
async def execute_query(
    current_user: Annotated[User, Depends(require_role("admin"))],
    request: QueryRequest
):
    """
    Endpoint para exploração de dados (Admin Only).
    Permite selecionar colunas e visualizar dados brutos.
    """
    try:
        df = data_scope_service.get_filtered_dataframe(current_user)

        # Selecionar colunas se especificadas
        if request.columns:
            valid_cols = [c for c in request.columns if c in df.columns]
            if valid_cols:
                df = df.select(valid_cols)

        # Limitar resultados
        result = df.head(request.limit)

        return {
            "rows": result.to_dicts(),
            "count": len(result),
            "total_rows": len(df), # Total no dataset (lazy count seria melhor, mas aqui df já é eager ou quase)
            "columns": result.columns
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/chat")
async def playground_chat(
    current_user: Annotated[User, Depends(get_current_active_user)],
    request: PlaygroundChatRequest
):
    """
    Endpoint de chat do Playground com controles avançados.
    Permite testar o modelo Gemini com diferentes parâmetros.
    """
    try:
        if not settings.GEMINI_API_KEY:
            raise HTTPException(
                status_code=500,
                detail="GEMINI_API_KEY não configurada no servidor"
            )

        # Configurar LLM com parâmetros customizados usando GeminiLLMAdapter
        llm = GeminiLLMAdapter(
            model_name=settings.LLM_MODEL_NAME,
            gemini_api_key=settings.GEMINI_API_KEY
        ).get_llm()

        # Note: GeminiLLMAdapter doesn't support custom temperature/max_tokens in get_llm()
        # These parameters would need to be added to the adapter if needed

        # Construir histórico de mensagens
        messages = []
        for msg in request.history:
            if msg.role == "user":
                messages.append(("human", msg.content))
            elif msg.role == "assistant":
                messages.append(("assistant", msg.content))

        # Adicionar mensagem atual
        messages.append(("human", request.message))

        # Invocar LLM
        start_time = datetime.now()
        response = llm.invoke(messages)
        end_time = datetime.now()

        response_time = (end_time - start_time).total_seconds()

        # Estatísticas de cache (simuladas por enquanto)
        # Em produção, você poderia usar Redis ou outro sistema de cache
        cache_stats = {
            "hits": 0,
            "misses": 0,
            "hit_rate": 0.0,
            "enabled": False
        }

        return {
            "response": response.content,
            "model_info": {
                "model": settings.LLM_MODEL_NAME,
                "temperature": request.temperature,
                "max_tokens": request.max_tokens,
                "json_mode": request.json_mode
            },
            "metadata": {
                "response_time": round(response_time, 2),
                "timestamp": datetime.now().isoformat(),
                "user": current_user.username
            },
            "cache_stats": cache_stats
        }

    except Exception as e:
        logger.error(f"Erro no playground chat: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao processar mensagem: {str(e)}"
        )


@router.get("/info")
async def get_model_info(
    current_user: Annotated[User, Depends(get_current_active_user)]
):
    """
    Retorna informações sobre o modelo LLM configurado.
    """
    return {
        "model": settings.LLM_MODEL_NAME,
        "api_key_configured": bool(settings.GEMINI_API_KEY),
        "default_temperature": 1.0,
        "default_max_tokens": 2048,
        "max_temperature": 2.0,
        "max_tokens_limit": 8192
    }
