"""
Chat Endpoints
BI Chat with AI assistant
"""

from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import ORJSONResponse, StreamingResponse
from pydantic import BaseModel
from pathlib import Path
import json
import asyncio

from app.api.dependencies import get_current_active_user
from app.infrastructure.database.models import User

# Project root (6 níveis acima deste arquivo: chat.py -> endpoints -> v1 -> api -> app -> backend -> ROOT)
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent.parent.parent

router = APIRouter(prefix="/chat", tags=["Chat"])


class ChatRequest(BaseModel):
    query: str


class ChatResponse(BaseModel):
    response: str


@router.get("/stream")
async def stream_chat(
    q: str,
    token: str,  # ✅ Token via query parameter (EventSource limitation)
    request: Request,
):
    """
    Streaming endpoint usando Server-Sent Events (SSE)
    ✅ Autenticação via query parameter (EventSource não suporta headers)
    ✅ Com suporte a Last-Event-ID para reconexão inteligente
    """
    import sys
    import logging
    from app.api.dependencies import get_current_user_from_token

    logger = logging.getLogger(__name__)

    # ✅ Validar token manualmente
    try:
        current_user = await get_current_user_from_token(token)
        logger.info(f"SSE authenticated user: {current_user.username}")
    except Exception as e:
        logger.error(f"SSE authentication failed: {e}")
        async def error_generator():
            yield f"data: {json.dumps({'error': 'Não autenticado'})}\n\n"
        return StreamingResponse(error_generator(), media_type="text/event-stream")

    # ✅ CRÍTICO: Obter Last-Event-ID para reconexão
    last_event_id = request.headers.get("Last-Event-ID")

    print(f"==> SSE STREAM REQUEST: {q} (Last-Event-ID: {last_event_id}) <==", file=sys.stderr, flush=True)
    
    async def event_generator():
        try:
            # Iniciar contador de eventos
            event_counter = int(last_event_id) if last_event_id else 0
            
            # SISTEMA ROBUSTO COM REGEX (100% OFFLINE)
            from app.core.robust_chatbi import RobustChatBI
            from pathlib import Path
            
            # Caminho do Parquet
            docker_path = Path("/app/data/parquet/admmat.parquet")
            dev_path = Path(__file__).resolve().parent.parent.parent.parent.parent.parent / "data" / "parquet" / "admmat.parquet"
            parquet_path = docker_path if docker_path.exists() else dev_path
            
            response_text = ""
            
            try:
                # Inicializar sistema robusto
                if not hasattr(event_generator, '_chatbi'):
                    print("DEBUG: Inicializando RobustChatBI...", file=sys.stderr, flush=True)
                    event_generator._chatbi = RobustChatBI(parquet_path)
                
                # Processar pergunta com REGEX
                safe_q = q.encode('ascii', 'ignore').decode('ascii')
                print(f"DEBUG: Recebida pergunta: '{safe_q}'", file=sys.stderr, flush=True)
                result = event_generator._chatbi.process_query(q)
                
                response_text = result["text"]
                safe_response = response_text.encode('ascii', 'ignore').decode('ascii')
                print(f"DEBUG: Resposta gerada (len={len(response_text)}): {safe_response[:50]}...", file=sys.stderr, flush=True)
                    
            except Exception as e:
                print(f"ERRO CRÍTICO no processamento: {e}", file=sys.stderr, flush=True)
                import traceback
                traceback.print_exc(file=sys.stderr)
                response_text = "Desculpe, ocorreu um erro interno."
            
            # Streaming com velocidade natural (sem delay artificial)
            words = response_text.split()
            chunk_size = 5  # Aumentado para 5 palavras por chunk para maior throughput
            
            print(f"DEBUG: Iniciando streaming de {len(words)} palavras...", file=sys.stderr, flush=True)
            
            for i in range(0, len(words), chunk_size):
                chunk_words = words[i:i + chunk_size]
                chunk_text = " " + " ".join(chunk_words) if i > 0 else " ".join(chunk_words)
                
                event_counter += 1
                
                # Log a cada 20 chunks para não poluir demais
                if i % 100 == 0:
                    safe_chunk = chunk_text.encode('ascii', 'ignore').decode('ascii')
                    print(f"DEBUG: Enviando chunk {i}: '{safe_chunk}'", file=sys.stderr, flush=True)
                
                yield f"id: {event_counter}\n"
                yield f"data: {json.dumps({'text': chunk_text, 'done': False})}\n\n"
                
                # REMOVIDO: await asyncio.sleep(0.1) - O frontend deve lidar com a animação
                # await asyncio.sleep(0.01) # Pequeno yield para não bloquear o event loop, se necessário

            
            print("DEBUG: Streaming concluído. Enviando sinal de done.", file=sys.stderr, flush=True)
            yield f"id: {event_counter + 1}\n"
            yield f"data: {json.dumps({'text': '', 'done': True})}\n\n"
            
            # Sinalizar fim do stream
            event_counter += 1
            yield f"id: {event_counter}\n"
            yield f"data: {json.dumps({'done': True})}\n\n"
            
            print(f"==> Stream concluído: {event_counter} eventos <==", file=sys.stderr, flush=True)
            
        except Exception as e:
            logger.error(f"Erro no streaming: {e}")
            yield f"data: {json.dumps({'error': str(e)})}\n\n"
    
    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",  # Nginx compatibility
        }
    )



