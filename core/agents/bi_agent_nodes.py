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
    Classifica a intenção do utilizador para roteamento do fluxo.
    As intenções possíveis são:
    - 'python_analysis': Para perguntas complexas que exigem análise, agregação ou ranking (ex: 'top 5', 'mais vendido').
    - 'gerar_grafico': Para pedidos diretos de gráficos sem lógica complexa.
    - 'resposta_simples': Para consultas que podem ser respondidas com filtros simples.
    """
    user_query = state['messages'][-1]['content']
    logger.info(f"[NODE] classify_intent: Recebida query '{user_query}'")
    
    prompt = f"""
    Analise a consulta do utilizador e classifique a intenção principal para guiar o fluxo de análise de dados. Responda APENAS com um objeto JSON.

    **Intenções Possíveis:**

    1.  **`python_analysis`**: Use esta intenção para perguntas que exigem **análise, ranking, agregação ou comparações**.
        - Palavras-chave: "qual mais", "top", "maior", "menor", "evolução", "comparar", "análise de", "ranking de".
        - **Exemplos:**
            - "qual produto mais vende no segmento tecidos?" → `{{"intent": "python_analysis"}}`
            - "top 5 categorias por venda" → `{{"intent": "python_analysis"}}`
            - "mostre a evolução de vendas nos últimos 6 meses" → `{{"intent": "python_analysis"}}`
            - "compare as vendas dos segmentos A e B" → `{{"intent": "python_analysis"}}`

    2.  **`gerar_grafico`**: Use para pedidos **diretos e simples** de gráficos, onde a dimensão e a métrica são claras.
        - **Exemplos:**
            - "gere um gráfico de vendas por categoria" → `{{"intent": "gerar_grafico"}}`
            - "gráfico de produtos por segmento" → `{{"intent": "gerar_grafico"}}`

    3.  **`resposta_simples`**: Use para perguntas que podem ser respondidas com uma **filtragem direta**, sem agregação complexa.
        - **Exemplos:**
            - "liste os produtos da categoria 'AVIAMENTOS'" → `{{"intent": "resposta_simples"}}`
            - "qual o estoque do produto 12345?" → `{{"intent": "resposta_simples"}}`
            - "produtos com estoque zero" → `{{"intent": "resposta_simples"}}`

    **REGRAS:**
    - Priorize `python_analysis` se a pergunta contiver qualquer forma de ranking ou agregação.
    - Responda APENAS com o objeto JSON contendo a chave 'intent'.

    **Consulta do Usuário:**
    "{user_query}"

    **JSON de Saída:**
    """
    
    # Use json_mode=True para forçar a resposta em JSON
    response_dict = llm_adapter.get_completion(messages=[{"role": "user", "content": prompt}], json_mode=True)
    plan_str = response_dict.get("content", "{}")
    
    # Fallback para extrair JSON de blocos de markdown
    if "```json" in plan_str:
        match = re.search(r"""```json\n(.*?)```""", plan_str, re.DOTALL)
        if match:
            plan_str = match.group(1).strip()

    try:
        plan = json.loads(plan_str)
    except json.JSONDecodeError:
        logger.warning(f"Não foi possível decodificar o JSON da intenção: {plan_str}")
        # Fallback para a intenção mais poderosa em caso de erro de parsing
        plan = {"intent": "python_analysis", "entities": {}}

    intent = plan.get('intent', 'python_analysis')
    logger.info(f"[NODE] classify_intent: Intenção classificada como '{intent}'")
    
    # Assegura que o plan sempre tenha a chave 'intent'
    if 'intent' not in plan:
        plan['intent'] = intent
        
    return {"plan": plan, "intent": intent}




def generate_parquet_query(state: AgentState, llm_adapter: BaseLLMAdapter, parquet_adapter: ParquetAdapter) -> Dict[str, Any]:
    """
    Gera um dicionário de filtros para consulta Parquet a partir da pergunta do utilizador, usando o schema do arquivo Parquet e descrições de colunas.
    """
    user_query = state['messages'][-1]['content']
    logger.info(f"[NODE] generate_parquet_query: Gerando filtros para '{user_query}'")

    # Importar field_mapper
    from core.utils.field_mapper import get_field_mapper
    
    # Obter o schema do arquivo Parquet para dar contexto ao LLM
    try:
        schema = parquet_adapter.get_schema()
    except Exception as e:
        logger.error(f"Erro ao obter o schema do arquivo Parquet: {e}", exc_info=True)
        return {"parquet_filters": {}, "final_response": {"type": "error", "content": "Não foi possível aceder ao schema do arquivo Parquet para gerar a consulta."}}

    # Load the focused catalog (catalog_focused.json)
    import os
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    catalog_file_path = os.path.join(base_dir, "data", "catalog_focused.json")
    
    try:
        with open(catalog_file_path, 'r', encoding='utf-8') as f:
            catalog_data = json.load(f)
        
        # Find the entry for admatao.parquet
        admatao_catalog = next((entry for entry in catalog_data if entry.get("file_name") == "admatao.parquet"), None)
        
        if admatao_catalog and "column_descriptions" in admatao_catalog:
            column_descriptions = admatao_catalog["column_descriptions"]
            column_descriptions_str = json.dumps(column_descriptions, indent=2, ensure_ascii=False)
        else:
            column_descriptions_str = "Nenhuma descrição de coluna disponível."
            logger.warning("Descrições de coluna para admatao.parquet não encontradas no catálogo.")

    except FileNotFoundError:
        column_descriptions_str = "Erro: Arquivo de catálogo não encontrado."
        logger.error(f"Arquivo de catálogo não encontrado em {catalog_file_path}", exc_info=True)
    except Exception as e:
        column_descriptions_str = f"Erro ao carregar descrições de coluna: {e}"
        logger.error(f"Erro ao carregar descrições de coluna: {e}", exc_info=True)
    
    # Inicializar field_mapper
    field_mapper = get_field_mapper(catalog_file_path)
    
    # Gerar mapeamento de campos para o prompt
    field_mapping_guide = """
