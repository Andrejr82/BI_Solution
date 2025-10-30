"""
API Backend FastAPI para integração com Frontend React
Fornece endpoints REST para o claude-share-buddy frontend
Mantém compatibilidade com Streamlit existente
Data: 2025-10-25
"""

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
import os
import sys
from datetime import datetime
import logging
from contextlib import asynccontextmanager

# Adicionar path do projeto
sys.path.insert(0, os.path.dirname(__file__))

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# ============================================================================
# MODELS (Pydantic)
# ============================================================================

class ChatRequest(BaseModel):
    """Request para endpoint de chat"""
    message: str = Field(..., min_length=1, description="Mensagem do usuário")
    session_id: str = Field(default="anonymous", description="ID da sessão")

class ChatResponse(BaseModel):
    """Response do endpoint de chat"""
    success: bool
    response: Dict[str, Any]
    timestamp: str

class HealthResponse(BaseModel):
    """Response do health check"""
    status: str
    timestamp: str
    version: str
    backend: Dict[str, Any]

class MetricsResponse(BaseModel):
    """Response de métricas"""
    success: bool
    metrics: Dict[str, Any]
    timestamp: str

class ExamplesResponse(BaseModel):
    """Response de exemplos"""
    success: bool
    examples: Dict[str, List[str]]
    timestamp: str

class FeedbackRequest(BaseModel):
    """Request para feedback"""
    type: str = Field(..., description="Tipo: 'positive' ou 'negative'")
    query: str = Field(default="", description="Query original")
    code: str = Field(default="", description="Código gerado")
    comment: str = Field(default="", description="Comentário do usuário")

class LoginRequest(BaseModel):
    """Request para login"""
    username: str = Field(..., min_length=3, description="Nome de usuário")
    password: str = Field(..., min_length=3, description="Senha")

class LoginResponse(BaseModel):
    """Response do login"""
    success: bool
    message: str
    user: Optional[Dict[str, Any]] = None
    token: Optional[str] = None

# ============================================================================
# BACKEND INITIALIZATION (Lazy Loading)
# ============================================================================

backend_components = None

def initialize_backend():
    """Inicializa componentes do backend Agent_Solution_BI"""
    global backend_components

    if backend_components is not None:
        return backend_components

    try:
        logger.info("Inicializando backend Agent_Solution_BI...")

        from core.factory.component_factory import ComponentFactory
        from core.connectivity.parquet_adapter import ParquetAdapter
        from core.agents.code_gen_agent import CodeGenAgent
        from core.graph.graph_builder import GraphBuilder
        from core.utils.query_history import QueryHistory

        # Inicializar LLM
        llm_adapter = ComponentFactory.get_llm_adapter("gemini")

        # Inicializar ParquetAdapter
        parquet_path = os.path.join(os.getcwd(), "data", "parquet", "*.parquet")
        parquet_adapter = ParquetAdapter(parquet_path)

        # Inicializar CodeGen
        code_gen_agent = CodeGenAgent(llm_adapter=llm_adapter, data_adapter=parquet_adapter)

        # Inicializar QueryHistory
        history_path = os.path.join(os.getcwd(), "data", "query_history")
        query_history = QueryHistory(history_dir=history_path)

        # Construir Grafo
        graph_builder = GraphBuilder(
            llm_adapter=llm_adapter,
            parquet_adapter=parquet_adapter,
            code_gen_agent=code_gen_agent
        )
        agent_graph = graph_builder.build()

        backend_components = {
            "llm_adapter": llm_adapter,
            "parquet_adapter": parquet_adapter,
            "code_gen_agent": code_gen_agent,
            "agent_graph": agent_graph,
            "query_history": query_history,
            "initialized_at": datetime.now().isoformat()
        }

        logger.info("✅ Backend inicializado com sucesso!")
        return backend_components

    except Exception as e:
        logger.error(f"❌ Erro ao inicializar backend: {e}", exc_info=True)
        return None