@router.post("", response_class=ORJSONResponse)
async def send_chat_message(
    request: ChatRequest,
    current_user: Annotated[User, Depends(get_current_active_user)],
) -> dict:
    """
    Send a message to the BI Chat assistant
    
    Processes natural language queries using Agent System (with fallback to direct Parquet queries)
    """
    import sys
    import polars as pl
    from pathlib import Path
    import logging
    import asyncio
    
    logger = logging.getLogger(__name__)
    query = request.query
    
    print(f"==> CHAT REQUEST: {query} <==", file=sys.stderr, flush=True)

    # ✅ AGENTE DESABILITADO TEMPORARIAMENTE - Usando fallback direto ao Parquet
    use_agent = False

    # Tentar usar sistema de agentes primeiro COM TIMEOUT
    if use_agent:
        try:
            from app.core.query_processor import QueryProcessor

            # Inicializar QueryProcessor (singleton)
            if not hasattr(send_chat_message, '_query_processor'):
                print("==> Inicializando QueryProcessor... <==", file=sys.stderr, flush=True)
                send_chat_message._query_processor = QueryProcessor()
                print("==> QueryProcessor inicializado! <==", file=sys.stderr, flush=True)

            print("==> Processando query com agente... <==", file=sys.stderr, flush=True)

            # ✅ TIMEOUT DE 10 SEGUNDOS (reduzido de 30s)
            result = await asyncio.wait_for(
                asyncio.to_thread(send_chat_message._query_processor.process_query, query),
                timeout=10.0
            )

            print(f"==> Agente retornou: {type(result)} <==", file=sys.stderr, flush=True)

            # Extrair resposta do resultado
            if isinstance(result, dict):
                response_text = result.get("output", "")
                if response_text:
                    print(f"==> Resposta válida: {response_text[:100]}... <==", file=sys.stderr, flush=True)
                    return ChatResponse(response=response_text)

                # Se não houver resposta válida, fazer fallback
                print("==> Agente não retornou resposta válida, usando fallback <==", file=sys.stderr, flush=True)
        except asyncio.TimeoutError:
            print("==> TIMEOUT: Agente demorou mais de 30s, usando fallback <==", file=sys.stderr, flush=True)
        except Exception as e:
            print(f"==> ERRO no agente: {e}, usando fallback <==", file=sys.stderr, flush=True)
            logger.warning(f"Sistema de agentes não disponível ({e}), usando fallback para Parquet")
    
    # FALLBACK: Consultas diretas ao Parquet (código anterior)
    try:
        # Caminho híbrido Docker/Dev
        docker_path = Path("/app/data/parquet/admmat.parquet")
        dev_path = PROJECT_ROOT / "data" / "parquet" / "admmat.parquet"

        parquet_path = docker_path if docker_path.exists() else dev_path

        # OTIMIZAÇÃO: Usar scan_parquet (lazy) ao invés de read_parquet (eager)
        # Carrega apenas dados necessários, muito mais rápido
        print(f"==> Carregando dados do Parquet (lazy scan)... <==", file=sys.stderr, flush=True)
        lf = pl.scan_parquet(parquet_path)

        query_lower = query.lower()
        
        # Processar diferentes tipos de perguntas
        if "vendas" in query_lower or "sales" in query_lower or "total" in query_lower:
            # OTIMIZAÇÃO: Usar count() no lazy frame (muito mais rápido que len(df))
            total = lf.select(pl.count()).collect().item()
            response = f"📊 **Análise de Vendas**\n\nCom base nos dados reais, temos um total de **{total:,} registros** de vendas no sistema.\n\nEste número representa todas as transações registradas no banco de dados."
            
        elif "produtos" in query_lower or "products" in query_lower:
            # Verificar colunas disponíveis
            schema_cols = lf.collect_schema().names()
            if "PRODUTO" in schema_cols:
                # OTIMIZAÇÃO: Operações no lazy frame antes de collect
                unique_products = lf.select(pl.col("PRODUTO").n_unique()).collect().item()
                top_products = (
                    lf.group_by("PRODUTO")
                    .agg(pl.count().alias("count"))
                    .sort("count", descending=True)
                    .head(5)
                    .collect()
                )

                response = f"📦 **Análise de Produtos**\n\nTemos **{unique_products:,} produtos únicos** no catálogo.\n\n**Top 5 Produtos Mais Vendidos:**\n"
                for row in top_products.iter_rows():
                    response += f"- {row[0]}: {row[1]:,} vendas\n"
            else:
                response = "📦 Informação de produtos não disponível no momento."
                
        elif "colunas" in query_lower or "campos" in query_lower or "dados" in query_lower:
            # OTIMIZAÇÃO: Pegar schema sem carregar dados
            schema_cols = lf.collect_schema().names()
            total_count = lf.select(pl.count()).collect().item()

            cols = schema_cols[:20]
            response = f"📋 **Estrutura dos Dados**\n\nO dataset possui **{len(schema_cols)} colunas** e **{total_count:,} registros**.\n\n**Principais colunas:**\n"
            for col in cols:
                response += f"- {col}\n"
            if len(schema_cols) > 20:
                response += f"\n... e mais {len(schema_cols) - 20} colunas."
                
        elif "estatísticas" in query_lower or "resumo" in query_lower or "overview" in query_lower:
            # OTIMIZAÇÃO: Tudo no lazy frame
            schema_cols = lf.collect_schema().names()
            total_count = lf.select(pl.count()).collect().item()

            response = f"📈 **Resumo Estatístico**\n\n"
            response += f"- **Total de registros:** {total_count:,}\n"
            response += f"- **Total de colunas:** {len(schema_cols)}\n"
            if "PRODUTO" in schema_cols:
                unique_prods = lf.select(pl.col('PRODUTO').n_unique()).collect().item()
                response += f"- **Produtos únicos:** {unique_prods:,}\n"
            response += f"\n💡 Faça perguntas específicas sobre vendas, produtos ou qualquer coluna do dataset!"
            
        else:
            # Resposta genérica com informações úteis
            # OTIMIZAÇÃO: Usar lazy frame
            schema_cols = lf.collect_schema().names()
            total_count = lf.select(pl.count()).collect().item()

            response = f"🤖 **Assistente BI**\n\nRecebi sua pergunta: '{query}'\n\n"
            response += f"Tenho acesso a **{total_count:,} registros** com **{len(schema_cols)} colunas** de dados.\n\n"
            response += "**Perguntas que posso responder:**\n"
            response += "- Quantas vendas tivemos?\n"
            response += "- Quais são os produtos mais vendidos?\n"
            response += "- Mostre as colunas disponíveis\n"
            response += "- Faça um resumo estatístico\n"

        return {"response": response}
        
    except Exception as e:
        # Último fallback em caso de erro
        print(f"==> ERRO no fallback: {e} <==", file=sys.stderr, flush=True)
        return {
            "response": f"❌ Erro ao processar consulta: {str(e)}\n\nPor favor, tente reformular sua pergunta."
        }

