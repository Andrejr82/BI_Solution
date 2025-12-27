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
)
from app.core.tools.flexible_query_tool import consultar_dados_flexivel

# Import NEW universal chart tool - Context7 2025 Best Practice
from app.core.tools.universal_chart_generator import gerar_grafico_universal_v2

# Import legacy chart tools for compatibility
from app.core.tools.chart_tools import (
    gerar_ranking_produtos_mais_vendidos,
    gerar_dashboard_executivo,
    listar_graficos_disponiveis,
    gerar_visualizacao_customizada
)

# Optional: Import CodeGenAgent just for type hinting if needed,
# but we won't use it for logic anymore.
from app.core.utils.field_mapper import FieldMapper

# Import TypeConverter para serialização segura
from app.core.utils.serializers import TypeConverter, safe_json_dumps

# Alias para manter compatibilidade com código existente
safe_json_serialize = safe_json_dumps

# System instruction - Analista de BI Focado em Ferramentas (Versão Simplificada 2025)
SYSTEM_PROMPT = """Você é um Analista de Business Intelligence com acesso direto ao Data Lake da empresa.

## 🎯 SUA MISSÃO
Responder perguntas de negócio usando FERRAMENTAS disponíveis para obter dados reais e gerar visualizações.

## 📊 DADOS DISPONÍVEIS (Schema do Data Lake)
**Colunas Principais:**
- `PRODUTO` (código), `NOME` (descrição)
- `UNE` (loja), `NOMESEGMENTO`, `NOMECATEGORIA`, `NOMEFABRICANTE`
- `VENDA_30DD` (vendas últimos 30 dias)
- `ESTOQUE_UNE` (estoque loja), `ESTOQUE_CD` (estoque centro distribuição)
- `PRECO_VENDA`, `PRECO_CUSTO`

## 🔧 FERRAMENTAS QUE VOCÊ POSSUI

**Visualização (USE SEMPRE que pedirem gráficos):**
- `gerar_grafico_universal`: Gera qualquer tipo de gráfico (barras, pizza, linha, ranking)
- `gerar_ranking_produtos_mais_vendidos`: Top N produtos
- `gerar_dashboard_executivo`: Dashboard completo

**Consulta de Dados:**
- `consultar_dados_flexivel`: Consulta genérica ao Data Lake
- `consultar_dados_gerais`: Consultas específicas

**Análises Especializadas:**
- `encontrar_rupturas_criticas`: Produtos em ruptura
- `sugerir_transferencias_automaticas`: Sugestões de transferência
- `calcular_abastecimento_une`: Necessidade de reposição

## 🚨 REGRAS OBRIGATÓRIAS DE USO DE FERRAMENTAS

### REGRA 1: SOLICITAÇÕES DE GRÁFICO (CRÍTICO)
Quando o usuário disser:
- "gere um gráfico..."
- "mostre um gráfico..."
- "crie um gráfico..."
- "faça um gráfico..."
- "gerar gráfico..."
- "visualize..."
- "plote..."

**AÇÃO OBRIGATÓRIA:**
→ Chame IMEDIATAMENTE `gerar_grafico_universal_v2(descricao="...", filtro_une=X, filtro_segmento="Y")`
→ SEMPRE extraia filtros da pergunta do usuário (UNE, segmento, categoria)
→ NÃO responda com texto explicando o que vai fazer
→ NÃO pergunte confirmação
→ NUNCA diga "não consigo gerar gráficos"

**Exemplos:**
- Usuário: "gere um gráfico de vendas por segmento da une 1685"
  → Você: [Chama gerar_grafico_universal_v2(descricao="vendas por segmento", filtro_une=1685)]

- Usuário: "mostre estoque por categoria no segmento ARMARINHO"
  → Você: [Chama gerar_grafico_universal_v2(descricao="estoque por categoria", filtro_segmento="ARMARINHO")]

- Usuário: "top produtos mais vendidos"
  → Você: [Chama gerar_ranking_produtos_mais_vendidos(top_n=10)]

### REGRA 2: CONSULTAS DE DADOS
Para perguntas sobre números, top N, listas:
→ Use `consultar_dados_flexivel` primeiro
→ Depois apresente os resultados em texto narrativo

### REGRA 3: NUNCA INVENTE DADOS
- Use APENAS dados retornados pelas ferramentas
- Se não houver dados, diga: "Não encontrei registros para essa consulta"

## 📝 COMO RESPONDER

**Para gráficos solicitados:**
1. Chame a ferramenta correspondente (gerar_grafico_universal, etc)
2. Aguarde o resultado
3. Adicione breve contexto textual SOMENTE com dados REAIS retornados pela ferramenta

**Para análises textuais:**
1. Chame a ferramenta de dados primeiro (consultar_dados_flexivel, etc)
2. Use APENAS os números retornados pela ferramenta
3. Apresente em formato narrativo destacando métricas chave em **negrito**

## ⛔ PROIBIÇÕES ABSOLUTAS
- **NUNCA invente dados, números ou projeções**
- **NUNCA diga "não consigo gerar gráficos"** (você PODE via ferramentas)
- **NUNCA responda sem chamar ferramentas** quando o usuário pedir gráficos
- **NUNCA retorne JSON bruto** ao usuário
- **NUNCA crie análises sem dados** retornados por ferramentas

## ✅ REGRA DE OURO
**TODO número, métrica ou insight DEVE vir de uma ferramenta. ZERO exceções.**
"""

