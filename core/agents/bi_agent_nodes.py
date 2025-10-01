"""
Nós (estados) para o StateGraph da arquitetura avançada do Agent_BI.
Cada função representa um passo no fluxo de processamento da consulta.
"""
import logging
import json
import re
from typing import Dict, Any
import pandas as pd
import numpy as np

# Importações corrigidas baseadas na estrutura completa do projeto
from core.agent_state import AgentState
from core.llm_base import BaseLLMAdapter
from core.agents.code_gen_agent import CodeGenAgent
from core.tools.data_tools import fetch_data_from_query
from core.connectivity.parquet_adapter import ParquetAdapter


from core.utils.json_utils import _clean_json_values # Import the cleaning function


logger = logging.getLogger(__name__)

def classify_intent(state: AgentState, llm_adapter: BaseLLMAdapter) -> Dict[str, Any]:
    """
    Classifica a intenção do utilizador usando um LLM e extrai entidades.
    """
    logger.info("Nó: classify_intent")
    user_query = state['messages'][-1].content
    
    prompt = f"""
    Analise a consulta do utilizador e classifique a intenção principal.
    Responda APENAS com um objeto JSON válido contendo as chaves 'intent' e 'entities'.
    Intenções possíveis: 'gerar_grafico', 'consulta_sql_complexa', 'resposta_simples'.

<<<<<<< HEAD
    **ATENÇÃO ESPECIAL PARA ANÁLISES VISUAIS:**
=======
    **ATENÇÃO ESPECIAL PARA ANÁLISES TEMPORAIS:**
>>>>>>> 946e2ce9d874562f3c9e0f0d54e9c41c50cb3399
    Se a consulta mencionar:
    - "evolução", "tendência", "ao longo do tempo", "histórico"
    - "últimos X meses", "mensais", "meses"
    - "crescimento", "declínio", "variação temporal"
<<<<<<< HEAD
    - "TOP", "melhores", "maiores", "principais", "ranking"
    - "mais vendidos", "menos vendidos", "top 10", "top 5"
    - "gráfico", "gráficos", "visualização", "mostre"

    SEMPRE classifique como 'gerar_grafico' e inclua nas entities:
    - Para temporal: "temporal": true, "periodo": "mensal", "tipo_analise": "evolucao"
    - Para ranking: "ranking": true, "limite": N, "metrica": "vendas"
=======

    SEMPRE classifique como 'gerar_grafico' e inclua nas entities:
    - "temporal": true
    - "periodo": "mensal" ou "multiplos_meses"
    - "tipo_analise": "evolucao" ou "tendencia"
>>>>>>> 946e2ce9d874562f3c9e0f0d54e9c41c50cb3399

    **Exemplos:**
    - "Gere um gráfico de vendas do produto 369947" → intent: "gerar_grafico", entities: {{"produto": 369947, "metrica": "vendas"}}
    - "Mostre a evolução de vendas nos últimos 6 meses" → intent: "gerar_grafico", entities: {{"temporal": true, "periodo": "6_meses", "metrica": "vendas", "tipo_analise": "evolucao"}}
    - "Tendência de vendas do produto 369947" → intent: "gerar_grafico", entities: {{"produto": 369947, "temporal": true, "metrica": "vendas", "tipo_analise": "tendencia"}}

    Consulta: "{user_query}"
    """
    
    # Use json_mode=True para forçar a resposta em JSON
    response_dict = llm_adapter.get_completion(messages=[{"role": "user", "content": prompt}], json_mode=True)
    plan_str = response_dict.get("content", "{}")
    
    # Fallback para extrair JSON de blocos de markdown
    if "```json" in plan_str:
        match = re.search(r"""```json
(.*?)```""", plan_str, re.DOTALL)
        if match:
            plan_str = match.group(1).strip()

    try:
        plan = json.loads(plan_str)
    except json.JSONDecodeError:
        logger.warning(f"Não foi possível decodificar o JSON da intenção: {plan_str}")
        plan = {"intent": "resposta_simples", "entities": {}}

    logger.info(f"Intenção classificada: {plan.get('intent')}")
    return {"plan": plan, "intent": plan.get('intent')}


