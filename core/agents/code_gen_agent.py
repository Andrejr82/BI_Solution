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

# ✅ NOVO: Import Polars (condicional)
try:
    import polars as pl
    POLARS_AVAILABLE = True
except ImportError:
    pl = None
    POLARS_AVAILABLE = False
import plotly.express as px
from typing import List, Dict, Any, Tuple # Import necessary types
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
from core.learning.self_healing_system import SelfHealingSystem
from core.config.column_mapping import normalize_column_name, validate_columns, get_essential_columns
from core.utils.column_validator import (
    validate_query_code,
    extract_columns_from_query,
    ColumnValidationError
)
from core.rag.query_retriever import QueryRetriever
from core.rag.example_collector import ExampleCollector
from core.agents.polars_load_data import create_optimized_load_data

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

        # ✅ CORREÇÃO: Usar nomes REAIS do Parquet (confirmados via read_parquet_schema em 2025-10-27)
        self.column_descriptions = {
            "codigo": "Código único do produto (COLUNA PARQUET: codigo)",
            "nome_produto": "Nome/descrição do produto (COLUNA PARQUET: nome_produto)",
            "nomesegmento": "Segmento do produto (COLUNA PARQUET: nomesegmento) - Ex: TECIDOS, PAPELARIA, etc.",
            "NOMECATEGORIA": "Categoria do produto (COLUNA PARQUET: NOMECATEGORIA)",
            "nomegrupo": "Grupo do produto (COLUNA PARQUET: nomegrupo)",
            "NOMESUBGRUPO": "Subgrupo do produto (COLUNA PARQUET: NOMESUBGRUPO)",
            "NOMEFABRICANTE": "Fabricante do produto (COLUNA PARQUET: NOMEFABRICANTE)",
            "venda_30_d": "Total de vendas nos últimos 30 dias (COLUNA PARQUET: venda_30_d)",
            "estoque_atual": "Quantidade em estoque total da UNE (COLUNA PARQUET: estoque_atual)",
            "estoque_lv": "Estoque na Linha Verde/área de venda (COLUNA PARQUET: estoque_lv)",
            "estoque_cd": "Estoque no Centro de Distribuição (COLUNA PARQUET: estoque_cd)",
            "preco_38_percent": "Preço de venda com 38% de margem (COLUNA PARQUET: preco_38_percent)",
            "une": "ID numérico da loja/unidade (COLUNA PARQUET: une) - Ex: 1, 2586, 2720",
            "une_nome": "Nome da loja/unidade (COLUNA PARQUET: une_nome) - Ex: SCR, MAD, 261, ALC, NIL",
            "tipo": "Tipo de produto (COLUNA PARQUET: tipo)",
            "embalagem": "Embalagem do produto (COLUNA PARQUET: embalagem)",
            "ean": "Código de barras (COLUNA PARQUET: ean)",
            "media_considerada_lv": "Média de vendas considerada para reposição (COLUNA PARQUET: media_considerada_lv)",
            "abc_une_30_dd": "Classificação ABC da UNE nos últimos 30 dias (COLUNA PARQUET: abc_une_30_dd)",
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

        # Inicializar pattern_matcher, code_validator e RAG
        try:
            self.query_retriever = QueryRetriever()
            self.example_collector = ExampleCollector()
            self.rag_enabled = True
            self.logger.info("Sistema RAG inicializado com sucesso")
        except Exception as e:
            self.logger.warning(f"RAG não disponível: {e}. Continuando sem RAG.")
            self.query_retriever = None
            self.example_collector = None
            self.rag_enabled = False

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

        # Inicializar Self-Healing System (Auto-correção)
        try:
            self.self_healing = SelfHealingSystem(
                llm_adapter=llm_adapter,
                schema_validator=True
            )
            self.logger.info("✅ SelfHealingSystem inicializado (Auto-correção ativa)")
        except Exception as e:
            self.logger.warning(f"⚠️ SelfHealingSystem não disponível: {e}")
            self.self_healing = None

        # ⚡ SOLUÇÃO ZERO-CLICK: Cache é gerenciado 100% automaticamente
        # Usuário NÃO precisa clicar em nada, deslogar ou recarregar página

        # 1. Limpar cache antigo (5 minutos - MUITO curto para forçar regeneração rápida)
        self._clean_old_cache(max_age_hours=0.08)  # ~5 minutos

        # 2. Invalidar cache quando prompt/código muda (detecta correções automaticamente)
        self._check_and_invalidate_cache_if_prompt_changed()

        self.logger.info("CodeGenAgent inicializado.")

    def _execute_generated_code(self, code: str, local_scope: Dict[str, Any]):
        q = Queue()
        output_capture = io.StringIO()
        original_stdout = sys.stdout
        original_stderr = sys.stderr

        # Função helper para ser injetada no escopo de execução
        def load_data(filters: Dict[str, Any] = None):
            """
            🚀 OTIMIZADO: Carrega o dataframe usando PolarsDaskAdapter (híbrido Polars/Dask).

            Args:
                filters: Dicionário opcional de filtros para aplicar ANTES de carregar dados.
                        Ex: {'UNE': 'MAD'}, {'NOMESEGMENTO': 'TECIDOS'}, {'PRODUTO': 12345}
                        Filtros reduzem drasticamente memória e tempo de carregamento.

            Returns:
                pandas DataFrame (já filtrado se filters fornecido)

            IMPORTANTE:
            - COM filtros: Usa PolarsDaskAdapter (predicate pushdown, 5-10x mais rápido)
            - SEM filtros: Carrega apenas 10k linhas (proteção contra OOM)
            """
            import pandas as pd
            import os

            if self.data_adapter and filters:
                # ✅ USAR ADAPTER COM FILTROS (Polars/Dask com predicate pushdown)
                import time
                start_time = time.time()

                self.logger.info("=" * 80)
                self.logger.info("🔍 PLANO A - LOAD_DATA() COM FILTROS")
                self.logger.info(f"   Filtros aplicados: {filters}")
                self.logger.info(f"   Adapter: PolarsDaskAdapter (predicate pushdown)")

                try:
                    # Delegar para adapter (usa Polars ou Dask automaticamente)
                    result_list = self.data_adapter.execute_query(filters)
                    elapsed = time.time() - start_time

                    self.logger.info(f"✅ SUCESSO - {len(result_list):,} registros carregados em {elapsed:.2f}s")
                    self.logger.info(f"   Performance: {len(result_list)/elapsed:.0f} registros/segundo")
                    self.logger.info("=" * 80)

                    return pd.DataFrame(result_list)

                except Exception as e:
                    elapsed = time.time() - start_time
                    self.logger.error("=" * 80)
                    self.logger.error(f"❌ ERRO ao carregar com filtros (após {elapsed:.2f}s)")
                    self.logger.error(f"   Tipo: {type(e).__name__}")
                    self.logger.error(f"   Mensagem: {str(e)}")
                    self.logger.error("=" * 80)
                    # Fallback para modo sem filtros (limitado)
                    self.logger.warning("⚠️  Caindo para modo sem filtros (limitado a 10k linhas)")
                    filters = None  # Trigger fallback abaixo

            if not filters:
                # ⚠️ SEM FILTROS - Modo de proteção (limitar a 10k linhas)
                self.logger.warning("⚠️  load_data() SEM filtros - LIMITANDO a 10.000 linhas para evitar OOM")
                self.logger.warning("   RECOMENDAÇÃO: Passe filtros para carregar dados completos")
                self.logger.warning("   Exemplo: load_data(filters={'UNE': 'MAD', 'NOMESEGMENTO': 'TECIDOS'})")

                import dask.dataframe as dd

                # Definir parquet_path para uso no fallback
                parquet_path = None

                if self.data_adapter:
                    file_path = getattr(self.data_adapter, 'file_path', None)
                    if file_path:
                        parquet_path = file_path  # Salvar para fallback
                        ddf = dd.read_parquet(file_path, engine='pyarrow')
                    else:
                        raise AttributeError(f"Adapter {type(self.data_adapter).__name__} não tem file_path")
                else:
                    # Fallback: carregar diretamente do Parquet
                    parquet_dir = os.path.join(os.getcwd(), "data", "parquet")
                    parquet_pattern = os.path.join(parquet_dir, "*.parquet")
                    if not os.path.exists(parquet_dir):
                        raise FileNotFoundError(f"Diretório Parquet não encontrado em {parquet_dir}")
                    parquet_path = parquet_pattern  # Salvar para fallback
                    ddf = dd.read_parquet(parquet_pattern, engine='pyarrow')

                # Normalizar colunas
                column_mapping = {
                    'une': 'UNE_ID',
                    'nomesegmento': 'NOMESEGMENTO',
                    'codigo': 'PRODUTO',
                    'nome_produto': 'NOME',
                    'une_nome': 'UNE',
                    'nomegrupo': 'NOMEGRUPO',
                    'ean': 'EAN',
                    'preco_38_percent': 'LIQUIDO_38',
                    'venda_30_d': 'VENDA_30DD',
                    'estoque_atual': 'ESTOQUE_UNE',
                    'embalagem': 'EMBALAGEM',
                    'tipo': 'TIPO',
                    'NOMECATEGORIA': 'NOMECATEGORIA',
                    'NOMESUBGRUPO': 'NOMESUBGRUPO',
                    'NOMEFABRICANTE': 'NOMEFABRICANTE'
                }

                rename_dict = {k: v for k, v in column_mapping.items() if k in ddf.columns}
                ddf = ddf.rename(columns=rename_dict)

                # Converter tipos
                if 'ESTOQUE_UNE' in ddf.columns:
                    ddf['ESTOQUE_UNE'] = dd.to_numeric(ddf['ESTOQUE_UNE'], errors='coerce').fillna(0)

                for i in range(1, 13):
                    col_name = f'mes_{i:02d}'
                    if col_name in ddf.columns:
                        ddf[col_name] = dd.to_numeric(ddf[col_name], errors='coerce').fillna(0)

                # ⚠️ LIMITAR A 10K LINHAS (proteção contra OOM)
                self.logger.info(f"⚡ load_data(): Limitando a 10.000 linhas (sem filtros)")
                import time as time_module
                start_compute = time_module.time()

                try:
                    # Computar apenas primeiras 10k linhas
                    df_pandas = ddf.head(10000, npartitions=-1)
                except Exception as compute_error:
                    self.logger.error(f"❌ Erro ao computar Dask: {compute_error}")
                    self.logger.warning("🔄 Tentando fallback: carregar direto do Parquet com pandas (modo otimizado)")

                    # Estratégia de fallback melhorada
                    try:
                        if parquet_path:
                            # Estratégia 1: Usar pandas com limite de linhas e colunas essenciais
                            self.logger.info("   Tentando carregar com pandas (apenas colunas essenciais)...")

                            # Resolver wildcard pattern
                            import glob
                            if '*' in parquet_path:
                                parquet_files = glob.glob(parquet_path)
                                if not parquet_files:
                                    raise FileNotFoundError(f"Nenhum arquivo encontrado em: {parquet_path}")
                                parquet_path = parquet_files[0]  # Usar primeiro arquivo
                                self.logger.info(f"📁 Usando arquivo: {os.path.basename(parquet_path)}")

                            # Colunas essenciais para análises básicas (NOMES CORRETOS DO PARQUET)
                            essential_cols = get_essential_columns()
                            self.logger.info(f"   Carregando colunas essenciais: {essential_cols}")

                            df_pandas = pd.read_parquet(
                                parquet_path,
                                engine='pyarrow',
                                columns=essential_cols
                            ).head(10000)

                            self.logger.info(f"✅ Fallback bem-sucedido: {len(df_pandas)} registros carregados com {len(df_pandas.columns)} colunas")
                        else:
                            raise FileNotFoundError(f"Parquet path não disponível: {parquet_path}")

                    except Exception as fallback_error:
                        self.logger.error(f"❌ Fallback otimizado falhou: {fallback_error}")

                        # Estratégia 2: Carregar apenas 1000 linhas como último recurso
                        try:
                            self.logger.warning("   Tentando carregar apenas 1000 linhas como último recurso...")
                            df_pandas = ddf.head(1000, npartitions=-1)
                            self.logger.info(f"⚠️  Carregado dataset MUITO reduzido: {len(df_pandas)} linhas")
                        except:
                            self.logger.error(f"❌ Todas as estratégias de fallback falharam")
                            # Mensagem amigável ao usuário (sem stacktrace técnico)
                            error_msg = (
                                "❌ **Erro ao Processar Consulta**\n\n"
                                "O sistema está com recursos limitados no momento.\n\n"
                                "**💡 Sugestões:**\n"
                                "- Tente uma consulta mais específica (ex: filtre por UNE ou segmento)\n"
                                "- Divida sua análise em partes menores\n"
                                "- Aguarde alguns segundos e tente novamente\n\n"
                                "**Exemplo de consulta específica:**\n"
                                "`Top 10 produtos da UNE SCR do segmento TECIDOS`"
                            )
                            raise RuntimeError(error_msg)

                end_compute = time_module.time()
                self.logger.info(f"✅ load_data(): {len(df_pandas)} registros carregados (LIMITADO) em {end_compute - start_compute:.2f}s")

                return df_pandas

        # ✅ NOVO: Usar load_data otimizada com Polars
        try:
            # Usar pattern correto: admmat*.parquet (não admmat_une*.parquet)
            parquet_path = os.path.join("data", "parquet", "admmat*.parquet")
            optimized_load_data = create_optimized_load_data(parquet_path, self.data_adapter)
            local_scope['load_data'] = optimized_load_data
            self.logger.info("✅ Using optimized Polars load_data()")
        except Exception as e:
            self.logger.warning(f"⚠️ Erro ao criar load_data otimizada: {e}. Usando versão antiga.")
            local_scope['load_data'] = load_data  # Fallback para versão antiga

        local_scope['dd'] = dd  # Adicionar Dask ao escopo para código gerado (se necessário)
        local_scope['time'] = __import__('time')  # Adicionar módulo time ao escopo para evitar UnboundLocalError
        local_scope['pl'] = pl  # ✅ NOVO: Adicionar Polars ao escopo
        local_scope['pd'] = pd  # Adicionar Pandas para compatibilidade

        def worker():
            sys.stdout = output_capture
            sys.stderr = output_capture
            try:
                exec(code, local_scope)
                q.put(local_scope.get('result'))
            except KeyError as e:
                # ✅ TRATAMENTO ESPECÍFICO: Erro de coluna não encontrada
                error_msg = str(e)

                # Detectar se é erro de coluna
                if "nome_produto" in error_msg or "KeyError" in str(type(e).__name__):
                    self.logger.error(f"❌ Erro de coluna não encontrada: {e}")

                    # Tentar extrair nome da coluna do erro
                    import re
                    col_match = re.search(r"['\"]([^'\"]+)['\"]", error_msg)
                    if col_match:
                        missing_col = col_match.group(1)
                        self.logger.error(f"   Coluna faltante: '{missing_col}'")

                    # Criar erro mais informativo
                    enhanced_error = ColumnValidationError(
                        missing_col if col_match else "desconhecida",
                        suggestions=[],
                        available_columns=[]
                    )
                    q.put(enhanced_error)
                else:
                    q.put(e)

            except Exception as e:
                # ✅ TRATAMENTO GENÉRICO: Capturar outros erros do Polars
                error_type = type(e).__name__

                # Detectar erros comuns do Polars
                if any(err in error_type for err in ["ColumnNotFoundError", "SchemaError", "ComputeError"]):
                    self.logger.error(f"❌ Erro do Polars: {error_type} - {e}")

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

    def _detect_complex_query(self, query: str) -> bool:
        """
        Detecta se query requer raciocínio multi-step (chain-of-thought).

        Baseado em: Context7 - OpenAI Prompt Engineering Best Practices
        """
        complex_keywords = [
            'análise abc', 'distribuição', 'sazonalidade', 'tendência',
            'comparar', 'comparação', 'correlação', 'previsão',
            'alertas', 'insights', 'padrões', 'anomalias'
        ]
        query_lower = query.lower()
        return any(kw in query_lower for kw in complex_keywords)

    def _build_structured_prompt(self, user_query: str, rag_examples: list = None) -> str:
        """
        Constrói prompt estruturado seguindo OpenAI best practices.

        Baseado em: Context7 - Developer Message Pattern + Few-Shot Learning

        Hierarquia:
        1. Developer message - Identidade e comportamento do agente
        2. Few-shot examples - Exemplos rotulados (do RAG)
        3. User message - Query atual com instruções específicas

        Args:
            user_query: Query do usuário
            rag_examples: Lista de exemplos similares do RAG (opcional)

        Returns:
            Prompt estruturado em formato string
        """

        # 1️⃣ DEVELOPER MESSAGE - Identidade e Comportamento
        developer_context = f"""# 🤖 IDENTIDADE E COMPORTAMENTO

Você é um especialista em análise de dados Python com foco em:
- **Pandas/Polars**: Manipulação eficiente de DataFrames
- **Plotly**: Visualizações interativas de alta qualidade
- **Análise de Negócios**: Varejo, vendas, estoque, categorização

## 🎯 Seu Objetivo

Gerar código Python **limpo, eficiente e seguro** que responda à pergunta do usuário usando o dataset de vendas fornecido.

## 📊 CONTEXTO DO DOMÍNIO

**Dataset**: Vendas de varejo (produtos, UNEs/lojas, categorias, estoques)
**Período**: 12 meses de histórico (mes_01 = mais recente, mes_12 = mais antigo)
**Métricas Principais**:
- `venda_30_d`: Vendas dos últimos 30 dias (MÉTRICA PRIMÁRIA)
- `estoque_atual`: Estoque total disponível
- `preco_38_percent`: Preço de venda com margem de 38%
- `mes_01` a `mes_12`: Vendas mensais (série temporal)

## 🗂️ SCHEMA DE COLUNAS DISPONÍVEIS

{json.dumps(self.column_descriptions, indent=2, ensure_ascii=False)}

## ⚠️ REGRAS CRÍTICAS

1. **Nomes de Colunas**: SEMPRE use nomes EXATOS do schema (case-sensitive)
2. **Validação**: SEMPRE valide colunas antes de usar (ex: `if 'une_nome' in df.columns`)
3. **Performance**: SEMPRE use Polars para grandes datasets (scan_parquet com lazy evaluation)
4. **Segurança**: NUNCA use `eval()` ou `exec()` com input do usuário
5. **Output**: SEMPRE retorne resultados em formato estruturado (dict, DataFrame ou Plotly Figure)
6. **Comentários**: SEMPRE adicione comentários explicativos no código

## 🎯 REGRAS DE RANKING (TOP N vs TODOS)

**DETECÇÃO DE INTENÇÃO:**
- **"top 10", "top 5", "maiores", "menores" + NÚMERO** → Use `.head(N)` para limitar
- **"ranking de TODAS", "ranking COMPLETO", "TODAS as unes/produtos"** → NÃO use `.head()`, mostre TODOS
- **"ranking" genérico SEM "todas/todos" E SEM número** → Use `.head(10)` como padrão (melhor visualização)

**EXEMPLOS:**

```python
# ✅ CASO 1: "gere gráfico ranking de vendas das unes" (SEM "top N", SEM "todas")
df = load_data()
ranking = df.groupby('une_nome')['venda_30_d'].sum().sort_values(ascending=False).reset_index()
df_top10 = ranking.head(10)  # Padrão: top 10 para visualização limpa
result = px.bar(df_top10, x='une_nome', y='venda_30_d')

# ✅ CASO 2: "gere gráfico ranking de TODAS as unes" (EXPLICITAMENTE "todas")
df = load_data()
ranking_completo = df.groupby('une_nome')['venda_30_d'].sum().sort_values(ascending=False).reset_index()
# NÃO usar .head() quando usuário pede "todas"
result = px.bar(ranking_completo, x='une_nome', y='venda_30_d')

# ✅ CASO 3: "top 5 unes por vendas" (Número EXPLÍCITO)
df = load_data()
ranking = df.groupby('une_nome')['venda_30_d'].sum().sort_values(ascending=False).reset_index()
df_top5 = ranking.head(5)
result = px.bar(df_top5, x='une_nome', y='venda_30_d')
```

**PALAVRAS-CHAVE DE DETECÇÃO:**
- **Limitar**: "top", "maiores", "principais", "primeiros" + NÚMERO
- **Não limitar**: "todas", "todos", "completo", "completa", "integral"
"""

        # 2️⃣ FEW-SHOT EXAMPLES - Exemplos Rotulados do RAG
        few_shot_section = ""
        if rag_examples and len(rag_examples) > 0:
            few_shot_section = "\n\n# 📚 EXEMPLOS DE QUERIES BEM-SUCEDIDAS (Few-Shot Learning)\n\n"
            few_shot_section += "Use os exemplos abaixo como referência para gerar código similar:\n\n"

            for i, ex in enumerate(rag_examples[:3], 1):  # Máximo 3 exemplos
                similarity = ex.get('similarity_score', 0)
                few_shot_section += f"""## Exemplo {i} (Similaridade: {similarity:.1%})

**Query do Usuário:** "{ex.get('query_user', 'N/A')}"

**Código Python Gerado:**
```python
{ex.get('code_generated', 'N/A')}
```

**Resultado:** {ex.get('result_type', 'success')} | {ex.get('rows_returned', 0)} registros retornados

---

"""

        # 3️⃣ CHAIN-OF-THOUGHT (para queries complexas)
        cot_section = ""
        if self._detect_complex_query(user_query):
            cot_section = """

## 🧠 RACIOCÍNIO PASSO-A-PASSO (Chain of Thought)

Esta é uma query complexa. Divida o problema em etapas:

**Etapa 1: Análise da Query**
- Qual a métrica principal? (vendas, estoque, preço)
- Qual a dimensão de análise? (produto, UNE, categoria, tempo)
- Há filtros específicos? (segmento, categoria, período, UNE)

**Etapa 2: Planejamento do Código**
- Quais colunas do schema serão necessárias?
- Quais transformações? (group by, pivot, melt, cálculos)
- Qual visualização? (gráfico de barras, linha, pizza, tabela)

**Etapa 3: Implementação**
- Código Python otimizado com validação
- Tratamento de valores NA/null
- Comentários explicativos

Execute cada etapa mentalmente antes de gerar o código final.

"""

        # 4️⃣ USER MESSAGE - Query Atual
        user_message = f"""

## 🎯 QUERY ATUAL DO USUÁRIO

**Pergunta:** {user_query}

## 📝 INSTRUÇÕES DE GERAÇÃO

1. **Analise** a query e identifique:
   - Tipo de análise (ranking, filtro, agregação, visualização)
   - Colunas necessárias do schema
   - Filtros aplicáveis

2. **Gere código Python** que:
   - Use a função `load_data()` para carregar dados
   - Valide colunas antes de usar
   - Implemente a lógica de análise solicitada
   - Retorne resultado em variável `result`

3. **Formato de Saída**:
   - Para tabelas: `result` = DataFrame
   - Para gráficos: `result` = Plotly Figure (px.bar, px.pie, px.line)
   - Para métricas: `result` = dict com valores

## 💻 CÓDIGO PYTHON A SER GERADO:

```python
# Seu código aqui
```
"""

        # CONCATENAR TODAS AS SEÇÕES
        full_prompt = developer_context + few_shot_section + cot_section + user_message

        return full_prompt

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
            # ✅ CORREÇÃO: Usar nomes REAIS do Parquet (confirmados via read_parquet_schema)
            important_columns = [
                "codigo", "nome_produto", "nomesegmento", "NOMECATEGORIA", "nomegrupo", "NOMESUBGRUPO",
                "NOMEFABRICANTE", "venda_30_d", "estoque_atual", "preco_38_percent",
                "une", "une_nome", "tipo", "embalagem", "ean",
                # Colunas temporais para gráficos de evolução
                "mes_01", "mes_02", "mes_03", "mes_04", "mes_05", "mes_06",
                "mes_07", "mes_08", "mes_09", "mes_10", "mes_11", "mes_12",
                # Colunas de análise adicional
                "media_considerada_lv", "estoque_lv", "estoque_cd", "abc_une_30_dd"
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

            # ✅ CORREÇÃO CRÍTICA: Atualizar instruções para usar 'une_nome' (não 'UNE')
            valid_unes = """
**🚨 VALORES VÁLIDOS DE LOJAS/UNIDADES (SCHEMA CORRETO DO PARQUET):**

O Parquet possui DUAS colunas relacionadas a UNE:
1. **une** (int) - ID numérico da loja (ex: 1, 2586, 2720)
2. **une_nome** (str) - Nome da loja (ex: 'SCR', 'MAD', '261')

**NOMES VÁLIDOS (coluna une_nome):**
'SCR', 'ALC', 'DC', 'CFR', 'PET', 'VVL', 'VIL', 'REP', 'JFA', 'NIT',
'CGR', 'OBE', 'CXA', '261', 'BGU', 'ALP', 'BAR', 'CP2', 'JRD', 'NIG',
'ITA', 'MAD', 'JFJ', 'CAM', 'VRD', 'SGO', 'NFR', 'TIJ', 'ANG', 'BON',
'IPA', 'BOT', 'NIL', 'TAQ', 'RDO', '3RS', 'STS', 'NAM'

**✅ EXEMPLOS CORRETOS (usar une_nome, NÃO 'UNE'):**
```python
# Filtrar por nome de loja (use une_nome!)
df_mad = df[df['une_nome'] == 'MAD']
df_scr = df[df['une_nome'] == 'SCR']
df_261 = df[df['une_nome'] == '261']
df_nil = df[df['une_nome'] == 'NIL']
```

**❌ ERRADO (NÃO use 'UNE', essa coluna NÃO EXISTE no Parquet!):**
```python
df_mad = df[df['UNE'] == 'MAD']  # ❌ KeyError: 'UNE'
```

**REGRA DE OURO:** SEMPRE use 'une_nome' para filtrar por loja!
Se precisar do ID numérico, use a coluna 'une' (minúsculo).
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

            # 🎯 PILAR 2.5: RAG - Busca semântica de queries similares (expandir Few-Shot Learning)
            rag_examples = []
            if self.rag_enabled and self.query_retriever:
                try:
                    similar_queries = self.query_retriever.find_similar_queries(user_query, top_k=3)
                    if similar_queries:
                        # Filtrar apenas exemplos com alta similaridade (> 0.7)
                        rag_examples = [ex for ex in similar_queries if ex.get('similarity_score', 0) > 0.7]

                        if rag_examples:
                            self.logger.info(f"🔍 RAG: {len(rag_examples)} queries similares de alta qualidade encontradas (melhor match: {similar_queries[0].get('similarity_score', 0):.2%})")
                        else:
                            self.logger.debug("ℹ️ RAG: Nenhuma query com similaridade > 0.7 encontrada")
                    else:
                        self.logger.debug("ℹ️ RAG: Nenhuma query similar encontrada no banco")
                except Exception as e:
                    self.logger.warning(f"⚠️ Erro ao buscar queries similares (RAG): {e}")

            # ✅ NOVO: Construir prompt estruturado usando Context7 best practices
            # Developer message + Few-shot learning + Chain-of-thought
            system_prompt = self._build_structured_prompt(user_query, rag_examples=rag_examples)

            # Adicionar contexto de exemplos do PatternMatcher (se houver)
            if examples_context:
                system_prompt += f"\n\n{examples_context}"

            self.logger.info(f"✅ Prompt estruturado gerado: {len(system_prompt)} caracteres, {len(rag_examples)} exemplos RAG")

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

            # 🔧 SELF-HEALING: Validação e auto-correção PRÉ-execução
            if self.self_healing:
                try:
                    # Obter schema de colunas disponíveis
                    schema_columns = list(self.column_descriptions.keys())

                    healing_context = {
                        'query': user_query,
                        'schema_columns': schema_columns
                    }

                    # Validar e tentar curar
                    is_valid, healed_code, feedback = self.self_healing.validate_and_heal(
                        code_to_execute,
                        healing_context
                    )

                    if feedback:
                        for msg in feedback:
                            self.logger.info(f"🔧 Self-Healing: {msg}")

                    if healed_code != code_to_execute:
                        self.logger.info("✅ Código auto-corrigido pelo SelfHealingSystem")
                        code_to_execute = healed_code

                    if not is_valid:
                        self.logger.warning("⚠️ Self-Healing detectou problemas que podem causar erro")

                except Exception as e:
                    self.logger.warning(f"⚠️ Erro no Self-Healing pré-execução: {e}")

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
            elif isinstance(result, list) and len(result) > 0 and 'plotly' in str(type(result[0])):
                # ✅ CORREÇÃO: Lista de Figures Plotly (múltiplos gráficos)
                self.logger.info(f"Resultado: {len(result)} gráficos Plotly.")

                # Aplicar tema escuro a cada Figure
                figures_json = []
                for i, fig in enumerate(result):
                    if 'plotly' in str(type(fig)):
                        # ✨ APLICAR TEMA ESCURO CHATGPT
                        fig.update_layout(
                            plot_bgcolor='#2a2b32',
                            paper_bgcolor='#2a2b32',
                            font=dict(color='#ececf1', family='sans-serif'),
                            title=dict(font=dict(color='#ececf1', size=18)),
                            xaxis=dict(
                                gridcolor='#444654',
                                tickfont=dict(color='#ececf1'),
                                title=dict(font=dict(color='#ececf1'))
                            ),
                            yaxis=dict(
                                gridcolor='#444654',
                                tickfont=dict(color='#ececf1'),
                                title=dict(font=dict(color='#ececf1'))
                            ),
                            margin=dict(l=60, r=40, t=40, b=80),
                            hoverlabel=dict(
                                bgcolor='#2a2b32',
                                bordercolor='#10a37f',
                                font=dict(color='#ececf1')
                            ),
                            legend=dict(
                                font=dict(color='#ececf1'),
                                bgcolor='rgba(42, 43, 50, 0.8)'
                            )
                        )
                        figures_json.append(pio.to_json(fig))
                    else:
                        self.logger.warning(f"⚠️ Item {i} na lista não é uma Figure Plotly: {type(fig)}")

                # 🚀 Registrar query bem-sucedida (múltiplos gráficos)
                self._log_successful_query(user_query, code_to_execute, len(figures_json))
                return {"type": "multiple_charts", "output": figures_json}
            elif 'plotly' in str(type(result)):
                self.logger.info(f"Resultado: Gráfico Plotly.")

                # ✨ APLICAR TEMA ESCURO CHATGPT (20/10/2025)
                result.update_layout(
                    plot_bgcolor='#2a2b32',
                    paper_bgcolor='#2a2b32',
                    font=dict(color='#ececf1', family='sans-serif'),
                    title=dict(font=dict(color='#ececf1', size=18)),
                    xaxis=dict(
                        gridcolor='#444654',
                        tickfont=dict(color='#ececf1'),
                        title=dict(font=dict(color='#ececf1'))
                    ),
                    yaxis=dict(
                        gridcolor='#444654',
                        tickfont=dict(color='#ececf1'),
                        title=dict(font=dict(color='#ececf1'))
                    ),
                    margin=dict(l=60, r=40, t=40, b=80),
                    hoverlabel=dict(
                        bgcolor='#2a2b32',
                        bordercolor='#10a37f',
                        font=dict(color='#ececf1')
                    ),
                    legend=dict(
                        font=dict(color='#ececf1'),
                        bgcolor='rgba(42, 43, 50, 0.8)'
                    )
                )

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

            # 🔧 SELF-HEALING: Tentar corrigir erro automaticamente
            if self.self_healing and not hasattr(self, '_healing_retry_count'):
                try:
                    self._healing_retry_count = 0

                    self.logger.info(f"🔧 Self-Healing: Tentando corrigir {error_type}...")

                    # Obter schema de colunas
                    schema_columns = list(self.column_descriptions.keys())
                    healing_context = {
                        'query': user_query,
                        'schema_columns': schema_columns
                    }

                    # Tentar curar (máximo 2 retries)
                    success, corrected_code, explanation = self.self_healing.heal_after_error(
                        code_to_execute,
                        e,
                        healing_context,
                        max_retries=2
                    )

                    if success and corrected_code != code_to_execute:
                        self.logger.info(f"✅ Self-Healing: {explanation}")
                        self.logger.info(f"🔄 Tentando novamente com código corrigido...")

                        # Limpar cache e atualizar com código corrigido
                        if cache_key in self.code_cache:
                            del self.code_cache[cache_key]

                        self.code_cache[cache_key] = corrected_code

                        # Retry com código corrigido (máximo 1 vez)
                        if self._healing_retry_count < 1:
                            self._healing_retry_count += 1
                            try:
                                # Re-executar com código corrigido
                                local_scope = {
                                    "pd": pd,
                                    "px": px,
                                    "result": None,
                                    "df_raw_data": pd.DataFrame(raw_data) if raw_data else None,
                                }
                                result = self._execute_generated_code(corrected_code, local_scope)

                                # Sucesso! Retornar resultado
                                self.logger.info("✅ Self-Healing: Código corrigido executado com sucesso!")
                                delattr(self, '_healing_retry_count')

                                # Processar resultado normalmente
                                if isinstance(result, pd.DataFrame):
                                    self._log_successful_query(user_query, corrected_code, len(result))
                                    return {"type": "dataframe", "output": result}
                                elif isinstance(result, pd.Series):
                                    result_df = result.reset_index()
                                    self._log_successful_query(user_query, corrected_code, len(result_df))
                                    return {"type": "dataframe", "output": result_df}
                                elif 'plotly' in str(type(result)):
                                    self._log_successful_query(user_query, corrected_code, 1)
                                    return {"type": "chart", "output": pio.to_json(result)}
                                else:
                                    return {"type": "text", "output": str(result)}

                            except Exception as retry_error:
                                self.logger.warning(f"⚠️ Self-Healing retry falhou: {retry_error}")
                                delattr(self, '_healing_retry_count')
                        else:
                            delattr(self, '_healing_retry_count')

                    else:
                        self.logger.warning(f"⚠️ Self-Healing não conseguiu corrigir automaticamente")

                except Exception as healing_error:
                    self.logger.warning(f"⚠️ Erro no Self-Healing pós-erro: {healing_error}")
                    if hasattr(self, '_healing_retry_count'):
                        delattr(self, '_healing_retry_count')

            # 🔄 AUTO-RECOVERY: Detectar erros comuns e limpar cache (fallback)
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

            elif "UnboundLocalError" in error_type or "cannot access local variable" in error_msg:
                should_retry = True
                self.logger.warning(f"⚠️ Detectado UnboundLocalError - possível conflito de escopo")

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
        + RAG: Coleta automática para banco de exemplos.
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

        # 🎯 RAG: Coletar query bem-sucedida para treinamento contínuo
        if self.rag_enabled and self.example_collector:
            try:
                # Detectar intenção baseado no código gerado
                intent = "python_analysis"
                if 'plotly' in code or 'px.' in code:
                    intent = "visualization"
                elif '.groupby' in code:
                    intent = "aggregation"
                elif '.nlargest' in code or '.nsmallest' in code:
                    intent = "ranking"

                # Coletar exemplo
                self.example_collector.collect_successful_query(
                    user_query=user_query,
                    code_generated=code,
                    result_rows=result_rows,
                    intent=intent
                )
                self.logger.debug(f"📚 RAG: Query coletada para banco de exemplos")
            except Exception as e:
                self.logger.warning(f"⚠️ Erro ao coletar query no RAG: {e}")

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
            # ✅ INCREMENTAR VERSÃO para forçar regeneração após correção de schema
            prompt_components = {
                'columns': list(self.column_descriptions.keys()),
                'descriptions': list(self.column_descriptions.values()),
                # Adicionar outros componentes que afetam o prompt
                'version': '5.0_context7_prompt_engineering_few_shot_learning_20251027'  # ✅ NOVA VERSÃO
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

    def detect_broad_query(self, query: str) -> Tuple[bool, str]:
        """
        Detecta se uma query é muito ampla e pode causar timeout.
        """
        query_lower = query.lower()

        # Critérios de queries amplas
        broad_keywords = ["todos", "todas", "geral", "completo", "tudo", "vendas", "estoque"]
        specific_keywords = ["top", "limite", "une", "segmento", "categoria", "grupo", "fabricante", "preço", "<", ">", "="]

        has_broad = any(kw in query_lower for kw in broad_keywords)
        has_specific = any(kw in query_lower for kw in specific_keywords)
        has_number = any(char.isdigit() for char in query_lower)

        if has_broad and not has_specific and not has_number:
            return True, "Keyword ampla detectada sem filtros específicos ou limites numéricos"

        if "ranking" in query_lower and not has_specific and not has_number:
            return True, "Ranking sem limite ou filtro específico"

        # Check for queries that are implicitly broad
        if not has_specific and not has_number:
            return True, "Query sem filtros específicos ou limites numéricos"

        return False, "Query específica OK"

    def get_educational_message(self, query: str, reason: str) -> str:
        """
        Gera uma mensagem educativa para queries amplas.
        """
        return f"""
🔍 Query Muito Ampla Detectada

**Sua Pergunta:** "{query}"

**Motivo:** {reason}

**Por que isso acontece?**
- Processar milhões de registros pode levar muito tempo e causar erros.

**✅ Como fazer queries eficientes:**

**Exemplos de queries válidas:**
   1. Top 10 produtos mais vendidos da UNE NIG
   2. Produtos do segmento ARMARINHO com estoque < 10
   3. Vendas da UNE BEL nos últimos 30 dias

**💡 Dicas:**
1. Especifique uma UNE (loja)
2. Use limites (Top 10, Top 20)
3. Aplique filtros (segmento, preço, etc.)
4. Defina um período de tempo

**💡 Sugestão:** Tente 'Top 10 produtos mais vendidos da UNE [código]'
"""
