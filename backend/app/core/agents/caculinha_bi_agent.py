import json
import logging
import numpy as np
import pandas as pd
from decimal import Decimal
from datetime import datetime, date
from typing import Any, Dict, List, Optional
from langchain_core.language_models import BaseChatModel
from langchain_core.tools import BaseTool

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

# Optional: Import CodeGenAgent just for type hinting if needed,
# but we won't use it for logic anymore.
from app.core.utils.field_mapper import FieldMapper

logger = logging.getLogger(__name__)


def safe_json_serialize(obj: Any) -> str:
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
        return json.dumps(obj, ensure_ascii=False, default=default_handler)
    except Exception as e:
        logger.error(f"Failed to serialize object: {e}", exc_info=True)
        # Ultimate fallback: return error as JSON
        return json.dumps({"error": f"Serialization failed: {str(e)}"}, ensure_ascii=False)

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
        ]

        # Convert LangChain tools to Gemini Function Declarations
        self.gemini_tools = self._convert_tools_to_gemini_format(self.bi_tools)
        
        # System instruction - Conversacional + BI Expert
        self.system_prompt = """Você é o Assistente de BI da Caculinha, powered by Gemini 2.0.
Você é um assistente conversacional inteligente com expertise em Business Intelligence e análise de dados.

PERSONALIDADE:
- Conversacional e amigável, como ChatGPT
- Responda a QUALQUER pergunta, não apenas sobre BI ou dados
- Para perguntas gerais (saudações, conhecimentos gerais, etc.): responda normalmente de forma útil e precisa
- Para perguntas sobre dados de BI: use suas ferramentas especializadas

QUANDO USAR FERRAMENTAS BI:
Use as ferramentas APENAS quando o usuário perguntar sobre:
- Dados de estoque, vendas, produtos, lojas (UNE)
- Análises de transferências, abastecimento, rupturas
- Preços, margens, fabricantes, segmentos
- Qualquer consulta que envolva o banco de dados admmat.parquet

BANCO DE DADOS: admmat.parquet (1.113.822 registros, 97 colunas)

COLUNAS PRINCIPAIS DISPONÍVEIS:
- **Identificação**: id, PRODUTO (código), NOME (nome do produto)
- **Localização**: UNE (código da loja), UNE_NOME (nome da loja)
- **Classificação**: NOMESEGMENTO, NOMECATEGORIA, NOMEFABRICANTE, TIPO, EMBALAGEM
- **Estoque**: ESTOQUE_UNE (atual), ESTOQUE_LV (linha verde), ESTOQUE_CD (centro distribuição)
- **Vendas**: VENDA_30DD (vendas últimos 30 dias), ULTIMA_VENDA_DATA_UNE
- **Preços**: PRECO_VENDA, PRECO_CUSTO
- **Status**: SITUACAO, PICKLIST_SITUACAO

MAPEAMENTO DE FILTROS (use exatamente esses nomes):
- Para filtrar por UNE: {"une": 2365} ou {"UNE": 2365}
- Para filtrar por fabricante: {"nomefabricante": "NOME_FABRICANTE"}
- Para filtrar por produto: {"codigo": "123456"} ou {"PRODUTO": "123456"}
- Para filtrar por segmento: {"nomesegmento": "TECIDOS"}

FERRAMENTAS DISPONÍVEIS:

1. **consultar_dados_flexivel** - USE PARA QUALQUER CONSULTA DE DADOS
   Parâmetros importantes:
   - filtros: {"une": 2365, "nomesegmento": "TECIDOS"}
   - agregacao: "sum", "avg", "count", "min", "max"
   - coluna_agregacao: "venda_30dd", "estoque_atual", "preco_venda"
   - agrupar_por: ["une"], ["nomefabricante"], ["nomesegmento"]
   - ordenar_por: "venda_30dd", "estoque_atual"
   - limite: número de resultados (padrão 20)

2. **consultar_dados_gerais** - Alternativa para consultas simples

3. **calcular_abastecimento_une** - Produtos que precisam reposição

4. **calcular_mc_produto** - Média Comum (MC) de produtos

5. **calcular_preco_final_une** - Preços com descontos aplicados

6. **sugerir_transferencias_automaticas** - Sugestões de transferência entre lojas

7. **validar_transferencia_produto** - Validar viabilidade de transferências

8. **encontrar_rupturas_criticas** - Produtos em ruptura crítica

EXEMPLOS DE USO:

Pergunta: "Olá, como você está?"
Resposta: "Olá! Estou muito bem, obrigado por perguntar! 😊 Como posso ajudá-lo hoje? Posso responder perguntas gerais ou ajudá-lo com análises de dados de BI da Caculinha."

Pergunta: "Qual é a capital do Brasil?"
Resposta: "A capital do Brasil é Brasília, localizada no Distrito Federal. Foi inaugurada em 21 de abril de 1960 durante o governo de Juscelino Kubitschek."

Pergunta: "Vendas totais do segmento TECIDOS na UNE 2365"
Usar: consultar_dados_flexivel(filtros={"une": 2365, "nomesegmento": "TECIDOS"}, agregacao="sum", coluna_agregacao="venda_30dd")

Pergunta: "Produtos do fabricante TNT"
Usar: consultar_dados_flexivel(filtros={"nomefabricante": "TNT"}, limite=20)

Pergunta: "Total de vendas da UNE 261"
Usar: consultar_dados_flexivel(filtros={"une": 261}, agregacao="sum", coluna_agregacao="venda_30dd")

Pergunta: "Top 10 mais vendidos"
Usar: consultar_dados_flexivel(ordenar_por="venda_30dd", ordem_desc=True, limite=10)

Pergunta: "Estoque por segmento"
Usar: consultar_dados_flexivel(agregacao="sum", coluna_agregacao="estoque_atual", agrupar_por=["nomesegmento"])

DIRETRIZES:
- Responda QUALQUER pergunta, não se limite apenas a BI
- Para perguntas gerais: seja útil, preciso e conversacional
- Para perguntas sobre dados: SEMPRE use as ferramentas, NUNCA invente dados
- Use os nomes de colunas EXATOS listados acima
- Se a coluna não existir, informe ao usuário
- Formate números: 1.234,56 (BR) ou use separadores de milhar
- Seja conciso mas informativo
- Use emojis: 📊 📈 ⚠️ ✅ 📦 💰 😊 👋
"""

    def _convert_tools_to_gemini_format(self, tools: List[BaseTool]) -> Dict[str, List[Dict[str, Any]]]:
        """Converts LangChain tools to Gemini API format."""
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

    def run(self, user_query: str, chat_history: Optional[List[Dict]] = None) -> Dict[str, Any]:
        """
        Executes the agent loop:
        1. Send query + tools to LLM.
        2. If LLM wants to call tool -> Execute tool -> Send result back to LLM.
        3. Repeat until LLM returns text.
        """
        logger.info(f"CaculinhaBIAgent (Modern): Processing query: {user_query}")

        messages = [{"role": "system", "content": self.system_prompt}]
        
        # Add chat history if available
        if chat_history:
            for msg in chat_history:
                role = msg.get("role", "user")
                content = msg.get("content", "")
                messages.append({"role": role, "content": content})

        # Add current user query
        messages.append({"role": "user", "content": user_query})

        max_turns = 5
        current_turn = 0

        while current_turn < max_turns:
            try:
                # Call LLM with tools
                # Note: self.llm is GeminiLLMAdapter
                response = self.llm.get_completion(messages, tools=self.gemini_tools)
                
                if "error" in response:
                    logger.error(f"LLM Error: {response['error']}")
                    return self._generate_error_response(response['error'])

                # Check for tool calls
                if "tool_calls" in response:
                    tool_calls = response["tool_calls"]
                    messages.append({
                        "role": "model",
                        "tool_calls": tool_calls
                    })

                    # Execute each tool
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
                                tool_result = tool_output
                            except Exception as e:
                                logger.error(f"Error executing {func_name}: {e}")
                                tool_result = {"error": str(e)}
                        else:
                            tool_result = {"error": f"Tool {func_name} not found"}

                        # Add tool result to messages (User role with function_response)
                        # The adapter expects specific structure for function responses
                        # Use safe_json_serialize to handle MapComposite and other non-serializable types
                        messages.append({
                            "role": "function", # Adapter will map this to user/function_response
                            "function_call": {"name": func_name}, # Metadata for adapter
                            "content": safe_json_serialize(tool_result)
                        })
                    
                    # Loop continues to send tool outputs back to LLM
                    current_turn += 1
                    continue
                
                # If no tool calls, it's a text response (Final Answer)
                content = response.get("content", "")
                
                # Check if it's a "Code Result" (tabular data) from the tool result
                # If the last message was a tool result, we might want to return that structure
                # But typically the LLM summarizes it.
                # We will return standard text response.
                
                return {
                    "type": "text",
                    "result": content
                }

            except Exception as e:
                logger.error(f"Exception in agent run loop: {e}", exc_info=True)
                return self._generate_error_response(str(e))

        return self._generate_error_response("Maximum conversation turns exceeded.")

    def _generate_error_response(self, error_msg: str) -> Dict[str, Any]:
        return {
            "type": "text",
            "result": f"Desculpe, encontrei um erro ao processar sua solicitação: {error_msg}"
        }