def clarify_requirements(state: AgentState) -> Dict[str, Any]:
    """
    Verifica se informações para um gráfico estão em falta.
    """
    logger.info("Nó: clarify_requirements")
    plan = state.get("plan", {})
    entities = plan.get("entities", {})

    if state.get("intent") == "gerar_grafico":
        missing_info = []

        # ✅ Para análises temporais, menos clarificações são necessárias
        if entities.get("temporal"):
            logger.info("🕰️ TEMPORAL ANALYSIS - Skipping clarification for time-based charts")
            return {"clarification_needed": False}

        # Clarificações tradicionais apenas para gráficos não-temporais
        if not entities.get("dimension") and not entities.get("temporal"):
            missing_info.append("dimensão")
        if not entities.get("metric") and not entities.get("metrica"):
            missing_info.append("métrica")

        if missing_info:
            options = {
                "message": f"Para gerar o gráfico, preciso que especifique: {', '.join(missing_info)}.",
                "choices": {
                    "dimensions": ["Por Categoria", "Por Segmento", "Por Produto"],
                    "chart_types": ["Barras", "Linhas", "Evolução Temporal"]
                }
            }
            return {"clarification_needed": True, "clarification_options": options}

    return {"clarification_needed": False}

def generate_parquet_query(state: AgentState, llm_adapter: BaseLLMAdapter, parquet_adapter: ParquetAdapter) -> Dict[str, Any]:
    """
    Gera um dicionário de filtros para consulta Parquet a partir da pergunta do utilizador, usando o schema do arquivo Parquet e descrições de colunas.
    """
    logger.info("Nó: generate_parquet_query")
    user_query = state['messages'][-1].content

    # Obter o schema do arquivo Parquet para dar contexto ao LLM
    try:
        schema = parquet_adapter.get_schema()
    except Exception as e:
        logger.error(f"Erro ao obter o schema do arquivo Parquet: {e}", exc_info=True)
        return {"parquet_filters": {}, "final_response": {"type": "error", "content": "Não foi possível aceder ao schema do arquivo Parquet para gerar a consulta."}}

    # Load the cleaned catalog
<<<<<<< HEAD
    catalog_file_path = "data/catalog_cleaned.json"
=======
    catalog_file_path = "C:\\Users\\André\\Documents\\Agent_BI\\data\\catalog_cleaned.json"
>>>>>>> 946e2ce9d874562f3c9e0f0d54e9c41c50cb3399
    try:
        with open(catalog_file_path, 'r', encoding='utf-8') as f:
            catalog_data = json.load(f)
        
<<<<<<< HEAD
        # Find the entry for admmat.parquet
        admatao_catalog = next((entry for entry in catalog_data if entry.get("file_name") == "admmat.parquet"), None)
=======
        # Find the entry for admatao.parquet
        admatao_catalog = next((entry for entry in catalog_data if entry.get("file_name") == "admatao.parquet"), None)
>>>>>>> 946e2ce9d874562f3c9e0f0d54e9c41c50cb3399
        
        if admatao_catalog and "column_descriptions" in admatao_catalog:
            column_descriptions = admatao_catalog["column_descriptions"]
            column_descriptions_str = json.dumps(column_descriptions, indent=2, ensure_ascii=False)
        else:
            column_descriptions_str = "Nenhuma descrição de coluna disponível."
<<<<<<< HEAD
            logger.warning("Descrições de coluna para admmat.parquet não encontradas no catálogo.")
=======
            logger.warning("Descrições de coluna para admatao.parquet não encontradas no catálogo.")
