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
import numpy as np
import pandas as pd
from decimal import Decimal
from datetime import datetime, date

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
from app.core.agents.caculinha_bi_agent import CaculinhaBIAgent, SYSTEM_PROMPT
from app.core.llm_gemini_adapter import GeminiLLMAdapter
from app.core.utils.error_handler import APIError
from app.core.utils.session_manager import SessionManager
from app.core.utils.semantic_cache import cache_get, cache_set, cache_stats
from app.core.utils.response_validator import validate_response, validator_stats

logger = logging.getLogger(__name__)


def safe_json_dumps(obj: Any, **kwargs) -> str:
    """
    Safely serialize any Python object to JSON string.
    Handles MapComposite, numpy types, pandas types, datetime, and other non-serializable objects.
    """
    def default_handler(o):
        # Handle numpy types
        if isinstance(o, (np.integer, np.int64, np.int32, np.int16, np.int8)):
            return int(o)
        elif isinstance(o, (np.floating, np.float64, np.float32, np.float16)):
            if np.isnan(o) or np.isinf(o):
                return None
            return float(o)
        elif isinstance(o, np.ndarray):
            return o.tolist()
        elif isinstance(o, np.bool_):
            return bool(o)

        # Handle pandas types
        elif isinstance(o, pd.Timestamp):
            return o.isoformat()
        elif isinstance(o, pd.Timedelta):
            return str(o)
        elif pd.isna(o):
            return None

        # Handle datetime types
        elif isinstance(o, (datetime, date)):
            return o.isoformat()

        # Handle Decimal
        elif isinstance(o, Decimal):
            return float(o)

        # Handle bytes
        elif isinstance(o, bytes):
            return o.decode('utf-8', errors='ignore')

        # Handle SQLAlchemy Row/MapComposite and similar mapping types
        elif hasattr(o, '_mapping'):
            return dict(o._mapping)
        elif hasattr(o, '__dict__') and not isinstance(o, type):
            # Generic object with __dict__
            return {k: v for k, v in o.__dict__.items() if not k.startswith('_')}

        # Last resort: convert to string
        else:
            return str(o)

    try:
        # Merge default handler with any custom kwargs
        if 'default' not in kwargs:
            kwargs['default'] = default_handler
        return json.dumps(obj, **kwargs)
    except Exception as e:
        logger.error(f"Failed to serialize object: {e}", exc_info=True)
        # Ultimate fallback: return error as JSON
        return json.dumps({"error": f"Serialization failed: {str(e)}"}, ensure_ascii=False)


# ✅ PERFORMANCE FIX: Lazy Initialization - Agentes são criados no primeiro request
# Isso reduz startup de ~15s para <3s
# Trade-off: Primeira query +2-3s, mas startup instantâneo
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
    """
    Lazy initialization: Executado apenas no primeiro request ao invés de no startup.
    Reduz tempo de inicialização do backend de ~15s para <3s.
    """
    global llm, field_mapper, query_retriever, pattern_matcher, response_cache, query_history, code_gen_agent, caculinha_bi_agent, session_manager
    if llm is None:
        logger.info("🚀 [LAZY INIT] Initializing LLM and Agents on first request...")
        if not settings.GEMINI_API_KEY:
            logger.error("GEMINI_API_KEY is not set. LLM will not be initialized.")
            raise ValueError("GEMINI_API_KEY must be set in environment variables.")

        # System instruction from CaculinhaBIAgent
        logger.info("Using Simplified System Prompt (Context7 removed)")

        # 🔧 FIX: CaculinhaBIAgent expects the ADAPTER, not the inner LLM
        llm = GeminiLLMAdapter(
            model_name=settings.LLM_MODEL_NAME,
            gemini_api_key=settings.GEMINI_API_KEY,
            system_instruction=SYSTEM_PROMPT
        )

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
        logger.info("✅ [LAZY INIT] LLM and Agents initialized successfully.")

# ❌ REMOVIDO: _initialize_agents_and_llm() executado no import time
# ✅ AGORA: Inicializado no primeiro request via _initialize_agents_and_llm()

