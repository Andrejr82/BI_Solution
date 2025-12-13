"""
Chat Endpoints
BI Chat with AI assistant
"""

from typing import Annotated, Dict, Any, Optional
from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.responses import ORJSONResponse, StreamingResponse
from pydantic import BaseModel
from pathlib import Path
import json
import asyncio
import logging
import sys

# Import core dependencies
from app.api.dependencies import get_current_active_user
from app.infrastructure.database.models import User
from app.config.settings import settings
from app.core.utils.response_cache import ResponseCache
from app.core.utils.query_history import QueryHistory
from app.core.utils.field_mapper import FieldMapper
from app.core.rag.query_retriever import QueryRetriever
from app.core.learning.pattern_matcher import PatternMatcher
from app.core.agents.code_gen_agent import CodeGenAgent
from app.core.agents.caculinha_bi_agent import CaculinhaBIAgent
from app.core.llm_gemini_adapter import GeminiLLMAdapter
from app.core.utils.error_handler import APIError
from app.core.utils.session_manager import SessionManager
from app.core.utils.semantic_cache import cache_get, cache_set, cache_stats
from app.core.utils.response_validator import validate_response, validator_stats

logger = logging.getLogger(__name__)

# Initialize agents and LLM globally for performance.
llm = None
field_mapper = None
query_retriever = None
pattern_matcher = None
response_cache = None
query_history = None
code_gen_agent = None
caculinha_bi_agent = None
session_manager = None

def _initialize_agents_and_llm():
    global llm, field_mapper, query_retriever, pattern_matcher, response_cache, query_history, code_gen_agent, caculinha_bi_agent, session_manager
    if llm is None:
        logger.info("Initializing LLM and Agents...")
        if not settings.GEMINI_API_KEY:
            logger.error("GEMINI_API_KEY is not set. LLM will not be initialized.")
            raise ValueError("GEMINI_API_KEY must be set in environment variables.")

        llm = GeminiLLMAdapter(model_name=settings.LLM_MODEL_NAME, gemini_api_key=settings.GEMINI_API_KEY).get_llm()
        
        field_mapper = FieldMapper()
        query_retriever = QueryRetriever(
            embedding_model_name=settings.RAG_EMBEDDING_MODEL,
            faiss_index_path=settings.RAG_FAISS_INDEX_PATH,
            examples_path=settings.LEARNING_EXAMPLES_PATH
        )
        pattern_matcher = PatternMatcher()
        response_cache = ResponseCache(cache_dir="data/cache", ttl_minutes=settings.CACHE_TTL_MINUTES)
        query_history = QueryHistory(history_dir="data/query_history")
        session_manager = SessionManager(storage_dir="app/data/sessions")

        code_gen_agent = CodeGenAgent(
            llm=llm,
            field_mapper=field_mapper,
            query_retriever=query_retriever,
            pattern_matcher=pattern_matcher,
            response_cache=response_cache,
            query_history=query_history
        )
        caculinha_bi_agent = CaculinhaBIAgent(
            llm=llm,
            code_gen_agent=code_gen_agent,
            field_mapper=field_mapper
        )
        logger.info("LLM and Agents initialized successfully.")

_initialize_agents_and_llm()

router = APIRouter(prefix="/chat", tags=["Chat"])


class ChatRequest(BaseModel):
    query: str


class ChatResponse(BaseModel):
    response: str