class CaculinhaBIAgent:
    """
    Agent responsible for Business Intelligence queries using Gemini Native Function Calling.
    Replaces the legacy keyword-based routing and CodeGenAgent fallback.
    """
    def __init__(self, llm: Any, code_gen_agent: Any, field_mapper: FieldMapper):
        # llm is expected to be GeminiLLMAdapter
        self.llm = llm
        self.field_mapper = field_mapper
        
        # We keep code_gen_agent in init to maintain compatibility with chat.py,
        # but we won't use it effectively.
        self.code_gen_agent = code_gen_agent

        # Define available tools - ORDEM IMPORTA! Ferramentas mais genéricas primeiro
        self.bi_tools = [
            consultar_dados_flexivel,  # NOVA: Ferramenta genérica e flexível
            consultar_dados_gerais,
            calcular_abastecimento_une,
            calcular_mc_produto,
            calcular_preco_final_une,
            validar_transferencia_produto,
            sugerir_transferencias_automaticas,
            encontrar_rupturas_criticas,
            # Ferramentas VISUAIS (Context7 2025 - Nova Geração)
            gerar_grafico_universal_v2,  # FIX: Nova ferramenta com filtros dinâmicos
            gerar_ranking_produtos_mais_vendidos,
            gerar_dashboard_executivo,
            listar_graficos_disponiveis,
            gerar_visualizacao_customizada,
        ]

        # Convert LangChain tools to Gemini Function Declarations
        self.gemini_tools = self._convert_tools_to_gemini_format(self.bi_tools)
        
        # System instruction - Conversacional + BI Expert (Context7 Enhanced v2025)
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

    def _clean_schema(self, schema: Dict[str, Any]) -> Dict[str, Any]:
        """
        Recursively cleans Pydantic JSON Schema for Gemini compatibility.
        Removes 'anyOf', 'title', 'default', 'additionalProperties', and handles Optional types.
        """
        if not isinstance(schema, dict):
            return schema
            
        new_schema = schema.copy()
        
        # Remove incompatible keys
        if "title" in new_schema:
            del new_schema["title"]
        if "default" in new_schema:
            # Gemini sometimes complains about defaults in complex ways,
            # but keeping them is usually fine. Removing 'title' is most important.
            del new_schema["default"]
        if "additionalProperties" in new_schema:
            # Gemini API doesn't support 'additionalProperties' field
            del new_schema["additionalProperties"]

        # Handle anyOf (generated by Pydantic for Optional[Type])
        if "anyOf" in new_schema:
            options = new_schema.pop("anyOf")
            # Find the first non-null option
            valid_option = next((opt for opt in options if opt.get("type") != "null"), None)
            if valid_option:
                # Merge the valid option into the current schema
                # We recurse here to clean the child option too
                cleaned_child = self._clean_schema(valid_option)
                new_schema.update(cleaned_child)
            else:
                # Fallback if all are null (unlikely) or empty
                new_schema["type"] = "string" 

        # Recurse into properties
        if "properties" in new_schema:
            for prop, prop_schema in new_schema["properties"].items():
                new_schema["properties"][prop] = self._clean_schema(prop_schema)
        
        # Recurse into array items
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
        Executes the agent loop:
        1. Send query + tools to LLM.
        2. If LLM wants to call tool -> Execute tool -> Send result back to LLM.
        3. Repeat until LLM returns text.
        
        Args:
            user_query: The user's question
            chat_history: Previous conversation messages
            on_progress: Async callback function for status updates (e.g. tool execution started)
        """
        logger.info(f"CaculinhaBIAgent (Modern Async): Processing query: {user_query}")

        messages = []

        # OPTIMIZATION 2025: Context Pruning - Manter apenas últimas 6 mensagens
        if chat_history:
            filtered_history = [msg for msg in chat_history if msg.get("role") != "system"]
            recent_history = filtered_history[-6:] if len(filtered_history) > 6 else filtered_history

            for msg in recent_history:
                role = msg.get("role", "user")
                content = msg.get("content", "")
                messages.append({"role": role, "content": content})

        # Add current user query
        messages.append({"role": "user", "content": user_query})

        # ✅ FIX: DETECÇÃO DE KEYWORDS (mesmo código do run())
        graph_keywords = [
            "gere um gráfico", "mostre um gráfico", "crie um gráfico", "faça um gráfico",
            "gerar gráfico", "gerar grafico", "gere grafico", "mostre grafico",
            "criar gráfico", "criar grafico", "plote", "visualize", "visualização"
        ]
        user_query_lower = user_query.lower()
        is_graph_request = any(kw in user_query_lower for kw in graph_keywords)

        # ✅ FIX: FEW-SHOT EXAMPLES (mesmo código do run())
        if len(messages) <= 2:
            logger.info("[ASYNC] Injetando Few-Shot Examples")
            few_shot_examples = [
                {"role": "user", "content": "gere um gráfico de vendas por categoria"},
                {
                    "role": "model",
                    "tool_calls": [{
                        "id": "call_example_1",
                        "type": "function",
                        "function": {
                            "name": "gerar_grafico_universal",
                            "arguments": json.dumps({"descricao": "vendas por categoria"})
                        }
                    }]
                },
                {
                    "role": "function",
                    "function_call": {"name": "gerar_grafico_universal"},
                    "content": json.dumps({
                        "status": "success",
                        "chart_data": "{\"data\": [], \"layout\": {}}",
                        "summary": {"mensagem": "Gráfico gerado"}
                    })
                },
                {"role": "model", "content": "Aqui está o gráfico solicitado."}
            ]
            messages = messages[:-1] + few_shot_examples + [messages[-1]]

        # ✅ FIX: PREFILL (mesmo código do run())
        if is_graph_request:
            logger.warning(f"[ASYNC] GRAFICO DETECTADO - Ativando PREFILL")
            messages.append({
                "role": "model",
                "content": "Vou gerar o gráfico usando a ferramenta apropriada:"
            })

        max_turns = 10  # ✅ FIXED: Aumentado de 5 para 10 para queries complexas
        current_turn = 0
        successful_tool_calls = 0  # 🚨 NOVO: Contador de ferramentas bem-sucedidas

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
                    tools=self.gemini_tools
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

                    # Execute each tool
                    should_exit_early = False
                    for tc in tool_calls:
                        func_name = tc["function"]["name"]
                        func_args = json.loads(tc["function"]["arguments"])
                        
                        # Notify tool start
                        if on_progress:
                            await on_progress({"type": "tool_progress", "tool": func_name, "status": "executing"})

                        # Find the matching tool
                        tool_to_run = next((t for t in self.bi_tools if t.name == func_name), None)
                        
                        tool_result = None
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
                                
                                tool_result = convert_mapcomposite(tool_output)

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

                            except Exception as e:
                                logger.error(f"Error executing {func_name}: {e}")
                                tool_result = {"error": str(e)}
                        else:
                            tool_result = {"error": f"Tool {func_name} not found"}

                        # Add tool result to messages
                        messages.append({
                            "role": "function",
                            "function_call": {"name": func_name},
                            "content": safe_json_serialize(tool_result)
                        })

                    if should_exit_early:
                        logger.info("[ASYNC] Saindo do loop para retornar grafico imediatamente.")
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
                    # CONTEXT7: Limpar o conteúdo de texto do LLM se contiver JSON bruto
                    import re
                    if isinstance(content, str):
                        # Remover blocos JSON grandes da resposta de texto
                        json_pattern = r'\{[\s\S]*?"data"[\s\S]*?"layout"[\s\S]*?\}'
                        content_clean = re.sub(json_pattern, "", content).strip()
                        if content_clean:
                            content = content_clean
                        else:
                            content = "Aqui está o gráfico solicitado:"

                    return {
                        "type": "code_result",
                        "result": {
                            "result": found_chart_summary,
                            "chart_spec": found_chart_data
                        },
                        "chart_spec": found_chart_data,
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

        # OPTIMIZATION 2025: Context Pruning - Manter apenas últimas 6 mensagens (3 turnos)
        # Ref: ChatGPT engineering best practices - reduz latência em ~40-60%
        # https://signoz.io/guides/open-ai-api-latency/
        if chat_history:
            # Filtrar mensagens system
            filtered_history = [msg for msg in chat_history if msg.get("role") != "system"]

            # CRITICAL: Prunning - Pegar apenas últimas 6 mensagens (últimos 3 turnos de conversa)
            # Isso reduz drasticamente o tamanho do contexto enviado ao Gemini
            recent_history = filtered_history[-6:] if len(filtered_history) > 6 else filtered_history

            for msg in recent_history:
                role = msg.get("role", "user")
                content = msg.get("content", "")
                messages.append({"role": role, "content": content})

            if len(filtered_history) > 6:
                logger.info(f"[CONTEXT PRUNING] Histórico reduzido: {len(filtered_history)} → {len(recent_history)} mensagens")

        # Add current user query
        messages.append({"role": "user", "content": user_query})

        # ✅ FIX CRÍTICO: DETECÇÃO DE KEYWORDS DE GRÁFICO
        graph_keywords = [
            "gere um gráfico", "mostre um gráfico", "crie um gráfico", "faça um gráfico",
            "gerar gráfico", "gerar grafico", "gere grafico", "mostre grafico",
            "criar gráfico", "criar grafico", "plote", "visualize", "visualização"
        ]
        user_query_lower = user_query.lower()
        is_graph_request = any(kw in user_query_lower for kw in graph_keywords)

        # ✅ FIX: FEW-SHOT EXAMPLES - Injetar exemplos de uso correto de ferramentas
        # APENAS se histórico estiver vazio ou pequeno (primeiras interações)
        if len(messages) <= 2:  # Usuário atual + no máximo 1 mensagem anterior
            logger.info("Injetando Few-Shot Examples para treinar function calling")
            few_shot_examples = [
                {"role": "user", "content": "gere um gráfico de vendas por categoria"},
                {
                    "role": "model",
                    "tool_calls": [{
                        "id": "call_example_1",
                        "type": "function",
                        "function": {
                            "name": "gerar_grafico_universal",
                            "arguments": json.dumps({"descricao": "vendas por categoria"})
                        }
                    }]
                },
                {
                    "role": "function",
                    "function_call": {"name": "gerar_grafico_universal"},
                    "content": json.dumps({
                        "status": "success",
                        "chart_data": "{\"data\": [], \"layout\": {}}",
                        "summary": {"mensagem": "Gráfico gerado com sucesso"}
                    })
                },
                {"role": "model", "content": "Aqui está o gráfico de vendas por categoria solicitado."}
            ]
            # Inserir examples ANTES da query atual
            messages = messages[:-1] + few_shot_examples + [messages[-1]]

        # ✅ FIX: PREFILL - Forçar início de resposta para gráficos
        # Se detectou keyword de gráfico, adicionar prefill que força o LLM a usar ferramenta
        if is_graph_request:
            logger.warning(f"GRAFICO DETECTADO: '{user_query[:50]}...' - Ativando PREFILL")
            # Adicionar mensagem parcial do modelo forçando uso da ferramenta
            # Isso "guia" o LLM a continuar com function calling
            messages.append({
                "role": "model",
                "content": "Vou gerar o gráfico usando a ferramenta apropriada:"
            })

        max_turns = 10  # ✅ FIXED: Aumentado de 5 para 10 para queries complexas
        current_turn = 0
        successful_tool_calls = 0  # NOVO: Contador de ferramentas bem-sucedidas

        while current_turn < max_turns:
            try:
                # Call LLM with tools
                # Note: self.llm is GeminiLLMAdapter
                response = self.llm.get_completion(messages, tools=self.gemini_tools)

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
                            "function_call": {"name": func_name}, # Metadata for adapter
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

                # CRITICAL FIX: NUNCA retornar JSON cru ao usuário (Context7 Storytelling)
                if isinstance(content, str):
                    # Se content parece JSON de gráfico/dados, limpar
                    if content.strip().startswith("{") and ('"data"' in content or '"layout"' in content or '"chart_spec"' in content):
                        try:
                            json.loads(content)  # Validar se é JSON
                            logger.warning("CONTEXT7 VIOLATION: LLM retornou JSON puro. Substituindo.")
                            content = "Aqui estão os dados solicitados."
                        except:
                            pass  # Não é JSON válido, manter original
                    # Se tem blocos JSON enormes inline, remover
                    import re
                    json_pattern = r'\{[\s\S]*?"data"[\s\S]*?"layout"[\s\S]*?\}'
                    if re.search(json_pattern, content):
                        content = re.sub(json_pattern, "", content).strip()
                        if not content:
                            content = "Aqui estão os dados solicitados."

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
                    # CONTEXT7: Limpar o conteúdo de texto do LLM se contiver JSON bruto
                    import re
                    if isinstance(content, str):
                        # Remover blocos JSON grandes da resposta de texto
                        json_pattern = r'\{[\s\S]*?"data"[\s\S]*?"layout"[\s\S]*?\}'
                        content_clean = re.sub(json_pattern, "", content).strip()
                        if content_clean:
                            content = content_clean
                        else:
                            content = "Aqui está o gráfico solicitado:"
                        logger.info(f"CONTEXT7: Texto do LLM limpo de JSON bruto. Novo texto: {content[:100]}...")

                    return {
                        "type": "code_result",
                        "result": {
                            "result": found_chart_summary,
                            "chart_spec": found_chart_data
                        },
                        "chart_spec": found_chart_data,
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