>>>>>>> 946e2ce9d874562f3c9e0f0d54e9c41c50cb3399

    except FileNotFoundError:
        column_descriptions_str = "Erro: Arquivo de catálogo não encontrado."
        logger.error(f"Arquivo de catálogo não encontrado em {catalog_file_path}", exc_info=True)
    except Exception as e:
        column_descriptions_str = f"Erro ao carregar descrições de coluna: {e}"
        logger.error(f"Erro ao carregar descrições de coluna: {e}", exc_info=True)


    prompt = f"""
    Você é um especialista em análise de dados com Pandas. Sua tarefa é gerar um objeto JSON representando filtros para um DataFrame Pandas, com base na pergunta do usuário, no schema do arquivo Parquet e nas descrições das colunas fornecidas.

    **Instruções:**
    1.  Analise a pergunta do usuário para entender a informação solicitada e os filtros necessários.
    2.  Use o schema do arquivo Parquet e as descrições das colunas para identificar as colunas corretas.
    3.  Gere APENAS um objeto JSON válido. Não inclua explicações, comentários ou qualquer outro texto.
    4.  O JSON deve ter o formato: `{{"coluna": "valor_exato"}}` para filtros de igualdade, ou `{{"coluna": ">valor"}}`, `{{"coluna": "<valor"}}`, etc., para comparações.
    5.  Use os nomes de colunas EXATOS fornecidos no schema e nas descrições.
    6.  **Mesmo que a pergunta seja para gerar um gráfico, se ela contiver condições de filtragem (ex: "produto X", "mês Y", "categoria Z"), você DEVE traduzir essas condições em filtros JSON.**
    7.  Se não for possível gerar filtros a partir da pergunta, retorne um objeto JSON vazio: `{{}}`.

    **Schema do Arquivo Parquet:**
    ```
    {schema}
    ```

    **Descrições das Colunas:**
    ```json
    {column_descriptions_str}
    ```

    **Pergunta do Usuário:**
    "{user_query}"

    **Exemplo:**
    Pergunta: "gere um gráfico de vendas do produto 123"
    Filtros JSON: `{{"PRODUTO": 123}}`

    **Filtros JSON:**
    """

    response_dict = llm_adapter.get_completion(messages=[{"role": "user", "content": prompt}], json_mode=True)
    filters_str = response_dict.get("content", "{}").strip()

    # Fallback para extrair JSON de blocos de markdown
    if "```json" in filters_str:
        match = re.search(r"""```json\n(.*?)```""", filters_str, re.DOTALL)
        if match:
            filters_str = match.group(1).strip()

    try:
        parquet_filters = json.loads(filters_str)
    except json.JSONDecodeError:
        logger.warning(f"Não foi possível decodificar o JSON dos filtros Parquet: {filters_str}")
        parquet_filters = {}
    
    logger.info(f"Filtros Parquet gerados: {parquet_filters}")

    return {"parquet_filters": parquet_filters}


def execute_query(state: AgentState, parquet_adapter: ParquetAdapter) -> Dict[str, Any]:
    """
    Executa os filtros Parquet do estado.
    """
    logger.info("Nó: execute_query")
    parquet_filters = state.get("parquet_filters", {})
    user_query = state['messages'][-1].content

    logger.info(f"📊 QUERY EXECUTION - User query: '{user_query}'")
    logger.info(f"📊 QUERY EXECUTION - Filters: {parquet_filters}")

    # Se não há filtros específicos, executamos uma consulta que retorna uma amostra dos dados
    # Isso é necessário para gráficos que precisam de dados gerais (ex: vendas por categoria)
    if not parquet_filters:
        logger.info("Nenhum filtro específico. Obtendo amostra de dados para análise.")
        # Para gráficos gerais, precisamos de dados. Usamos filtros vazios que retornarão uma amostra
        retrieved_data = fetch_data_from_query.invoke({"query_filters": {}, "parquet_adapter": parquet_adapter})
    else:
        retrieved_data = fetch_data_from_query.invoke({"query_filters": parquet_filters, "parquet_adapter": parquet_adapter})

    # ✅ LOG DETALHADO DOS RESULTADOS
    if isinstance(retrieved_data, list):
        if retrieved_data and "error" in retrieved_data[0]:
            logger.error(f"❌ QUERY ERROR: {retrieved_data[0]}")
        else:
            logger.info(f"✅ QUERY SUCCESS: Retrieved {len(retrieved_data)} rows")
            if retrieved_data:
                logger.info(f"📋 SAMPLE DATA COLUMNS: {list(retrieved_data[0].keys()) if retrieved_data else 'No data'}")
    else:
        logger.warning(f"⚠️ UNEXPECTED DATA TYPE: {type(retrieved_data)}")

    return {"retrieved_data": retrieved_data}

