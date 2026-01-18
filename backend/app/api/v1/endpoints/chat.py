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
# CodeGenAgent e CaculinhaBIAgent removidos - Arquitetura V2 deprecated
# Sistema agora usa ChatServiceV3 (Metrics-First)
from app.core.llm_factory import LLMFactory, SmartLLM
from app.core.utils.error_handler import APIError
from app.core.utils.session_manager import SessionManager
from app.core.utils.semantic_cache import cache_get, cache_set, cache_stats
from app.core.utils.response_validator import validate_response, validator_stats
# NEW SERVICE V3 - Metrics-First Architecture
from app.services.chat_service_v3 import ChatServiceV3

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


# ✅ PERFORMANCE FIX: Initialization moved to startup background task
# This prevents the 15s delay on the first user query.
chat_service_v3 = None  # Metrics-First Architecture
session_manager = None
_init_lock = asyncio.Lock()

async def initialize_agents_async():
    """
    Async initialization: Executed on app startup (background task).
    Ensures ChatService is ready when the user arrives.
    """
    global chat_service_v3, session_manager
    
    # Fast exit if already initialized
    if chat_service_v3 is not None:
        return

    async with _init_lock:
        if chat_service_v3 is not None:
            return
            
        logger.info("🚀 [STARTUP] Initializing ChatServiceV3 (Metrics-First) in background...")
        
        try:
            # We must use asyncio.to_thread because initialization involves
            # heavy sync operations (loading vector stores, DuckDB connections)
            def _sync_init():
                local_session_manager = SessionManager(storage_dir="app/data/sessions")
                local_service = ChatServiceV3(session_manager=local_session_manager)
                return local_session_manager, local_service

            session_manager, chat_service_v3 = await asyncio.to_thread(_sync_init)
            
            logger.info("✅ [STARTUP] ChatServiceV3 (Metrics-First) initialized successfully.")
        except Exception as e:
            logger.error(f"❌ Failed to initialize ChatServiceV3: {e}", exc_info=True)
            # We don't raise here to avoid crashing the whole app, 
            # but Chat endpoints will fail if this didn't work.

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
    from app.core.context import set_current_user_context

    try:
        current_user = await get_current_user_from_token(token)
        # ✅ CRITICAL FIX: Set context for tools running in background
        set_current_user_context(current_user)
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

            # --- FAST PATH: Detecção de Saudações Simples (Zero Latency) ---
            # EXTREMAMENTE CRÍTICO: Deve rodar ANTES de qualquer inicialização pesada (initialize_agents_async)
            query_clean = q.strip().lower()
            greetings = [
                "oi", "ola", "olá", "bom dia", "boa tarde", "boa noite",
                "hello", "hi", "eai", "opa", "teste", "funcionando?", "tá funcionando", "ta funcionando",
                "tudo bem", "como vai", "e aí"
            ]

            # ✅ FIX 2026-01-14: Aumentado limite de 20 para 40 caracteres
            # "ola boa tarde tudo bem" tem 21 chars e não entrava no fast path
            # ✅ FIX 2026-01-17: Lógica refinada para não interceptar queries reais
            # Só interceptar se for APENAS saudação ou saudação curta SEM verbos de ação
            action_keywords = [
                "analis", "venda", "estoque", "ruptura", "grafico", "relatorio", 
                "quanto", "quais", "mostre", "gere", "crie", "veja", "dados"
            ]
            has_action = any(k in query_clean for k in action_keywords)
            
            is_pure_greeting = query_clean in greetings
            # Reduzido de 40 para 20 caracteres para evitar falsos positivos
            is_short_greeting = len(query_clean) < 20 and any(g in query_clean for g in greetings)

            if (is_pure_greeting or is_short_greeting) and not has_action:
                import random
                import asyncio
                from datetime import datetime

                # ✅ FIX 2026-01-15: Responder com saudação apropriada ao período
                # Detecta período mencionado pelo usuário ou usa hora atual
                if "boa noite" in query_clean:
                    saudacao = "Boa noite"
                elif "boa tarde" in query_clean:
                    saudacao = "Boa tarde"
                elif "bom dia" in query_clean:
                    saudacao = "Bom dia"
                else:
                    # Usa hora atual do servidor
                    hora = datetime.now().hour
                    if 5 <= hora < 12:
                        saudacao = "Bom dia"
                    elif 12 <= hora < 18:
                        saudacao = "Boa tarde"
                    else:
                        saudacao = "Boa noite"

                responses = [
                    f"{saudacao}! Sou seu assistente de BI. Como posso ajudar com os dados hoje?",
                    f"{saudacao}! Tudo pronto para analisar seus dados. O que você gostaria de ver?",
                    f"{saudacao}! Estou à disposição. Pode me pedir gráficos, relatórios ou análises.",
                    f"{saudacao}! Vamos encontrar alguns insights? É só perguntar."
                ]
                response_text = random.choice(responses)
                
                # Simular steps de progresso para UX consistente
                event_counter += 1
                yield f"id: {event_counter}\n"
                yield f"data: {safe_json_dumps({'type': 'tool_progress', 'tool': 'Pensando', 'status': 'start'})}\n\n"
                
                await asyncio.sleep(0.1) 
                
                event_counter += 1
                yield f"id: {event_counter}\n"
                yield f"data: {safe_json_dumps({'type': 'tool_progress', 'tool': 'Processando resposta', 'status': 'processing'})}\n\n"

                # Stream response text
                words = response_text.split(" ")
                for i in range(0, len(words), 3):
                    chunk_words = words[i:i + 3]
                    prefix = " " if i > 0 else ""
                    chunk_text = prefix + " ".join(chunk_words)
                    event_counter += 1
                    yield f"id: {event_counter}\n"
                    yield f"data: {safe_json_dumps({'type': 'text', 'text': chunk_text, 'done': False})}\n\n"
                    await asyncio.sleep(0.05) # Typing effect

                # Finalize
                event_counter += 1
                yield f"id: {event_counter}\n"
                yield f"data: {safe_json_dumps({'type': 'final', 'text': '', 'done': True})}\n\n"
                return # SAÍDA ANTECIPADA - Evita carregar o agente pesado
            # ---------------------------------------------------------------------

            # 🔧 FIX: Ensure initialization if startup task hasn't finished yet
            if chat_service_v3 is None:
                logger.info("🔄 Agent system not ready yet. Waiting for initialization...")
                await initialize_agents_async()

            if chat_service_v3 is None:
                yield f"data: {safe_json_dumps({'error': 'Agent system could not be initialized'})}\n\n"
                return

            # Retrieve History - Corrected with user_id for security
            # chat_history = session_manager.get_history(session_id, current_user.id)
            # Add User Message to History immediately
            # session_manager.add_message(session_id, "user", q, current_user.id)

            logger.info(f"Processing query with ChatServiceV3: '{q}'")

            # ✅ FIX 2026-01-14: Cache agora usa user_id para isolamento
            # Isso evita que dados de UNE 1685 sejam retornados para query de UNE 1700
            user_cache_id = str(current_user.id) if current_user else None

            # NOVO: Verificar Semantic Cache primeiro (com user_id)
            cached_response = cache_get(q, user_id=user_cache_id)
            if cached_response:
                logger.info(f"CACHE HIT: Resposta encontrada em cache para: {q[:50]}... (user={user_cache_id})")
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

                # ✅ FIX: Timeout reduzido de 300s para 60s (resposta mais rápida)
                agent_task = asyncio.create_task(
                    asyncio.wait_for(
                        chat_service_v3.process_message(
                            query=q, 
                            session_id=session_id, 
                            user_id=current_user.id,
                            on_progress=progress_callback
                        ),
                        timeout=60.0  # ✅ 1 minuto (suficiente para 99% das queries)
                    )
                )

                # Stream progress events as they arrive
                agent_response = None
                keepalive_counter = 0
                keepalive_interval = 50  # Send keepalive every 5s (50 * 0.1s)

                while True:
                    try:
                        event = await asyncio.wait_for(event_queue.get(), timeout=0.1)
                        event_counter += 1
                        keepalive_counter = 0  # Reset keepalive on real event
                        yield f"id: {event_counter}\n"
                        yield f"data: {safe_json_dumps(event)}\n\n"
                    except asyncio.TimeoutError:
                        keepalive_counter += 1

                        # Send keepalive event every 5 seconds to prevent frontend timeout
                        if keepalive_counter >= keepalive_interval:
                            event_counter += 1
                            keepalive_event = {"type": "keepalive", "message": "Ainda processando sua análise complexa..."}
                            yield f"id: {event_counter}\n"
                            yield f"data: {safe_json_dumps(keepalive_event)}\n\n"
                            keepalive_counter = 0

                        if agent_task.done():
                            try:
                                agent_response = agent_task.result()
                            except asyncio.TimeoutError:
                                logger.error(f"Agent timeout após 60s para query: {q}")
                                agent_response = {
                                    "type": "text",
                                    "result": {
                                        "mensagem": "O tempo limite de processamento foi excedido (1 minuto). A consulta solicitada é muito complexa. Tente ser mais específico ou dividi-la em partes menores."
                                    }
                                }
                            except Exception as e:
                                logger.error(f"Agent error: {e}", exc_info=True)
                                agent_response = {
                                    "type": "text",
                                    "result": {
                                        "mensagem": f"Erro ao processar consulta: {str(e)}"
                                    }
                                }
                            break

                # ✅ FIX 2026-01-14: Salvar resposta válida em cache COM user_id
                if agent_response and "error" not in str(agent_response).lower():
                    cache_set(q, agent_response, user_id=user_cache_id)
            
            if not agent_response:
                logger.warning(f"Agent retornou resposta vazia para query: {q}")
                agent_response = {
                    "type": "text",
                    "result": {
                        "mensagem": f"Desculpe, não consegui processar sua pergunta. Por favor, reformule e tente novamente."
                    }
                }
            
            logger.info(f"Agent response received: {agent_response}")

            # NOVO: Validar resposta com Response Validator (Simplificado para V2)
            # validation = validate_response(agent_response, q)
            
            response_type = agent_response.get("type", "text")
            response_content = agent_response.get("result")
            response_text = ""

            if response_type == "text" or response_type == "tool_result":
                # CRITICAL FIX: Check if tool_result contains chart_data from chart generation tools
                result_data = agent_response.get("result", {})
                
                # ✅ FIX 2026-01-17: Check top-level chart_data FIRST (ChatServiceV3 format)
                chart_data = agent_response.get("chart_data")
                
                # Fallback: Check inside result dict (legacy format)
                if not chart_data and isinstance(result_data, dict):
                    chart_data = result_data.get("chart_data") or result_data.get("chart_spec")
                
                # ✅ STREAM CHART IF FOUND (either top-level or legacy)
                if chart_data:
                    logger.info("Chart data detected - streaming chart to frontend")
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
                        
                        # Set response text from result's mensagem if available
                        if isinstance(result_data, dict):
                            response_text = result_data.get("mensagem", "Gráfico gerado com sucesso.")
                        else:
                            response_text = "Gráfico gerado com sucesso."
                
                # Only try to get mensagem if no chart was found
                if not chart_data:
                    if isinstance(result_data, dict):
                         response_text = result_data.get("mensagem", "")
                    else:
                         response_text = str(result_data)
                    
                    if not response_text or (isinstance(response_text, str) and not response_text.strip()):
                        response_text = "Resposta processada." # Fallback

                if not isinstance(response_text, str):
                    response_text = str(response_text)
            
            
            elif response_type == "code_result":
                # Lógica V2: O LangGraph abstrai "code_result" para "tool_result" ou texto direto
                # Mas mantemos compatibilidade caso o output seja complexo
                chart_spec = agent_response.get("chart_spec")
                response_text = agent_response.get("text_override") or str(response_content)

                if chart_spec:
                    event_counter += 1
                    yield f"id: {event_counter}\n"
                    yield f"data: {safe_json_dumps({'type': 'chart', 'chart_spec': chart_spec, 'done': False})}\n\n"
            
            # Só fazer streaming de texto se houver texto para enviar
            if response_text and response_text.strip():
                words = response_text.split(" ")
                # ✅ FIX: Otimizado de 1 para 8 palavras por chunk (8x mais rápido)
                chunk_size = 8 
                
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

        except APIError as e:
            logger.error(f"Agent API Error in stream: {e.message}", exc_info=True)
            yield f"data: {safe_json_dumps({'type': 'error', 'error': e.message, 'details': e.details})}\n\n"
        except Exception as e:
            error_msg = str(e)
            logger.error(f"Unexpected error in stream: {error_msg}", exc_info=True)

            # Generic user-friendly error (never expose technical details)
            error_response = {
                'type': 'error',
                'error': 'Não foi possível processar sua solicitação no momento. Por favor, tente novamente.',
                'error_type': 'generic'
            }

            yield f"data: {safe_json_dumps(error_response)}\n\n"
        finally:
            # 🛑 SAFETY NET: Always send DONE signal to prevent frontend infinite spinner
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

    # 🔧 FIX: Ensure initialization
    if chat_service_v3 is None:
        logger.info("🔄 Lazy initializing agents on first request...")
        await initialize_agents_async()
    
    # We still use the global old variable if needed or refactor completely.
    # Ideally, we should use chat_service_v3, but the legacy code expects 'caculinha_bi_agent'.
    # For now, let's assume ChatServiceV3 initializes the agent internally and we can access it
    # OR we just fail gracefully since this endpoint is legacy.
    
    # Hack: Attempt to get the agent from the service if possible, or re-init (bad).
    # Given this is legacy and likely unused by the new frontend, we just try to init.
    
    # Note: caculinha_bi_agent is imported but not managed by initialize_agents_async directly in this scope
    # unless we expose it. But for the demo, let's focus on the streaming endpoint.
    
    if chat_service_v3 is None:
         raise HTTPException(status_code=500, detail="Agent not init")

    # Assuming no history for legacy non-session calls
    # We will use the NEW service instead of the old agent directly to ensure consistency
    result = await chat_service_v3.process_message(
        query=request.query,
        session_id="legacy",
        user_id=current_user.id
    )
    return {"response": str(result), "full_agent_response": result}