## Mapeamento de Campos (OBRIGATÓRIO)

Quando o usuário mencionar:
- "segmento" → use: NOMESEGMENTO
- "categoria" → use: NomeCategoria
- "grupo" → use: NOMEGRUPO
- "subgrupo" → use: NomeSUBGRUPO
- "código" ou "produto" → use: PRODUTO
- "nome" → use: NOME
- "estoque" → use: ESTOQUE_UNE
- "preço" → use: LIQUIDO_38
- "vendas" ou "vendas 30 dias" → use: VENDA_30DD
- "fabricante" → use: NomeFabricante

**REGRAS CRÍTICAS:**
1. NUNCA use "SEGMENTO", sempre use "NOMESEGMENTO"
2. NUNCA use "CATEGORIA", sempre use "NomeCategoria"
3. NUNCA use "CODIGO", sempre use "PRODUTO"
4. Para estoque zero: filtre por ESTOQUE_UNE = 0
5. Para campos de texto: use valores em MAIÚSCULAS
"""


    prompt = f"""
    Você é um especialista em traduzir perguntas de negócio em filtros de dados JSON. Sua tarefa é analisar a **NOVA Pergunta do Usuário** e convertê-la em um objeto JSON de filtros, usando o schema e as regras de mapeamento fornecidas.

    {field_mapping_guide}

    **Instruções Críticas:**
    1.  **FOCO TOTAL NA NOVA PERGUNTA:** Sua resposta DEVE ser uma tradução direta da **NOVA Pergunta do Usuário**.
    2.  **EXTRAÇÃO DE CÓDIGOS:** Se a pergunta contiver um número que se pareça com um código de produto (geralmente com 5 ou mais dígitos), você DEVE extraí-lo como um filtro para a coluna `PRODUTO`.
    3.  **NÃO COPIE OS EXEMPLOS:** Os exemplos abaixo são apenas um guia de estilo e formato. Não os use como base para a sua resposta.
    4.  **GERE APENAS JSON:** Sua saída final deve ser um único e válido objeto JSON, sem nenhum texto ou explicação adicional.
    5.  **CONSULTA VAZIA:** Se a pergunta não contiver nenhum filtro (ex: "liste todas as categorias"), retorne um objeto JSON vazio: `{{}}`.

    **Schema do Arquivo Parquet (para referência de colunas):**
    ```
    {schema}
    ```

    ---

    **Exemplos de Formato (Use apenas como guia):**

    - **Exemplo 1 (Filtro de Código de Produto):**
      - Pergunta: "qual o estoque do produto 369947?"
      - Filtros JSON: `{{"PRODUTO": 369947}}`

    - **Exemplo 2 (Filtro Composto):**
      - Pergunta: "quais são as categorias do segmento tecidos com estoque 0?"
      - Filtros JSON: `{{"NOMESEGMENTO": "TECIDO", "ESTOQUE_UNE": 0}}`
    
    - **Exemplo 3 (Filtro de Texto):**
      - Pergunta: "liste produtos da categoria aviamentos"
      - Filtros JSON: `{{"NomeCategoria": "AVIAMENTOS"}}`

    ---

    **NOVA Pergunta do Usuário (TRADUZIR ESTA):**
    "{user_query}"

    **Filtros JSON Resultantes:**
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

    # ✅ MAPEAMENTO DE COLUNAS: LLM usa nomes padronizados, Parquet tem nomes reais
    column_mapping = {
        'PRODUTO': 'codigo',
        'NOME': 'nome_produto',
        'NOMESEGMENTO': 'nomesegmento',
        'NomeCategoria': 'NOMECATEGORIA',
        'NOMEGRUPO': 'nomegrupo',
        'NomeSUBGRUPO': 'NOMESUBGRUPO',
        'VENDA_30DD': 'venda_30_d',
        'ESTOQUE_UNE': 'estoque_atual',
        'LIQUIDO_38': 'preco_38_percent',
        'UNE_NOME': 'une_nome',
        'NomeFabricante': 'NOMEFABRICANTE'
    }

    # Aplicar mapeamento nos filtros
    mapped_filters = {}
    for key, value in parquet_filters.items():
        mapped_key = column_mapping.get(key, key)
        mapped_filters[mapped_key] = value

    logger.info(f"Filtros originais: {parquet_filters}")
    logger.info(f"Filtros mapeados: {mapped_filters}")

    return {"parquet_filters": mapped_filters}