def generate_plotly_spec(state: AgentState, llm_adapter: BaseLLMAdapter, code_gen_agent: CodeGenAgent) -> Dict[str, Any]:
    """
    Gera uma especificação JSON para Plotly usando o CodeGenAgent.
    """
    logger.info("Nó: generate_plotly_spec")
    raw_data = state.get("retrieved_data")
    user_query = state['messages'][-1].content
    plan = state.get("plan", {})
    intent = plan.get("intent")
    entities = plan.get("entities", {})

    logger.info(f"📈 CHART GENERATION - User query: '{user_query}'")
    logger.info(f"📈 CHART GENERATION - Intent: {intent}")
    logger.info(f"📈 CHART GENERATION - Data available: {len(raw_data) if raw_data else 0} rows")

    # 🔍 Detectar se é uma análise temporal
    temporal_keywords = ['evolução', 'tendência', 'ao longo', 'mensais', 'últimos meses', 'histórico', 'temporal', 'meses']
    is_temporal = any(keyword in user_query.lower() for keyword in temporal_keywords)
    logger.info(f"📈 TEMPORAL ANALYSIS DETECTED: {is_temporal}")

    if not raw_data or (isinstance(raw_data, list) and raw_data and "error" in raw_data[0]):
        return {"final_response": {"type": "text", "content": "Não foi possível obter dados para gerar o gráfico."}}

    try:
        if not raw_data:
            return {"final_response": {"type": "text", "content": "A consulta não retornou dados para visualização."}}

        # Constrói um prompt para o CodeGenAgent para gerar código Python que produz um gráfico Plotly
        # Inclui os dados brutos como contexto para o CodeGenAgent
        # O CodeGenAgent já tem acesso ao parquet_dir e outras libs necessárias
        prompt_for_code_gen = f"""
        Com base na seguinte consulta do usuário e nos dados brutos fornecidos, gere um script Python
        que utilize a biblioteca Plotly Express para criar um gráfico.
        O script deve armazenar o objeto da figura Plotly resultante em uma variável chamada `result`.
        Não inclua `fig.show()` ou `fig.write_json()`.

        **Consulta do Usuário:** "{user_query}"
        **Intenção Detectada:** "{intent}"
        **Análise Temporal:** {'SIM - Use dados mensais mes_01 a mes_12' if is_temporal else 'NÃO - Use dados agregados'}
        **Entidades Extraídas:** {json.dumps(entities, ensure_ascii=False)}
        **Dados Brutos (primeiras 5 linhas para referência):**
        ```json
        {pd.DataFrame(raw_data).head(5).to_json(orient="records", indent=2)}
        ```
        **Dados Brutos Completos (para uso no script):**
        A variável `df_raw_data` já contém um Pandas DataFrame com todos os dados brutos.
        Você deve usar `df_raw_data` como sua fonte de dados para o gráfico.

        **Exemplo de script Python para um gráfico de barras:**
        ```python
        import pandas as pd
        import plotly.express as px

        # df_raw_data já está disponível aqui como um Pandas DataFrame
        # Exemplo:
        # df_raw_data['coluna_numerica'] = pd.to_numeric(df_raw_data['coluna_numerica'], errors='coerce').fillna(0)
        
        # Crie seu gráfico Plotly Express aqui
        fig = px.bar(df_raw_data, x="coluna_dimensao", y="coluna_metrica", title="Título do Gráfico")
        result = fig
        ```
        Gere APENAS o script Python.
        """
        
        # O CodeGenAgent espera um dicionário com a query e os dados brutos
        # para que ele possa criar o DataFrame `df_raw_data` no escopo de execução.
        code_gen_input = {
            "query": prompt_for_code_gen,
            "raw_data": raw_data # Passa os dados brutos completos
        }
        
        # Chama o CodeGenAgent para gerar e executar o código
        # O CodeGenAgent retornará um dicionário com 'type' e 'output'
        logger.info("🚀 Calling code_gen_agent.generate_and_execute_code...")
        code_gen_response = code_gen_agent.generate_and_execute_code(code_gen_input)
        logger.info(f"📋 CodeGenAgent response type: {code_gen_response.get('type')}")
        logger.info(f"📋 CodeGenAgent response output length: {len(str(code_gen_response.get('output', '')))}")

        if code_gen_response.get("type") == "chart":
