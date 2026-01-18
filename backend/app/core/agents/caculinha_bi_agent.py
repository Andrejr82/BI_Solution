import json
import logging
import asyncio
import numpy as np
import pandas as pd
from decimal import Decimal
from datetime import datetime, date
from typing import Any, Dict, List, Optional, Callable, Awaitable

logger = logging.getLogger(__name__)

# Safe Import for LangChain dependencies
LANGCHAIN_AVAILABLE = False
try:
    from langchain_core.language_models import BaseChatModel
    from langchain_core.tools import BaseTool
    LANGCHAIN_AVAILABLE = True
except (ImportError, OSError):
    logger.warning("LangChain dependencies missing. CaculinhaBIAgent will run in degraded mode.")
    BaseChatModel = object # Dummy for type hinting
    BaseTool = object # Dummy for type hinting

from app.core.tools.une_tools import (
    calcular_abastecimento_une,
    calcular_mc_produto,
    calcular_preco_final_une,
    validar_transferencia_produto,
    sugerir_transferencias_automaticas,
    encontrar_rupturas_criticas,
    consultar_dados_gerais,
    analisar_produto_todas_lojas,  # ✅ FIX 2026-01-15: Análise multi-loja sem loop
)
from app.core.tools.flexible_query_tool import consultar_dados_flexivel
from app.core.tools.anomaly_detection import analisar_anomalias # NOVA FERRAMENTA
from app.core.tools.metadata_tools import consultar_dicionario_dados, analisar_historico_vendas  # Ferramentas de metadados e previsão
from app.core.data_source_manager import get_data_manager # Para injeção dinâmica

# Import NEW universal chart tool - Context7 2025 Best Practice
from app.core.tools.universal_chart_generator import gerar_grafico_universal_v2

# Import legacy chart tools for compatibility
from app.core.tools.chart_tools import (
    gerar_ranking_produtos_mais_vendidos,
    gerar_dashboard_executivo,
    listar_graficos_disponiveis,
    gerar_visualizacao_customizada
)

# Import NEW semantic search tool - RAG Implementation 2025
from app.core.tools.semantic_search_tool import buscar_produtos_inteligente

# Import RAG Hybrid Retriever - Query Example Retrieval 2025
from app.core.rag.hybrid_retriever import HybridRetriever

# Optional: Import CodeGenAgent just for type hinting if needed,
# but we won't use it for logic anymore.
from app.core.utils.field_mapper import FieldMapper

# Import TypeConverter para serialização segura
from app.core.utils.serializers import TypeConverter, safe_json_dumps

# Import Tool Scoping - Security 2025
from app.core.utils.tool_scoping import ToolPermissionManager, get_scoped_tools

# Alias para manter compatibilidade com código existente
safe_json_serialize = safe_json_dumps

# System instruction - Master Prompt: Assistente de BI Analítico Avançado
# DEPRECATED: Este arquivo faz parte da arquitetura V2 (removida)
# O SYSTEM_PROMPT agora está em ChatServiceV3

# Fallback SYSTEM_PROMPT para compatibilidade temporária
SYSTEM_PROMPT = """Você é o Caçulinha BI, assistente de análise de dados.
Este agente está deprecated. Use ChatServiceV3 para novas implementações."""