def execute_query(state: AgentState, parquet_adapter: ParquetAdapter) -> Dict[str, Any]:
    """
    Executa os filtros Parquet do estado.
    """
    user_query = state['messages'][-1]['content']
    parquet_filters = state.get('parquet_filters', {})

    logger.info(f"[NODE] execute_query: Executando com filtros {parquet_filters}")
    logger.info(f"📊 QUERY EXECUTION - User query: '{user_query}'")
    logger.info(f"📊 QUERY EXECUTION - Filters: {parquet_filters}")

    # A lógica de fallback para filtros vazios foi removida, pois era a causa do MemoryError.
    # Agora, a proteção no ParquetAdapter será acionada se os filtros estiverem vazios.
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
    Gera uma especificação JSON para Plotly ou uma resposta textual usando o CodeGenAgent.
    Este nó agora lida com dois cenários:
    1.  **Com `raw_data`**: Gera um gráfico a partir de dados pré-filtrados.
    2.  **Sem `raw_data` (fluxo `python_analysis`)**: Gera um script Python para fazer a análise completa (filtrar, agregar, etc.).
    """
    logger.info("Nó: generate_plotly_spec")
    raw_data = state.get("retrieved_data")
    user_query = state['messages'][-1]['content']
    plan = state.get("plan", {})
    intent = plan.get("intent")

    logger.info(f"🐍 Python CodeGen - User query: '{user_query}'")
    logger.info(f"🐍 Python CodeGen - Intent: {intent}")
    logger.info(f"🐍 Python CodeGen - Data available: {len(raw_data) if raw_data else 'No pre-loaded data'}")

    # Verifica se o estado de erro já foi definido por um nó anterior
    if raw_data and isinstance(raw_data, list) and raw_data and "error" in raw_data[0]:
        return {"final_response": {"type": "text", "content": raw_data[0]["error"]}}

    try:
        # Cenário 1: Análise complexa, sem dados pré-carregados.
        # O CodeGenAgent deve fazer o trabalho completo.
        if not raw_data:
            prompt_for_code_gen = f"""
            **TAREFA:** Você deve escrever um script Python para responder à pergunta do usuário.

            **INSTRUÇÕES OBRIGATÓRIAS:**
            1. **CARREGUE OS DADOS:** Inicie seu script com a linha: `df = load_data()`
            2. **RESPONDA À PERGUNTA:** Usando o dataframe `df`, escreva o código para responder à seguinte pergunta: "{user_query}"
            3. **SALVE O RESULTADO NA VARIÁVEL `result`:** A última linha do seu script DEVE ser a atribuição do resultado final à variável `result`. Esta é a única forma que o sistema tem para ver sua resposta. NÃO use `print()`.

            **Exemplo de Script:**
            ```python
            # Passo 1: Carregar dados
            df = load_data()

            # Passo 2: Responder à pergunta (ex: "ranking de vendas do segmento tecidos")
            tecidos_df = df[df['NOMESEGMENTO'].str.upper() == 'TECIDO']
            ranking = tecidos_df.groupby('NOME')['VENDA_30DD'].sum().sort_values(ascending=False).reset_index()

            # Passo 3: Salvar resultado
            result = ranking
            ```

            **Seu Script Python (Lembre-se, a última linha deve ser `result = ...`):**
            """
        # Cenário 2: Geração de gráfico a partir de dados pré-carregados.
        else:
            prompt_for_code_gen = f"""
            Com base na consulta do usuário e no DataFrame Pandas `df_raw_data` já disponível, gere um script Python para criar um gráfico com Plotly Express.
            O objeto da figura Plotly resultante deve ser armazenado em uma variável chamada `result`.
            Não inclua `fig.show()`.

            **Consulta do Usuário:** "{user_query}"
            **Dados Brutos (amostra):**
            ```json
            {pd.DataFrame(raw_data).head(3).to_json(orient="records", indent=2)}
            ```

            **Seu Script Python:**
            """

        # O CodeGenAgent espera um dicionário com a query e os dados brutos (se existirem)
        code_gen_input = {
            "query": prompt_for_code_gen,
            "raw_data": raw_data  # Passa os dados brutos ou None
        }
        
        logger.info(f"\n--- PROMPT PARA CODEGENAGENT ---\n{prompt_for_code_gen}\n---------------------------------")
        
        logger.info("🚀 Calling code_gen_agent.generate_and_execute_code...")
        code_gen_response = code_gen_agent.generate_and_execute_code(code_gen_input)
        logger.info(f"📋 CodeGenAgent response type: {code_gen_response.get('type')}")

        # Processa a resposta do CodeGenAgent
        if code_gen_response.get("type") == "chart":
            plotly_spec = json.loads(code_gen_response.get("output"))
            return {"plotly_spec": plotly_spec}
        elif code_gen_response.get("type") == "dataframe":
            # Se o resultado for um dataframe, converte para uma lista de dicionários para a resposta final
            df_result = code_gen_response.get("output")
            return {"retrieved_data": df_result.to_dict(orient='records')}
        elif code_gen_response.get("type") == "text":
            # Se for texto, encapsula na estrutura de resposta final
            return {"final_response": {"type": "text", "content": str(code_gen_response.get("output"))}}
        elif code_gen_response.get("type") == "error":
            return {"final_response": {"type": "text", "content": code_gen_response.get("output")}}
        else:
            return {"final_response": {"type": "text", "content": f"Resposta inesperada do agente de código: {code_gen_response.get('output')}"}}

    except Exception as e:
        logger.error(f"Erro ao gerar script Python com CodeGenAgent: {e}", exc_info=True)
        return {"final_response": {"type": "text", "content": f"Não consegui gerar a análise. Erro interno: {e}"}}


def format_final_response(state: AgentState) -> Dict[str, Any]:
    """
    Formata a resposta final para o utilizador.
    """
    user_query = state['messages'][-1]['content']
    logger.info(f"[NODE] format_final_response: Formatando resposta para '{user_query}'")

    # 📝 Construir resposta baseada no estado
    response = {}
    if state.get("clarification_needed"):
        response = {"type": "clarification", "content": state.get("clarification_options")}
        logger.info(f"💬 CLARIFICATION RESPONSE for query: '{user_query}'")
    elif state.get("plotly_spec"):
        response = {"type": "chart", "content": state.get("plotly_spec")}
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