@router.get("/stream")
async def stream_chat(
    q: str,
    token: str,
    session_id: str,
    request: Request,
):
    """
    Streaming endpoint using Server-Sent Events (SSE)
    Integrates the agent system for dynamic responses.
    """
    from app.api.dependencies import get_current_user_from_token

    try:
        current_user = await get_current_user_from_token(token)
        logger.info(f"SSE authenticated user: {current_user.username}")
    except Exception as e:
        logger.error(f"SSE authentication failed: {e}")
        async def error_generator():
            yield f"data: {json.dumps({'error': 'Não autenticado'})}\n\n"
        return StreamingResponse(error_generator(), media_type="text/event-stream")

    last_event_id = request.headers.get("Last-Event-ID")
    logger.info(f"==> SSE STREAM REQUEST: {q} (Session: {session_id}) (Last-Event-ID: {last_event_id}) <==")
    
    async def event_generator():
        try:
            event_counter = int(last_event_id) if last_event_id else 0
            
            if caculinha_bi_agent is None:
                yield f"data: {json.dumps({'error': 'Agent system not initialized'})}\n\n"
                return

            # Retrieve History
            chat_history = session_manager.get_history(session_id)
            # Add User Message to History immediately
            session_manager.add_message(session_id, "user", q)

            logger.info(f"Processing query with CaculinhaBIAgent: '{q}' | History len: {len(chat_history)}")
            
            # ✅ NOVO: Verificar Semantic Cache primeiro
            cached_response = cache_get(q)
            if cached_response:
                logger.info(f"✅ CACHE HIT: Resposta encontrada em cache para: {q[:50]}...")
                event_counter += 1
                yield f"id: {event_counter}\n"
                yield f"data: {json.dumps({'type': 'cache_hit', 'done': False})}\n\n"
                agent_response = cached_response
            else:
                # Run Agent with History (cache miss)
                agent_response = await asyncio.to_thread(caculinha_bi_agent.run, user_query=q, chat_history=chat_history)
                
                # Salvar resposta válida em cache
                if agent_response and "error" not in str(agent_response).lower():
                    cache_set(q, agent_response)
                    logger.info(f"Cache SET: Resposta salva para: {q[:50]}...")
            
            if not agent_response:
                logger.warning(f"Agent retornou resposta vazia para query: {q}")
                agent_response = {
                    "type": "text",
                    "result": {
                        "mensagem": f"Desculpe, não consegui processar sua pergunta. Por favor, reformule e tente novamente."
                    }
                }
            
            logger.info(f"Agent response received: {agent_response}")

            # ✅ NOVO: Validar resposta com Response Validator
            validation = validate_response(agent_response, q)
            if not validation.is_valid:
                logger.warning(f"⚠️ Validação: confidence={validation.confidence:.2f}, issues={validation.issues}")
                # Adicionar aviso à resposta se houver problemas
                if validation.confidence < 0.5:
                    event_counter += 1
                    yield f"id: {event_counter}\n"
                    yield f"data: {json.dumps({'type': 'warning', 'message': 'Resposta com baixa confiança. Verifique os dados.', 'done': False})}\n\n"
            else:
                logger.info(f"✅ Validação OK: confidence={validation.confidence:.2f}")

            response_type = agent_response.get("type", "text")
            response_content = agent_response.get("result")
            response_text = ""

            if response_type == "text" or response_type == "tool_result":
                response_text = agent_response.get("result", {}).get("mensagem", "") if response_type == "tool_result" else agent_response.get("result", "")
                if not response_text:
                    response_text = str(agent_response.get("result", ""))
                
                if not response_text or (isinstance(response_text, str) and not response_text.strip()):
                    response_text = "Resposta processada, mas nenhum texto foi gerado. Por favor, tente reformular sua pergunta."

                if not isinstance(response_text, str):
                    response_text = str(response_text)
            
            elif response_type == "code_result":
                chart_spec = agent_response.get("chart_spec")

                if response_content and isinstance(response_content, dict) and "result" in response_content:
                    table_data = response_content.get("result")
                    if isinstance(table_data, list) and len(table_data) > 0 and isinstance(table_data[0], dict):
                        event_counter += 1
                        yield f"id: {event_counter}\n"
                        columns = list(table_data[0].keys())
                        yield f"data: {json.dumps({'type': 'table', 'data': table_data, 'columns': columns, 'done': False})}\n\n"
                        logger.info(f"Streaming table data with {len(table_data)} rows...")
                        response_text = f"Análise concluída com {len(table_data)} registros."
                    else:
                        response_text = f"Resultados da sua análise:\n```json\n{json.dumps(response_content, indent=2, ensure_ascii=False)}\n```"
                elif response_content:
                    response_text = f"Resultados da sua análise:\n```json\n{json.dumps(response_content, indent=2, ensure_ascii=False)}\n```"
                else:
                    response_text = "Sua análise foi processada."

                if chart_spec:
                    event_counter += 1
                    yield f"id: {event_counter}\n"
                    yield f"data: {json.dumps({'type': 'chart', 'chart_spec': chart_spec, 'done': False})}\n\n"
                    logger.info("Streaming chart spec...")
            
            # Save Assistant Response to History
            session_manager.add_message(session_id, "assistant", response_text)

            words = response_text.split(" ")
            # Use smaller chunks for smoother streaming (like a real typewriter)
            chunk_size = 1 
            
            logger.info(f"Initiating text streaming of {len(words)} words...")
            
            for i in range(0, len(words), chunk_size):
                chunk_words = words[i:i + chunk_size]
                # Reconstruct spacing correctly
                prefix = " " if i > 0 else ""
                chunk_text = prefix + " ".join(chunk_words)
                
                event_counter += 1
                
                yield f"id: {event_counter}\n"
                yield f"data: {json.dumps({'type': 'text', 'text': chunk_text, 'done': False})}\n\n"
                
                # Small delay to simulate typing speed if needed, but usually network latency is enough
                # await asyncio.sleep(0.01)

            logger.info("Text streaming complete. Sending done signal.")
            yield f"id: {event_counter + 1}\n"
            yield f"data: {json.dumps({'type': 'final', 'text': '', 'done': True})}\n\n"
            
        except APIError as e:
            logger.error(f"Agent API Error in stream: {e.message}", exc_info=True)
            yield f"data: {json.dumps({'type': 'error', 'error': e.message, 'details': e.details})}\n\n"
            yield f"data: {json.dumps({'type': 'final', 'text': '', 'done': True})}\n\n"
        except Exception as e:
            logger.error(f"Unexpected error in stream: {e}", exc_info=True)
            yield f"data: {json.dumps({'type': 'error', 'error': 'Um erro inesperado ocorreu. Tente novamente mais tarde.'})}\n\n"
            yield f"data: {json.dumps({'type': 'final', 'text': '', 'done': True})}\n\n"
    
    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        }
    )