class CaculinhaBIAgent:
    """
    Agent responsible for Business Intelligence queries using Gemini Native Function Calling.
    Replaces the legacy keyword-based routing and CodeGenAgent fallback.
    """
    def __init__(
        self,
        llm: Any,
        code_gen_agent: Any,
        field_mapper: FieldMapper,
        user_role: str = "analyst",  # NEW: Role-based tool scoping (default: analyst)
        enable_rag: bool = True  # ASYNC RAG 2025-12-27: Re-enabled with background warming (non-blocking)
    ):
        # llm is expected to be GeminiLLMAdapter
        self.llm = llm
        self.field_mapper = field_mapper
        self.user_role = user_role  # Store user role for tool scoping
        self.enable_rag = enable_rag  # Store RAG config

        # We keep code_gen_agent in init to maintain compatibility with chat.py,
        # but we won't use it effectively.
        self.code_gen_agent = code_gen_agent

        # Initialize RAG Retriever (lazy - background warming, não bloqueia)
        if self.enable_rag:
            try:
                self.retriever = HybridRetriever()
                logger.info("RAG Hybrid Retriever criado (warming será iniciado em background)")
                # NOTE: Warming será iniciado no primeiro run_async() via _start_rag_warming()
            except Exception as e:
                logger.warning(f"Falha ao criar RAG retriever: {e}. Continuando sem RAG.")
                self.retriever = None
                self.enable_rag = False
        else:
            self.retriever = None
            logger.info("RAG desabilitado (enable_rag=False)")

        # Define ALL available tools - ORDEM IMPORTA! Ferramentas mais genéricas primeiro
        all_bi_tools = [
            # METADATA & INTROSPECTION (NEW 2026 - Self-Awareness)
            consultar_dicionario_dados,
            analisar_historico_vendas,  # NEW 2026: Análise de histórico e previsão

            # DATA QUERY TOOLS (Generic → Specific)
            consultar_dados_flexivel,  # NOVA: Ferramenta genérica e flexível
            analisar_produto_todas_lojas,  # ✅ FIX 2026-01-15: Análise multi-loja (evita loop)
            analisar_anomalias,  # NEW 2026: Detecção de anomalias estatísticas
            buscar_produtos_inteligente,  # NEW 2025: RAG semantic search
            consultar_dados_gerais,
            # BUSINESS LOGIC TOOLS
            calcular_abastecimento_une,
            calcular_mc_produto,
            calcular_preco_final_une,
            validar_transferencia_produto,
            sugerir_transferencias_automaticas,
            encontrar_rupturas_criticas,
            # VISUALIZATION TOOLS (Context7 2025 - Nova Geração)
            gerar_grafico_universal_v2,  # FIX: Nova ferramenta com filtros dinâmicos
            gerar_ranking_produtos_mais_vendidos,
            gerar_dashboard_executivo,
            listar_graficos_disponiveis,
            gerar_visualizacao_customizada,
        ]

        # Apply role-based tool scoping (Security 2025)
        self.bi_tools = ToolPermissionManager.get_tools_for_role(
            all_tools=all_bi_tools,
            user_role=self.user_role
        )

        logger.info(
            f"Agent initialized with {len(self.bi_tools)}/{len(all_bi_tools)} tools "
            f"for role '{self.user_role}'"
        )

        # Convert LangChain tools to Gemini Function Declarations
        self.gemini_tools = self._convert_tools_to_gemini_format(self.bi_tools)
        
        # System instruction - Conversacional + BI Expert (Context7 Enhanced v2025)
        # DYNAMIC PROMPTING: Injetar schema real na inicialização
        try:
            manager = get_data_manager()
            # Tentar obter colunas (cache hit provável)
            cols = manager.get_columns()
            
            # Filtrar colunas importantes (evitar poluir com as 100)
            # Mas garantir que as críticas estejam lá
            important_keywords = ['PRODUTO', 'NOME', 'UNE', 'SEGMENTO', 'CATEGORIA', 'VENDA', 'ESTOQUE', 'PRECO', 'CUSTO', 'LIQUIDO', 'MARGEM', 'FABRICANTE']
            priority_cols = [c for c in cols if any(k in c.upper() for k in important_keywords)]
            other_cols = [c for c in cols if c not in priority_cols]
            
            # Montar string de schema
            schema_str = "**Colunas Prioritárias (Use estas preferencialmente):**\n"
            schema_str += ", ".join([f"`{c}`" for c in priority_cols])
            schema_str += "\n\n**Outras Colunas Disponíveis:**\n"
            schema_str += ", ".join([f"`{c}`" for c in other_cols[:30]]) # Limit to 30 others to save tokens
            if len(other_cols) > 30:
                schema_str += f"... (+{len(other_cols)-30} colunas. Use `consultar_dicionario_dados` para ver todas)"
                
            # Substituir no template
            # Procura a seção ## DADOS DISPONÍVEIS e substitui ou anexa
            self.system_prompt = SYSTEM_PROMPT.replace(
                "**Colunas Principais:**", 
                f"**SCHEMA REAL DO BANCO DE DADOS (Carregado Dinamicamente):**\n{schema_str}\n\n**Colunas Legadas (Referência):**"
            )
            logger.info("Dynamic Schema Injection: Sucesso")
            
        except Exception as e:
            logger.warning(f"Dynamic Schema Injection Failed: {e}. Using static prompt.")
            self.system_prompt = SYSTEM_PROMPT

    def _convert_tools_to_gemini_format(self, tools: List[BaseTool]) -> Dict[str, List[Dict[str, Any]]]:
        declarations = []
        for tool in tools:
            # Generate schema using LangChain's standardized method
            # compatible with Pydantic v1 and v2
            try:
                schema = tool.get_input_schema().model_json_schema()
            except AttributeError:
                # Fallback for older Pydantic or specific Tool implementations
                if hasattr(tool, 'args_schema') and tool.args_schema:
                    if hasattr(tool.args_schema, 'schema'):
                         schema = tool.args_schema.schema()
                    else:
                         schema = {}
                else:
                    schema = {}
            
            # Clean schema to be compatible with Gemini (remove anyOf, titles)
            cleaned_schema = self._clean_schema(schema)
            
            # Ensure 'properties' and 'required' are present if parameters exist
            parameters = {
                "type": "object",
                "properties": cleaned_schema.get("properties", {}),
                "required": cleaned_schema.get("required", [])
            }

            declarations.append({
                "name": tool.name,
                "description": tool.description,
                "parameters": parameters
            })
        
        return {"function_declarations": declarations}

    def _clean_context7_violations(self, content: str, context_type: str = "generic") -> str:
        """
        Remove JSON bruto e estruturas técnicas das respostas (Context7 Storytelling).

        Args:
            content: Conteúdo a limpar
            context_type: Tipo de contexto ("chart", "data", "analysis", "generic")

        Returns:
            Conteúdo limpo com narrativa natural
        """
        if not isinstance(content, str) or not content:
            return content

        import re

        original_content = content
        cleaned = content

        # 1. Detectar e remover markdown JSON blocks (```json...```)
        markdown_json_pattern = r'```json\s*\n(.*?)\n```'
        if re.search(markdown_json_pattern, cleaned, re.DOTALL):
            logger.warning("[CONTEXT7] Detectado markdown JSON block. Removendo.")
            cleaned = re.sub(markdown_json_pattern, "", cleaned, flags=re.DOTALL)

        # 2. Detectar e remover blocos JSON inline grandes (chart specs, etc)
        # Padrão para detectar objetos JSON com "data" e "layout" (Plotly)
        plotly_json_pattern = r'\{[\s\S]*?"data"[\s\S]*?"layout"[\s\S]*?\}'
        if re.search(plotly_json_pattern, cleaned):
            logger.warning("[CONTEXT7] Detectado Plotly JSON inline. Removendo.")
            cleaned = re.sub(plotly_json_pattern, "", cleaned)

        # 3. Detectar JSON puro no início (objeto ou array)
        stripped = cleaned.strip()
        if (stripped.startswith("{") or stripped.startswith("[")) and len(stripped) > 50:
            # Tentar validar se é JSON
            try:
                json.loads(stripped)
                logger.warning("[CONTEXT7] Detectado JSON puro. Substituindo com narrativa.")
                cleaned = ""  # Limpar completamente, será substituído abaixo
            except json.JSONDecodeError:
                pass  # Não é JSON válido, manter

        # 4. Se ficou vazio ou muito curto, substituir com narrativa contextual
        cleaned = cleaned.strip()
        if not cleaned or len(cleaned) < 10:
            if context_type == "chart":
                cleaned = "Aqui está o gráfico que você solicitou."
            elif context_type == "data":
                cleaned = "Recuperei os dados solicitados e organizei para você."
            elif context_type == "analysis":
                cleaned = "Com base nos dados disponíveis, aqui está a análise:"
            else:
                cleaned = "Processado com sucesso."

            logger.info(f"[CONTEXT7] Substituído com narrativa contextual ({context_type})")

        # 5. Se mudou, logar a transformação
        if cleaned != original_content:
            logger.info(f"[CONTEXT7] Limpeza aplicada. Antes: {len(original_content)} chars, Depois: {len(cleaned)} chars")

        return cleaned

    async def _start_rag_warming(self) -> None:
        """
        Inicia warming do RAG em background (non-blocking).
        Chamado apenas uma vez no primeiro run_async().
        """
        if not self.enable_rag or self.retriever is None:
            return

        try:
            # Start warming in background (fire and forget)
            asyncio.create_task(self.retriever.start_background_warming())
            logger.info("[RAG] Background warming task criado")
        except Exception as e:
            logger.error(f"[RAG] Erro ao iniciar warming: {e}", exc_info=True)

    async def _get_rag_examples(self, query: str, top_k: int = 3) -> str:
        """
        Recupera exemplos similares e formata como BLOCO DE CONTEXTO SEGURO.
        Muda de 'lista de mensagens' para 'string formatada com instruções'.
        
        Returns:
            String formatada com XML tags <reference_context>
        """
        if not self.enable_rag or self.retriever is None:
            return ""

        try:
            # Use async retrieve
            similar_docs = await self.retriever.retrieve_async(
                query,
                top_k=top_k,
                method='hybrid',
                wait_if_warming=False
            )

            if not similar_docs:
                return ""

            logger.info(f"[RAG] Recuperados {len(similar_docs)} exemplos para contexto")

            # Formata como bloco de texto instrucional
            context_block = "\n\n<reference_context>\n"
            context_block += "⚠️ EXEMPLOS DE INTERAÇÕES PASSADAS (PARA APRENDER A LÓGICA):\n"
            context_block += "INSTRUÇÃO CRÍTICA: Use estes exemplos APENAS para entender qual ferramenta chamar ou como formatar a resposta.\n"
            context_block += "PROIBIDO: Não copie números, IDs ou nomes destes exemplos. Os dados abaixo são OBSOLETOS.\n\n"

            for i, doc in enumerate(similar_docs[:top_k]):
                doc_data = doc.get('doc', doc)
                user_q = doc_data.get('query', doc_data.get('user_query', ''))
                assist_r = doc_data.get('response', doc_data.get('assistant_response', ''))
                
                # Truncar resposta se for muito longa para economizar tokens e reduzir ruído
                if len(assist_r) > 500:
                    assist_r = assist_r[:500] + "... (truncado)"

                context_block += f"--- EXEMPLO {i+1} ---\n"
                context_block += f"Pergunta: {user_q}\n"
                context_block += f"Ação Correta: {assist_r}\n"

            context_block += "</reference_context>\n"
            return context_block

        except Exception as e:
            logger.error(f"[RAG] Erro ao recuperar exemplos: {e}", exc_info=True)
            return ""

    def _clean_schema(self, schema: Dict[str, Any]) -> Dict[str, Any]:
        """
        Recursively cleans Pydantic JSON Schema for Gemini compatibility.
        """
        if not isinstance(schema, dict):
            return schema
            
        new_schema = schema.copy()
        
        # Remove incompatible keys
        if "title" in new_schema:
            del new_schema["title"]
        if "default" in new_schema:
            del new_schema["default"]
        if "additionalProperties" in new_schema:
            del new_schema["additionalProperties"]

        # Handle anyOf
        if "anyOf" in new_schema:
            options = new_schema.pop("anyOf")
            valid_option = next((opt for opt in options if opt.get("type") != "null"), None)
            if valid_option:
                cleaned_child = self._clean_schema(valid_option)
                new_schema.update(cleaned_child)
            else:
                new_schema["type"] = "string" 

        # Recurse
        if "properties" in new_schema:
            for prop, prop_schema in new_schema["properties"].items():
                new_schema["properties"][prop] = self._clean_schema(prop_schema)
        
        if "items" in new_schema:
            new_schema["items"] = self._clean_schema(new_schema["items"])

        return new_schema

    async def run_async(
        self, 
        user_query: str, 
        chat_history: Optional[List[Dict]] = None,
        on_progress: Optional[Callable[[Dict[str, Any]], Awaitable[None]]] = None
    ) -> Dict[str, Any]:
        """
        Async version of run method.
        """
        logger.info(f"CaculinhaBIAgent (Modern Async): Processing query: {user_query}")

        # START RAG WARMING
        await self._start_rag_warming()

        messages = []

        # OPTIMIZATION: Context Pruning
        if chat_history:
            filtered_history = [msg for msg in chat_history if msg.get("role") != "system"]
            recent_history = filtered_history[-15:] if len(filtered_history) > 15 else filtered_history

            for msg in recent_history:
                role = msg.get("role", "user")
                content = msg.get("content", "")
                messages.append({"role": role, "content": content})

        # ✅ FIX RAG: Context Fencing Injection com TIMEOUT
        # Em vez de adicionar mensagens fake, adicionamos um bloco de contexto na mensagem do usuário
        try:
            # ✅ FIX: Timeout de 500ms para não bloquear (continua sem RAG se demorar)
            rag_context_str = await asyncio.wait_for(
                self._get_rag_examples(user_query, top_k=1),  # ✅ Reduzido de 2 para 1 exemplo
                timeout=0.5  # 500ms timeout
            )
        except asyncio.TimeoutError:
            logger.warning("[RAG] Timeout de 500ms excedido. Continuando sem RAG.")
            rag_context_str = ""
        except Exception as e:
            logger.error(f"[RAG] Erro ao recuperar contexto: {e}")
            rag_context_str = ""
        
        # Combinar query do usuário com o contexto RAG (se houver)
        # BEST PRACTICE: Contexto ANTES da Query (Recency Bias)
        if rag_context_str:
            full_prompt_content = rag_context_str + "\n\n" + "PERGUNTA DO USUÁRIO AGORA:\n" + user_query
            logger.info("[RAG] Contexto PREPENDED na mensagem do usuário (Context Fencing)")
        else:
            full_prompt_content = user_query

        # Add current user query (enhanced)
        messages.append({"role": "user", "content": full_prompt_content})

        # DETECÇÃO DE KEYWORDS (mesmo código do run())
        graph_keywords = [
            "gere um gráfico", "mostre um gráfico", "crie um gráfico", "faça um gráfico",
            "gerar gráfico", "gerar grafico", "gere grafico", "mostre grafico",
            "criar gráfico", "criar grafico", "plote", "visualize", "visualização"
        ]
        
        # NOVA: Detecção de análise crítica e relatórios (REGRA 5)
        analysis_keywords = [
            "analise", "análise", "críticas", "criticas", "problemas", "melhorias",
            "recomendações", "recomendacoes", "diagnóstico", "diagnostico",
            "avaliação", "avaliacao", "o que devo fazer", "pontos de atenção",
            "pontos de atencao", "ações", "acoes", "relatório", "relatorio",
            "relatório executivo", "relatorio executivo", "relatório de",
            "relatorio de", "gere um relatório", "gere um relatorio"
        ]
        
        user_query_lower = user_query.lower()
        is_graph_request = any(kw in user_query_lower for kw in graph_keywords)
        is_analysis_request = any(kw in user_query_lower for kw in analysis_keywords)

        # ✅ FIX 2025-12-28: PRIORIZAÇÃO INTELIGENTE
        # Se usuário pede EXPLICITAMENTE gráfico, mesmo em análise → GRÁFICO
        # Se usuário pede APENAS análise/relatório (sem gráfico) → TEXTO
        if is_graph_request and is_analysis_request:
            # Caso: "gere um relatório com gráfico" ou "mostre gráfico de vendas do segmento X"
            # PRIORIDADE: Gráfico (usuário quer visualização)
            is_analysis_request = False
            logger.info(f"[GRAPH PRIORITY] Usuário solicitou gráfico explicitamente - modo visualização")
        elif is_analysis_request and not is_graph_request:
            # Caso: "analise o grupo oxford", "gere um relatório de vendas"
            # MODO TEXTO: Análise textual estruturada
            logger.info(f"[ANALYSIS MODE] Análise crítica/relatório detectado - modo textual")

        # FIX 2026-01-09: Detectar se estamos usando Groq/SmartLLM
        # Few-Shot Examples causam erro 400 no Groq (formato function_call incompatível)
        is_groq_mode = False
        llm_class_name = type(self.llm).__name__
        if llm_class_name == "SmartLLM":
            is_groq_mode = getattr(self.llm, 'primary', 'google') == 'groq'
        elif llm_class_name == "GroqLLMAdapter":
            is_groq_mode = True
        
        if is_groq_mode:
            logger.info("[GROQ] Modo Groq detectado - Few-Shot Examples desabilitados")

        # ✅ FIX: FEW-SHOT EXAMPLES - Simplificados para 1 exemplo curto (reduz tokens)
        # DIFERENCIAÇÃO CRÍTICA: Gráficos vs Análises Textuais
        # FIX 2026-01-09: Desabilitar quando Groq (causa erro 400 tool_use_failed)
        if len(messages) <= 2 and not is_groq_mode:
            logger.info("[ASYNC] Injetando Few-Shot Example simplificado (1 exemplo)")

            # Escolher exemplos baseado no tipo de request
            if is_analysis_request:
                # ✅ FIX: 1 exemplo curto de análise textual (~600 tokens ao invés de ~2000)
                logger.info("[ASYNC] Usando few-shot example de ANÁLISE TEXTUAL (simplificado)")
                few_shot_examples = [
                    # Exemplo único: Análise Crítica de Segmento
                    {"role": "user", "content": "analise o segmento TECIDOS e me aponte as críticas"},
                    {
                        "role": "model",
                        "tool_calls": [{
                            "id": "call_example_1",
                            "type": "function",
                            "function": {
                                "name": "consultar_dados_flexivel",
                                "arguments": json.dumps({
                                    "filtros": {"NOMESEGMENTO": "TECIDOS"},
                                    "colunas": ["PRODUTO", "NOME", "VENDA_30DD", "ESTOQUE_UNE"],
                                    "limite": 50
                                })
                            }
                        }]
                    },
                    {
                        "role": "function",
                        "function_call": {"name": "consultar_dados_flexivel"},
                        "content": json.dumps({
                            "status": "success",
                            "resultados": [
                                {"PRODUTO": "123", "NOME": "Produto A", "VENDA_30DD": 50, "ESTOQUE_UNE": 10}
                            ]
                        })
                    },
                    {
                        "role": "model",
                        "content": "**Análise do Segmento TECIDOS**\n\n**Diagnóstico:**\n- Produto A: Risco de ruptura (50 vendas, 10 estoque)\n\n**Recomendações:**\n1. Reabastecer urgente\n2. Revisar mix de produtos"
                    }
                ]
            else:
                # ✅ FIX: 1 exemplo curto de gráfico (~400 tokens)
                logger.info("[ASYNC] Usando few-shot example de GRÁFICOS (simplificado)")
                few_shot_examples = [
                    # Exemplo único: Gráfico simples
                    {"role": "user", "content": "gere um gráfico de vendas por categoria"},
                    {
                        "role": "model",
                        "tool_calls": [{
                            "id": "call_example_1",
                            "type": "function",
                            "function": {
                                "name": "gerar_grafico_universal_v2",
                                "arguments": json.dumps({"descricao": "vendas por categoria", "tipo_grafico": "auto"})
                            }
                        }]
                    },
                    {
                        "role": "function",
                        "function_call": {"name": "gerar_grafico_universal_v2"},
                        "content": json.dumps({
                            "status": "success",
                            "chart_data": "{\"data\": [], \"layout\": {}}",
                            "summary": {"mensagem": "Gráfico gerado"}
                        })
                    },
                    {"role": "model", "content": "Aqui está o gráfico solicitado."}
                ]

            messages = messages[:-1] + few_shot_examples + [messages[-1]]

        # ✅ FIX: PREFILL - Guiar LLM para resposta correta
        if is_graph_request:
            logger.warning(f"[ASYNC] GRAFICO DETECTADO - Ativando PREFILL")
            messages.append({
                "role": "model",
                "content": "Vou gerar o gráfico usando a ferramenta apropriada:"
            })
        elif is_analysis_request:
            logger.warning(f"[ASYNC] ANALISE CRITICA DETECTADA - Ativando PREFILL TEXTUAL")
            messages.append({
                "role": "model",
                "content": "Vou analisar os dados e fornecer uma análise textual estruturada com diagnóstico, críticas e recomendações:"
            })

        max_turns = 20  # ✅ FIX 2025-12-28: Aumentado de 10 para 20 para análises críticas e relatórios complexos
        current_turn = 0
        successful_tool_calls = 0  # 🚨 NOVO: Contador de ferramentas bem-sucedidas

        # ✅ CRITICAL FIX 2025-12-28: Filtrar ferramentas de gráfico para análises críticas
        # Forçar uso de ferramentas de consulta de dados ao invés de gráficos
        tools_to_use = self.gemini_tools
        if is_analysis_request:
            # Criar lista filtrada de ferramentas (sem gráficos)
            analysis_tool_names = [
                "consultar_dados_flexivel",
                "buscar_produtos_inteligente",
                "consultar_dados_gerais",
                "calcular_abastecimento_une",
                "calcular_mc_produto",
                "calcular_preco_final_une",
                "validar_transferencia_produto",
                "sugerir_transferencias_automaticas",
                "encontrar_rupturas_criticas"
            ]

            filtered_declarations = [
                decl for decl in self.gemini_tools.get("function_declarations", [])
                if decl["name"] in analysis_tool_names
            ]

            tools_to_use = {"function_declarations": filtered_declarations}
            logger.info(f"[ANALYSIS MODE] Filtered tools: {len(filtered_declarations)} tools (removed chart tools)")

        while current_turn < max_turns:
            try:
                # Notify thinking
                if on_progress:
                    await on_progress({"type": "tool_progress", "tool": "Pensando", "status": "start"})

                # Call LLM with tools (Blocking call wrapped in thread)
                # self.llm is GeminiLLMAdapter which is synchronous
                response = await asyncio.to_thread(
                    self.llm.get_completion,
                    messages,
                    tools=tools_to_use
                )

                if "error" in response:
                    logger.error(f"LLM Error: {response['error']}")
                    return self._generate_error_response(response['error'])

                # ✅ FIX: LOGGING (mesmo do run())
                response_type = "tool_call" if "tool_calls" in response else "text"
                logger.info(f"[ASYNC] LLM Response Type: {response_type}")

                if response_type == "text" and is_graph_request and successful_tool_calls == 0:
                    logger.error(f"[ASYNC] WARNING: LLM IGNOROU PEDIDO DE GRAFICO!")
                    logger.error(f"WARNING - User Query: {user_query}")
                    logger.error(f"WARNING - LLM Response: {response.get('content', '')[:300]}")

                    # FALLBACK AUTOMÁTICO
                    logger.warning(f"[ASYNC] FALLBACK: Forcando gerar_grafico_universal_v2")
                    synthetic_tool_call = {
                        "id": "call_fallback_graph_async",
                        "type": "function",
                        "function": {
                            "name": "gerar_grafico_universal_v2",
                            "arguments": json.dumps({"descricao": user_query})
                        }
                    }
                    response["tool_calls"] = [synthetic_tool_call]
                    logger.warning(f"[ASYNC] FALLBACK APLICADO")

                # Check for tool calls
                if "tool_calls" in response:
                    tool_calls = response["tool_calls"]
                    messages.append({
                        "role": "model",
                        "tool_calls": tool_calls
                    })

                    # PARALLEL EXECUTION 2025: Executar todas as ferramentas simultaneamente
                    # Define helper function for individual execution
                    async def execute_single_tool(tc):
                        func_name = tc["function"]["name"]
                        try:
                            func_args = json.loads(tc["function"]["arguments"])
                        except json.JSONDecodeError:
                            return func_name, {"error": "Invalid JSON arguments"}

                        # Notify tool start
                        if on_progress:
                            await on_progress({"type": "tool_progress", "tool": func_name, "status": "executing"})

                        tool_to_run = next((t for t in self.bi_tools if t.name == func_name), None)
                        
                        if tool_to_run:
                            try:
                                # Execute tool (Blocking call wrapped in thread)
                                tool_output = await asyncio.to_thread(tool_to_run.invoke, func_args)
                                
                                # Convert MapComposite
                                def convert_mapcomposite(obj):
                                    if hasattr(obj, '_mapping'):
                                        return dict(obj._mapping)
                                    elif isinstance(obj, dict):
                                        return {k: convert_mapcomposite(v) for k, v in obj.items()}
                                    elif isinstance(obj, list):
                                        return [convert_mapcomposite(item) for item in obj]
                                    return obj
                                
                                return func_name, convert_mapcomposite(tool_output)
                            except Exception as e:
                                logger.error(f"Error executing {func_name}: {e}")
                                return func_name, {"error": str(e)}
                        else:
                            return func_name, {"error": f"Tool {func_name} not found"}

                    # Execute all tools in parallel
                    logger.info(f"[ASYNC] Disparando {len(tool_calls)} ferramentas em PARALELO")
                    tasks = [execute_single_tool(tc) for tc in tool_calls]
                    results = await asyncio.gather(*tasks)

                    # Process results sequentially
                    should_exit_early = False
                    
                    # Create a map of results by function name to match with call IDs
                    # Note: This assumes unique function names per turn, or we need to map by index if reliable
                    # Better approach: Map by call ID if we passed it to execute_single_tool, but we didn't.
                    # Since we iterate tasks in same order as tool_calls, we can zip them.
                    
                    for i, (func_name, tool_result) in enumerate(results):
                        original_tool_call = tool_calls[i]
                        tool_call_id = original_tool_call.get("id")
                        
                        # OPTIMIZATION 2025: Success detection and early exit for charts
                        if isinstance(tool_result, dict):
                            is_chart = "chart_data" in tool_result or "chart_spec" in tool_result
                            is_success = tool_result.get("status") == "success" or len(tool_result.get("resultados", [])) > 0
                            
                            if is_chart and is_success:
                                logger.info(f"[ASYNC] SUCESSO: Grafico gerado por {func_name}. Forcando saida antecipada.")
                                successful_tool_calls += 1
                                should_exit_early = True
                            elif is_success:
                                successful_tool_calls += 1

                        # OTIMIZAÇÃO DE SERIALIZAÇÃO: Offload para thread (CPU bound para grandes JSONs)
                        serialized_content = await asyncio.to_thread(safe_json_serialize, tool_result)

                        # Add tool result to messages with CORRECT ID
                        messages.append({
                            "role": "function", # Adapter converts to 'tool'
                            "name": func_name,  # Helpful for adapter fallback
                            "tool_call_id": tool_call_id, # CRITICAL for Groq
                            "content": serialized_content
                        })

                    if should_exit_early:
                        logger.info("[ASYNC] SUCESSO: Gráfico detectado. Encerrando loop de ferramentas para priorizar entrega.")
                        # BREAK LOOP: Don't ask LLM to narrate immediately to avoid loop risk.
                        # Instead, we will force the loop to end and let the final check handle the chart response.
                        break
                    
                    # Loop continues
                    current_turn += 1
                    continue
                
                # If no tool calls, it's a text response (Final Answer)
                content = response.get("content", "")

                # Notify finalizing
                if on_progress:
                     await on_progress({"type": "tool_progress", "tool": "Processando resposta", "status": "finishing"})

                # Same logic as run() for parsing result...
                # (Duplicating logic from run() to ensure consistency)
                
                # Acumuladores para múltiplos resultados de ferramentas
                found_chart_data = None
                found_chart_summary = None
                found_table_mensagem = None
                found_resultados = None

                for msg in reversed(messages):
                    if msg.get("role") == "function":
                        try:
                            content_str = msg.get("content", "{}")
                            func_content = json.loads(content_str)

                            chart_data = func_content.get("chart_data")
                            if chart_data and func_content.get("status") == "success" and found_chart_data is None:
                                if isinstance(chart_data, str):
                                    try:
                                        chart_data = json.loads(chart_data)
                                    except json.JSONDecodeError:
                                        continue
                                found_chart_data = chart_data
                                found_chart_summary = func_content.get("summary", {})
                            
                            mensagem = func_content.get("mensagem", "")
                            if isinstance(mensagem, str) and "|" in mensagem and "---" in mensagem and found_table_mensagem is None:
                                found_table_mensagem = mensagem
                            
                            resultados = func_content.get("resultados", [])
                            if isinstance(resultados, list) and len(resultados) > 0 and found_resultados is None:
                                found_resultados = resultados

                        except Exception as e:
                            logger.error(f"DEBUG: Erro ao parsear mensagem de função: {e}")
                            continue

                # PRIORIDADE DE RETORNO: Gráfico tem maior prioridade
                if found_chart_data is not None:
                    # CONTEXT7: Limpar JSON bruto e aplicar narrativa
                    content = self._clean_context7_violations(content, context_type="chart")

                    return {
                        "type": "code_result",
                        "result": {
                            "result": found_chart_summary,
                            "chart_spec": found_chart_data
                        },
                        "chart_spec": found_chart_data,
                        "text_override": content
                    }
                
                # PRIORIDADE 2: Dados Tabulares (Se encontrou resultados mas não é gráfico)
                elif found_resultados is not None:
                    # CONTEXT7: Limpar JSON bruto e aplicar narrativa
                    content = self._clean_context7_violations(content, context_type="data")
                    
                    return {
                        "type": "code_result",
                        "result": found_resultados, # Lista de dicts para o frontend renderizar Tabela
                        "text_override": content
                    }

                # SAFETY NET: Check if the content is the specific JSON ReAct pattern OR just a JSON block and extract/convert
                try:
                    if isinstance(content, str):
                        content_stripped = content.strip()
                        # Caso 1: JSON Puro (o problema relatado)
                        if content_stripped.startswith("{") and content_stripped.endswith("}"):
                            try:
                                json_data = json.loads(content_stripped)
                                
                                # Se for o formato analítico específico que o usuário mostrou
                                if "analise_executiva" in json_data:
                                    # Converter para Markdown Bonito
                                    md_output = ""
                                    
                                    # 1. Manchete
                                    exec_data = json_data.get("analise_executiva", {})
                                    emoji_status = "🚨" if "ALERTA" in str(exec_data.get("status_geral", "")).upper() else "📊"
                                    md_output += f"### {emoji_status} {exec_data.get('manchete', 'Análise de Dados')}\n\n"
                                    
                                    # 2. Diagnóstico
                                    md_output += "**Diagnóstico Detalhado:**\n"
                                    diag_data = json_data.get("diagnostico_por_unidade", {})
                                    for unidade, dados in diag_data.items():
                                        insight = dados.get("insight", "")
                                        situacao = dados.get("situacao", "")
                                        md_output += f"- **{unidade} ({situacao})**: {insight}\n"
                                    md_output += "\n"
                                    
                                    # 3. Estratégia
                                    md_output += "**Estratégia Recomendada:**\n"
                                    strategies = json_data.get("estrategia_recomendada", [])
                                    if isinstance(strategies, list):
                                        for strat in strategies:
                                            md_output += f"- {strat}\n"
                                    elif isinstance(strategies, str):
                                        md_output += f"{strategies}\n"
                                        
                                    logger.info("SAFETY NET: Converteu JSON analítico para Markdown.")
                                    content = md_output

                                # Caso 2: ReAct Pattern (Legacy)
                                elif "action" in json_data and "content" in json_data:
                                    logger.info("SAFETY NET: Extracted content from ReAct JSON pattern.")
                                    content = json_data["content"]
                                
                            except json.JSONDecodeError:
                                pass # Não é JSON válido, segue o baile
                except Exception as e:
                    logger.warning(f"SAFETY NET: Failed to parse potential JSON content: {e}")

                # Se não há gráfico, retornar APENAS texto analítico (O usuário NÃO quer tabelas)
                return {
                    "type": "text",
                    "result": content
                }

            except Exception as e:
                logger.error(f"Exception in agent run loop: {e}", exc_info=True)
                return self._generate_error_response(str(e))

        # FIX: Antes de retornar erro, verificar se há gráfico gerado com sucesso
        # Isso evita perder o trabalho se o LLM não retornou texto mas gerou o gráfico
        logger.warning("[ASYNC] Max turns atingido. Verificando se ha grafico para retornar...")

        for msg in reversed(messages):
            if msg.get("role") == "function":
                try:
                    content_str = msg.get("content", "{}")
                    func_content = json.loads(content_str)
                    chart_data = func_content.get("chart_data")

                    if chart_data and func_content.get("status") == "success":
                        logger.info("[ASYNC] Grafico encontrado! Retornando mesmo sem texto final do LLM.")
                        if isinstance(chart_data, str):
                            try:
                                chart_data = json.loads(chart_data)
                            except:
                                pass

                        return {
                            "type": "code_result",
                            "result": {
                                "result": func_content.get("summary", {}),
                                "chart_spec": chart_data
                            },
                            "chart_spec": chart_data,
                            "text_override": "Aqui está o gráfico solicitado."
                        }
                except:
                    continue

        return self._generate_error_response("Maximum conversation turns exceeded.")

    def run(self, user_query: str, chat_history: Optional[List[Dict]] = None) -> Dict[str, Any]:
        """
        Executes the agent loop:
        1. Send query + tools to LLM.
        2. If LLM wants to call tool -> Execute tool -> Send result back to LLM.
        3. Repeat until LLM returns text.
        """
        logger.info(f"CaculinhaBIAgent (Modern): Processing query: {user_query}")

        # ✅ CRITICAL FIX: NÃO incluir system como mensagem
        # System instruction já está configurada no GeminiLLMAdapter via system_instruction parameter
        # Gemini NÃO aceita role="system" no array de mensagens - deve usar system_instruction no modelo
        # Ref: https://ai.google.dev/gemini-api/docs/system-instructions
        messages = []

        # OPTIMIZATION 2025: Context Pruning - Manter apenas últimas 15 mensagens (7 turnos)
        # Ref: Llama-3 supports 128k context, we can increase history significantly.
        # https://signoz.io/guides/open-ai-api-latency/
        if chat_history:
            # Filtrar mensagens system
            filtered_history = [msg for msg in chat_history if msg.get("role") != "system"]

            # CRITICAL: Prunning - Pegar apenas últimas 15 mensagens (últimos 7 turnos de conversa)
            # Isso aproveita o contexto estendido do Llama-3 no Groq
            recent_history = filtered_history[-15:] if len(filtered_history) > 15 else filtered_history

            for msg in recent_history:
                role = msg.get("role", "user")
                content = msg.get("content", "")
                messages.append({"role": role, "content": content})

            if len(filtered_history) > 15:
                logger.info(f"[CONTEXT PRUNING] Histórico reduzido: {len(filtered_history)} → {len(recent_history)} mensagens (Llama-3 Extended)")

        # RAG: Retrieve similar examples before processing query
        # NOTE: run() is sync, so we skip RAG warming and use sync retrieve
        rag_context_str = ""
        if self.enable_rag and self.retriever and self.retriever._initialized:
            try:
                # Reutilizar lógica de formatação do _get_rag_examples mas de forma síncrona
                similar_docs = self.retriever.retrieve(user_query, top_k=2, method='hybrid')
                if similar_docs:
                    rag_context_str = "\n\n<reference_context>\n"
                    rag_context_str += "⚠️ EXEMPLOS DE INTERAÇÕES PASSADAS (PARA APRENDER A LÓGICA):\n"
                    rag_context_str += "INSTRUÇÃO CRÍTICA: Use estes exemplos APENAS para entender qual ferramenta chamar ou como formatar a resposta.\n"
                    rag_context_str += "PROIBIDO: Não copie números, IDs ou nomes destes exemplos. Os dados abaixo são OBSOLETOS.\n\n"

                    for i, doc in enumerate(similar_docs[:2]):
                        doc_data = doc.get('doc', doc)
                        user_q = doc_data.get('query', doc_data.get('user_query', ''))
                        assist_r = doc_data.get('response', doc_data.get('assistant_response', ''))
                        if len(assist_r) > 500: assist_r = assist_r[:500] + "..."
                        
                        rag_context_str += f"--- EXEMPLO {i+1} ---\nPergunta: {user_q}\nAção Correta: {assist_r}\n"
                    
                    rag_context_str += "</reference_context>\n"
                    logger.info(f"[RAG] Contexto injetado com sucesso (Sync Mode)")
            except Exception as e:
                logger.warning(f"[RAG] Erro ao recuperar exemplos no run() sync: {e}")

        # Add current user query (with context PREPENDED)
        if rag_context_str:
            full_prompt_content = rag_context_str + "\n\n" + "PERGUNTA DO USUÁRIO AGORA:\n" + user_query
        else:
            full_prompt_content = user_query
            
        messages.append({"role": "user", "content": full_prompt_content})

        # FIX CRÍTICO: DETECÇÃO DE KEYWORDS DE GRÁFICO E ANÁLISE
        graph_keywords = [
            "gere um gráfico", "mostre um gráfico", "crie um gráfico", "faça um gráfico",
            "gerar gráfico", "gerar grafico", "gere grafico", "mostre grafico",
            "criar gráfico", "criar grafico", "plote", "visualize", "visualização"
        ]

        # NOVA: Detecção de análise crítica e relatórios (REGRA 5)
        analysis_keywords = [
            "analise", "análise", "críticas", "criticas", "problemas", "melhorias",
            "recomendações", "recomendacoes", "diagnóstico", "diagnostico",
            "avaliação", "avaliacao", "o que devo fazer", "pontos de atenção",
            "pontos de atencao", "ações", "acoes", "relatório", "relatorio",
            "relatório executivo", "relatorio executivo", "relatório de",
            "relatorio de", "gere um relatório", "gere um relatorio"
        ]

        user_query_lower = user_query.lower()
        is_graph_request = any(kw in user_query_lower for kw in graph_keywords)
        is_analysis_request = any(kw in user_query_lower for kw in analysis_keywords)

        # ✅ FIX 2025-12-28: PRIORIZAÇÃO INTELIGENTE (mesmo lógica do async)
        # Se usuário pede EXPLICITAMENTE gráfico, mesmo em análise → GRÁFICO
        # Se usuário pede APENAS análise/relatório (sem gráfico) → TEXTO
        if is_graph_request and is_analysis_request:
            # Caso: "gere um relatório com gráfico" ou "mostre gráfico de vendas do segmento X"
            # PRIORIDADE: Gráfico (usuário quer visualização)
            is_analysis_request = False
            logger.info(f"[GRAPH PRIORITY] Usuário solicitou gráfico explicitamente - modo visualização")
        elif is_analysis_request and not is_graph_request:
            # Caso: "analise o grupo oxford", "gere um relatório de vendas"
            # MODO TEXTO: Análise textual estruturada
            logger.info(f"[ANALYSIS MODE] Análise crítica/relatório detectado - modo textual")

        # ✅ FIX: FEW-SHOT EXAMPLES - DIFERENCIAÇÃO: Gráficos vs Análises Textuais
        # APENAS se histórico estiver vazio ou pequeno (primeiras interações)
        if len(messages) <= 2:
            logger.info("Injetando Few-Shot Examples com v2 para treinar function calling")

            # Escolher exemplos baseado no tipo de request
            if is_analysis_request:
                # EXEMPLOS DE ANÁLISE TEXTUAL (mesmo do async)
                logger.info("Usando few-shot examples de ANÁLISE TEXTUAL")
                few_shot_examples = [
                    # Exemplo 1: Análise Crítica de Segmento
                    {"role": "user", "content": "analise o segmento TECIDOS e me aponte as críticas"},
                    {
                        "role": "model",
                        "tool_calls": [{
                            "id": "call_example_1",
                            "type": "function",
                            "function": {
                                "name": "consultar_dados_flexivel",
                                "arguments": json.dumps({
                                    "filtros": {"NOMESEGMENTO": "TECIDOS"},
                                    "colunas": ["PRODUTO", "NOME", "VENDA_30DD", "ESTOQUE_UNE", "PRECO_VENDA", "NOMECATEGORIA"],
                                    "limite": 100
                                })
                            }
                        }]
                    },
                    {
                        "role": "function",
                        "function_call": {"name": "consultar_dados_flexivel"},
                        "content": json.dumps({
                            "status": "success",
                            "resultados": [
                                {"PRODUTO": "123", "NOME": "Produto A", "VENDA_30DD": 50, "ESTOQUE_UNE": 10, "PRECO_VENDA": 15.0, "NOMECATEGORIA": "CAT1"},
                                {"PRODUTO": "456", "NOME": "Produto B", "VENDA_30DD": 5, "ESTOQUE_UNE": 100, "PRECO_VENDA": 20.0, "NOMECATEGORIA": "CAT2"}
                            ]
                        })
                    },
                    {
                        "role": "model",
                        "content": "**Análise do Segmento TECIDOS**\n\n**Diagnóstico:**\n- 2 produtos analisados\n- Vendas totais 30 dias: **55 unidades**\n- Estoque total: **110 unidades**\n\n**Críticas Identificadas:**\n1. **Produto B (456)**: Baixo giro - apenas 5 vendas com estoque de 100 unidades (excesso de estoque)\n2. **Produto A (123)**: Risco de ruptura - 50 vendas com apenas 10 unidades em estoque\n\n**Recomendações:**\n1. **URGENTE**: Reabastecer Produto A para evitar ruptura\n2. **Médio Prazo**: Reduzir estoque do Produto B via promoção ou transferência\n3. **Análise**: Revisar mix de produtos TECIDOS para otimizar giro"
                    },

                    # Exemplo 2: Diagnóstico de Fabricante
                    {"role": "user", "content": "analise o grupo OXFORD e me aponte as criticas"},
                    {
                        "role": "model",
                        "tool_calls": [{
                            "id": "call_example_2",
                            "type": "function",
                            "function": {
                                "name": "consultar_dados_gerais",
                                "arguments": json.dumps({"busca_termo": "OXFORD"})
                            }
                        }]
                    },
                    {
                        "role": "function",
                        "function_call": {"name": "consultar_dados_gerais"},
                        "content": json.dumps({
                            "status": "success",
                            "total": 250,
                            "mensagem": "250 produtos encontrados do fabricante OXFORD"
                        })
                    },
                    {
                        "role": "model",
                        "content": "**Análise do Grupo OXFORD**\n\n**Diagnóstico Geral:**\n- Total de produtos: **250 SKUs**\n- Fabricante com presença significativa no catálogo\n\n**Pontos Críticos Identificados:**\n1. **Volume de SKUs**: 250 produtos podem indicar complexidade excessiva no mix\n2. **Necessidade de Análise Detalhada**: Recomendo investigar giro individual de cada produto\n3. **Oportunidade**: Avaliar concentração de vendas (Princípio de Pareto)\n\n**Ações Recomendadas:**\n1. **IMEDIATO**: Analisar curva ABC dos produtos OXFORD\n2. **CURTO PRAZO**: Identificar produtos de baixo giro para descontinuação\n3. **MÉDIO PRAZO**: Negociar melhores condições com fornecedor para itens de alto giro\n4. **CONTÍNUO**: Monitorar rupturas nos produtos classe A"
                    }
                ]
            else:
                # EXEMPLOS DE GRÁFICOS (padrão)
                logger.info("Usando few-shot examples de GRÁFICOS")
                few_shot_examples = [
                    # Exemplo 1: Gráfico simples
                    {"role": "user", "content": "gere um gráfico de vendas por categoria"},
                    {
                        "role": "model",
                        "tool_calls": [{
                            "id": "call_example_1",
                            "type": "function",
                            "function": {
                                "name": "gerar_grafico_universal_v2",
                                "arguments": json.dumps({"descricao": "vendas por categoria", "tipo_grafico": "auto"})
                            }
                        }]
                    },
                    {
                        "role": "function",
                        "function_call": {"name": "gerar_grafico_universal_v2"},
                        "content": json.dumps({
                            "status": "success",
                            "chart_data": "{\"data\": [], \"layout\": {}}",
                            "summary": {"mensagem": "Gráfico gerado com sucesso"}
                        })
                    },
                    {"role": "model", "content": "Analisei as vendas por categoria. Aqui está o gráfico solicitado."}
                ]

            # Inserir examples ANTES da query atual
            messages = messages[:-1] + few_shot_examples + [messages[-1]]

        # ✅ FIX: PREFILL - Guiar LLM para resposta correta
        if is_graph_request:
            logger.warning(f"GRAFICO DETECTADO: '{user_query[:50]}...' - Ativando PREFILL")
            messages.append({
                "role": "model",
                "content": "Vou gerar o gráfico usando a ferramenta apropriada:"
            })
        elif is_analysis_request:
            logger.warning(f"ANALISE CRITICA DETECTADA: '{user_query[:50]}...' - Ativando PREFILL TEXTUAL")
            messages.append({
                "role": "model",
                "content": "Vou analisar os dados e fornecer uma análise textual estruturada com diagnóstico, críticas e recomendações:"
            })

        max_turns = 20  # ✅ FIX 2025-12-28: Aumentado de 10 para 20 para análises críticas e relatórios complexos
        current_turn = 0
        successful_tool_calls = 0  # NOVO: Contador de ferramentas bem-sucedidas

        # ✅ CRITICAL FIX 2025-12-28: Filtrar ferramentas de gráfico para análises críticas
        # Forçar uso de ferramentas de consulta de dados ao invés de gráficos
        tools_to_use = self.gemini_tools
        if is_analysis_request:
            # Criar lista filtrada de ferramentas (sem gráficos)
            analysis_tool_names = [
                "consultar_dados_flexivel",
                "buscar_produtos_inteligente",
                "consultar_dados_gerais",
                "calcular_abastecimento_une",
                "calcular_mc_produto",
                "calcular_preco_final_une",
                "validar_transferencia_produto",
                "sugerir_transferencias_automaticas",
                "encontrar_rupturas_criticas"
            ]

            filtered_declarations = [
                decl for decl in self.gemini_tools.get("function_declarations", [])
                if decl["name"] in analysis_tool_names
            ]

            tools_to_use = {"function_declarations": filtered_declarations}
            logger.info(f"[ANALYSIS MODE] Filtered tools: {len(filtered_declarations)} tools (removed chart tools)")

        while current_turn < max_turns:
            try:
                # Call LLM with tools
                # Note: self.llm is GeminiLLMAdapter
                response = self.llm.get_completion(messages, tools=tools_to_use)

                if "error" in response:
                    logger.error(f"LLM Error: {response['error']}")
                    return self._generate_error_response(response['error'])

                # FIX: LOGGING DETALHADO - Detectar quando LLM ignora solicitações de gráfico
                response_type = "tool_call" if "tool_calls" in response else "text"
                logger.info(f"LLM Response Type: {response_type}")

                # ALERTA se pediu gráfico mas LLM respondeu só com texto
                if response_type == "text" and is_graph_request and successful_tool_calls == 0:
                    logger.error(f"WARNING: LLM IGNOROU PEDIDO DE GRAFICO!")
                    logger.error(f"WARNING - User Query: {user_query}")
                    logger.error(f"WARNING - LLM Text Response: {response.get('content', '')[:300]}")
                    logger.error(f"WARNING - Total messages in context: {len(messages)}")

                    # FALLBACK AUTOMÁTICO: Se LLM ignorou, forçar chamada da ferramenta manualmente
                    logger.warning(f"FALLBACK: Forcando chamada manual de gerar_grafico_universal_v2")
                    # Criar tool call sintético
                    synthetic_tool_call = {
                        "id": "call_fallback_graph",
                        "type": "function",
                        "function": {
                            "name": "gerar_grafico_universal_v2",
                            "arguments": json.dumps({"descricao": user_query})
                        }
                    }
                    # Injetar tool call sintético na resposta
                    response["tool_calls"] = [synthetic_tool_call]
                    logger.warning(f"FALLBACK APLICADO: Tool call sintetico criado")

                # Check for tool calls
                if "tool_calls" in response:
                    tool_calls = response["tool_calls"]
                    messages.append({
                        "role": "model",
                        "tool_calls": tool_calls
                    })

                    # Execute each tool
                    should_exit_early = False
                    for tc in tool_calls:
                        func_name = tc["function"]["name"]
                        tool_call_id = tc.get("id") # CRITICAL: Capture ID
                        func_args = json.loads(tc["function"]["arguments"])
                        
                        logger.info(f"Agent calling tool: {func_name} with args: {func_args}")
                        
                        # Find the matching tool
                        tool_to_run = next((t for t in self.bi_tools if t.name == func_name), None)
                        
                        tool_result = None
                        if tool_to_run:
                            try:
                                # Execute tool
                                tool_output = tool_to_run.invoke(func_args)

                                # CRITICAL FIX: Detectar se gerou gráfico com sucesso
                                if isinstance(tool_output, dict):
                                    is_chart = "chart_data" in tool_output or "chart_spec" in tool_output
                                    is_success = tool_output.get("status") == "success" or len(tool_output.get("resultados", [])) > 0
                                    
                                    if is_chart and is_success:
                                        logger.info(f"SUCESSO: Grafico gerado por {func_name}. Forcando saida antecipada.")
                                        successful_tool_calls += 1
                                        should_exit_early = True
                                    elif is_success:
                                        successful_tool_calls += 1

                                # CRÍTICO: Converter MapComposite para dict ANTES de serializar
                                def convert_mapcomposite(obj):
                                    """Recursivamente converte MapComposite para dict"""
                                    if hasattr(obj, '_mapping'):
                                        return dict(obj._mapping)
                                    elif isinstance(obj, dict):
                                        return {k: convert_mapcomposite(v) for k, v in obj.items()}
                                    elif isinstance(obj, list):
                                        return [convert_mapcomposite(item) for item in obj]
                                    return obj
                                
                                # Converter o output antes de usar
                                tool_result = convert_mapcomposite(tool_output)
                                logger.info(f"Tool {func_name} executed successfully, result type: {type(tool_result)}")
                            except Exception as e:
                                logger.error(f"Error executing {func_name}: {e}", exc_info=True)
                                tool_result = {"error": str(e)}
                        else:
                            tool_result = {"error": f"Tool {func_name} not found"}

                        # Add tool result to messages
                        messages.append({
                            "role": "function", # Adapter will map this to user/function_response
                            "name": func_name,
                            "tool_call_id": tool_call_id, # CRITICAL
                            "content": safe_json_serialize(tool_result)
                        })

                    if should_exit_early:
                        logger.info("Saindo do loop para retornar grafico imediatamente.")
                        # ✅ FIX: Forçar uma última iteração para LLM gerar texto narrativo
                        # Adicionar mensagem sintética para forçar resposta final
                        messages.append({
                            "role": "user",
                            "content": "Apresente o gráfico de forma clara e concisa."
                        })
                        # Continuar para obter resposta final do LLM
                        current_turn += 1
                        continue

                    # Loop continues to send tool outputs back to LLM
                    current_turn += 1
                    continue
                
                # If no tool calls, it's a text response (Final Answer)
                content = response.get("content", "")

                # CONTEXT7: Limpar JSON bruto da resposta (improved 2025-12-27)
                content = self._clean_context7_violations(content, context_type="generic")

                # NOVO: Verificar TODAS as ferramentas para encontrar gráficos ou tabelas
                # PRIORIDADE: Gráficos > Tabelas Markdown > Dados brutos > Texto do LLM
                logger.info(f"DEBUG: Verificando dados tabulares/gráficos. Total de mensagens: {len(messages)}")

                # Acumuladores para múltiplos resultados de ferramentas
                found_chart_data = None
                found_chart_summary = None
                found_table_mensagem = None
                found_resultados = None

                # Percorrer TODAS as mensagens de função (não parar no primeiro)
                for msg in reversed(messages):
                    if msg.get("role") == "function":
                        try:
                            content_str = msg.get("content", "{}")
                            func_content = json.loads(content_str)

                            # PRIMEIRO: Verificar se a ferramenta retornou um gráfico (chart_data)
                            chart_data = func_content.get("chart_data")
                            if chart_data and func_content.get("status") == "success" and found_chart_data is None:
                                logger.info(f"SUCESSO: Gráfico detectado (chart_type: {func_content.get('chart_type', 'unknown')})")

                                # CRÍTICO: chart_data pode ser string JSON (de fig.to_json())
                                # O frontend espera um objeto, não uma string
                                if isinstance(chart_data, str):
                                    try:
                                        chart_data = json.loads(chart_data)
                                        logger.info("chart_data parseado de string para objeto")
                                    except json.JSONDecodeError:
                                        logger.error("Falha ao parsear chart_data como JSON")
                                        continue  # Tentar próxima mensagem

                                found_chart_data = chart_data
                                found_chart_summary = func_content.get("summary", {})
                                # Continuar buscando para não perder outras ferramentas
                            
                            # SEGUNDO: Verificar se a mensagem contém uma tabela Markdown
                            mensagem = func_content.get("mensagem", "")
                            if isinstance(mensagem, str) and "|" in mensagem and "---" in mensagem and found_table_mensagem is None:
                                logger.info(f"SUCESSO: Tabela Markdown detectada na mensagem da ferramenta!")
                                found_table_mensagem = mensagem
                            
                            # TERCEIRO: Verificar se há dados brutos para retornar
                            resultados = func_content.get("resultados", [])
                            if isinstance(resultados, list) and len(resultados) > 0 and found_resultados is None:
                                logger.info(f"SUCESSO: Dados tabulares detectados: {len(resultados)} registros")
                                found_resultados = resultados

                        except Exception as e:
                            logger.error(f"DEBUG: Erro ao parsear mensagem de função: {e}")
                            continue  # Tentar próxima mensagem

                # PRIORIDADE DE RETORNO: Gráfico tem maior prioridade
                if found_chart_data is not None:
                    # CONTEXT7: Limpar JSON bruto e aplicar narrativa
                    content = self._clean_context7_violations(content, context_type="chart")

                    return {
                        "type": "code_result",
                        "result": {
                            "result": found_chart_summary,
                            "chart_spec": found_chart_data
                        },
                        "chart_spec": found_chart_data,
                        "text_override": content
                    }
                
                # PRIORIDADE 2: Dados Tabulares (Se encontrou resultados mas não é gráfico)
                elif found_resultados is not None:
                    # CONTEXT7: Limpar JSON bruto e aplicar narrativa
                    content = self._clean_context7_violations(content, context_type="data")
                    
                    return {
                        "type": "code_result",
                        "result": found_resultados, # Lista de dicts para o frontend renderizar Tabela
                        "text_override": content
                    }

                # SAFETY NET: Check if the content is the specific JSON ReAct pattern OR just a JSON block and extract/convert
                try:
                    if isinstance(content, str):
                        content_stripped = content.strip()
                        # Caso 1: JSON Puro (o problema relatado)
                        if content_stripped.startswith("{") and content_stripped.endswith("}"):
                            try:
                                json_data = json.loads(content_stripped)
                                
                                # Se for o formato analítico específico que o usuário mostrou
                                if "analise_executiva" in json_data:
                                    # Converter para Markdown Bonito
                                    md_output = ""
                                    
                                    # 1. Manchete
                                    exec_data = json_data.get("analise_executiva", {})
                                    emoji_status = "🚨" if "ALERTA" in str(exec_data.get("status_geral", "")).upper() else "📊"
                                    md_output += f"### {emoji_status} {exec_data.get('manchete', 'Análise de Dados')}\n\n"
                                    
                                    # 2. Diagnóstico
                                    md_output += "**Diagnóstico Detalhado:**\n"
                                    diag_data = json_data.get("diagnostico_por_unidade", {})
                                    for unidade, dados in diag_data.items():
                                        insight = dados.get("insight", "")
                                        situacao = dados.get("situacao", "")
                                        md_output += f"- **{unidade} ({situacao})**: {insight}\n"
                                    md_output += "\n"
                                    
                                    # 3. Estratégia
                                    md_output += "**Estratégia Recomendada:**\n"
                                    strategies = json_data.get("estrategia_recomendada", [])
                                    if isinstance(strategies, list):
                                        for strat in strategies:
                                            md_output += f"- {strat}\n"
                                    elif isinstance(strategies, str):
                                        md_output += f"{strategies}\n"
                                        
                                    logger.info("SAFETY NET: Converteu JSON analítico para Markdown.")
                                    content = md_output

                                # Caso 2: ReAct Pattern (Legacy)
                                elif "action" in json_data and "content" in json_data:
                                    logger.info("SAFETY NET: Extracted content from ReAct JSON pattern.")
                                    content = json_data["content"]
                                
                            except json.JSONDecodeError:
                                pass # Não é JSON válido, segue o baile
                except Exception as e:
                    logger.warning(f"SAFETY NET: Failed to parse potential JSON content: {e}")

                # Caso contrário, retornar resposta de texto normal do LLM
                return {
                    "type": "text",
                    "result": content
                }

            except Exception as e:
                logger.error(f"Exception in agent run loop: {e}", exc_info=True)
                return self._generate_error_response(str(e))

        # FIX: Antes de retornar erro, verificar se há gráfico gerado com sucesso
        # Isso evita perder o trabalho se o LLM não retornou texto mas gerou o gráfico
        logger.warning("Max turns atingido. Verificando se ha grafico para retornar...")

        for msg in reversed(messages):
            if msg.get("role") == "function":
                try:
                    content_str = msg.get("content", "{}")
                    func_content = json.loads(content_str)
                    chart_data = func_content.get("chart_data")

                    if chart_data and func_content.get("status") == "success":
                        logger.info("Grafico encontrado! Retornando mesmo sem texto final do LLM.")
                        if isinstance(chart_data, str):
                            try:
                                chart_data = json.loads(chart_data)
                            except:
                                pass

                        return {
                            "type": "code_result",
                            "result": {
                                "result": func_content.get("summary", {}),
                                "chart_spec": chart_data
                            },
                            "chart_spec": chart_data,
                            "text_override": "Aqui está o gráfico solicitado."
                        }
                except:
                    continue

        return self._generate_error_response("Maximum conversation turns exceeded.")

    def _create_tool_summary(self, tool_result: Dict[str, Any], func_name: str) -> Dict[str, Any]:
        """
        OPTIMIZATION 2025: Cria resumo compacto de tool response
        Reduz tamanho do contexto enviado ao LLM em 70-90%
        Ref: ChatGPT engineering - context filtering
        """
        if not isinstance(tool_result, dict):
            return tool_result

        # Se é erro, retornar completo
        if "error" in tool_result:
            return tool_result

        summary = {}

        # 1. Agregações - retornar completo (já são pequenas)
        if "resultado_agregado" in tool_result or "valor" in tool_result:
            return tool_result

        # 2. Listas de resultados - enviar apenas amostra + metadados
        if "resultados" in tool_result and isinstance(tool_result["resultados"], list):
            resultados = tool_result["resultados"]
            total = len(resultados)

            # Enviar apenas 3 registros de amostra ao LLM
            summary["resultados"] = resultados[:3] if total > 3 else resultados
            summary["total_resultados"] = total
            summary["_amostra"] = True if total > 3 else False

            # Manter mensagem se existir
            if "mensagem" in tool_result:
                summary["mensagem"] = tool_result["mensagem"]

            logger.info(f"[TOOL SUMMARY] {func_name}: {total} registros → enviando amostra de {len(summary['resultados'])}")
            return summary

        # 3. Chart data - PRESERVAR chart_data completo para renderização no frontend
        # CRITICAL FIX: As ferramentas de gráfico retornam 'chart_data', não 'chart_spec'
        if "chart_data" in tool_result:
            # Preservar chart_data COMPLETO - será usado pelo frontend para renderizar
            summary["status"] = tool_result.get("status", "success")
            summary["chart_type"] = tool_result.get("chart_type", "unknown")
            summary["chart_data"] = tool_result["chart_data"]  # MANTER INTACTO
            summary["mensagem"] = tool_result.get("mensagem", "Gráfico gerado com sucesso")
            
            if "summary" in tool_result:
                summary["summary"] = tool_result["summary"]

            logger.info(f"[TOOL SUMMARY] {func_name}: Chart data preservado (chart_type={summary['chart_type']})")
            return summary

        # 4. Chart spec (legacy) - enviar apenas metadados para o LLM
        if "chart_spec" in tool_result:
            spec = tool_result.get("chart_spec", {})
            summary["chart_type"] = spec.get("type", "unknown")
            summary["chart_generated"] = True
            summary["chart_spec"] = spec  # Preservar chart_spec para o frontend
            summary["mensagem"] = tool_result.get("mensagem", "Gráfico gerado com sucesso")

            # Contar pontos de dados
            if "data" in spec and isinstance(spec["data"], list) and len(spec["data"]) > 0:
                summary["data_points"] = len(spec["data"][0].get("x", []))

            logger.info(f"[TOOL SUMMARY] {func_name}: Chart spec preservado")
            return summary

        # 5. Outros casos - retornar original se pequeno
        return tool_result


    def _generate_error_response(self, error_msg: str) -> Dict[str, Any]:
        return {
            "type": "text",
            "result": f"Desculpe, encontrei um erro ao processar sua solicitação: {error_msg}"
        }