<<<<<<< HEAD
            # Se o CodeGenAgent retornou um gráfico, usa diretamente o objeto
            plotly_fig = code_gen_response.get("output")
            # Se for string JSON, parse; se for objeto, usa direto
            if isinstance(plotly_fig, str):
                plotly_spec = json.loads(plotly_fig)
            else:
                plotly_spec = plotly_fig
=======
            # Se o CodeGenAgent retornou um gráfico, extrai o JSON do Plotly
            plotly_spec = json.loads(code_gen_response.get("output"))
>>>>>>> 946e2ce9d874562f3c9e0f0d54e9c41c50cb3399
            return {"plotly_spec": plotly_spec}
        elif code_gen_response.get("type") == "error":
            return {"final_response": {"type": "text", "content": code_gen_response.get("output")}}
        else:
            # Se o CodeGenAgent retornou texto ou dataframe, ou algo inesperado
            return {"final_response": {"type": "text", "content": f"O agente gerou uma resposta inesperada ao tentar criar o gráfico: {code_gen_response.get('output')}"}}

    except Exception as e:
        logger.error(f"Erro ao gerar especificação Plotly via CodeGenAgent: {e}", exc_info=True)
        return {"final_response": {"type": "text", "content": f"Não consegui gerar o gráfico. Erro interno: {e}"}}


def format_final_response(state: AgentState) -> Dict[str, Any]:
    """
    Formata a resposta final para o utilizador.
    """
    logger.info("Nó: format_final_response")
    user_query = state['messages'][-1].content

    # 📝 Construir resposta baseada no estado
    response = {}
    if state.get("clarification_needed"):
        response = {"type": "clarification", "content": state.get("clarification_options")}
        logger.info(f"💬 CLARIFICATION RESPONSE for query: '{user_query}'")
    elif state.get("plotly_spec"):
<<<<<<< HEAD
        plotly_obj = state.get("plotly_spec")
        # Se for objeto Plotly, converter para JSON para serialização
        if hasattr(plotly_obj, 'to_dict'):
            chart_content = plotly_obj.to_dict()
        else:
            chart_content = plotly_obj
        response = {"type": "chart", "content": chart_content}
=======
        response = {"type": "chart", "content": state.get("plotly_spec")}
>>>>>>> 946e2ce9d874562f3c9e0f0d54e9c41c50cb3399
        logger.info(f"📈 CHART RESPONSE for query: '{user_query}'")
    elif state.get("retrieved_data"):
        response = {"type": "data", "content": _clean_json_values(state.get("retrieved_data"))}
        logger.info(f"📊 DATA RESPONSE for query: '{user_query}' - {len(state.get('retrieved_data', []))} rows")
    else:
        response = {"type": "text", "content": "Não consegui processar a sua solicitação."}
        logger.warning(f"❓ DEFAULT RESPONSE for query: '{user_query}' - No specific response type matched")

    # ✅ GARANTIR que a pergunta do usuário seja preservada no histórico
    final_messages = state['messages'] + [{"role": "assistant", "content": response}]

    # 🔍 LOG DO RESULTADO FINAL
    logger.info(f"✅ FINAL RESPONSE - Type: {response.get('type')}, User Query: '{user_query}'")
    logger.info(f"📋 MESSAGE HISTORY - Total messages: {len(final_messages)}")

    return {"messages": final_messages, "final_response": response}
