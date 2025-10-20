"""
Módulo para core/agents/code_gen_agent.py. Define a classe principal 'CodeGenAgent'. Fornece as funções: generate_and_execute_code, worker.
"""

# core/agents/code_gen_agent.py
import logging
import os
import json
import re
import pandas as pd
import dask.dataframe as dd  # Dask para lazy loading
import time
import plotly.express as px
from typing import List, Dict, Any # Import necessary types
import threading
from queue import Queue
import pickle
import faiss
import numpy as np
from sentence_transformers import SentenceTransformer
import io
import sys
import plotly.io as pio
import uuid
from core.utils.json_utils import _clean_json_values # Import the cleaning function

from core.llm_base import BaseLLMAdapter
from core.learning.pattern_matcher import PatternMatcher
from core.validation.code_validator import CodeValidator
from core.learning.dynamic_prompt import DynamicPrompt

class CodeGenAgent:
    """
    Agente especializado em gerar e executar código Python para análise de dados.
    """
    def __init__(self, llm_adapter: BaseLLMAdapter, data_adapter: any = None):
        """
        Inicializa o agente com o adaptador LLM e opcionalmente o adaptador de dados.

        Args:
            llm_adapter: Adaptador LLM para geração de código
            data_adapter: (Opcional) Adaptador de dados para injeção de load_data()
                         Se None, load_data() usará path padrão do Parquet
        """
        self.logger = logging.getLogger(__name__)
        self.llm = llm_adapter
        self.data_adapter = data_adapter  # Pode ser None (fallback para path padrão)
        self.code_cache = {}

        # Inicializar dicionário de descrições de colunas ANTES de verificar cache
        self.column_descriptions = {
            "PRODUTO": "Código único do produto",
            "NOME": "Nome/descrição do produto",
            "NOMESEGMENTO": "Segmento do produto (TECIDOS, PAPELARIA, etc.)",
            "NOMECATEGORIA": "Categoria do produto",
            "NOMEGRUPO": "Grupo do produto",
            "NOMESUBGRUPO": "Subgrupo do produto",
            "NOMEFABRICANTE": "Fabricante do produto",
            "VENDA_30DD": "Total de vendas nos últimos 30 dias",
            "ESTOQUE_UNE": "Quantidade em estoque",
            "LIQUIDO_38": "Preço de venda",
            "UNE": "Nome da loja/unidade (ex: SCR, MAD, 261, ALC, NIL, etc.)",
            "UNE_ID": "ID numérico da loja (ex: 1=SCR, 2720=MAD, 1685=261)",
            "TIPO": "Tipo de produto",
            "EMBALAGEM": "Embalagem do produto",
            "EAN": "Código de barras",
            # 📊 COLUNAS TEMPORAIS - Vendas mensais (mes_01 = mês mais recente)
            "mes_01": "Vendas do mês mais recente (mês 1)",
            "mes_02": "Vendas de 2 meses atrás",
            "mes_03": "Vendas de 3 meses atrás",
            "mes_04": "Vendas de 4 meses atrás",
            "mes_05": "Vendas de 5 meses atrás",
            "mes_06": "Vendas de 6 meses atrás",
            "mes_07": "Vendas de 7 meses atrás",
            "mes_08": "Vendas de 8 meses atrás",
            "mes_09": "Vendas de 9 meses atrás",
            "mes_10": "Vendas de 10 meses atrás",
            "mes_11": "Vendas de 11 meses atrás",
            "mes_12": "Vendas de 12 meses atrás (mês mais antigo)"
        }

        # Inicializar pattern_matcher and code_validator
        from collections import defaultdict
        try:
            self.pattern_matcher = PatternMatcher()
            self.logger.info("✅ PatternMatcher inicializado (Few-Shot Learning ativo)")
        except Exception as e:
            self.logger.warning(f"⚠️ PatternMatcher não disponível: {e}")
            self.pattern_matcher = None

        self.code_validator = CodeValidator()
        self.error_counts = defaultdict(int)
        self.logs_dir = os.path.join(os.getcwd(), "data", "learning")
        os.makedirs(self.logs_dir, exist_ok=True)

        # Inicializar DynamicPrompt (Pilar 4)
        try:
            self.dynamic_prompt = DynamicPrompt()
            self.logger.info("✅ DynamicPrompt inicializado (Pilar 4 ativo)")
        except Exception as e:
            self.logger.warning(f"⚠️ DynamicPrompt não disponível: {e}")
            self.dynamic_prompt = None

        # Limpar cache antigo automaticamente (> 2h - reduzido para evitar código obsoleto)
        self._clean_old_cache(max_age_hours=2)

        # 🔄 VERSIONING DE CACHE: Invalidar cache quando prompt muda
        self._check_and_invalidate_cache_if_prompt_changed()

        self.logger.info("CodeGenAgent inicializado.")

    def _execute_generated_code(self, code: str, local_scope: Dict[str, Any]):
        q = Queue()
        output_capture = io.StringIO()
        original_stdout = sys.stdout
        original_stderr = sys.stderr

        # Função helper para ser injetada no escopo de execução
        def load_data():
            """
            Carrega o dataframe usando Dask (lazy loading).
            IMPORTANTE: Retorna um Dask DataFrame - aplique filtros ANTES de .compute()!
            """
            import dask.dataframe as dd

            if self.data_adapter:
                # ParquetAdapter tem file_path
                file_path = getattr(self.data_adapter, 'file_path', None)
                if file_path:
                    # 🚀 CARREGAR COMO DASK DATAFRAME (lazy)
                    ddf = dd.read_parquet(file_path, engine='pyarrow')
                else:
                    raise AttributeError(f"Adapter {type(self.data_adapter).__name__} não tem file_path")
            else:
                # Fallback: carregar diretamente do Parquet (legacy/compatibilidade)
                import os
                parquet_dir = os.path.join(os.getcwd(), "data", "parquet")
                parquet_pattern = os.path.join(parquet_dir, "*.parquet")
                if not os.path.exists(parquet_dir):
                    raise FileNotFoundError(f"Diretório Parquet não encontrado em {parquet_dir}")
                # 🚀 CARREGAR COMO DASK DATAFRAME (lazy) - LER TODOS OS ARQUIVOS!
                ddf = dd.read_parquet(parquet_pattern, engine='pyarrow')

            # ✅ NORMALIZAR COLUNAS: Mapear para os nomes esperados pelo LLM (em Dask)
            column_mapping = {
                'une': 'UNE_ID',  # Renomear 'une' para evitar conflito com 'UNE' (de une_nome)
                'nomesegmento': 'NOMESEGMENTO',
                'codigo': 'PRODUTO',
                'nome_produto': 'NOME',
                'une_nome': 'UNE',  # une_nome vira UNE (nome da loja)
                'nomegrupo': 'NOMEGRUPO',
                'ean': 'EAN',
                'preco_38_percent': 'LIQUIDO_38',
                'venda_30_d': 'VENDA_30DD',
                'estoque_atual': 'ESTOQUE_UNE',
                'embalagem': 'EMBALAGEM',
                'tipo': 'TIPO'
            }

            # Aplicar mapeamento apenas para colunas que existem (Dask suporta .rename)
            rename_dict = {k: v for k, v in column_mapping.items() if k in ddf.columns}
            ddf = ddf.rename(columns=rename_dict)

            # ✅ CONVERTER ESTOQUE_UNE PARA NUMÉRICO (Dask suporta map_partitions)
            if 'ESTOQUE_UNE' in ddf.columns:
                ddf['ESTOQUE_UNE'] = dd.to_numeric(ddf['ESTOQUE_UNE'], errors='coerce').fillna(0)

            # RETORNAR DASK DATAFRAME - O código gerado deve chamar .compute() após filtros!
            return ddf

        local_scope['load_data'] = load_data
        local_scope['dd'] = dd  # Adicionar Dask ao escopo para código gerado

        def worker():
            sys.stdout = output_capture
            sys.stderr = output_capture
            try:
                exec(code, local_scope)
                q.put(local_scope.get('result'))
            except Exception as e:
                q.put(e)
            finally:
                sys.stdout = original_stdout
                sys.stderr = original_stderr

        thread = threading.Thread(target=worker)
        thread.start()
        thread.join(timeout=120.0)

        captured_output = output_capture.getvalue()
        if captured_output:
            self.logger.info(f"Saída do código gerado:\n{captured_output}")

        if thread.is_alive():
            raise TimeoutError("A execução do código gerado excedeu o tempo limite.")
        else:
            result = q.get()
            if isinstance(result, Exception):
                raise result
            return result

    def _normalize_query(self, query: str) -> str:
        """
        Normaliza query para melhorar cache hit rate.
        Remove stopwords e variações irrelevantes, mantendo semântica.
        """
        query = query.lower().strip()

        # Stopwords comuns em português que não afetam a semântica da query
        stopwords = [
            'qual', 'quais', 'mostre', 'me', 'gere', 'por favor', 'por gentileza',
            'poderia', 'pode', 'consegue', 'você', 'o', 'a', 'os', 'as',
            'um', 'uma', 'uns', 'umas', 'de', 'da', 'do', 'das', 'dos'
        ]

        # Remover stopwords
        words = query.split()
        filtered_words = [w for w in words if w not in stopwords]
        query = ' '.join(filtered_words)

        # Normalizar variações comuns
        replacements = {
            'gráfico': 'graf',
            'gráficos': 'graf',
            'grafico': 'graf',
            'graficos': 'graf',
            'ranking': 'rank',
            'rankings': 'rank',
            'top 5': 'top5',
            'top 10': 'top10',
            'top 20': 'top20',
            'últimos': 'ultimos',
            'último': 'ultimo',
            'análise': 'analise',
            'análises': 'analise',
        }

        for old, new in replacements.items():
            query = query.replace(old, new)

        # Remover espaços extras
        query = ' '.join(query.split())

        return query

    def generate_and_execute_code(self, input_data: Dict[str, Any]) -> dict:
        """
        Gera, executa e retorna o resultado do código Python para uma dada consulta.
        Esta versão foi refatorada para usar diretamente o prompt fornecido e injetar uma função `load_data`.
        """
        prompt = input_data.get("query", "")
        raw_data = input_data.get("raw_data", [])
        user_query = input_data.get("query", "")  # Definir no início para evitar UnboundLocalError

        # 🎯 Cache inteligente V2: Normalizar query para maior hit rate
        # Isso permite que "Mostre o ranking de papelaria" = "ranking papelaria" = "top 10 papelaria"
        normalized_query = self._normalize_query(user_query)
        query_lower = user_query.lower()
        intent_markers = []

        # Detectar tipo de análise
        if any(word in query_lower for word in ['gráfico', 'chart', 'visualização', 'plot', 'graf']):
            intent_markers.append('viz')
        if any(word in query_lower for word in ['ranking', 'top', 'rank']):
            intent_markers.append('rank')

        # Detectar segmento específico (extrair para evitar cache cruzado)
        import re as regex_module
        segment_match = regex_module.search(r'(tecido|papelaria|armarinho|festas|artes|casa|decoração|higiene|beleza|esporte|lazer|bazar|elétrica|limpeza|sazonais|informática|embalagens)', query_lower)
        if segment_match:
            intent_markers.append(f'seg_{segment_match.group(1)}')

        # Gerar chave de cache única baseada em query NORMALIZADA + intenção
        # Usar query normalizada aumenta hit rate em ~30-50%
        cache_key = hash(normalized_query + '_'.join(intent_markers) + (json.dumps(raw_data, sort_keys=True) if raw_data else ""))

        self.logger.debug(f"Cache: query_original='{user_query}' → normalized='{normalized_query}' → key={cache_key}")

        if cache_key in self.code_cache:
            code_to_execute = self.code_cache[cache_key]
            self.logger.info(f"Código recuperado do cache.")
        else:
            # Construir contexto com descrições das colunas mais importantes
            important_columns = [
                "PRODUTO", "NOME", "NOMESEGMENTO", "NOMECATEGORIA", "NOMEGRUPO", "NOMESUBGRUPO",
                "NOMEFABRICANTE", "VENDA_30DD", "ESTOQUE_UNE", "LIQUIDO_38",
                "UNE", "UNE_ID", "TIPO", "EMBALAGEM", "EAN",
                # Colunas temporais para gráficos de evolução
                "mes_01", "mes_02", "mes_03", "mes_04", "mes_05", "mes_06",
                "mes_07", "mes_08", "mes_09", "mes_10", "mes_11", "mes_12"
            ]

            column_context = "📊 COLUNAS DISPONÍVEIS:\n"
            for col in important_columns:
                if col in self.column_descriptions:
                    column_context += f"- {col}: {self.column_descriptions[col]}\n"

            # Adicionar valores válidos de segmentos com mapeamento inteligente
            valid_segments = """
**VALORES VÁLIDOS DE SEGMENTOS (NOMESEGMENTO):**
Use EXATAMENTE estes valores no código Python (incluindo acentos e plural/singular):

1. 'TECIDOS' → se usuário mencionar: tecido, tecidos, segmento tecido, tecidos e armarinhos
2. 'ARMARINHO E CONFECÇÃO' → se usuário mencionar: armarinho, confecção, aviamentos
3. 'PAPELARIA' → se usuário mencionar: papelaria, papel, cadernos
4. 'CASA E DECORAÇÃO' → se usuário mencionar: casa, decoração, utilidades domésticas
5. 'ARTES' → se usuário mencionar: artes, artesanato, pintura
6. 'SAZONAIS' → se usuário mencionar: sazonais, páscoa, natal, datas comemorativas
7. 'FESTAS' → se usuário mencionar: festas, aniversário, balões
8. 'INFORMÁTICA' → se usuário mencionar: informática, eletrônica, computadores
9. 'HIGIENE E BELEZA' → se usuário mencionar: higiene, beleza, cosméticos
10. 'ESPORTE E LAZER' → se usuário mencionar: esporte, lazer, brinquedos
11. 'EMBALAGENS E DESCARTÁVEIS' → se usuário mencionar: embalagens, descartáveis
12. 'BAZAR' → se usuário mencionar: bazar, utilidades
13. 'ELÉTRICA E MANUTENÇÃO' → se usuário mencionar: elétrica, manutenção, ferramentas
14. 'MATERIAL DE LIMPEZA' → se usuário mencionar: limpeza, produtos de limpeza

**REGRA DE OURO:** Interprete a intenção do usuário e mapeie para o valor EXATO da lista acima!
"""

            # Lista de UNEs válidas
            valid_unes = """
**VALORES VÁLIDOS DE LOJAS/UNIDADES (coluna UNE - nomes):**
Quando o usuário mencionar uma loja, use EXATAMENTE estes nomes:

'SCR', 'ALC', 'DC', 'CFR', 'PET', 'VVL', 'VIL', 'REP', 'JFA', 'NIT',
'CGR', 'OBE', 'CXA', '261', 'BGU', 'ALP', 'BAR', 'CP2', 'JRD', 'NIG',
'ITA', 'MAD', 'JFJ', 'CAM', 'VRD', 'SGO', 'NFR', 'TIJ', 'ANG', 'BON',
'IPA', 'BOT', 'NIL', 'TAQ', 'RDO', '3RS', 'STS', 'NAM'

**EXEMPLOS DE MAPEAMENTO:**
- Usuário diz "une mad" ou "une MAD" → Filtrar: df[df['UNE'] == 'MAD']
- Usuário diz "une 261" → Filtrar: df[df['UNE'] == '261']
- Usuário diz "une scr" → Filtrar: df[df['UNE'] == 'SCR']
- Usuário diz "une nil" → Filtrar: df[df['UNE'] == 'NIL']

**IMPORTANTE:** A coluna 'UNE' contém o NOME da loja (texto), não o ID numérico!
Se precisar do ID numérico, use a coluna 'UNE_ID'.
"""

            # 🎯 PILAR 2: Injetar exemplos contextuais baseados em padrões (Few-Shot Learning)
            examples_context = ""
            if self.pattern_matcher:
                try:
                    # Buscar padrão similar à query do usuário
                    matched_pattern = self.pattern_matcher.match_pattern(user_query)
                    if matched_pattern:
                        # Formatar exemplos para injeção no prompt
                        examples_context = self.pattern_matcher.format_examples_for_prompt(matched_pattern, max_examples=2)
                        self.logger.info(f"🎯 Few-Shot Learning: Padrão '{matched_pattern.pattern_name}' identificado com {len(matched_pattern.examples)} exemplos")
                    else:
                        self.logger.debug("ℹ️ Nenhum padrão específico identificado para esta query")
                except Exception as e:
                    self.logger.warning(f"⚠️ Erro ao buscar padrões: {e}")

            system_prompt = f"""Você é um especialista em análise de dados Python com pandas e interpretação de linguagem natural.

{column_context}

{valid_segments}

{valid_unes}

{examples_context}

**🚀 INSTRUÇÃO CRÍTICA #0 - DASK DATAFRAME:**
⚠️ **ATENÇÃO:** load_data() retorna um **Dask DataFrame** (lazy loading), NÃO um pandas DataFrame!

**VOCÊ DEVE:**
1. Aplicar todos os filtros no Dask DataFrame primeiro
2. Chamar `.compute()` APENAS UMA VEZ, logo após filtros/groupby
3. Depois de `.compute()`, você terá um pandas DataFrame normal
4. NUNCA chamar `.compute()` múltiplas vezes ou em pandas DataFrame!

✅ **CORRETO - Exemplo 1 (com filtro):**
```python
ddf = load_data()  # Dask DataFrame (lazy)
ddf_filtered = ddf[(ddf['PRODUTO'].astype(str) == '369947') & (ddf['UNE'] == 'SCR')]  # Filtro no Dask
df = ddf_filtered.compute()  # ✅ Computar UMA VEZ
result = px.bar(df, x='NOME', y='VENDA_30DD')  # df é pandas agora
```

✅ **CORRETO - Exemplo 2 (com groupby):**
```python
ddf = load_data()  # Dask DataFrame (lazy)
ddf_papelaria = ddf[ddf['NOMESEGMENTO'] == 'PAPELARIA']  # Filtro no Dask
vendas_por_une = ddf_papelaria.groupby('UNE')['VENDA_30DD'].sum()  # Ainda Dask
df_result = vendas_por_une.compute().reset_index()  # ✅ Computar UMA VEZ
une_mais_vendedora = df_result.sort_values(by='VENDA_30DD', ascending=False).head(1)  # pandas ops
result = une_mais_vendedora  # ✅ df_result é pandas, NÃO chamar .compute() de novo!
```

❌ **ERRADO - Múltiplos .compute():**
```python
ddf = load_data()
df = ddf[ddf['NOMESEGMENTO'] == 'PAPELARIA'].compute()  # compute #1
result = df.groupby('UNE')['VENDA_30DD'].sum().compute()  # ❌ ERRO! df já é pandas!
```

❌ **ERRADO - .compute() no DataFrame completo:**
```python
df = load_data().compute()  # ❌ ERRO: carrega 2.2M linhas na memória!
```

**REGRA ABSOLUTA:**
- Chame `.compute()` APENAS UMA VEZ, após todos os filtros Dask
- Depois de `.compute()`, trabalhe com pandas normalmente (SEM .compute()!)

---

**🚨 INSTRUÇÃO CRÍTICA #1 - TRATAMENTO DE VALORES NA/NULL:**
⚠️ **ATENÇÃO:** Colunas do Parquet podem conter valores NA (null/NaN) que causam erros!

**VOCÊ DEVE:**
1. SEMPRE preencher ou remover NA ANTES de comparações
2. NUNCA usar `.apply()` com lambdas que comparam valores (use operações vetorizadas!)
3. Se precisar de `.apply()`, forneça `meta=` e trate NA na função

❌ **ERRADO - Causa erro 'boolean value of NA is ambiguous':**
```python
ddf = load_data()
# Comparação direta com NA causa erro
ddf['flag'] = ddf.apply(lambda row: row['exposicao_minima'] < row['VENDA_30DD'], axis=1)
```

✅ **CORRETO - Opção 1 (PREFERIDA - mais rápida):**
```python
ddf = load_data()
# Preencher NA com 0 ANTES de comparar
ddf['exposicao_minima'] = ddf['exposicao_minima'].fillna(0)
ddf['VENDA_30DD'] = ddf['VENDA_30DD'].fillna(0)
# Operação vetorizada (SEM apply!)
ddf['flag'] = ddf['exposicao_minima'] < ddf['VENDA_30DD']
df = ddf.compute()
result = df
```

✅ **CORRETO - Opção 2 (remover NA):**
```python
ddf = load_data()
# Remover linhas com NA nas colunas relevantes
ddf = ddf.dropna(subset=['exposicao_minima', 'VENDA_30DD'])
ddf['flag'] = ddf['exposicao_minima'] < ddf['VENDA_30DD']
df = ddf.compute()
result = df
```

✅ **CORRETO - Opção 3 (apenas se apply for REALMENTE necessário):**
```python
ddf = load_data()
# Usar apply com meta= e tratamento de NA
ddf['flag'] = ddf.apply(
    lambda row: (
        row['exposicao_minima'] < row['VENDA_30DD']
        if pd.notna(row['exposicao_minima']) and pd.notna(row['VENDA_30DD'])
        else False
    ),
    axis=1,
    meta=('flag', 'bool')  # OBRIGATÓRIO!
)
df = ddf.compute()
result = df
```

**REGRA DE OURO:** Sempre use operações vetorizadas (opção 1). Evite `.apply()` sempre que possível!

**COLUNAS COMUNS COM NA:**
- `exposicao_minima` - pode ter NA
- `ESTOQUE_UNE` - pode ter NA
- Colunas de vendas mensais (`mes_01` a `mes_12`) - podem ter NA

**ANTES DE QUALQUER COMPARAÇÃO:**
```python
# Sempre preencher NA nas colunas que vai usar
ddf['coluna1'] = ddf['coluna1'].fillna(0)
ddf['coluna2'] = ddf['coluna2'].fillna(0)
# Agora pode comparar com segurança
ddf['resultado'] = ddf['coluna1'] > ddf['coluna2']
```

---

**INSTRUÇÕES CRÍTICAS:**
1. **INTERPRETAÇÃO INTELIGENTE**: Se o usuário mencionar "tecido" (singular), você DEVE usar 'TECIDOS' (plural) no código!
2. **MAPEAMENTO AUTOMÁTICO**: Use a lista de valores válidos acima para mapear termos do usuário → valores exatos do banco
3. **NOMES DE COLUNAS**: Use sempre MAIÚSCULAS conforme listado
4. **ACENTOS**: Mantenha acentuação exata (CONFECÇÃO, DECORAÇÃO, INFORMÁTICA, etc.)
5. **VENDAS**: Sempre use VENDA_30DD para métricas de vendas
6. **ESTOQUE**: Use ESTOQUE_UNE para estoque
7. **USE OS EXEMPLOS ACIMA** como referência se foram fornecidos!

**⚠️ DETECÇÃO DE RUPTURA:**
Se o usuário perguntar sobre "ruptura", "produtos em falta", "estoque zero":
- Ruptura significa ESTOQUE_UNE == 0 OU ESTOQUE_UNE < exposicao_minima
- Para identificar segmentos com ruptura: agrupe por NOMESEGMENTO onde ESTOQUE_UNE <= 0
- Exemplo: `df[df['ESTOQUE_UNE'] <= 0].groupby('NOMESEGMENTO')['PRODUTO'].count()`

**REGRAS PARA RANKINGS/TOP N:**
- Se a pergunta mencionar "ranking", "top", "maior", "mais vendido" → você DEVE fazer groupby + sum + sort_values
- Se mencionar "top 10", "top 5" → adicione .head(N) ou .nlargest(N) ANTES de criar gráfico
- SEMPRE agrupe por NOME (nome do produto) para rankings de produtos
- SEMPRE ordene por VENDA_30DD (vendas em 30 dias) de forma DECRESCENTE (ascending=False)
- **🚨 CRÍTICO:** SEMPRE use `.reset_index()` após `.groupby().sum()` ou `.groupby().agg()` ANTES de chamar `.sort_values()`
- **IMPORTANTE:** NÃO retorne apenas o filtro! Sempre faça o groupby quando houver ranking/top!

**⚠️ REGRA ANTI-ERRO SERIES:**
Ao fazer agregações (groupby + sum/mean/count), SEMPRE use `.reset_index()` ANTES de `.sort_values()`:
```python
# ❌ ERRADO: Series não tem .sort_values() confiável
result = df.groupby('NOME')['VENDA_30DD'].sum().sort_values()

# ✅ CORRETO: Converter para DataFrame primeiro
result = df.groupby('NOME')['VENDA_30DD'].sum().reset_index().sort_values(by='VENDA_30DD', ascending=False)
```

**🎯 DETECÇÃO DE GRÁFICOS - REGRA ABSOLUTA:**
Se o usuário mencionar qualquer uma destas palavras-chave, você DEVE gerar um gráfico Plotly:
- Palavras-chave visuais: "gráfico", "chart", "visualização", "plotar", "plot", "barras", "pizza", "linhas", "scatter"
- Palavras-chave analíticas: "ranking", "top N", "top 10", "maiores", "menores", "comparação"

**⚠️ REGRA CRÍTICA - GRÁFICOS PLOTLY:**
Quando gerar gráficos Plotly (px.bar, px.pie, px.line):
1. Filtre e limite os dados (.nlargest, .head, filtros) ANTES de criar o gráfico
2. NUNCA use .head() ou .nlargest() DEPOIS de px.bar/px.pie/px.line
3. A variável result deve conter o objeto Figure diretamente

❌ ERRADO (causa erro 'Figure' object has no attribute 'head'):
```python
df_top = df.nlargest(10, 'VENDA_30DD')
result = px.bar(df_top, x='NOME', y='VENDA_30DD')
result = result.head(10)  # ❌ Figure não tem .head()!
```

✅ CORRETO:
```python
df_top = df.nlargest(10, 'VENDA_30DD')  # Limite ANTES
result = px.bar(df_top, x='NOME', y='VENDA_30DD')  # result é Figure
```

**TIPOS DE GRÁFICOS DISPONÍVEIS:**
- px.bar() - Gráfico de barras (use para rankings, comparações)
- px.pie() - Gráfico de pizza (use para proporções)
- px.line() - Gráfico de linhas (use para tendências temporais)
- px.scatter() - Gráfico de dispersão (use para correlações)

**EXEMPLOS COMPLETOS DE GRÁFICOS:**

1. **Gráfico de Barras - Top 10:**
```python
df = load_data()
df_filtered = df[df['NOMESEGMENTO'] == 'TECIDOS']
df_top10 = df_filtered.nlargest(10, 'VENDA_30DD')
result = px.bar(df_top10, x='NOME', y='VENDA_30DD', title='Top 10 Produtos - Tecidos')
```

2. **Gráfico de Pizza - Distribuição por Segmento:**
```python
df = load_data()
vendas_por_segmento = df.groupby('NOMESEGMENTO')['VENDA_30DD'].sum().reset_index()
result = px.pie(vendas_por_segmento, names='NOMESEGMENTO', values='VENDA_30DD', title='Vendas por Segmento')
```

3. **Gráfico de Barras - Comparação de Grupos:**
```python
df = load_data()
papelaria = df[df['NOMESEGMENTO'] == 'PAPELARIA']
vendas_por_grupo = papelaria.groupby('NOMEGRUPO')['VENDA_30DD'].sum().sort_values(ascending=False).head(5).reset_index()
result = px.bar(vendas_por_grupo, x='NOMEGRUPO', y='VENDA_30DD', title='Top 5 Grupos - Papelaria')
```

**📊 GRÁFICOS DE EVOLUÇÃO TEMPORAL (MUITO IMPORTANTE!):**

Quando o usuário pedir "evolução", "tendência", "ao longo do tempo", "nos últimos N meses", "mensais":

✅ **USE AS COLUNAS mes_01 a mes_12** para criar gráficos de linha mostrando evolução temporal!

**IMPORTANTE:**
- mes_01 = mês mais recente
- mes_12 = mês mais antigo (12 meses atrás)
- Os valores são NUMÉRICOS (vendas do mês)

**EXEMPLO COMPLETO - Evolução de Vendas (6 meses):**
```python
ddf = load_data()
# Filtrar produto específico
ddf_filtered = ddf[ddf['PRODUTO'].astype(str) == '369947']
df = ddf_filtered.compute()

# Preparar dados temporais (6 meses mais recentes)
import pandas as pd
temporal_data = pd.DataFrame({{
    'Mês': ['Mês 6', 'Mês 5', 'Mês 4', 'Mês 3', 'Mês 2', 'Mês 1'],
    'Vendas': [
        df['mes_06'].sum(),
        df['mes_05'].sum(),
        df['mes_04'].sum(),
        df['mes_03'].sum(),
        df['mes_02'].sum(),
        df['mes_01'].sum()
    ]
}})

result = px.line(temporal_data, x='Mês', y='Vendas',
                 title='Evolução de Vendas - Últimos 6 Meses',
                 markers=True)
```

**EXEMPLO - Evolução de Vendas por Segmento (12 meses):**
```python
ddf = load_data()
ddf_filtered = ddf[ddf['NOMESEGMENTO'] == 'TECIDOS']
df = ddf_filtered.compute()

import pandas as pd
meses = ['Mês 12', 'Mês 11', 'Mês 10', 'Mês 9', 'Mês 8', 'Mês 7',
         'Mês 6', 'Mês 5', 'Mês 4', 'Mês 3', 'Mês 2', 'Mês 1']
vendas = [
    df['mes_12'].sum(), df['mes_11'].sum(), df['mes_10'].sum(),
    df['mes_09'].sum(), df['mes_08'].sum(), df['mes_07'].sum(),
    df['mes_06'].sum(), df['mes_05'].sum(), df['mes_04'].sum(),
    df['mes_03'].sum(), df['mes_02'].sum(), df['mes_01'].sum()
]

temporal_data = pd.DataFrame({{'Mês': meses, 'Vendas': vendas}})
result = px.line(temporal_data, x='Mês', y='Vendas',
                 title='Evolução Mensal - Tecidos',
                 markers=True)
```

**REGRA:** Se usuário pedir "últimos N meses", use mes_01 até mes_N (do mais recente ao mais antigo).

**MAPEAMENTO OBRIGATÓRIO DE SEGMENTOS:**
IMPORTANTE: O usuário pode usar termos no singular ou simplificados. Você DEVE usar os valores EXATOS da base de dados:

- Usuário diz: "tecido" ou "tecidos" → Você usa: df[df['NOMESEGMENTO'] == 'TECIDOS']
- Usuário diz: "papelaria" → Você usa: df[df['NOMESEGMENTO'] == 'PAPELARIA']
- Usuário diz: "armarinho" ou "confecção" → Você usa: df[df['NOMESEGMENTO'] == 'ARMARINHO E CONFECÇÃO']
- Usuário diz: "limpeza" → Você usa: df[df['NOMESEGMENTO'] == 'MATERIAL DE LIMPEZA']
- Usuário diz: "casa" ou "decoração" → Você usa: df[df['NOMESEGMENTO'] == 'CASA E DECORAÇÃO']
- Usuário diz: "festas" → Você usa: df[df['NOMESEGMENTO'] == 'FESTAS']
- Usuário diz: "higiene" ou "beleza" → Você usa: df[df['NOMESEGMENTO'] == 'HIGIENE E BELEZA']
- Usuário diz: "brinquedo" ou "brinquedos" → Você usa: df[df['NOMESEGMENTO'] == 'BRINQUEDOS']
- Usuário diz: "alimento" ou "alimentos" → Você usa: df[df['NOMESEGMENTO'] == 'ALIMENTOS']
- Usuário diz: "doce" ou "doces" → Você usa: df[df['NOMESEGMENTO'] == 'DOCES E SALGADOS']

⚠️ NUNCA use .str.upper() ou .str.contains() em comparações de segmento - use apenas == com o valor EXATO!

**🚀 OTIMIZAÇÃO DE PERFORMANCE - PREDICATE PUSHDOWN:**
Quando houver filtros específicos (segmento, UNE, produto), aplique os filtros O MAIS CEDO POSSÍVEL no código:

✅ **EFICIENTE (Predicate Pushdown):**
```python
df = load_data()
# Filtra IMEDIATAMENTE após carregar (menos memória, mais rápido)
df = df[df['NOMESEGMENTO'] == 'TECIDOS']
# Agora trabalha com dataset reduzido
df_top10 = df.nlargest(10, 'VENDA_30DD')
result = px.bar(df_top10, x='NOME', y='VENDA_30DD')
```

❌ **INEFICIENTE (Sem pushdown):**
```python
df = load_data()  # Carrega tudo (lento)
# Processa dataset inteiro
df_sorted = df.sort_values('VENDA_30DD', ascending=False)
# Filtra tarde demais
df_filtered = df_sorted[df_sorted['NOMESEGMENTO'] == 'TECIDOS'].head(10)
```

**REGRA:** Se a query mencionar filtros específicos (segmento, UNE, categoria), aplique-os na PRIMEIRA LINHA após load_data()!

Siga as instruções do usuário E faça o mapeamento inteligente de termos!"""

            # 🚀 PILAR 4: Adicionar avisos dinâmicos baseados em erros recentes
            if self.dynamic_prompt:
                try:
                    enhanced_prompt = self.dynamic_prompt.get_enhanced_prompt()
                    # Adicionar avisos ao system_prompt
                    system_prompt = system_prompt + "\n\n" + enhanced_prompt
                    self.logger.info("✅ Prompt enriquecido com DynamicPrompt (Pilar 4)")
                except Exception as e:
                    self.logger.warning(f"⚠️ Erro ao enriquecer prompt: {e}")

            # O agente agora usa o prompt diretamente, sem construir um novo.
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt}
            ]

            start_llm_query = time.time()
            llm_response = self.llm.get_completion(messages=messages)
            end_llm_query = time.time()
            self.logger.info(f"Tempo de consulta LLM: {end_llm_query - start_llm_query:.4f} segundos")

            if "error" in llm_response:
                self.logger.error(f"Erro ao obter resposta do LLM: {llm_response['error']}")
                return {"type": "error", "output": "Não foi possível gerar o código de análise."}

            code_to_execute = self._extract_python_code(llm_response.get("content", ""))

            if not code_to_execute:
                self.logger.warning("Nenhum código Python foi gerado pelo LLM.")
                return {"type": "text", "output": "Não consegui gerar um script para responder à sua pergunta."}

            # 🚀 QUICK WIN 1: Validar e corrigir Top N automaticamente
            # user_query já foi definido no início da função
            code_to_execute = self._validate_top_n(code_to_execute, user_query)

            # ✅ FASE 1: Validar código antes de executar
            validation_result = self.code_validator.validate(code_to_execute, user_query)

            if not validation_result['valid']:
                self.logger.warning(f"⚠️ Código com problemas: {validation_result['errors']}")

                # Tentar correção automática
                fix_result = self.code_validator.auto_fix(validation_result, user_query)

                if fix_result['fixed']:
                    self.logger.info(f"✅ Código corrigido automaticamente: {fix_result['fixes_applied']}")
                    code_to_execute = fix_result['code']
                else:
                    self.logger.warning(f"⚠️ Correção automática falhou. Erros restantes: {fix_result.get('remaining_errors', [])}")
                    # Continuar mesmo assim, mas com log

            # Validações adicionais com warnings (não bloqueiam execução)
            if validation_result.get('warnings'):
                self.logger.info(f"ℹ️ Avisos: {validation_result['warnings']}")

            if validation_result.get('suggestions'):
                self.logger.debug(f"💡 Sugestões: {validation_result['suggestions']}")

            self.code_cache[cache_key] = code_to_execute

        self.logger.info(f"\nCódigo a ser executado:\n---\n{code_to_execute}\n---")

        try:
            # ⚠️ IMPORTANTE: Reutilizar a função load_data() definida em _execute_generated_code
            # que já usa Dask e lê TODOS os arquivos Parquet (*.parquet)

            local_scope = {
                "pd": pd,
                "px": px,
                "result": None,
                "df_raw_data": pd.DataFrame(raw_data) if raw_data else None,
                # load_data será injetado em _execute_generated_code
            }
            
            px.defaults.template = "plotly_white"

            start_code_execution = time.time()
            result = self._execute_generated_code(code_to_execute, local_scope)
            end_code_execution = time.time()
            self.logger.info(f"Tempo de execução do código: {end_code_execution - start_code_execution:.4f} segundos")

            # ⚠️ VALIDAÇÃO CRÍTICA: Verificar se resultado é Dask não computado
            if hasattr(result, '_name') and 'dask' in str(type(result)).lower():
                self.logger.error(f"❌ ERRO: Código retornou Dask object não computado: {type(result)}")
                self.logger.error(f"   O código gerado deve chamar .compute() antes de retornar o resultado!")
                return {
                    "type": "error",
                    "output": "Erro interno: O código gerou um resultado Dask não computado. Tentando novamente..."
                }

            # Análise do tipo de resultado
            if isinstance(result, pd.DataFrame):
                self.logger.info(f"Resultado: DataFrame com {len(result)} linhas.")
                # 🚀 QUICK WIN 2: Registrar query bem-sucedida
                self._log_successful_query(user_query, code_to_execute, len(result))
                return {"type": "dataframe", "output": result}
            elif isinstance(result, pd.Series):
                self.logger.info(f"Resultado: Series com {len(result)} elementos.")
                # Converter Series para DataFrame para consistência
                result_df = result.reset_index()
                self._log_successful_query(user_query, code_to_execute, len(result_df))
                return {"type": "dataframe", "output": result_df}
            elif 'plotly' in str(type(result)):
                self.logger.info(f"Resultado: Gráfico Plotly.")
                # 🚀 QUICK WIN 2: Registrar query bem-sucedida (gráfico)
                self._log_successful_query(user_query, code_to_execute, 1)
                return {"type": "chart", "output": pio.to_json(result)}
            else:
                self.logger.info(f"Resultado: Texto.")
                return {"type": "text", "output": str(result)}
        
        except TimeoutError as e:
            self.logger.error("A execução do código excedeu o tempo limite.")
            # 🚀 QUICK WIN 3: Registrar erro
            self._log_error(user_query, code_to_execute, "timeout", str(e))
            return {"type": "error", "output": "A análise demorou muito e foi interrompida."}
        except Exception as e:
            error_msg = str(e)
            error_type = type(e).__name__

            # 🔄 AUTO-RECOVERY: Detectar erros comuns e limpar cache
            should_retry = False

            if "'DataFrame' object has no attribute 'compute'" in error_msg or \
               "'Series' object has no attribute 'compute'" in error_msg:
                should_retry = True
                self.logger.warning(f"⚠️ Detectado código com .compute() inválido")

            elif "boolean value of NA is ambiguous" in error_msg:
                should_retry = True
                self.logger.warning(f"⚠️ Detectado código sem tratamento de NA")

            elif "Invalid comparison between dtype=" in error_msg:
                should_retry = True
                self.logger.warning(f"⚠️ Detectado código sem conversão de tipos")

            elif "'Series' object has no attribute 'sort_values'" in error_msg or \
                 "AttributeError: 'Series'" in error_msg:
                should_retry = True
                self.logger.warning(f"⚠️ Detectado código com erro em Series (falta .reset_index()?)")

            if should_retry:

                self.logger.warning(f"⚠️ Detectado código com .compute() inválido em pandas object")
                self.logger.info(f"🔄 Limpando cache e tentando novamente com prompt atualizado...")

                # Limpar apenas o cache desta query específica
                if cache_key in self.code_cache:
                    del self.code_cache[cache_key]
                    self.logger.info(f"✅ Cache da query removido: {cache_key[:50]}...")

                # Tentar novamente (recursivo) - APENAS UMA VEZ
                if not hasattr(self, '_retry_flag'):
                    self._retry_flag = True
                    try:
                        result = self.generate_and_execute_code(user_query, raw_data, **kwargs)
                        return result
                    finally:
                        delattr(self, '_retry_flag')
                else:
                    self.logger.error(f"❌ Retry falhou. Erro persistente após limpeza de cache.")

            self.logger.error(f"Erro ao executar o código gerado: {e}", exc_info=True)
            # 🚀 QUICK WIN 3: Registrar erro
            self._log_error(user_query, code_to_execute, error_type, error_msg)
            return {"type": "error", "output": f"Ocorreu um erro ao executar a análise: {error_msg}"}
    def _extract_python_code(self, text: str) -> str | None:
        """Extrai o bloco de código Python da resposta do LLM."""
        match = re.search(r'```python\n(.*)```', text, re.DOTALL)
        return match.group(1).strip() if match else None

    # 🚀 QUICK WIN METHODS
    def _validate_top_n(self, code: str, user_query: str) -> str:
        """
        QUICK WIN 1: Valida se código tem .head(N) quando usuário pede 'top N'.
        Corrige automaticamente se necessário.
        """
        query_lower = user_query.lower()

        # Verificar se usuário pediu "top N"
        top_match = re.search(r'top\s+(\d+)', query_lower)

        # ✅ NÃO adicionar .head() se o código está gerando um gráfico Plotly
        # Gráficos já devem ter o filtro aplicado antes do px.bar/px.pie/etc
        is_plotly_chart = any(func in code for func in ['px.bar(', 'px.pie(', 'px.line(', 'px.scatter(', 'px.histogram('])

        if top_match and '.head(' not in code and not is_plotly_chart:
            n = top_match.group(1)
            self.logger.warning(f"⚠️ Query pede top {n} mas código não tem .head(). Corrigindo automaticamente...")

            # Tentar adicionar .head(N) antes de .reset_index()
            if '.reset_index()' in code:
                code = code.replace('.reset_index()', f'.head({n}).reset_index()')
            # Ou antes do resultado final
            elif 'result = ' in code:
                # Encontrar a última atribuição a result
                lines = code.split('\n')
                for i in range(len(lines) - 1, -1, -1):
                    if lines[i].strip().startswith('result = '):
                        # Adicionar .head(N) se ainda não existir
                        if '.head(' not in lines[i]:
                            lines[i] = lines[i].replace('result = ', f'result = ').rstrip()
                            if not lines[i].endswith(')'):
                                lines[i] = f"{lines[i]}.head({n})"
                        break
                code = '\n'.join(lines)

            self.logger.info(f"✅ Código corrigido automaticamente com .head({n})")
        elif is_plotly_chart:
            self.logger.info(f"ℹ️ Código gera gráfico Plotly - não adicionando .head() automático")

        return code

    def _log_successful_query(self, user_query: str, code: str, result_rows: int):
        """
        QUICK WIN 2: Registra queries bem-sucedidas para análise futura.
        """
        from datetime import datetime

        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'query': user_query,
            'code': code,
            'rows': result_rows,
            'success': True
        }

        # Salvar em arquivo diário
        date_str = datetime.now().strftime('%Y%m%d')
        log_file = os.path.join(self.logs_dir, f'successful_queries_{date_str}.jsonl')

        try:
            with open(log_file, 'a', encoding='utf-8') as f:
                f.write(json.dumps(log_entry, ensure_ascii=False) + '\n')
            self.logger.debug(f"✅ Query registrada em {log_file}")
        except Exception as e:
            self.logger.warning(f"⚠️ Erro ao registrar query: {e}")

    def _log_error(self, user_query: str, code: str, error_type: str, error_message: str):
        """
        QUICK WIN 3: Registra erros por tipo para análise de padrões.
        """
        from datetime import datetime

        # Incrementar contador
        self.error_counts[error_type] += 1

        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'query': user_query,
            'code': code,
            'error_type': error_type,
            'error_message': str(error_message),
            'success': False
        }

        # Salvar em arquivo diário
        date_str = datetime.now().strftime('%Y%m%d')
        log_file = os.path.join(self.logs_dir, f'error_log_{date_str}.jsonl')

        try:
            with open(log_file, 'a', encoding='utf-8') as f:
                f.write(json.dumps(log_entry, ensure_ascii=False) + '\n')

            # Também salvar contador consolidado
            counter_file = os.path.join(self.logs_dir, f'error_counts_{date_str}.json')
            with open(counter_file, 'w', encoding='utf-8') as f:
                json.dump(dict(self.error_counts), f, indent=2, ensure_ascii=False)

            self.logger.debug(f"⚠️ Erro registrado: {error_type} (total: {self.error_counts[error_type]})")
        except Exception as e:
            self.logger.warning(f"⚠️ Erro ao registrar erro: {e}")

    def _clean_old_cache(self, max_age_hours=2):
        """Limpa cache antigo automaticamente (padrão: 2 horas)"""
        import os
        import time
        from pathlib import Path

        try:
            cache_dirs = [
                Path('data/cache'),
                Path('data/cache_agent_graph')
            ]

            now = time.time()
            max_age = max_age_hours * 60 * 60  # Converte horas para segundos
            removed_count = 0

            for cache_dir in cache_dirs:
                if not cache_dir.exists():
                    continue

                for cache_file in cache_dir.glob('*'):
                    if cache_file.is_file():
                        file_age = now - cache_file.stat().st_mtime
                        if file_age > max_age:
                            cache_file.unlink()
                            removed_count += 1

            if removed_count > 0:
                self.logger.info(f"🧹 Cache limpo: {removed_count} arquivos removidos (> 24h)")

        except Exception as e:
            self.logger.warning(f"⚠️ Erro ao limpar cache: {e}")

    def _check_and_invalidate_cache_if_prompt_changed(self):
        """
        🔄 VERSIONING DE CACHE: Invalida cache se o prompt mudou

        Calcula hash do prompt atual e compara com o hash salvo.
        Se diferente, limpa o cache para forçar regeneração com novo prompt.
        """
        import hashlib
        from pathlib import Path
        import json

        try:
            # Calcular hash do prompt atual (baseado em column_descriptions + segmentos válidos)
            prompt_components = {
                'columns': list(self.column_descriptions.keys()),
                'descriptions': list(self.column_descriptions.values()),
                # Adicionar outros componentes que afetam o prompt
                'version': '2.0_temporal_fix'  # Incrementar quando houver mudanças significativas
            }

            prompt_str = json.dumps(prompt_components, sort_keys=True)
            current_hash = hashlib.md5(prompt_str.encode()).hexdigest()

            # Arquivo para armazenar hash do prompt
            version_file = Path('data/cache/.prompt_version')

            # Verificar se há versão anterior
            if version_file.exists():
                try:
                    with open(version_file, 'r') as f:
                        saved_hash = f.read().strip()

                    if saved_hash != current_hash:
                        # PROMPT MUDOU! Limpar cache
                        self.logger.warning(f"⚠️  PROMPT MUDOU! Limpando cache para forçar regeneração...")
                        self.logger.info(f"   Hash anterior: {saved_hash}")
                        self.logger.info(f"   Hash novo: {current_hash}")

                        # Limpar todos os caches
                        cache_dirs = [
                            Path('data/cache'),
                            Path('data/cache_agent_graph')
                        ]

                        removed_count = 0
                        for cache_dir in cache_dirs:
                            if cache_dir.exists():
                                for cache_file in cache_dir.glob('*'):
                                    if cache_file.is_file() and cache_file.name != '.prompt_version':
                                        cache_file.unlink()
                                        removed_count += 1

                        self.logger.info(f"✅ Cache invalidado: {removed_count} arquivos removidos")

                except Exception as e:
                    self.logger.warning(f"⚠️ Erro ao ler versão do cache: {e}")

            # Salvar hash atual
            version_file.parent.mkdir(parents=True, exist_ok=True)
            with open(version_file, 'w') as f:
                f.write(current_hash)

        except Exception as e:
            self.logger.warning(f"⚠️ Erro ao verificar versão do cache: {e}")
