"""
Módulo para core/agents/caculinha_bi_agent.py. Fornece as funções: create_caculinha_bi_agent, generate_and_execute_python_code, agent_runnable_logic.
"""

import logging
import re
import json # Added import
import uuid # Added import
from typing import List, Dict, Any, Tuple
import pandas as pd
import os
from langchain_core.tools import tool
from langchain_core.runnables import Runnable, RunnableLambda
from langchain_core.messages import HumanMessage, AIMessage, ToolMessage, ToolCall
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from core.llm_langchain_adapter import CustomLangChainLLM

from core.connectivity.base import DatabaseAdapter
from core.config.settings import settings # Import the settings instance
from core.utils.field_mapper import get_field_mapper # Import do mapeador de campos

logger = logging.getLogger(__name__)

def create_caculinha_bi_agent(
    parquet_dir: str,
    code_gen_agent: Any, # Use Any for now to avoid circular imports
    llm_adapter: Any # Add llm_adapter for tool selection
) -> Tuple[Runnable, List]:
    """
    Cria um agente de BI substituto e suas ferramentas, com o adaptador de banco de dados injetado.

    Args:
        db_adapter: Uma instância que segue a interface DatabaseAdapter.

    Returns:
        Uma tupla contendo o agente executável e a lista de suas ferramentas.
    """

    from core.tools.data_tools import query_product_data, list_table_columns

    # Inicializar o mapeador de campos
    catalog_path = os.path.join(os.path.dirname(os.path.dirname(parquet_dir)), "data", "catalog_focused.json")
    field_mapper = get_field_mapper(catalog_path)
    logger.info(f"FieldMapper inicializado com catálogo: {catalog_path}")

    @tool
    def generate_and_execute_python_code(query: str) -> Dict[str, Any]:
        """Gera e executa código Python para análises complexas e gráficos."""
        logger.info(f"Gerando e executando código Python para a consulta: {query}")
        return code_gen_agent.generate_and_execute_code(query)

    # A lista de ferramentas agora é definida dentro do escopo que tem acesso ao db_adapter
    bi_tools = [query_product_data, list_table_columns, generate_and_execute_python_code]

    # --- LLM para Geração de SQL ---
    sql_gen_llm = ChatOpenAI(
        model=settings.LLM_MODEL_NAME,
        openai_api_key=settings.OPENAI_API_KEY.get_secret_value(),
        temperature=0,
    )

    # Get parquet schema usando o arquivo correto: admatao.parquet
    parquet_schema = {}
    try:
        # Tenta carregar do arquivo admatao.parquet
        parquet_file = os.path.join(parquet_dir, "admatao.parquet")
        if not os.path.exists(parquet_file):
            # Fallback para ADMAT_REBUILT.parquet se admatao não existir
            parquet_file = os.path.join(parquet_dir, "ADMAT_REBUILT.parquet")
        
        df_sample = pd.read_parquet(parquet_file, columns=[])
        for col in df_sample.columns:
            parquet_schema[col] = str(df_sample[col].dtype)
        logger.info(f"Schema carregado de: {parquet_file}")
    except Exception as e:
        logger.error(f"Erro ao inferir esquema do parquet: {e}")
        parquet_schema = {"error": "Não foi possível inferir o esquema do parquet."}
    
    # Gerar string de schema com descrições do catálogo
    schema_lines = []
    for col, dtype in parquet_schema.items():
        description = field_mapper.get_field_description(col)
        schema_lines.append(f"- {col} ({dtype}): {description}")
    schema_str = "\n".join(schema_lines)

    # Gerar mapeamento de campos para o prompt
    field_mapping_str = """
## Mapeamento de Campos (Linguagem Natural → Campo Real)

Quando o usuário mencionar:
- "segmento" → use: NOMESEGMENTO
- "categoria" → use: NomeCategoria
- "grupo" → use: NOMEGRUPO
- "subgrupo" → use: NomeSUBGRUPO
- "código" ou "código do produto" → use: PRODUTO
- "nome" ou "nome do produto" → use: NOME
- "estoque" (sem especificar) → use: ESTOQUE_UNE
- "estoque CD" → use: ESTOQUE_CD
- "estoque linha verde" ou "estoque LV" → use: ESTOQUE_LV
- "preço" → use: LIQUIDO_38
- "vendas 30 dias" ou "vendas" → use: VENDA_30DD
- "fabricante" → use: NomeFabricante
- "embalagem" → use: EMBALAGEM
- "última venda" → use: ULTIMA_VENDA_DATA_UNE

## Regras Especiais para Estoque

1. **Campo Padrão**: ESTOQUE_UNE (estoque na unidade de negócio)
2. **Estoque Zero**: Use sempre `(ESTOQUE_UNE = 0 OR ESTOQUE_UNE IS NULL)`
3. **Campos de Texto**: Use sempre UPPER() e LIKE para buscas
   - Exemplo: `UPPER(NOMESEGMENTO) LIKE '%TECIDO%'`
4. **Campos Numéricos**: Use operadores diretos (=, >, <, etc.)
   - Exemplo: `PRODUTO = 369947`
"""

    sql_gen_prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                """Você é um assistente de BI especializado. Sua tarefa é converter a consulta em linguagem natural do usuário em um objeto JSON que representa os filtros para consultar o arquivo admatao.parquet.

**IMPORTANTE: Use SEMPRE os nomes de campos EXATOS conforme o mapeamento abaixo.**

{field_mapping}

Use o seguinte esquema de dados para gerar os filtros JSON:
{tables}

Retorne APENAS o objeto JSON. Não inclua explicações ou qualquer outro texto.
O JSON deve ter a seguinte estrutura:
{{
    "target_file": "admatao.parquet",
    "filters": [
        {{"column": "nome_da_coluna_real", "operator": "operador", "value": "valor"}}
    ]
}}

Operadores suportados:
- Para campos de TEXTO (string): use "contains" sempre
- Para campos NUMÉRICOS: use "==", "!=", ">", "<"

**Exemplos Corretos:**

Exemplo 1:
Consulta: Qual é o preço do produto 369947?
JSON:
```json
{{
    "target_file": "admatao.parquet",
    "filters": [
        {{"column": "PRODUTO", "operator": "==", "value": 369947}}
    ]
}}
```

Exemplo 2:
Consulta: Quais são as categorias do segmento tecidos com estoque 0?
JSON:
```json
{{
    "target_file": "admatao.parquet",
    "filters": [
        {{"column": "NOMESEGMENTO", "operator": "contains", "value": "TECIDO"}},
        {{"column": "ESTOQUE_UNE", "operator": "==", "value": 0}}
    ]
}}
```

Exemplo 3:
Consulta: Liste produtos da categoria Aviamentos com vendas acima de 100.
JSON:
```json
{{
    "target_file": "admatao.parquet",
    "filters": [
        {{"column": "NomeCategoria", "operator": "contains", "value": "Aviamentos"}},
        {{"column": "VENDA_30DD", "operator": ">", "value": 100}}
    ]
}}
```

Exemplo 4:
Consulta: Mostre produtos do fabricante XYZ
JSON:
```json
{{
    "target_file": "admatao.parquet",
    "filters": [
        {{"column": "NomeFabricante", "operator": "contains", "value": "XYZ"}}
    ]
}}
```

**ATENÇÃO**: 
- NUNCA use "SEGMENTO", use "NOMESEGMENTO"
- NUNCA use "CATEGORIA", use "NomeCategoria"
- NUNCA use "CODIGO", use "PRODUTO"
- NUNCA use "EST_UNE", use "ESTOQUE_UNE"
"""
            ),
            ("user", "{query}")
        ]
    )

    sql_generator_chain = sql_gen_prompt | sql_gen_llm

    def agent_runnable_logic(state: Dict[str, Any]) -> Dict[str, Any]:
        last_message = state["messages"][-1]

        if isinstance(last_message, HumanMessage):
            user_query = last_message.content
            logger.info(f"Agente de BI recebeu a consulta: {user_query}")

            # LLM para decisão de ferramenta
            tool_selection_llm = CustomLangChainLLM(llm_adapter=llm_adapter)

            tool_selection_prompt = ChatPromptTemplate.from_messages(
                [
                    (
                        "system",
                        "Você é um assistente de BI. Sua tarefa é decidir qual ferramenta usar para responder à consulta do usuário. As ferramentas disponíveis são:\n" 
                        "- `query_product_data`: Para consultas que podem ser respondidas buscando dados específicos de produtos com filtros (ex: buscar preço de produto, listar produtos por categoria, categorias com estoque zero).\n" 
                        "- `list_table_columns`: Para listar todas as colunas de uma tabela (arquivo Parquet) específica.\n" 
                        "- `generate_and_execute_python_code`: Para análises complexas, cálculos, agregações ou geração de gráficos que exigem código Python.\n\n" 
                        "Retorne APENAS o nome da ferramenta: `query_product_data`, `list_table_columns` ou `generate_and_execute_python_code`.",
                    ),
                    ("user", "{query}"),
                ]
            )

            tool_selection_chain = tool_selection_prompt | tool_selection_llm
            
            # Decide qual ferramenta usar
            tool_decision_message = tool_selection_chain.invoke({"query": user_query})
            tool_decision = tool_decision_message.content.strip()
            logger.info(f"Decisão da ferramenta: {tool_decision}")

            if "query_product_data" in tool_decision:
                # Gerar JSON de filtros e retornar ToolCall
                generated_json_message = sql_generator_chain.invoke({
                    "query": user_query, 
                    "tables": schema_str,
                    "field_mapping": field_mapping_str
                })
                generated_json_content = generated_json_message.content.strip()
                
                json_match = re.search(r"```json\n(.*?)```", generated_json_content, re.DOTALL)
                if json_match:
                    json_str = json_match.group(1).strip()
                else:
                    json_str = generated_json_content
                
                try:
                    parsed_json = json.loads(json_str)
                    target_file = parsed_json.get("target_file", "admatao.parquet")
                    filters = parsed_json.get("filters", [])
                    logger.info(f"JSON de filtros gerado: {parsed_json}")
                    
                    # Return AIMessage encapsulating ToolCall for query_product_data
                    return {"messages": state["messages"] + [AIMessage(content="", tool_calls=[ToolCall(id=str(uuid.uuid4()), name="query_product_data", args={"target_file": target_file, "filters": filters})])]}
                except json.JSONDecodeError as e:
                    logger.error(f"Erro ao decodificar JSON gerado: {e}. Conteúdo: {json_str}")
                    return {"messages": state["messages"] + [AIMessage(content=f"Desculpe, não consegui processar sua consulta devido a um erro na geração dos filtros: {e}")]}

            elif "list_table_columns" in tool_decision:
                table_name = "admatao" # Atualizado para usar admatao
                logger.info(f"Listando colunas para a tabela: {table_name}")
                # Return AIMessage encapsulating ToolCall for list_table_columns
                return {"messages": state["messages"] + [AIMessage(content="", tool_calls=[ToolCall(id=str(uuid.uuid4()), name="list_table_columns", args={"table_name": table_name})])]}

            elif "generate_and_execute_python_code" in tool_decision:
                # Return AIMessage encapsulating ToolCall for CodeGenAgent
                return {"messages": state["messages"] + [AIMessage(content="", tool_calls=[ToolCall(id=str(uuid.uuid4()), name="generate_and_execute_python_code", args={"query": user_query})])]}
            else:
                return {"messages": [AIMessage(content="Desculpe, não consegui determinar a ferramenta apropriada para sua consulta.")]}

        elif isinstance(last_message, ToolMessage):
            # This path is taken after a tool has been executed by the ToolNode.
            # The agent needs to process the tool's output and generate an AIMessage.
            # The AIMessage generation is now handled by process_bi_tool_output_func in graph_builder.py
            return state
        else:
            # Handle other unexpected message types
            formatted_output = f"Erro: Tipo de mensagem inesperado no estado: {type(last_message)}"
            logger.error(formatted_output)
            return {"messages": state["messages"] + [AIMessage(content=formatted_output)]}

    # O runnable é a própria lógica do agente
    agent_runnable = RunnableLambda(agent_runnable_logic)

    return agent_runnable, bi_tools