# ============================================================================
# FASTAPI APP
# ============================================================================

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Gerenciar ciclo de vida da aplicação"""
    # Startup
    logger.info("🚀 Inicializando API Server...")
    initialize_backend()
    yield
    # Shutdown
    logger.info("🛑 Desligando API Server...")

app = FastAPI(
    title="Agent Solution BI API",
    description="API REST para integração com Frontend React e Streamlit",
    version="1.0.0",
    lifespan=lifespan
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8080", "http://localhost:8501"],  # Frontend React e Streamlit
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============================================================================
# ENDPOINTS
# ============================================================================

@app.get("/", response_model=Dict[str, str])
async def root():
    """Endpoint raiz"""
    return {
        "message": "Agent Solution BI API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/api/health"
    }

@app.get("/api/health", response_model=HealthResponse)
async def health_check():
    """Verifica saúde da API e backend"""
    components = initialize_backend()

    backend_status = {
        "initialized": components is not None,
        "components": list(components.keys()) if components else [],
        "initialized_at": components.get("initialized_at") if components else None
    }

    return HealthResponse(
        status="healthy" if components else "unhealthy",
        timestamp=datetime.now().isoformat(),
        version="1.0.0",
        backend=backend_status
    )

@app.post("/api/login", response_model=LoginResponse)
async def login(request: LoginRequest):
    """
    Autentica usuário usando o sistema de auth do backend

    Args:
        request: LoginRequest com username e password

    Returns:
        LoginResponse com sucesso, mensagem e dados do usuário
    """
    try:
        # Importar sistema de autenticação
        from core.database import sql_server_auth_db as auth_db

        # Autenticar usuário (retorna role, error_message)
        role, error_message = auth_db.autenticar_usuario(request.username, request.password)

        if role:
            # Login bem-sucedido
            # Carregar permissões do usuário
            try:
                permissions = auth_db.load_user_permissions(request.username)
            except:
                permissions = []

            return LoginResponse(
                success=True,
                message="Login realizado com sucesso!",
                user={
                    "username": request.username,
                    "role": role,
                    "permissions": permissions
                },
                token=f"session_{request.username}_{datetime.now().timestamp()}"
            )
        else:
            # Login falhou
            return LoginResponse(
                success=False,
                message=error_message or "Usuário ou senha inválidos"
            )

    except Exception as e:
        logger.error(f"Erro no login: {e}", exc_info=True)
        return LoginResponse(
            success=False,
            message=f"Erro ao processar login: {str(e)}"
        )

@app.post("/api/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Processa mensagem do chat e retorna resposta da IA

    Args:
        request: ChatRequest com message e session_id

    Returns:
        ChatResponse com a resposta processada
    """
    try:
        # Inicializar backend se necessário
        components = initialize_backend()
        if not components:
            raise HTTPException(status_code=500, detail="Backend não disponível")

        # Processar com agent_graph
        from langchain_core.messages import HumanMessage

        agent_graph = components['agent_graph']
        graph_input = {
            "messages": [HumanMessage(content=request.message)],
            "query": request.message
        }

        logger.info(f"Processando query: {request.message[:50]}...")
        final_state = agent_graph.invoke(graph_input)
        agent_response = final_state.get("final_response", {})

        # Registrar no histórico
        query_history = components['query_history']
        query_history.add_query(
            query=request.message,
            session_id=request.session_id,
            success=agent_response.get("type") != "error",
            results_count=len(agent_response.get("result", {}).get("chart_data", {}).get("x", [])),
            error=agent_response.get("content") if agent_response.get("type") == "error" else None,
            processing_time=agent_response.get("processing_time", 0)
        )

        return ChatResponse(
            success=True,
            response=agent_response,
            timestamp=datetime.now().isoformat()
        )

    except Exception as e:
        logger.error(f"Erro ao processar chat: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/metrics", response_model=MetricsResponse)
async def get_metrics():
    """Retorna métricas do sistema"""
    try:
        # TODO: Implementar métricas reais do sistema
        # Por enquanto, retornar dados mock
        metrics = {
            "vendas_hoje": "R$ 45.2K",
            "pedidos": 328,
            "ticket_medio": "R$ 137.80",
            "clientes_ativos": "1.2K",
            "trends": {
                "vendas": 12.5,
                "pedidos": 8.2,
                "ticket": -3.1,
                "clientes": 15.3
            }
        }

        return MetricsResponse(
            success=True,
            metrics=metrics,
            timestamp=datetime.now().isoformat()
        )

    except Exception as e:
        logger.error(f"Erro ao obter métricas: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/queries/history")
async def get_query_history(limit: int = 50):
    """Retorna histórico de queries"""
    try:
        components = initialize_backend()
        if not components:
            raise HTTPException(status_code=500, detail="Backend não disponível")

        query_history = components['query_history']

        # Obter histórico
        history = query_history.get_history(limit=limit)

        return {
            "success": True,
            "history": history,
            "count": len(history),
            "timestamp": datetime.now().isoformat()
        }

    except Exception as e:
        logger.error(f"Erro ao obter histórico: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/examples", response_model=ExamplesResponse)