@router.post("/feedback")
async def submit_feedback(
    response_id: str,
    feedback_type: str,
    current_user: Annotated[User, Depends(get_current_active_user)],
    comment: Optional[str] = None,
):
    if query_history is None:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="QueryHistory system not initialized."
        )
    
    feedback_entry = {
        "timestamp": "now", # Placeholder, would import datetime
        "user_id": current_user.username,
        "response_id": response_id,
        "feedback_type": feedback_type,
        "comment": comment
    }
    
    feedback_file_path = Path(settings.LEARNING_FEEDBACK_PATH) / "feedback.jsonl"
    os.makedirs(Path(settings.LEARNING_FEEDBACK_PATH), exist_ok=True)
    try:
        with open(feedback_file_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(feedback_entry, ensure_ascii=False) + "\n")
        logger.info(f"Feedback submitted by {current_user.username}: {feedback_entry}")
    except OSError as e:
        logger.error(f"Failed to write feedback to file: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to save feedback."
        )

    return {"message": "Feedback submitted successfully."}

@router.post("", response_class=ORJSONResponse)
async def send_chat_message(
    request: ChatRequest,
    current_user: Annotated[User, Depends(get_current_active_user)],
) -> dict:
    # Legacy - calling agent without history for now, or could pass session_id if we updated request model
    logger.warning("Legacy chat endpoint used.")
    if caculinha_bi_agent is None:
        raise HTTPException(status_code=500, detail="Agent not init")

    # Assuming no history for legacy non-session calls
    agent_response = await asyncio.to_thread(caculinha_bi_agent.run, user_query=request.query, chat_history=[])
    return {"response": str(agent_response), "full_agent_response": agent_response}