router = APIRouter(prefix="/chat", tags=["Chat"])


class ChatRequest(BaseModel):
    query: str


class FeedbackRequest(BaseModel):
    response_id: str
    feedback_type: str
    comment: Optional[str] = None


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
            yield f"data: {safe_json_dumps({'error': 'Não autenticado'})}\n\n"
        return StreamingResponse(error_generator(), media_type="text/event-stream")

    last_event_id = request.headers.get("Last-Event-ID")
    logger.info(f"==> SSE STREAM REQUEST: {q} (Session: {session_id}) (Last-Event-ID: {last_event_id}) <==")

    async def event_generator():
        try:
            event_counter = int(last_event_id) if last_event_id else 0

            # 🔧 FIX: Lazy initialization on first request
            if caculinha_bi_agent is None:
                logger.info("🔄 Lazy initializing agents on first request...")
                _initialize_agents_and_llm()

            if caculinha_bi_agent is None:
                yield f"data: {safe_json_dumps({'error': 'Agent system not initialized'})}\n\n"
                return

            # Retrieve History - Corrected with user_id for security
            chat_history = session_manager.get_history(session_id, current_user.id)
            # Add User Message to History immediately
            session_manager.add_message(session_id, "user", q, current_user.id)

            logger.info(f"Processing query with CaculinhaBIAgent: '{q}' | History len: {len(chat_history)}")
            
            # NOVO: Verificar Semantic Cache primeiro
            cached_response = cache_get(q)
            if cached_response:
                logger.info(f"CACHE HIT: Resposta encontrada em cache para: {q[:50]}...")
                event_counter += 1
                yield f"id: {event_counter}\n"
                yield f"data: {safe_json_dumps({'type': 'cache_hit', 'done': False})}\n\n"
                agent_response = cached_response
            else:
                # OPTIMIZATION 2025: Stream progress events during agent execution
                import asyncio
                event_queue = asyncio.Queue()

                async def progress_callback(event):
                    await event_queue.put(event)

                # Start agent in background task
                agent_task = asyncio.create_task(
                    caculinha_bi_agent.run_async(user_query=q, chat_history=chat_history, on_progress=progress_callback)
                )

                # Stream progress events as they arrive
                agent_response = None
                while True:
                    try:
                        event = await asyncio.wait_for(event_queue.get(), timeout=0.1)
                        event_counter += 1
                        yield f"id: {event_counter}\n"
                        yield f"data: {safe_json_dumps(event)}\n\n"
                    except asyncio.TimeoutError:
                        if agent_task.done():
                            agent_response = agent_task.result()
                            break

                # Salvar resposta válida em cache
                if agent_response and "error" not in str(agent_response).lower():
                    cache_set(q, agent_response)
            
            if not agent_response:
                logger.warning(f"Agent retornou resposta vazia para query: {q}")
                agent_response = {
                    "type": "text",
                    "result": {
                        "mensagem": f"Desculpe, não consegui processar sua pergunta. Por favor, reformule e tente novamente."
                    }
                }
            
            logger.info(f"Agent response received: {agent_response}")

            # NOVO: Validar resposta com Response Validator
            validation = validate_response(agent_response, q)
            if not validation.is_valid:
                logger.warning(f"Validacao: confidence={validation.confidence:.2f}, issues={validation.issues}")
                # Adicionar aviso à resposta se houver problemas
                if validation.confidence < 0.5:
                    event_counter += 1
                    yield f"id: {event_counter}\n"
                    yield f"data: {safe_json_dumps({'type': 'warning', 'message': 'Resposta com baixa confiança. Verifique os dados.', 'done': False})}\n\n"
            else:
                logger.info(f"Validacao OK: confidence={validation.confidence:.2f}")

            response_type = agent_response.get("type", "text")
            response_content = agent_response.get("result")
            response_text = ""

            if response_type == "text" or response_type == "tool_result":
                # CRITICAL FIX: Check if tool_result contains chart_data from chart generation tools
                result_data = agent_response.get("result", {})
                chart_data = None
                
                if isinstance(result_data, dict):
                    chart_data = result_data.get("chart_data")
                    if chart_data:
                        logger.info("Chart data detected in tool_result - streaming chart to frontend")
                        # Parse chart_data if it's a JSON string
                        import json
                        if isinstance(chart_data, str):
                            try:
                                chart_data = json.loads(chart_data)
                            except json.JSONDecodeError:
                                logger.error("Failed to parse chart_data JSON string")
                                chart_data = None
                        
                        if chart_data:
                            # Stream the chart
                            event_counter += 1
                            yield f"id: {event_counter}\n"
                            yield f"data: {safe_json_dumps({'type': 'chart', 'chart_spec': chart_data, 'done': False})}\n\n"
                            
                            # Set response text from summary or default
                            chart_summary = result_data.get("summary", {})
                            response_text = f"Aqui está o gráfico solicitado. Tipo: {result_data.get('chart_type', 'gráfico')}."
                            if chart_summary:
                                response_text += f" {chart_summary.get('mensagem', '')}"
                
                # Only try to get mensagem if no chart was found
                if not chart_data:
                    response_text = result_data.get("mensagem", "") if isinstance(result_data, dict) and response_type == "tool_result" else agent_response.get("result", "")
                    if not response_text:
                        response_text = str(agent_response.get("result", ""))
                    
                    if not response_text or (isinstance(response_text, str) and not response_text.strip()):
                        response_text = "Resposta processada, mas nenhum texto foi gerado. Por favor, tente reformular sua pergunta."

                if not isinstance(response_text, str):
                    response_text = str(response_text)
            
            
            elif response_type == "code_result":
                chart_spec = agent_response.get("chart_spec")
                text_override = agent_response.get("text_override")

                # Log para debug
                logger.info(f"DEBUG: response_content = {response_content}")
                
                # O agent retorna: {"result": {"result": [...], "chart_spec": ...}, "chart_spec": ...}
                # Então precisamos acessar response_content["result"] para pegar os dados
                if response_content and isinstance(response_content, dict):
                    # Verificar se há dados aninhados em "result"
                    if "result" in response_content:
                        table_data = response_content.get("result")
                    else:
                        # Caso os dados estejam diretamente em response_content
                        table_data = response_content
                    
                    logger.info(f"DEBUG: table_data type = {type(table_data)}, is_list = {isinstance(table_data, list)}")
                    if isinstance(table_data, list):
                        logger.info(f"DEBUG: table_data length = {len(table_data)}, first_item = {table_data[0] if len(table_data) > 0 else 'empty'}")
                    
                    if isinstance(table_data, list) and len(table_data) > 0 and isinstance(table_data[0], dict):
                        # Enviar texto introdutório ANTES da tabela
                        intro_text = f"Aqui estão os {len(table_data)} resultados da sua consulta:"
                        
                        # Stream do texto introdutório palavra por palavra
                        intro_words = intro_text.split(" ")
                        for i in range(0, len(intro_words), 1):
                            chunk_words = intro_words[i:i + 1]
                            prefix = " " if i > 0 else ""
                            chunk_text = prefix + " ".join(chunk_words)
                            event_counter += 1
                            yield f"id: {event_counter}\n"
                            yield f"data: {safe_json_dumps({'type': 'text', 'text': chunk_text, 'done': False})}\n\n"
                        
                        # Converter MapComposite para dict antes de serializar
                        def convert_row(row):
                            """Converte objetos MapComposite e similares para dict"""
                            if hasattr(row, '_mapping'):
                                return dict(row._mapping)
                            elif isinstance(row, dict):
                                # Converter valores internos também
                                return {k: (dict(v._mapping) if hasattr(v, '_mapping') else v) for k, v in row.items()}
                            return row
                        
                        # Converter todos os dados
                        clean_table_data = [convert_row(row) for row in table_data]
                        
                        # Agora enviar a tabela com dados limpos
                        event_counter += 1
                        yield f"id: {event_counter}\n"
                        columns = list(clean_table_data[0].keys())
                        yield f"data: {safe_json_dumps({'type': 'table', 'data': clean_table_data, 'columns': columns, 'done': False})}\n\n"
                        logger.info(f"Streaming table data with {len(clean_table_data)} rows...")
                        
                        # Limpar response_text para não enviar texto adicional
                        response_text = ""
                    else:
                        # Use override if available (Context7), otherwise fallback to JSON
                        if text_override:
                            response_text = text_override
                        else:
                            response_text = f"Resultados da sua análise:\n```json\n{safe_json_dumps(response_content, indent=2, ensure_ascii=False)}\n```"
                elif response_content:
                    if text_override:
                        response_text = text_override
                    else:
                        response_text = f"Resultados da sua análise:\n```json\n{safe_json_dumps(response_content, indent=2, ensure_ascii=False)}\n```"
                else:
                    response_text = text_override if text_override else "Sua análise foi processada."

                if chart_spec:
                    event_counter += 1
                    yield f"id: {event_counter}\n"
                    yield f"data: {safe_json_dumps({'type': 'chart', 'chart_spec': chart_spec, 'done': False})}\n\n"
                    logger.info("Streaming chart spec...")
            
            # Save Assistant Response to History - Corrected with user_id
            session_manager.add_message(session_id, "assistant", response_text if response_text else "Dados enviados", current_user.id)

            # Só fazer streaming de texto se houver texto para enviar
            if response_text and response_text.strip():
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
                    yield f"data: {safe_json_dumps({'type': 'text', 'text': chunk_text, 'done': False})}\n\n"
                    
                    # Small delay to simulate typing speed if needed, but usually network latency is enough
                    # await asyncio.sleep(0.01)

            logger.info("Text streaming complete. Sending done signal.")
            yield f"id: {event_counter + 1}\n"
            yield f"data: {safe_json_dumps({'type': 'final', 'text': '', 'done': True})}\n\n"

        except APIError as e:
            logger.error(f"Agent API Error in stream: {e.message}", exc_info=True)
            yield f"data: {safe_json_dumps({'type': 'error', 'error': e.message, 'details': e.details})}\n\n"
            yield f"data: {safe_json_dumps({'type': 'final', 'text': '', 'done': True})}\n\n"
        except Exception as e:
            logger.error(f"Unexpected error in stream: {e}", exc_info=True)
            yield f"data: {safe_json_dumps({'type': 'error', 'error': 'Um erro inesperado ocorreu. Tente novamente mais tarde.'})}\n\n"
            yield f"data: {safe_json_dumps({'type': 'final', 'text': '', 'done': True})}\n\n"
    
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
    feedback_data: FeedbackRequest,
    current_user: Annotated[User, Depends(get_current_active_user)],
):
    if query_history is None:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="QueryHistory system not initialized."
        )
    
    feedback_entry = {
        "timestamp": "now", # Placeholder, would import datetime
        "user_id": current_user.username,
        "response_id": feedback_data.response_id,
        "feedback_type": feedback_data.feedback_type,
        "comment": feedback_data.comment
    }
    
    feedback_file_path = Path(settings.LEARNING_FEEDBACK_PATH) / "feedback.jsonl"
    os.makedirs(Path(settings.LEARNING_FEEDBACK_PATH), exist_ok=True)
    try:
        with open(feedback_file_path, "a", encoding="utf-8") as f:
            f.write(safe_json_dumps(feedback_entry, ensure_ascii=False) + "\n")
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

    # 🔧 FIX: Lazy initialization on first request
    if caculinha_bi_agent is None:
        logger.info("🔄 Lazy initializing agents on first request...")
        _initialize_agents_and_llm()

    if caculinha_bi_agent is None:
        raise HTTPException(status_code=500, detail="Agent not init")

    # Assuming no history for legacy non-session calls
    agent_response = await asyncio.to_thread(caculinha_bi_agent.run, user_query=request.query, chat_history=[])
    return {"response": str(agent_response), "full_agent_response": agent_response}