async def get_examples():
    """Retorna exemplos de perguntas"""
    examples = {
        "vendas": [
            "Produto mais vendido",
            "Top 10 produtos",
            "Ranking de vendas na une scr"
        ],
        "unes": [
            "Ranking de vendas por UNE",
            "Top 5 produtos da une 261",
            "Vendas totais de cada une"
        ],
        "segmentos": [
            "Qual segmento mais vendeu?",
            "Top 10 produtos do segmento TECIDOS",
            "Ranking dos segmentos"
        ],
        "analises": [
            "Evolução de vendas dos últimos 12 meses",
            "Produtos sem movimento",
            "Análise ABC de produtos"
        ]
    }

    return ExamplesResponse(
        success=True,
        examples=examples,
        timestamp=datetime.now().isoformat()
    )

@app.post("/api/save-chart")
async def save_chart(request: Request):
    """Salva gráfico no dashboard"""
    try:
        data = await request.json()
        chart_data = data.get('chart_data')
        title = data.get('title', 'Gráfico')
        query = data.get('query', '')

        if not chart_data:
            raise HTTPException(status_code=400, detail="Dados do gráfico não fornecidos")

        # TODO: Implementar salvamento persistente

        return {
            "success": True,
            "message": "Gráfico salvo com sucesso",
            "timestamp": datetime.now().isoformat()
        }

    except Exception as e:
        logger.error(f"Erro ao salvar gráfico: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/feedback")
async def submit_feedback(feedback: FeedbackRequest):
    """Recebe feedback do usuário"""
    try:
        # TODO: Implementar salvamento de feedback em banco/arquivo
        logger.info(f"Feedback recebido: {feedback.type} para query: {feedback.query[:50] if feedback.query else 'N/A'}...")

        return {
            "success": True,
            "message": "Feedback registrado com sucesso",
            "timestamp": datetime.now().isoformat()
        }

    except Exception as e:
        logger.error(f"Erro ao processar feedback: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/diagnostics/db")
async def db_diagnostics():
    """Diagnóstico do banco de dados"""
    try:
        components = initialize_backend()
        if not components:
            raise HTTPException(status_code=500, detail="Backend não disponível")

        parquet_adapter = components['parquet_adapter']

        # Verificar status do Parquet
        parquet_check = os.path.join(os.getcwd(), "data", "parquet", "admmat.parquet")
        parquet_available = os.path.exists(parquet_check)

        diagnostics = {
            "parquet": {
                "available": parquet_available,
                "path": parquet_check,
                "status": "OK" if parquet_available else "NOT FOUND"
            },
            "backend": {
                "initialized": True,
                "components": list(components.keys())
            }
        }

        return {
            "success": True,
            "diagnostics": diagnostics,
            "timestamp": datetime.now().isoformat()
        }

    except Exception as e:
        logger.error(f"Erro no diagnóstico: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/learning/metrics")
async def learning_metrics():
    """Métricas do sistema de aprendizado"""
    # TODO: Implementar métricas reais de ML
    metrics = {
        "queries_processadas": "12.5K",
        "acuracia_media": "94.2%",
        "padroes_identificados": 387,
        "taxa_melhoria": "+8.5%",
        "recent_learnings": [
            {
                "category": "Vendas",
                "insight": "Identificado padrão sazonal em eletrônicos durante novembro-dezembro",
                "confidence": 92,
                "date": "14/01/2025"
            },
            {
                "category": "Estoque",
                "insight": "Correlação entre ruptura de estoque e dias da semana (sexta-feira)",
                "confidence": 88,
                "date": "13/01/2025"
            }
        ]
    }

    return {
        "success": True,
        "metrics": metrics,
        "timestamp": datetime.now().isoformat()
    }

# ============================================================================
# ERROR HANDLERS
# ============================================================================

@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """Handler para HTTPException"""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "error": exc.detail,
            "timestamp": datetime.now().isoformat()
        }
    )

@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Handler para exceções gerais"""
    logger.error(f"Erro não tratado: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "error": "Erro interno do servidor",
            "timestamp": datetime.now().isoformat()
        }
    )

# ============================================================================
# MAIN
# ============================================================================

if __name__ == "__main__":
    import uvicorn

    port = int(os.environ.get('PORT', 5000))
    host = os.environ.get('HOST', '0.0.0.0')

    logger.info(f"🚀 Iniciando API FastAPI na porta {port}")
    logger.info(f"📚 Documentação disponível em: http://{host}:{port}/docs")
    logger.info(f"🔧 Redoc disponível em: http://{host}:{port}/redoc")

    uvicorn.run(
        "api_server:app",
        host=host,
        port=port,
        reload=True,  # Auto-reload em desenvolvimento
        log_level="info"
    )
