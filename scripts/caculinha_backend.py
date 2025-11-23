# ------------------------------------------------------------
# FastAPI backend – Caçulinha Data Analyzer (sem Streamlit)
# ------------------------------------------------------------

import os
from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse, JSONResponse
from pydantic import BaseModel
from typing import Dict, Any, Generator

# ------------------------------------------------------------------
# Ajuste do PYTHONPATH para que os imports do projeto funcionem
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ""))
if PROJECT_ROOT not in os.sys.path:
    os.sys.path.append(PROJECT_ROOT)

# Imports dos módulos existentes
from core.llm_service import create_llm_service
from core.connectivity.hybrid_adapter import HybridDataAdapter
from core.auth import login as auth_login, sessao_expirada

# ------------------------------------------------------------------
app = FastAPI(title="Caçulinha Backend", version="0.1.0")

# Instâncias singleton
llm_service = create_llm_service()
data_adapter = HybridDataAdapter()

# ------------------------------------------------------------------
class ChatRequest(BaseModel):
    prompt: str
    context: Dict[str, Any] | None = None
    stream: bool = False
    mask_pii: bool = True

class LoginRequest(BaseModel):
    username: str
    password: str

# ------------------------------------------------------------------
@app.get("/health")
def health():
    return {"status": "ok"}

# ------------------------------------------------------------------
@app.post("/auth/login")
def login(req: LoginRequest):
    """Endpoint de login – delega ao módulo core.auth."""
    try:
        result = auth_login(username=req.username, password=req.password)
        return JSONResponse(content=result)
    except Exception as exc:
        raise HTTPException(status_code=401, detail=str(exc))

# ------------------------------------------------------------------
@app.post("/chat")
async def chat(request: ChatRequest):
    """Encaminha a pergunta ao LLM. Suporta streaming opcional."""
    try:
        if request.stream:
            def generator() -> Generator[bytes, None, None]:
                for chunk in llm_service.get_response_stream(
                    prompt=request.prompt,
                    context=request.context,
                    mask_pii_data=request.mask_pii,
                ):
                    yield chunk.encode("utf-8")
            return StreamingResponse(generator(), media_type="text/plain")
        else:
            full = llm_service.get_response(
                prompt=request.prompt,
                context=request.context,
                mask_pii_data=request.mask_pii,
            )
            return JSONResponse(content={"response": full})
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))

# ------------------------------------------------------------------
@app.get("/data/status")
def data_status():
    """Retorna informações de conexão do HybridDataAdapter."""
    try:
        status = data_adapter.get_status()
        return JSONResponse(content=status)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))

# ------------------------------------------------------------------
@app.get("/session/expired")
def session_expired():
    """Verifica se a sessão do usuário expirou (reúso do módulo auth)."""
    try:
        expired = sessao_expirada()
        return JSONResponse(content={"expired": expired})
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))
