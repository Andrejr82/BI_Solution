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
from core.llm_adapter import CustomLangChainLLM



from core.connectivity.base import DatabaseAdapter
from core.config.settings import get_safe_settings
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

    from core.tools.data_tools import fetch_data_from_query
    from core.tools.une_tools import (
        calcular_abastecimento_une,
        calcular_mc_produto,
        calcular_preco_final_une
    )

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
    bi_tools = [
        fetch_data_from_query,
        generate_and_execute_python_code,
        calcular_abastecimento_une,
        calcular_mc_produto,
        calcular_preco_final_une
    ]

    settings = get_safe_settings()

    sql_gen_llm = CustomLangChainLLM(llm_adapter=llm_adapter)

    # Get parquet schema usando o arquivo correto: admmat.parquet
    parquet_schema = {}
    try:
        # Tenta carregar do arquivo admmat.parquet
        parquet_file = os.path.join(parquet_dir, "admmat.parquet")
        if not os.path.exists(parquet_file):
            # Fallback para ADMAT_REBUILT.parquet se admmat não existir
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
                """
Você é um assistente de BI especializado. Sua tarefa é converter a consulta em linguagem natural do usuário em um objeto JSON que representa os filtros para consultar o arquivo admmat.parquet.

**IMPORTANTE: Use SEMPRE os nomes de campos EXATOS conforme o mapeamento abaixo.**

{field_mapping}

Use o seguinte esquema de dados para gerar os filtros JSON:
{tables}

Retorne APENAS o objeto JSON. Não inclua explicações ou qualquer outro texto.
O JSON deve ter a seguinte estrutura:
{{
    "target_file": "admmat.parquet",
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
    "target_file": "admmat.parquet",
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
    "target_file": "admmat.parquet",
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
    "target_file": "admmat.parquet",
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
    "target_file": "admmat.parquet",
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
                        """Você é um assistente de BI. Sua tarefa é decidir qual ferramenta usar para responder à consulta do usuário. As ferramentas disponíveis são:\n\n"""
                        "**FERRAMENTAS GERAIS:**\n"
                        "- `fetch_data_from_query`: Para consultas que podem ser respondidas buscando dados específicos de produtos com filtros (ex: buscar preço de produto, listar produtos por categoria, categorias com estoque zero).\n"
                        "- `generate_and_execute_python_code`: Para análises complexas, cálculos, agregações ou geração de gráficos que exigem código Python.\n\n"
                        "**FERRAMENTAS UNE (Unidade de Negócio):**\n"
                        "- `calcular_abastecimento_une`: Para calcular produtos que precisam abastecimento em uma UNE específica. Use quando o usuário perguntar sobre 'abastecimento', 'reposição', 'produtos para abastecer', 'estoque baixo em UNE', ou mencionar uma UNE específica (ex: UNE 2586).\n"
                        "- `calcular_mc_produto`: Para consultar MC (Média Comum) de um produto específico em uma UNE. Use quando o usuário perguntar sobre 'MC', 'Média Comum', 'média de vendas', ou solicitar recomendações de estoque para um produto específico.\n"
                        "- `calcular_preco_final_une`: Para calcular preço final aplicando política UNE (varejo/atacado, ranking, forma de pagamento). Use quando o usuário perguntar sobre 'preço final', 'calcular preço', 'preço com desconto', 'preço atacado', 'preço varejo', ou mencionar formas de pagamento (vista, 30d, 90d, 120d).\n\n"
                        "**EXEMPLOS DE ROTEAMENTO:**\n"
                        "- 'Quais produtos precisam abastecimento na UNE 2586?' → `calcular_abastecimento_une`\n"
                        "- 'Qual a MC do produto 704559?' → `calcular_mc_produto`\n"
                        "- 'Calcule o preço de R$ 800 no ranking 0 a vista' → `calcular_preco_final_une`\n"
                        "- 'Mostre produtos do segmento TECIDOS' → `fetch_data_from_query`\n"
                        "- 'Faça um gráfico de vendas' → `generate_and_execute_python_code`\n\n"
                        "Retorne APENAS o nome da ferramenta.",
                    ),
                    ("user", "{query}"),
                ]
            )

            tool_selection_chain = tool_selection_prompt | tool_selection_llm
            
            # Decide qual ferramenta usar
            tool_decision_message = tool_selection_chain.invoke({"query": user_query})
            tool_decision = tool_decision_message.content.strip()
            logger.info(f"Decisão da ferramenta: {tool_decision}")

            if "fetch_data_from_query" in tool_decision:
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
                    target_file = parsed_json.get("target_file", "admmat.parquet")
                    filters = parsed_json.get("filters", [])
                    logger.info(f"JSON de filtros gerado: {parsed_json}")
                    
                    # Return AIMessage encapsulating ToolCall for fetch_data_from_query
                    return {"messages": state["messages"] + [AIMessage(content="", tool_calls=[ToolCall(id=str(uuid.uuid4()), name="fetch_data_from_query", args={"target_file": target_file, "filters": filters})])]}
                except json.JSONDecodeError as e:
                    logger.error(f"Erro ao decodificar JSON gerado: {e}. Conteúdo: {json_str}")
                    return {"messages": state["messages"] + [AIMessage(content=f"Desculpe, não consegui processar sua consulta devido a um erro na geração dos filtros: {e}")]}



            elif "generate_and_execute_python_code" in tool_decision:
                # Return AIMessage encapsulating ToolCall for CodeGenAgent
                return {"messages": state["messages"] + [AIMessage(content="", tool_calls=[ToolCall(id=str(uuid.uuid4()), name="generate_and_execute_python_code", args={"query": user_query})])]}

            elif "calcular_abastecimento_une" in tool_decision:
                # Extrair UNE ID e segmento da query usando LLM
                logger.info("Roteando para calcular_abastecimento_une")
                extract_prompt = ChatPromptTemplate.from_messages([
                    ("system",
                     "Extraia o ID da UNE e o segmento (opcional) da consulta do usuário.\n"
                     "Retorne APENAS um JSON no formato:\n"
                     '{{"une_id": <número>, "segmento": "<nome ou null>"}}\n'
                     "Exemplos:\n"
                     '- "produtos para abastecer na UNE 2586" → {{"une_id": 2586, "segmento": null}}\n'
                     '- "abastecimento de TECIDOS na UNE 2599" → {{"une_id": 2599, "segmento": "TECIDOS"}}\n'
                     '- "reposição na loja 2720 segmento PAPELARIA" → {{"une_id": 2720, "segmento": "PAPELARIA"}}'),
                    ("user", "{query}")
                ])
                extract_chain = extract_prompt | sql_gen_llm
                extract_result = extract_chain.invoke({"query": user_query})
                try:
                    json_match = re.search(r"```json\n(.*?)```", extract_result.content, re.DOTALL)
                    if json_match:
                        json_str = json_match.group(1).strip()
                    else:
                        json_str = extract_result.content.strip()
                    params = json.loads(json_str)
                    une_id = params.get("une_id")
                    segmento = params.get("segmento")

                    if une_id is None:
                        return {"messages": state["messages"] + [AIMessage(content="Por favor, especifique o ID da UNE na consulta (ex: UNE 2586).")]}

                    # Garantir que une_id seja int
                    une_id = int(une_id)

                    args = {"une_id": une_id}
                    if segmento:
                        args["segmento"] = segmento

                    return {"messages": state["messages"] + [AIMessage(content="", tool_calls=[ToolCall(id=str(uuid.uuid4()), name="calcular_abastecimento_une", args=args)])]}
                except (json.JSONDecodeError, KeyError) as e:
                    logger.error(f"Erro ao extrair parâmetros para calcular_abastecimento_une: {e}")
                    return {"messages": state["messages"] + [AIMessage(content="Não consegui identificar o ID da UNE. Por favor, especifique (ex: 'UNE 2586').")]}

            elif "calcular_mc_produto" in tool_decision:
                # Extrair produto_id e une_id da query
                logger.info("Roteando para calcular_mc_produto")
                extract_prompt = ChatPromptTemplate.from_messages([
                    ("system",
                     "Extraia o código do produto e o ID da UNE da consulta do usuário.\n"
                     "Retorne APENAS um JSON no formato:\n"
                     '{{"produto_id": <número>, "une_id": <número>}}\n'
                     "Exemplos:\n"
                     '- "MC do produto 704559 na UNE 2586" → {{"produto_id": 704559, "une_id": 2586}}\n'
                     '- "média comum do código 123456 loja 2599" → {{"produto_id": 123456, "une_id": 2599}}'),
                    ("user", "{query}")
                ])
                extract_chain = extract_prompt | sql_gen_llm
                extract_result = extract_chain.invoke({"query": user_query})
                try:
                    json_match = re.search(r"```json\n(.*?)```", extract_result.content, re.DOTALL)
                    if json_match:
                        json_str = json_match.group(1).strip()
                    else:
                        json_str = extract_result.content.strip()
                    params = json.loads(json_str)
                    produto_id = params.get("produto_id")
                    une_id = params.get("une_id")

                    if produto_id is None or une_id is None:
                        return {"messages": state["messages"] + [AIMessage(content="Por favor, especifique o código do produto e o ID da UNE (ex: 'produto 704559 na UNE 2586').")]}

                    # Garantir que sejam int
                    produto_id = int(produto_id)
                    une_id = int(une_id)

                    return {"messages": state["messages"] + [AIMessage(content="", tool_calls=[ToolCall(id=str(uuid.uuid4()), name="calcular_mc_produto", args={"produto_id": produto_id, "une_id": une_id})])]}
                except (json.JSONDecodeError, KeyError) as e:
                    logger.error(f"Erro ao extrair parâmetros para calcular_mc_produto: {e}")
                    return {"messages": state["messages"] + [AIMessage(content="Não consegui identificar o produto e UNE. Use o formato: 'MC do produto <código> na UNE <id>'.")]}

            elif "calcular_preco_final_une" in tool_decision:
                # Extrair valor_compra, ranking, forma_pagamento da query
                logger.info("Roteando para calcular_preco_final_une")
                extract_prompt = ChatPromptTemplate.from_messages([
                    ("system",
                     "Extraia o valor da compra, ranking e forma de pagamento da consulta do usuário.\n"
                     "Retorne APENAS um JSON no formato:\n"
                     '{{"valor_compra": <número>, "ranking": <0-4>, "forma_pagamento": "<vista|30d|90d|120d>"}}\n'
                     "Exemplos:\n"
                     '- "preço de R$ 800 ranking 0 a vista" → {{"valor_compra": 800.0, "ranking": 0, "forma_pagamento": "vista"}}\n'
                     '- "calcule 1500 reais no ranking 2 pagando em 30 dias" → {{"valor_compra": 1500.0, "ranking": 2, "forma_pagamento": "30d"}}'),
                    ("user", "{query}")
                ])
                extract_chain = extract_prompt | sql_gen_llm
                extract_result = extract_chain.invoke({"query": user_query})
                logger.info(f"LLM output for calcular_preco_final_une: {extract_result.content}")

                try:
                    json_match = re.search(r"```json\n(.*?)```", extract_result.content, re.DOTALL)
                    if json_match:
                        json_str = json_match.group(1).strip()
                    else:
                        json_str = extract_result.content.strip()
                    params = json.loads(json_str)
                    valor_compra = params.get("valor_compra")
                    ranking = params.get("ranking")
                    forma_pagamento = params.get("forma_pagamento")

                    if valor_compra is None or ranking is None or forma_pagamento is None:
                        return {"messages": state["messages"] + [AIMessage(content="Por favor, especifique: valor da compra, ranking (0-4) e forma de pagamento (vista, 30d, 90d, 120d).")]}

                    # Garantir tipos corretos
                    valor_compra = float(valor_compra)
                    ranking = int(ranking)

                    return {"messages": state["messages"] + [AIMessage(content="", tool_calls=[ToolCall(id=str(uuid.uuid4()), name="calcular_preco_final_une", args={"valor_compra": valor_compra, "ranking": ranking, "forma_pagamento": forma_pagamento})])]}
                except (json.JSONDecodeError, KeyError) as e:
                    logger.error(f"Erro ao extrair parâmetros para calcular_preco_final_une: {e}")
                    return {"messages": state["messages"] + [AIMessage(content="Não consegui identificar os parâmetros. Use: 'calcular preço de R$ <valor> ranking <0-4> forma de pagamento <vista/30d/90d/120d>'.")]}

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