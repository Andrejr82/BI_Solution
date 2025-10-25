"""
Motor de Consultas Diretas - Zero LLM para Economia Máxima
Sistema que executa consultas pré-definidas sem usar tokens da LLM.
"""

import pandas as pd
import dask.dataframe as dd
import json
import logging
from typing import Dict, List, Any, Optional, Tuple, Union
from datetime import datetime
import re
from pathlib import Path
import traceback

from core.connectivity.parquet_adapter import ParquetAdapter
from core.visualization.advanced_charts import AdvancedChartGenerator
from core.utils.logger_config import (
    get_logger,
    log_query_attempt,
    log_performance_metric,
    log_critical_error
)

logger = get_logger('agent_bi.direct_query')

class DirectQueryEngine:
    """Motor de consultas diretas que NÃO usa LLM para economizar tokens."""

    def __init__(self, parquet_adapter: Union[ParquetAdapter, Any]):
        """
        Inicializa o motor com o adapter de dados.

        Args:
            parquet_adapter: ParquetAdapter ou HybridDataAdapter (SQL Server + Parquet)
        """
        self.parquet_adapter = parquet_adapter
        self.chart_generator = AdvancedChartGenerator()
        self.query_cache = {}
        self.templates = self._load_query_templates()
        self.keywords_map = self._build_keywords_map()
        self.patterns = self._load_query_patterns()

        # Cache de dados frequentes
        self._cached_data = {}
        self._cache_timestamp = None

        # ⚡ CACHE CRÍTICO: DataFrame Dask em memória para performance
        self._cached_dask_df = None
        self._cache_source = None  # Rastrear fonte (sql/parquet)

        logger.info(f"DirectQueryEngine inicializado - {len(self.patterns)} padroes carregados - ZERO LLM tokens")

    @staticmethod
    def _safe_get_int(params: Dict[str, Any], key: str, default: int = 10) -> int:
        """Obtém valor inteiro de params com validação segura."""
        try:
            value = params.get(key, default)
            return int(value) if value is not None else default
        except (ValueError, TypeError):
            logger.warning(f"Falha ao converter '{key}': {params.get(key)} para int. Usando default: {default}")
            return default

    @staticmethod
    def _safe_get_str(params: Dict[str, Any], key: str, default: str = '') -> str:
        """Obtém valor string de params com validação segura."""
        try:
            value = params.get(key, default)
            return str(value).strip() if value is not None else default
        except (ValueError, TypeError):
            logger.warning(f"Falha ao converter '{key}': {params.get(key)} para str. Usando default: '{default}'")
            return default

    @staticmethod
    def _normalize_une_filter(df: pd.DataFrame, une_input: str) -> pd.DataFrame:
        """Normaliza filtro de UNE para aceitar código OU sigla."""
        une_upper = str(une_input).upper().strip()

        # Tentar filtrar por sigla (une_nome) OU por código (une)
        result = df[
            (df['une_nome'].str.upper() == une_upper) |
            (df['une'].astype(str) == une_upper)
        ]

        # Se vazio e input é numérico, tentar como int
        if result.empty and une_upper.isdigit():
            try:
                result = df[df['une'] == int(une_upper)]
            except:
                pass

        return result

    def _normalize_query(self, query: str) -> str:
        """Normaliza query do usuário para melhor matching."""
        # Remove espaços múltiplos
        query = re.sub(r'\s+', ' ', query.strip())

        # Expansões comuns
        expansions = {
            r'\bp/\b': 'para',
            r'\bvc\b': 'você',
            r'\btb\b': 'também',
            r'\bmto\b': 'muito',
            r'\bq\b': 'que',
            r'\bn\b': 'não',
        }

        for pattern, replacement in expansions.items():
            query = re.sub(pattern, replacement, query, flags=re.IGNORECASE)

        return query

    def _load_query_templates(self) -> Dict[str, Any]:
        """Carrega templates de consultas pré-definidas."""
        templates_path = Path("data/business_question_templates_expanded.json")

        if templates_path.exists():
            with open(templates_path, 'r', encoding='utf-8') as f:
                return json.load(f)

        # Fallback com templates essenciais hardcoded
        return {
            "essential_queries": {
                "produto_mais_vendido": {
                    "type": "ranking",
                    "data_source": "vendas_totais",
                    "group_by": "nome_produto",
                    "order": "desc",
                    "limit": 1
                },
                "filial_mais_vendeu": {
                    "type": "ranking",
                    "data_source": "vendas_totais",
                    "group_by": "une_nome",
                    "order": "desc",
                    "limit": 1
                },
                "segmento_campao": {
                    "type": "ranking",
                    "data_source": "vendas_totais",
                    "group_by": "nomesegmento",
                    "order": "desc",
                    "limit": 1
                }
            }
        }

    def _load_query_patterns(self) -> List[Dict[str, Any]]:
        """Carrega padrões de perguntas do arquivo JSON."""
        patterns_path = Path("data/query_patterns_training.json")

        if patterns_path.exists():
            try:
                with open(patterns_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    return data.get("patterns", [])
            except Exception as e:
                logger.warning(f"Erro ao carregar padrões: {e}")

        return []

    def _build_keywords_map(self) -> Dict[str, str]:
        """Mapeia palavras-chave para queries diretas - SEM LLM."""
        return {
            # Produtos
            "produto mais vendido": "produto_mais_vendido",
            "top produto": "produto_mais_vendido",
            "produto líder": "produto_mais_vendido",
            "produto campeão": "produto_mais_vendido",
            "produtos sem movimento": "produtos_sem_vendas",
            "produtos parados": "produtos_sem_vendas",
            "produtos sem vendas": "produtos_sem_vendas",

            # Filiais
            "filial mais vendeu": "filial_mais_vendeu",
            "filial líder": "filial_mais_vendeu",
            "top filial": "filial_mais_vendeu",
            "une mais vendeu": "filial_mais_vendeu",
            "ranking filiais": "ranking_filiais",
            "ranking unes": "ranking_filiais",

            # Segmentos
            "segmento mais vendeu": "segmento_campao",
            "segmento líder": "segmento_campao",
            "top segmento": "segmento_campao",
            "segmento campeão": "segmento_campao",
            "ranking segmentos": "ranking_segmentos",

            # Fabricantes (NOVO - Fase 1)
            "ranking fabricantes": "ranking_fabricantes",
            "ranking de fabricantes": "ranking_fabricantes",
            "top fabricantes": "ranking_fabricantes",
            "fabricantes mais vendem": "ranking_fabricantes",
            "melhores fabricantes": "ranking_fabricantes",

            # Rankings Gerais (NOVO - Fase 1)
            "ranking de vendas": "ranking_geral",
            "ranking geral": "ranking_geral",
            "top vendas": "ranking_geral",
            "melhores": "ranking_geral",

            # Comparação e Análise ABC (NOVO - Fase 2)
            "comparação de segmentos": "comparacao_segmentos",
            "comparar segmentos": "comparacao_segmentos",
            "compare segmentos": "comparacao_segmentos",
            "segmentos vs": "comparacao_segmentos",
            "análise abc": "analise_abc",
            "classificação abc": "analise_abc",
            "curva abc": "analise_abc",
            "produtos abc": "analise_abc",
            "classe abc": "analise_abc",

            # Estoque (NOVO - Fase 2)
            "estoque alto": "estoque_alto",
            "excesso de estoque": "estoque_alto",
            "estoque excessivo": "estoque_alto",
            "produtos com estoque alto": "estoque_alto",

            # Segmento e Categoria (NOVO - Fase 2 refinada)
            "produtos que mais vendem no segmento": "top_produtos_por_segmento",
            "mais vendidos no segmento": "top_produtos_por_segmento",
            "top produtos segmento": "top_produtos_por_segmento",
            "distribuição de vendas por categoria": "distribuicao_categoria",
            "distribuição por categoria": "distribuicao_categoria",
            "vendas por categoria": "distribuicao_categoria",

            # Diversidade e Penetração (NOVO - Fase 2 refinada)
            "diversidade de produtos": "diversidade_produtos",
            "produtos únicos": "diversidade_produtos",
            "penetração": "diversidade_produtos",
            "quantos produtos": "diversidade_produtos",

            # Crescimento e Sazonalidade (já existem patterns, mas adicionando keywords)
            "crescimento percentual": "crescimento_segmento",
            "maior crescimento": "crescimento_segmento",
            "sazonalidade": "sazonalidade",
            "sazonal": "sazonalidade",
            "padrão de vendas sazonal": "sazonalidade",
            "meses que vendem mais": "sazonalidade",

            # Ranking UNEs e queries por UNE (NOVO - Fase 2 refinada)
            "qual une vende mais": "ranking_unes_por_segmento",
            "ranking de unes": "ranking_geral",
            "une que mais vende": "ranking_unes_por_segmento",

            # Evolução mensal (NOVO - Fase 2 refinada)
            "evolução de vendas mensais": "evolucao_mes_a_mes",
            "evolução mensal": "evolucao_mes_a_mes",
            "vendas mensais": "evolucao_mes_a_mes",
            "mostre a evolução": "evolucao_mes_a_mes",

            # Pico de vendas, tendências e performance (NOVO - Fase 2 refinada final)
            "pico de vendas": "pico_vendas",
            "produtos tiveram pico": "pico_vendas",
            "produtos com pico": "pico_vendas",
            "tendência de vendas": "tendencia_vendas",
            "tendência dos últimos": "tendencia_vendas",
            "produtos acima da média": "produtos_acima_media",
            "vendas acima da média": "produtos_acima_media",
            "performance produtos": "produtos_acima_media",

            # Top produtos por segmento
            "top 10 produtos": "top_produtos_por_segmento",
            "10 produtos mais vendidos": "top_produtos_por_segmento",
            "produtos mais vendidos segmento": "top_produtos_por_segmento",
            "top produtos segmento": "top_produtos_por_segmento",
            "produtos por segmento": "top_produtos_por_segmento",

            # Estoque
            "estoque parado": "estoque_parado",
            "produtos estoque parado": "estoque_parado",
            "estoque sem giro": "estoque_parado",
            "produtos reposição": "produtos_reposicao",
            "estoque baixo": "produtos_reposicao",

            # Financeiro
            "faturamento": "faturamento_mensal",
            "faturamento mês": "faturamento_mensal",
            "receita": "faturamento_mensal",

            # Temporais
            "evolução vendas": "evolucao_vendas_mensais",
            "vendas mensais": "evolucao_vendas_mensais",
            "comparação mensal": "comparacao_mensal",
            "variação mensal": "variacao_mensal"
        }

    def _get_cached_base_data(self, full_dataset: bool = False) -> pd.DataFrame:
        """Obtém dados base do cache ou carrega se necessário.

        Args:
            full_dataset: Se True, carrega dataset completo. Se False, carrega amostra (500 registros).
        """
        cache_key = "full_data" if full_dataset else "base_data"
        current_time = datetime.now()

        # Cache por 5 minutos
        if (
            self._cache_timestamp is None
            or (current_time - self._cache_timestamp).seconds > 300
            or cache_key not in self._cached_data
        ):
            if full_dataset:
                logger.info("Carregando dataset COMPLETO - necessário para consulta específica")
            else:
                logger.info("Carregando dados base - cache expirado")

            self.parquet_adapter.connect()

            if full_dataset:
                # Para dataset completo, carregar diretamente do parquet
                self.parquet_adapter._load_dataframe()
                if self.parquet_adapter._dataframe is not None:
                    df = self.parquet_adapter._dataframe.copy()
                    logger.info(f"Dataset completo carregado: {len(df)} registros")
                else:
                    logger.error("Falha ao carregar dataset completo")
                    return pd.DataFrame()
            else:
                # Carregar apenas amostra para economizar memória
                base_data = self.parquet_adapter.execute_query({})

                if base_data and len(base_data) > 0:
                    df = pd.DataFrame(base_data)
                    logger.info(f"Amostra carregada: {len(df)} registros")
                else:
                    logger.error("Falha ao carregar dados base")
                    return pd.DataFrame()

            # Garantir que vendas_total existe
            vendas_cols = [col for col in ddf.columns if col.startswith('mes_') and col[4:].isdigit()]
            if vendas_cols and 'vendas_total' not in ddf.columns:
                df['vendas_total'] = df[vendas_cols].sum(axis=1)
                logger.info("Coluna vendas_total criada no dataset")

            self._cached_data[cache_key] = df
            self._cache_timestamp = current_time
            logger.info(f"Cache atualizado: {len(df)} registros")

        return self._cached_data[cache_key]

    def classify_intent_direct(self, user_query: str) -> Tuple[str, Dict[str, Any]]:
        """Classifica intenção SEM usar LLM - apenas keywords."""
        start_time = datetime.now()
        logger.info(f"CLASSIFICANDO INTENT: '{user_query}'")

        try:
            # Normalizar query antes de processar
            user_query = self._normalize_query(user_query)
            query_lower = user_query.lower()

            # 🔥 PRIORIDADE MÁXIMA: Detectar "ranking DE segmentos" (plural) - lista de segmentos
            if re.search(r'ranking\s*(de|dos)\s*segmentos', query_lower):
                result = ("ranking_segmentos", {})
                logger.info(f"✅ [PRIORIDADE MAXIMA] Classificado: ranking_segmentos (plural)")
                return result

            # 🔥 PRIORIDADE MÁXIMA: Detectar "top N produtos [do/no] segmento X"
            top_produtos_segmento_match = re.search(r'top\s+(\d+)\s+produtos\s*(do|no|de|em)?\s*segmento\s+(\w+)', query_lower)
            if top_produtos_segmento_match:
                limite = int(top_produtos_segmento_match.group(1))
                segmento_nome = top_produtos_segmento_match.group(3)
                result = ("top_produtos_por_segmento", {"segmento": segmento_nome, "limit": limite})
                logger.info(f"✅ [PRIORIDADE MAXIMA] Classificado: top_produtos_por_segmento (top {limite} do segmento: {segmento_nome})")
                return result

            # 🔥 PRIORIDADE MÁXIMA: Detectar "ranking [de vendas] [no/do/em] segmento X" (singular)
            # ANTES de outros patterns para evitar confusão com "ranking DE segmentos"
            ranking_segmento_match = re.search(r'ranking\s*(de\s*vendas)?\s*(no|do|em)?\s*segmento\s+(\w+)(?!\s*s\b)', query_lower)
            if ranking_segmento_match and "segmentos" not in query_lower:
                segmento_nome = ranking_segmento_match.group(3)
                limite_match = re.search(r'top\s*(\d+)', query_lower)
                limite = int(limite_match.group(1)) if limite_match else 10
                result = ("top_produtos_por_segmento", {"segmento": segmento_nome, "limit": limite})
                logger.info(f"✅ [PRIORIDADE MAXIMA] Classificado: top_produtos_por_segmento (segmento: {segmento_nome}, limit: {limite})")
                return result

            # 🔥 PRIORIDADE MÁXIMA: Detectar "RANKING DE VENDAS NA UNE X" antes de tudo
            ranking_vendas_une_match = re.search(r'ranking\s*(de\s*vendas|vendas).*(na|da)\s*une\s+([A-Za-z0-9]+)', query_lower)
            if ranking_vendas_une_match:
                une_nome = ranking_vendas_une_match.group(3).upper()
                result = ("top_produtos_une_especifica", {"limite": 10, "une_nome": une_nome})
                logger.info(f"[OK] CLASSIFICADO COMO: top_produtos_une_especifica (ranking de vendas na une: '{une_nome}')")
                return result

            # 🔥 PRIORIDADE MÁXIMA: Detectar "RANKING DE PRODUTOS" genérico (sem UNE)
            ranking_produtos_match = re.search(r'^ranking\s*(de\s*)?(produtos|vendas)\s*$', query_lower)
            if ranking_produtos_match:
                result = ("top_produtos_por_segmento", {"segmento": "todos", "limit": 10})
                logger.info(f"[OK] CLASSIFICADO COMO: top_produtos_por_segmento (ranking geral de produtos)")
                return result

            # 🆕 PRIORIDADE ALTA: Testar padrões treináveis
            for pattern in self.patterns:
                match = re.search(pattern["regex"], query_lower, re.IGNORECASE)
                if match:
                    params = {}
                    # Extrair parâmetros do regex
                    for key, group_expr in pattern.get("extract", {}).items():
                        group_num = int(group_expr.replace("group(", "").replace(")", ""))
                        params[key] = match.group(group_num)

                    query_type = pattern["id"]
                    logger.info(f"[OK] PADRAO MATCH: {pattern['name']} -> {query_type} com params: {params}")
                    return (query_type, params)

            # ALTA PRIORIDADE: Detectar consultas de PREÇO de produto em UNE específica
            preco_produto_une_match = re.search(r'(pre[çc]o|valor|custo).*produto\s*(\d{5,7}).*une\s*([A-Za-z0-9]+)', query_lower)
            if preco_produto_une_match:
                produto_codigo = preco_produto_une_match.group(2)
                une_nome = preco_produto_une_match.group(3).upper()
                result = ("preco_produto_une_especifica", {"produto_codigo": produto_codigo, "une_nome": une_nome})
                logger.info(f"CLASSIFICADO COMO: preco_produto_une_especifica (produto: {produto_codigo}, une: {une_nome})")
                return result

            # ALTA PRIORIDADE: Detectar consultas de TOP PRODUTOS em UNE específica
            # Pattern melhorado para aceitar variações: "10 produtos mais vendidos na une tij"
            top_produtos_une_match = re.search(
                r'(?:quais?\s+(?:s[ãa]o\s+)?(?:os?\s+)?)?(\d+)\s*produtos\s*(?:mais\s*vendidos)?\s*(?:da|na)\s*une\s+([A-Za-z0-9]+)',
                query_lower
            )
            if top_produtos_une_match:
                limite = int(top_produtos_une_match.group(1))
                une_nome = top_produtos_une_match.group(2).upper()
                result = ("top_produtos_une_especifica", {"limite": limite, "une_nome": une_nome})
                logger.info(f"[OK] CLASSIFICADO COMO: top_produtos_une_especifica (limite: {limite}, une: '{une_nome}')")
                return result

            # ALTA PRIORIDADE: Detectar consultas de VENDAS DE UNE em MÊS específico
            vendas_une_mes_match = re.search(r'vendas.*une\s*([A-Za-z0-9]+).*em\s*(janeiro|fevereiro|março|abril|maio|junho|julho|agosto|setembro|outubro|novembro|dezembro|jan|fev|mar|abr|mai|jun|jul|ago|set|out|nov|dez)', query_lower)
            if vendas_une_mes_match:
                une_nome = vendas_une_mes_match.group(1).upper()
                mes_nome = vendas_une_mes_match.group(2).lower()
                result = ("vendas_une_mes_especifico", {"une_nome": une_nome, "mes_nome": mes_nome})
                logger.info(f"CLASSIFICADO COMO: vendas_une_mes_especifico (une: {une_nome}, mes: {mes_nome})")
                return result

            # ALTA PRIORIDADE: Detectar consultas de VENDAS TOTAIS DE CADA UNE
            vendas_todas_unes_match = re.search(r'vendas?\s*(totais?|total).*(cada\s*unes?|todas?\s*(as\s*)?unes?|por\s*unes?|de\s*todas?\s*(as\s*)?unes?)', query_lower)
            if vendas_todas_unes_match:
                result = ("ranking_vendas_unes", {})
                logger.info(f"CLASSIFICADO COMO: ranking_vendas_unes")
                return result

            # ALTA PRIORIDADE: Detectar consultas de PRODUTO MAIS VENDIDO EM CADA UNE
            produto_cada_une_match = re.search(r'produto\s*mais\s*vendido.*(cada\s*une|em\s*cada\s*une|por\s*une)', query_lower)
            if produto_cada_une_match:
                result = ("produto_mais_vendido_cada_une", {})
                logger.info(f"CLASSIFICADO COMO: produto_mais_vendido_cada_une")
                return result

            # ALTA PRIORIDADE: Detectar consultas de PRODUTO MAIS VENDIDO EM TODAS AS UNES
            produto_todas_unes_match = re.search(r'produto\s*mais\s*vendido.*(todas?\s*unes?|todas?\s*as\s*unes?|em\s*todas?\s*unes?)', query_lower)
            if produto_todas_unes_match:
                result = ("produto_mais_vendido_cada_une", {})
                logger.info(f"CLASSIFICADO COMO: produto_mais_vendido_cada_une (todas as UNEs)")
                return result

            # CORREÇÃO: Detectar GRÁFICO DE BARRAS para produto em TODAS AS UNEs (MAIOR PRIORIDADE)
            product_all_unes_match = re.search(r'(gr[áa]fico.*barras?|barras?).*produto\s*(\d{5,7}).*(todas.*unes?|todas.*filiais?)', query_lower)
            if product_all_unes_match:
                produto_codigo = product_all_unes_match.group(2)
                result = ("produto_vendas_todas_unes", {"produto_codigo": produto_codigo})
                logger.info(f"CLASSIFICADO COMO: produto_vendas_todas_unes (produto: {produto_codigo})")
                return result

            # Detectar GRÁFICO DE BARRAS para produto específico com UNE específica
            product_bar_une_match = re.search(r'(gr[áa]fico.*barras?|barras?).*produto\s*(\d{5,7}).*une\s*(\d+)', query_lower)
            if product_bar_une_match:
                produto_codigo = product_bar_une_match.group(2)
                une_codigo = product_bar_une_match.group(3)
                result = ("produto_vendas_une_barras", {"produto_codigo": produto_codigo, "une_codigo": une_codigo})
                logger.info(f"CLASSIFICADO COMO: produto_vendas_une_barras (produto: {produto_codigo}, une: {une_codigo})")
                return result

            # Detectar EVOLUÇÃO DE VENDAS para um produto específico
            product_evo_match = re.search(r'(gr[áa]fico|evolu[çc][ãa]o|hist[óo]rico|vendas\s+do\s+produto)\s.*?(\b\d{5,7}\b)', query_lower)
            if product_evo_match:
                produto_codigo = product_evo_match.group(2)
                result = ("evolucao_vendas_produto", {"produto_codigo": produto_codigo})
                logger.info(f"CLASSIFICADO COMO: evolucao_vendas_produto (código: {produto_codigo})")
                return result

            # Detectar top produtos por segmento com nome do segmento
            segmento_match = re.search(r'(top\s+\d+\s+produtos|produtos\s+mais\s+vendidos).*(segmento\s+(\w+)|(\w+)\s+segmento)', query_lower)
            if segmento_match:
                segmento_nome = segmento_match.group(3) or segmento_match.group(4)
                result = ("top_produtos_por_segmento", {"segmento": segmento_nome, "limit": 10})
                logger.info(f"CLASSIFICADO COMO: top_produtos_por_segmento (segmento: {segmento_nome})")
                return result

            # PRIORIDADE MÉDIA: Detectar "RANKING" genérico de produtos (DESATIVADO TEMPORARIAMENTE)
            # ranking_produtos_match = re.search(r'(ranking|top)\s*(de\s*)?(produtos|vendas)', query_lower)
            # if ranking_produtos_match and "une" not in query_lower and "segmento" not in query_lower:
            #     # Ranking geral de produtos
            #     limite_match = re.search(r'(\d+)\s*produtos', query_lower)
            #     limite = int(limite_match.group(1)) if limite_match else 10
            #     result = ("top_produtos_por_segmento", {"segmento": "todos", "limit": limite})
            #     logger.info(f"CLASSIFICADO COMO: top_produtos_por_segmento (ranking geral, limit: {limite})")
            #     return result

            # Buscar correspondência direta por keywords
            for keywords, query_type in self.keywords_map.items():
                if keywords in query_lower:
                    # Se for top produtos e não tem segmento específico, assumir que quer de todos
                    if query_type == "top_produtos_por_segmento" and "segmento" not in query_lower:
                        result = (query_type, {"segmento": "todos", "limit": 10})
                        logger.info(f"CLASSIFICADO COMO: {query_type} (todos os segmentos)")
                        return result

                    # Para queries que aceitam produtos específicos, detectar código de produto
                    params = {"matched_keywords": keywords, "user_query": user_query}
                    if query_type in ["evolucao_mes_a_mes", "vendas_produto_une"]:
                        product_match = re.search(r'\b(\d{5,7})\b', user_query)
                        if product_match:
                            params['produto'] = product_match.group(1)
                            logger.info(f"[i] Produto detectado: {params['produto']}")

                    result = (query_type, params)
                    logger.info(f"CLASSIFICADO COMO: {query_type} (keyword: {keywords})")
                    return result

            # Detectar números de produtos (agora com menor prioridade)
            product_match = re.search(r'\b\d{5,7}\b', user_query)
            if product_match:
                produto_codigo = product_match.group()
                result = ("consulta_produto_especifico", {"produto_codigo": produto_codigo})
                logger.info(f"CLASSIFICADO COMO: consulta_produto_especifico (código: {produto_codigo})")
                return result

            # Detectar nomes de UNE (com filtro de palavras comuns)
            # Palavras que NÃO são nomes de UNE
            palavras_ignorar = ['qual', 'da', 'de', 'do', 'na', 'no', 'em', 'por', 'para', 'com', 'sem', 'uma', 'cada', 'toda', 'todo', 'vende', 'mais', 'menos', 'que', 'foram', 'foram', 'teve', 'tem']

            une_match = re.search(r'\b(?:une|filial|loja)\s+([A-Za-z0-9]{2,})\b', query_lower)
            if une_match:
                une_name = une_match.group(1)
                # Só processar se não for palavra comum
                if une_name.lower() not in palavras_ignorar:
                    result = ("consulta_une_especifica", {"une_nome": une_name.upper()})
                    logger.info(f"CLASSIFICADO COMO: consulta_une_especifica (UNE: {une_name})")
                    return result

            # Default para análise geral
            result = ("analise_geral", {"tipo": "geral"})
            logger.warning(f"CLASSIFICADO COMO PADRÃO: analise_geral")
            return result

        except Exception as e:
            duration = (datetime.now() - start_time).total_seconds()
            log_critical_error(e, "classify_intent_direct", {"user_query": user_query})
            logger.error(f"ERRO NA CLASSIFICAÇÃO: {e}")
            return "analise_geral", {"tipo": "geral", "error": str(e)}

        finally:
            duration = (datetime.now() - start_time).total_seconds()
            log_performance_metric("classify_intent", duration, {"query_length": len(user_query)})

    def _get_base_dask_df(self) -> dd.DataFrame:
        """
        Cria DataFrame Dask base COM CACHE para performance máxima.

        Comportamento:
        - 1ª chamada: Carrega do SQL Server ou Parquet (3-5s)
        - Chamadas seguintes: Retorna cache em memória (~0s) ⚡

        Retorna:
            Dask DataFrame lazy com coluna vendas_total calculada.
        """
        # ⚡ CACHE HIT: Retornar DataFrame em cache se disponível
        if self._cached_dask_df is not None:
            logger.debug(f"[CACHE HIT] Usando Dask DataFrame em memória (fonte: {self._cache_source})")
            return self._cached_dask_df

        # 🔄 CACHE MISS: Carregar do fonte (SQL Server ou Parquet)
        logger.info("[CACHE MISS] Carregando dados do adapter...")

        # Verificar fonte atual (SQL Server ou Parquet)
        current_source = "parquet"  # default
        if hasattr(self.parquet_adapter, 'get_status'):
            # É HybridAdapter - verificar fonte ativa
            status = self.parquet_adapter.get_status()
            current_source = status.get('current_source', 'parquet')
            logger.info(f"Fonte de dados ativa: {current_source.upper()}")

        # Obter file_path do Parquet (compatível com ParquetAdapter e HybridAdapter)
        if hasattr(self.parquet_adapter, 'file_path'):
            parquet_path = self.parquet_adapter.file_path
        else:
            raise AttributeError("Adapter não tem file_path definido")

        # Ler parquet com Dask (lazy - não carrega dados em memória ainda!)
        ddf = dd.read_parquet(parquet_path, engine='pyarrow')

        # Criar coluna vendas_total somando meses (mes_01 a mes_12)
        vendas_colunas = [f'mes_{i:02d}' for i in range(1, 13)]
        vendas_colunas_existentes = [col for col in vendas_colunas if col in ddf.columns]

        if vendas_colunas_existentes and 'vendas_total' not in ddf.columns:
            # Converter colunas para numérico de forma lazy
            for col in vendas_colunas_existentes:
                ddf[col] = dd.to_numeric(ddf[col], errors='coerce')

            # Criar vendas_total como soma dos meses
            ddf = ddf.assign(vendas_total=ddf[vendas_colunas_existentes].fillna(0).sum(axis=1))
            logger.debug("Coluna vendas_total criada somando meses (lazy)")

        # Otimização: Definir índice para acelerar filtros por UNE
        if 'une_nome' in ddf.columns:
            logger.info("Otimizando DataFrame com índice em 'une_nome'...")
            ddf = ddf.set_index('une_nome', sorted=False)
            logger.info("Otimização com índice concluída.")

        # ⚡ ARMAZENAR EM CACHE para próximas queries
        self._cached_dask_df = ddf
        self._cache_source = current_source
        logger.info(f"[CACHE STORED] DataFrame Dask armazenado em memória (fonte: {current_source})")

        return ddf

    def clear_cache(self) -> None:
        """
        Limpa o cache do DataFrame Dask.
        Útil após atualização do Parquet ou reconexão do SQL Server.
        """
        self._cached_dask_df = None
        self._cache_source = None
        logger.info("[CACHE CLEARED] Cache do DataFrame limpo - próxima query recarregará dados")

    def execute_direct_query(self, query_type: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Executa consulta direta SEM usar LLM (refatorado para Dask lazy)."""
        start_time = datetime.now()
        logger.info(f"EXECUTANDO CONSULTA: {query_type} | Params: {params}")

        try:
            # Mapear query types antigos para novos
            query_type_aliases = {
                "rotacao_estoque": "rotacao_estoque_avancada"
            }
            query_type = query_type_aliases.get(query_type, query_type)
            if query_type in query_type_aliases.values():
                logger.info(f"ALIAS APLICADO: {list(query_type_aliases.keys())[0]} -> {query_type}")

            # Tratar fallback sem processar dados
            if query_type == 'fallback':
                return {
                    "type": "info",
                    "title": "Consulta não mapeada",
                    "summary": "Esta consulta não está mapeada para execução direta. Use o modo de análise com LLM.",
                    "tokens_used": 0
                }

            # Dispatch para método específico (SEM carregar dados!)
            method_name = f"_query_{query_type}"
            if hasattr(self, method_name):
                logger.info(f"EXECUTANDO MÉTODO: {method_name}")
                method = getattr(self, method_name)
                result = method(params)
            else:
                logger.warning(f"MÉTODO NÃO ENCONTRADO: {method_name} - usando fallback")
                result = self._query_fallback(query_type, params)

            # PROTEÇÃO CRÍTICA: Garantir que result nunca seja None
            if result is None:
                error_msg = f"Método {method_name} retornou None (bug de indentação no return)"
                logger.error(f"BUG CRÍTICO: {error_msg}")
                return {
                    "error": error_msg,
                    "type": "error",
                    "debug": f"Método: {method_name}, Params: {params}"
                }

            # Log do resultado
            success = result.get("type") != "error"
            error_msg = result.get("error") if not success else None

            log_query_attempt(f"{query_type}", query_type, params, success, error_msg)

            if success:
                logger.info(f"CONSULTA SUCESSO: {query_type} - {result.get('title', 'N/A')}")
            else:
                logger.error(f"CONSULTA FALHOU: {query_type} - {error_msg}")

            return result

        except Exception as e:
            error_msg = str(e)
            log_critical_error(e, "execute_direct_query", {"query_type": query_type, "params": params})
            log_query_attempt(f"{query_type}", query_type, params, False, error_msg)
            logger.error(f"ERRO CRÍTICO NA EXECUÇÃO: {query_type} - {error_msg}")
            logger.error(f"TRACEBACK: {traceback.format_exc()}")
            return {"error": error_msg, "type": "error"}

        finally:
            duration = (datetime.now() - start_time).total_seconds()
            log_performance_metric("execute_direct_query", duration, {
                "query_type": query_type,
                "params_count": len(params)
            })

    def _query_produto_mais_vendido(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Query: Produto mais vendido (Dask otimizado - agregar ANTES de compute).

        Params opcionais:
        - segmento: str - Filtrar por segmento específico (ex: "TECIDOS")
        - limite: int - Número de produtos no ranking (padrão: 10)
        """
        ddf = self._get_base_dask_df()

        # Filtrar por segmento se especificado
        segmento = self._safe_get_str(params, 'segmento', '').upper()
        if segmento:
            logger.info(f"[FILTRO] Aplicando filtro de segmento: {segmento}")
            ddf = ddf[ddf['nomesegmento'].str.upper().str.contains(segmento, na=False)]

        limite = self._safe_get_int(params, 'limite', 10)

        # OTIMIZAÇÃO: Agrupar por produto e somar vendas ANTES de compute (lazy)
        # Isso reduz drasticamente o uso de memória (1.1M linhas -> ~50k produtos)
        produtos_agregados = ddf.groupby('codigo').agg({
            'vendas_total': 'sum',
            'nome_produto': 'first',
            'preco_38_percent': 'first',
            'nomesegmento': 'first'
        }).reset_index()

        # Agora sim, compute apenas o top N (muito menor!)
        top_n = produtos_agregados.nlargest(limite, 'vendas_total').compute()

        if top_n.empty:
            msg_erro = f"Nenhum produto encontrado"
            if segmento:
                msg_erro += f" no segmento {segmento}"
            return {"error": msg_erro, "type": "error"}

        produto = top_n.iloc[0]

        # Gerar gráfico com top N
        chart = self.chart_generator.create_product_ranking_chart(
            top_n[['nome_produto', 'vendas_total']],
            limit=limite,
            chart_type='horizontal_bar'
        )

        # Título e resumo adaptados ao filtro
        titulo = "Produto Mais Vendido"
        resumo = f"O produto mais vendido é '{produto['nome_produto']}' com {produto['vendas_total']:,.0f} vendas."

        if segmento:
            titulo += f" - Segmento {segmento}"
            resumo = f"No segmento {segmento}, o produto mais vendido é '{produto['nome_produto']}' com {produto['vendas_total']:,.0f} vendas."

        return {
            "type": "produto_ranking",
            "title": titulo,
            "result": {
                "produto": produto['nome_produto'],
                "vendas": float(produto['vendas_total']),
                "codigo": produto.get('codigo', 'N/A'),
                "segmento": produto.get('nomesegmento', 'N/A')
            },
            "chart": chart,
            "summary": resumo,
            "tokens_used": 0  # ZERO tokens LLM
        }

    def _query_filial_mais_vendeu(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Query: Filial que mais vendeu."""
        ddf = self._get_base_dask_df()
        vendas_por_filial = ddf.groupby('une_nome')['vendas_total'].sum().compute().reset_index()
        vendas_por_filial = vendas_por_filial.sort_values('vendas_total', ascending=False)

        top_filial = vendas_por_filial.iloc[0]

        # Gerar gráfico
        chart = self.chart_generator.create_filial_performance_chart(
            vendas_por_filial.head(10),
            chart_type='bar'
        )

        return {
            "type": "filial_ranking",
            "title": "Filial que Mais Vendeu",
            "result": {
                "filial": top_filial['une_nome'],
                "vendas": float(top_filial['vendas_total'])
            },
            "chart": chart,
            "summary": f"A filial que mais vendeu é '{top_filial['une_nome']}' com {top_filial['vendas_total']:,.0f} vendas.",
            "tokens_used": 0
        }

    def _query_segmento_campao(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Query: Segmento campeão."""
        ddf = self._get_base_dask_df()
        vendas_por_segmento = ddf.groupby('nomesegmento')['vendas_total'].sum().compute().reset_index()
        vendas_por_segmento = vendas_por_segmento.sort_values('vendas_total', ascending=False)

        top_segmento = vendas_por_segmento.iloc[0]

        # Gerar gráfico - usar dados já agregados
        chart = self.chart_generator.create_segmentation_chart(
            vendas_por_segmento, 'nomesegmento', 'vendas_total', chart_type='pie'
        )

        return {
            "type": "segmento_ranking",
            "title": "Segmento Campeão",
            "result": {
                "segmento": top_segmento['nomesegmento'],
                "vendas": float(top_segmento['vendas_total'])
            },
            "chart": chart,
            "summary": f"O segmento campeão é '{top_segmento['nomesegmento']}' com {top_segmento['vendas_total']:,.0f} vendas.",
            "tokens_used": 0
        }

    def _query_produtos_sem_vendas(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Query: Produtos sem movimento."""
        ddf = self._get_base_dask_df()
        produtos_sem_vendas = ddf[ddf['vendas_total'] == 0].compute()
        count_sem_vendas = len(produtos_sem_vendas)

        # Top 10 produtos sem vendas com maior estoque
        if 'estoque_atual' in ddf.columns:
            top_sem_vendas = produtos_sem_vendas[produtos_sem_vendas['estoque_atual'] > 0].nlargest(10, 'estoque_atual')
        else:
            top_sem_vendas = produtos_sem_vendas.head(10)

        # BUGFIX: Return estava dentro do else - movido para fora
        # Também corrigindo 'df' para 'produtos_sem_vendas' ou usar len total do ddf
        total_produtos = len(ddf)  # Total de produtos
        return {
            "type": "produtos_sem_movimento",
            "title": "Produtos Sem Movimento",
            "result": {
                "total_produtos": count_sem_vendas,
                "percentual": round(count_sem_vendas / total_produtos * 100, 1) if total_produtos > 0 else 0,
                "produtos_exemplo": top_sem_vendas[['nome_produto']].head(5).to_dict('records') if not top_sem_vendas.empty else []
            },
            "summary": f"Encontrados {count_sem_vendas} produtos sem movimento ({count_sem_vendas/total_produtos*100:.1f}% do total)." if total_produtos > 0 else "Encontrados 0 produtos sem movimento.",
            "tokens_used": 0
        }

    def _query_estoque_parado(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Query: Estoque parado."""
        ddf = self._get_base_dask_df()
        estoque_parado = ddf[(ddf['vendas_total'] == 0) & (ddf['estoque_atual'] > 0)].compute()
        total_estoque_parado = estoque_parado['estoque_atual'].sum()
        count_produtos = len(estoque_parado)

        return {
            "type": "estoque_parado",
            "title": "Estoque Parado",
            "result": {
                "produtos_parados": count_produtos,
                "quantidade_total": float(total_estoque_parado),
                "valor_estimado": None  # Calculado em consulta específica se necessário
            },
            "summary": f"Identificados {count_produtos} produtos com estoque parado totalizando {total_estoque_parado:,.0f} unidades.",
            "tokens_used": 0
        }

    def _query_consulta_produto_especifico(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Query: Consulta produto específico por código."""
        ddf = self._get_base_dask_df()
        produto_codigo = params.get('produto_codigo')

        try:
            produto_codigo = int(produto_codigo)
        except (ValueError, TypeError):
            return {"error": f"Código de produto inválido: {produto_codigo}", "type": "error"}

        produto_data = ddf[ddf['codigo'] == produto_codigo].compute()

        if produto_data.empty:
            return {"error": f"Produto {produto_codigo} não encontrado", "type": "error"}

        # Se há múltiplas UNEs, agregar
        if len(produto_data) > 1:
            produto_info = {
                "codigo": produto_codigo,
                "nome": produto_data.iloc[0]['nome_produto'],
                "vendas_total": float(produto_data['vendas_total'].sum()),
                "unes": len(produto_data),
                "preco": float(produto_data.iloc[0].get('preco_38_percent', 0))
            }
        else:
            produto = produto_data.iloc[0]
            produto_info = {
                "codigo": produto_codigo,
                "nome": produto['nome_produto'],
                "vendas_total": float(produto['vendas_total']),
                "une": produto.get('une_nome', 'N/A'),
                "preco": float(produto.get('preco_38_percent', 0))
            }

        # BUGFIX: Return estava dentro do else - movido para fora
        return {
            "type": "produto_especifico",
            "title": f"Produto {produto_codigo}",
            "result": produto_info,
            "summary": f"Produto '{produto_info['nome']}' - Vendas: {produto_info['vendas_total']:,.0f} - Preço: R$ {produto_info['preco']:.2f}",
            "tokens_used": 0
        }

    def _query_preco_produto_une_especifica(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Query: Preço de produto específico em UNE específica."""
        ddf = self._get_base_dask_df()
        produto_codigo = params.get('produto_codigo')
        une_nome = params.get('une_nome')

        try:
            produto_codigo = int(produto_codigo)
        except (ValueError, TypeError):
            return {"error": f"Código de produto inválido: {produto_codigo}", "type": "error"}

        # Verificar se produto existe na UNE específica
        produto_une_data = ddf[(ddf['codigo'] == produto_codigo) & (ddf['une_nome'] == une_nome)].compute()

        if produto_une_data.empty:
            # Verificar se produto existe em outras UNEs
            produto_geral = ddf[ddf['codigo'] == produto_codigo].compute()
            if produto_geral.empty:
                return {"error": f"Produto {produto_codigo} não encontrado no sistema", "type": "error"}
            else:
                unes_disponiveis = produto_geral['une_nome'].unique()
                return {
                    "error": f"Produto {produto_codigo} não encontrado na UNE {une_nome}",
                    "type": "error",
                    "suggestion": f"Produto disponível nas UNEs: {', '.join(unes_disponiveis)}"
                }

        produto = produto_une_data.iloc[0]
        preco = float(produto.get('preco_38_percent', 0))

        # Calcular vendas se disponível
        vendas_meses = [f'mes_{i:02d}' for i in range(1, 13)]
        available_vendas = [col for col in vendas_meses if col in ddf.columns]
        vendas_total = 0
        if available_vendas:
            vendas_total = float(produto[available_vendas].sum())

        produto_info = {
            "codigo": produto_codigo,
            "nome": produto['nome_produto'],
            "une_codigo": produto['une'],
            "une_nome": produto['une_nome'],
            "preco": preco,
            "vendas_total": vendas_total,
            "estoque": float(produto.get('estoque_atual', 0)) if 'estoque_atual' in produto else None
        }

        return {
            "type": "preco_produto_une",
            "title": f"Preço do Produto {produto_codigo} na UNE {une_nome}",
            "result": produto_info,
            "summary": f"Produto '{produto_info['nome']}' na UNE {une_nome}: R$ {preco:.2f}",
            "tokens_used": 0
        }

    def _query_top_produtos_une_especifica(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Query: Top N produtos mais vendidos em UNE específica (OTIMIZADO - agregação lazy)."""
        ddf = self._get_base_dask_df()
        limite = self._safe_get_int(params, 'limite', 10)
        une_nome = self._safe_get_str(params, 'une_nome', '').upper()

        logger.info(f"[>] Buscando top {limite} produtos na UNE: '{une_nome}'")

        # Aplicar filtros no Dask (lazy) ANTES do compute
        une_upper = une_nome.strip()
        ddf_filtered = ddf[
            (ddf['une_nome'].str.upper() == une_upper) |
            (ddf['une'].astype(str) == une_upper)
        ]

        # BUGFIX: Removida verificação com head(1) que causava MemoryError
        # Vamos verificar apenas no resultado final após agregação
        # O Dask otimiza queries vazias automaticamente

        # Se input é numérico, tentar também como código UNE inteiro
        if une_upper.isdigit():
            try:
                ddf_filtered_int = ddf[ddf['une'] == int(une_upper)]
                # Combinar filtros: nome OU código
                ddf_filtered = ddf_filtered | ddf_filtered_int
            except:
                pass



        # OTIMIZAÇÃO CRÍTICA: Agregar ANTES de compute (lazy operations)
        # 1. Filtrar vendas > 0 (lazy)
        # 2. Agrupar por produto (lazy) - reduz de 50k linhas para ~5k produtos
        # 3. Só então computar o top N (muito menor!)

        ddf_filtered = ddf_filtered[ddf_filtered['vendas_total'] > 0]

        # Agrupar por produto (lazy - não computa ainda!)
        produtos_agrupados = ddf_filtered.groupby('codigo').agg({
            'vendas_total': 'sum',
            'nome_produto': 'first',
            'preco_38_percent': 'first',
            'nomesegmento': 'first'
        }).reset_index()

        # Ordenar e pegar top N (lazy)
        top_produtos_lazy = produtos_agrupados.nlargest(limite, 'vendas_total')

        # SÓ AGORA compute() - apenas top N produtos (ex: 10 linhas)
        top_produtos = top_produtos_lazy.compute()

        # Validação APÓS agregação (não causa MemoryError)
        if top_produtos.empty:
            # Verificar se a UNE existe no dataset para dar uma mensagem mais útil
            une_check_df = ddf[
                (ddf['une_nome'].str.upper() == une_upper) |
                (ddf['une'].astype(str) == une_upper)
            ]
            # head() em dask retorna um pandas DF, então não precisa de compute()
            if une_check_df.head(1).empty:
                # A UNE realmente não existe
                unes_disponiveis = sorted(ddf['une_nome'].unique().compute())
                suggestions = [u for u in unes_disponiveis if une_upper[:2] in u.upper()][:5]
                error_message = f"A UNE '{une_nome}' não foi encontrada."
                if suggestions:
                    error_message += f" Talvez você quisesse dizer uma destas: {', '.join(suggestions)}?"
                
                return {
                    "error": error_message,
                    "type": "error",
                    "suggestion": f"UNEs disponíveis para consulta: {', '.join(unes_disponiveis[:10])}..."
                }
            else:
                # A UNE existe, mas não tem produtos com vendas
                return {
                    "error": f"Nenhum produto com vendas encontrado na UNE {une_nome}",
                    "type": "error"
                }

        # Preparar dados para gráfico
        x_data = [produto['nome_produto'][:50] + '...' if len(produto['nome_produto']) > 50 else produto['nome_produto']
                  for _, produto in top_produtos.iterrows()]
        y_data = [float(produto['vendas_total']) for _, produto in top_produtos.iterrows()]

        # Cores baseadas na performance
        max_vendas = max(y_data) if y_data else 1
        colors = []
        for valor in y_data:
            if valor >= max_vendas * 0.7:
                colors.append('#2E8B57')  # Verde escuro para top performers
            elif valor >= max_vendas * 0.3:
                colors.append('#FFD700')  # Dourado para performance média
            else:
                colors.append('#CD5C5C')  # Vermelho suave para baixa performance

        # Criar dados do gráfico
        chart_data = {
            "x": x_data,
            "y": y_data,
            "type": "bar",
            "colors": colors,
            "show_values": True,
            "height": max(400, min(800, len(x_data) * 50)),
            "margin": {"l": 80, "r": 80, "t": 100, "b": 120}
        }

        # Preparar lista de produtos para resultado
        produtos_list = []
        for _, produto in top_produtos.iterrows():
            produtos_list.append({
                "codigo": int(produto['codigo']),
                "nome": produto['nome_produto'],
                "vendas": float(produto['vendas_total']),
                "preco": float(produto.get('preco_38_percent', 0)),
                "segmento": produto.get('nomesegmento', 'N/A')
            })

        total_vendas = sum(y_data)

        return {
            "type": "chart",
            "title": f"Top {limite} Produtos Mais Vendidos - UNE {une_nome}",
            "result": {
                "chart_data": chart_data,
                "une_nome": une_nome,
                "limite": limite,
                "produtos": produtos_list,
                "total_vendas": total_vendas,
                "total_produtos_une": len(top_produtos)
            },
            "summary": f"Top {limite} produtos mais vendidos na UNE {une_nome}. Total de vendas: {total_vendas:,.0f} unidades.",
            "tokens_used": 0
        }

    def _query_vendas_une_mes_especifico(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Query: Vendas de UNE específica em mês específico."""
        ddf = self._get_base_dask_df()
        une_nome = params.get('une_nome')
        mes_nome = params.get('mes_nome', '').lower()

        # Mapear nome do mês para coluna
        meses_map = {
            'janeiro': 'mes_01', 'jan': 'mes_01',
            'fevereiro': 'mes_02', 'fev': 'mes_02',
            'março': 'mes_03', 'mar': 'mes_03',
            'abril': 'mes_04', 'abr': 'mes_04',
            'maio': 'mes_05', 'mai': 'mes_05',
            'junho': 'mes_06', 'jun': 'mes_06',
            'julho': 'mes_07', 'jul': 'mes_07',
            'agosto': 'mes_08', 'ago': 'mes_08',
            'setembro': 'mes_09', 'set': 'mes_09',
            'outubro': 'mes_10', 'out': 'mes_10',
            'novembro': 'mes_11', 'nov': 'mes_11',
            'dezembro': 'mes_12', 'dez': 'mes_12'
        }

        coluna_mes = meses_map.get(mes_nome)
        if not coluna_mes:
            return {"error": f"Mês '{mes_nome}' não reconhecido", "type": "error"}

        # Verificar se UNE existe
        une_data = ddf[ddf['une_nome'] == une_nome].compute()
        if une_data.empty:
            unes_disponiveis = sorted(ddf['une_nome'].unique()).compute()
            suggestions = [u for u in unes_disponiveis if une_nome[:2].lower() in u.lower()][:3]
            if not suggestions:
                suggestions = unes_disponiveis[:5]

                return {
                "error": f"UNE {une_nome} não encontrada",
                "type": "error",
                "suggestion": f"Você quis dizer: {', '.join(suggestions)}?"
            }

        # Calcular total de vendas da UNE no mês específico
        # Check é feito durante compute, não antes
        # if coluna_mes not in ddf.columns:
        #     return {"error": f"Dados de vendas para {mes_nome} não disponíveis", "type": "error"}

        total_vendas_mes = float(une_data[coluna_mes].sum())
        total_produtos = len(une_data[une_data[coluna_mes] > 0])

        return {
            "type": "vendas_une_mes",
            "title": f"Vendas da UNE {une_nome} em {mes_nome.title()}",
            "result": {
                "une_nome": une_nome,
                "mes_nome": mes_nome.title(),
                "total_vendas": total_vendas_mes,
                "total_produtos": total_produtos,
                "media_por_produto": total_vendas_mes / total_produtos if total_produtos > 0 else 0
            },
            "summary": f"UNE {une_nome} vendeu {total_vendas_mes:,.0f} unidades em {mes_nome.title()}.",
            "tokens_used": 0
        }

    def _query_ranking_vendas_unes(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Query: Ranking de vendas totais por UNE."""
        ddf = self._get_base_dask_df()
        # Agrupar por UNE e somar todas as vendas
        vendas_por_une = ddf.groupby(['une', 'une_nome']).agg({
            'vendas_total': 'sum'
        }).compute().reset_index()

        # Ordenar por vendas totais (decrescente)
        vendas_por_une = vendas_por_une.sort_values('vendas_total', ascending=False)

        # Preparar dados para gráfico
        x_data = [f"{row['une_nome']}\n(UNE {row['une']})" for _, row in vendas_por_une.iterrows()]
        y_data = [float(row['vendas_total']) for _, row in vendas_por_une.iterrows()]

        # Cores baseadas na performance
        max_vendas = max(y_data) if y_data else 1
        colors = []
        for valor in y_data:
            if valor >= max_vendas * 0.7:
                colors.append('#2E8B57')  # Verde escuro para top performers
            elif valor >= max_vendas * 0.3:
                colors.append('#FFD700')  # Dourado para performance média
            else:
                colors.append('#CD5C5C')  # Vermelho suave para baixa performance

        # Criar dados do gráfico
        chart_data = {
            "x": x_data,
            "y": y_data,
            "type": "bar",
            "colors": colors,
            "show_values": True,
            "height": max(400, min(800, len(x_data) * 60)),
            "margin": {"l": 80, "r": 80, "t": 100, "b": 120}
        }

        total_vendas_geral = sum(y_data)

        return {
            "type": "chart",
            "title": "Ranking de Vendas por UNE",
            "result": {
                "chart_data": chart_data,
                "unes": len(vendas_por_une),
                "total_vendas": total_vendas_geral,
                "melhor_une": vendas_por_une.iloc[0]['une_nome'] if len(vendas_por_une) > 0 else None,
                "vendas_melhor": vendas_por_une.iloc[0]['vendas_total'] if len(vendas_por_une) > 0 else 0
            },
            "summary": f"Ranking de {len(vendas_por_une)} UNEs. Melhor: {vendas_por_une.iloc[0]['une_nome'] if len(vendas_por_une) > 0 else 'N/A'} com {vendas_por_une.iloc[0]['vendas_total'] if len(vendas_por_une) > 0 else 0:,.0f} vendas.",
            "tokens_used": 0
        }

    def _query_produto_mais_vendido_cada_une(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Query: Produto mais vendido em cada UNE (OTIMIZADO - sem loop)."""
        ddf = self._get_base_dask_df()

        # OTIMIZAÇÃO CRÍTICA: Usar groupby + idxmax ANTES de compute (lazy)
        # Agrupar por UNE e produto, somar vendas
        vendas_por_une_produto = ddf.groupby(['une_nome', 'codigo']).agg({
            'vendas_total': 'sum',
            'nome_produto': 'first'
        }).reset_index()

        # Computar só os dados agregados (muito menor)
        vendas_df = vendas_por_une_produto.compute()

        # Para cada UNE, pegar produto com maior vendas (pandas é rápido aqui)
        idx = vendas_df.groupby('une_nome')['vendas_total'].idxmax()
        produtos_por_une_df = vendas_df.loc[idx]

        # Converter para lista de dicts
        produtos_por_une = [{
            'une_nome': row['une_nome'],
            'produto_codigo': row['codigo'],
            'produto_nome': row['nome_produto'],
            'vendas_total': row['vendas_total']
        } for _, row in produtos_por_une_df.iterrows()]

        # Ordenar por vendas (descendente)
        produtos_por_une.sort(key=lambda x: x['vendas_total'], reverse=True)

        # Preparar dados para gráfico com nome do produto
        x_data = [f"UNE {item['une_nome']}\n{item['produto_nome'][:30]}{'...' if len(item['produto_nome']) > 30 else ''}" for item in produtos_por_une]
        y_data = [float(item['vendas_total']) for item in produtos_por_une]

        # Cores baseadas na performance
        max_vendas = max(y_data) if y_data else 1
        colors = []
        for valor in y_data:
            if valor >= max_vendas * 0.7:
                colors.append('#2E8B57')  # Verde escuro para top performers
            elif valor >= max_vendas * 0.3:
                colors.append('#FFD700')  # Dourado para performance média
            else:
                colors.append('#CD5C5C')  # Vermelho suave para baixa performance

        # Criar dados do gráfico
        chart_data = {
            "x": x_data,
            "y": y_data,
            "type": "bar",
            "colors": colors,
            "show_values": True,
            "height": max(400, min(800, len(x_data) * 60)),
            "margin": {"l": 80, "r": 80, "t": 100, "b": 120}
        }

        return {
            "type": "chart",
            "title": "Produto Mais Vendido em Cada UNE",
            "result": {
                "chart_data": chart_data,
                "produtos_por_une": produtos_por_une,
                "total_unes": len(produtos_por_une),
                "melhor_produto_geral": produtos_por_une[0] if produtos_por_une else None
            },
            "summary": f"Produtos mais vendidos em {len(produtos_por_une)} UNEs. Líder geral: {produtos_por_une[0]['produto_nome'] if produtos_por_une else 'N/A'} na UNE {produtos_por_une[0]['une_nome'] if produtos_por_une else 'N/A'} com {produtos_por_une[0]['vendas_total'] if produtos_por_une else 0:,.0f} vendas.",
            "tokens_used": 0
        }

    def _query_top_produtos_segmento_une(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Query: Top N produtos em segmento específico E UNE específica."""
        ddf = self._get_base_dask_df()
        limite = self._safe_get_int(params, 'limite', 10)
        segmento_nome = self._safe_get_str(params, 'segmento', '').upper()
        une_nome = self._safe_get_str(params, 'une_nome', '').upper()

        logger.info(f"[>] Buscando top {limite} produtos no segmento '{segmento_nome}' na UNE: '{une_nome}'")

        # Primeiro filtrar por segmento (lazy)
        segmento_upper = segmento_nome.strip()
        ddf_segmento = ddf[ddf['nomesegmento'].str.upper() == segmento_upper]

        # Verificar se segmento existe
        check_seg = ddf_segmento.head(1).compute()
        if check_seg.empty:
            segmentos_disponiveis = sorted(ddf['nomesegmento'].unique().compute())[:10]
            return {
                "error": f"Segmento '{segmento_nome}' não encontrado",
                "type": "error",
                "suggestion": f"Segmentos disponíveis: {', '.join(segmentos_disponiveis)}"
            }

        # Agora filtrar por UNE no subset do segmento (lazy)
        une_upper = une_nome.strip()
        ddf_filtered = ddf_segmento[
            (ddf_segmento['une_nome'].str.upper() == une_upper) |
            (ddf_segmento['une'].astype(str) == une_upper)
        ]

        # Se input numérico, tentar como int
        if une_upper.isdigit():
            try:
                ddf_filtered_int = ddf_segmento[ddf_segmento['une'] == int(une_upper)]
                check_df = ddf_filtered.head(1).compute()
                if check_df.empty:
                    ddf_filtered = ddf_filtered_int
            except:
                pass

        # Compute apenas dados duplamente filtrados (muito pequeno)
        une_data = ddf_filtered.compute()

        # Tratamento de UNE não encontrada
        if une_data.empty:
            unes_disponiveis = sorted(ddf_segmento['une_nome'].unique().compute())
            suggestions = [u for u in unes_disponiveis if une_nome[:2].lower() in u.lower()][:3]
            if not suggestions:
                suggestions = unes_disponiveis[:5]

            logger.error(f"[X] UNE '{une_nome}' nao encontrada. Sugestoes: {suggestions}")
            return {
                "error": f"UNE '{une_nome}' não encontrada",
                "type": "error",
                "suggestion": f"Você quis dizer: {', '.join(suggestions)}? UNEs disponíveis: {', '.join(unes_disponiveis[:10])}"
            }

        logger.info(f"[OK] UNE encontrada: {len(une_data)} registros")

        # Dados já filtrados por ambos os critérios
        df_filtered = une_data

        if df_filtered.empty:
            return {
                "error": f"Nenhum produto encontrado no segmento '{segmento_nome}' na UNE '{une_nome}'",
                "type": "error"
            }

        logger.info(f"[OK] Segmento filtrado: {len(df_filtered)} produtos na UNE")

        # Agrupar por produto e somar vendas
        produtos_vendas = df_filtered.groupby('codigo').agg(
            vendas_total=('vendas_total', 'sum'),
            nome_produto=('nome_produto', 'first'),
            nomesegmento=('nomesegmento', 'first'),
            preco_38_percent=('preco_38_percent', 'first')
        ).reset_index()

        # Pegar top N produtos
        top_produtos = produtos_vendas.nlargest(limite, 'vendas_total')

        if top_produtos.empty:
            return {"error": f"Nenhum produto com vendas no segmento '{segmento}' na UNE '{une_nome}'", "type": "error"}

        # Preparar dados para o gráfico
        x_data = [produto['nome_produto'][:50] for _, produto in top_produtos.iterrows()]  # Limitar nome
        y_data = [float(produto['vendas_total']) for _, produto in top_produtos.iterrows()]

        chart_data = {
            "x": x_data,
            "y": y_data,
            "type": "bar",
            "show_values": True
        }

        # Preparar lista de produtos
        produtos_list = []
        for _, produto in top_produtos.iterrows():
            produtos_list.append({
                "codigo": int(produto['codigo']),
                "nome": produto['nome_produto'],
                "vendas": float(produto['vendas_total']),
                "segmento": produto['nomesegmento'],
                "preco": float(produto.get('preco_38_percent', 0))
            })

        segmento_real = top_produtos.iloc[0]['nomesegmento']
        vendas_total = sum(y_data)
        lider = produtos_list[0]

        return {
            "type": "chart",
            "title": f"Top {limite} Produtos - {segmento_real} na UNE {une_nome}",
            "result": {
                "chart_data": chart_data,
                "produtos": produtos_list,
                "segmento": segmento_real,
                "une": une_nome,
                "total_produtos": len(produtos_list),
                "vendas_total": vendas_total
            },
            "summary": f"Top {limite} produtos em '{segmento_real}' na UNE {une_nome}. Líder: {lider['nome']} ({lider['vendas']:,.0f} vendas)",
            "tokens_used": 0
        }

    def _query_evolucao_vendas_produto(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Query: Evolução de vendas para um produto específico."""
        ddf = self._get_base_dask_df()
        produto_codigo = params.get('produto_codigo')
        try:
            produto_codigo = int(produto_codigo)
        except (ValueError, TypeError):
            return {"error": f"Código de produto inválido: {produto_codigo}", "type": "error"}

        produto_data = ddf[ddf['codigo'] == produto_codigo].compute()
        if produto_data.empty:
            return {"error": f"Produto {produto_codigo} não encontrado", "type": "error"}

        produto_nome = produto_data.iloc[0]['nome_produto']

        # Regex para encontrar colunas de vendas mensais (ex: 'mai-23', 'jun/23', 'mes_01', 'jan-24')
        sales_cols_re = re.compile(r'^(?:[a-z]{3}[-/]\d{2,4}|mes_\d{1,2})$', re.IGNORECASE)
        sales_cols = [col for col in ddf.columns if sales_cols_re.match(col)]

        if not sales_cols:
            return {"error": "Nenhuma coluna de vendas mensais encontrada no formato esperado.", "type": "error"}

        # Mapear nomes de meses para números
        month_map = {
            'jan': 1, 'fev': 2, 'mar': 3, 'abr': 4, 'mai': 5, 'jun': 6,
            'jul': 7, 'ago': 8, 'set': 9, 'out': 10, 'nov': 11, 'dez': 12
        }

        sales_timeseries = []
        product_sales_series = produto_data[sales_cols].iloc[0]

        for col_name, sales_value in product_sales_series.items():
            try:
                clean_col = col_name.lower().replace('/', '-')
                
                if clean_col.startswith('mes_'):
                    # Processar colunas 'mes_xx' sem ano específico
                    mes_num = int(clean_col.split('_')[1])
                    sales_timeseries.append({
                        "date": datetime(2023, mes_num, 1),  # Ano padrão 2023
                        "mes": f"{mes_num:02d}/2023",
                        "vendas": float(sales_value) if pd.notna(sales_value) else 0
                    })
                    continue

                month_str, year_str = clean_col.split('-')
                month = month_map[month_str[:3]]
                year = int(year_str)
                if year < 100: # Formato '23' -> 2023
                    year += 2000
                
                sales_timeseries.append({
                    "date": datetime(year, month, 1),
                    "mes": f"{month:02d}/{year}",
                    "vendas": float(sales_value) if pd.notna(sales_value) else 0
                })
            except (ValueError, KeyError) as e:
                logger.warning(f"Não foi possível processar a coluna de data '{col_name}': {e}")
                continue
        
        if not sales_timeseries:
            return {"error": "Não foi possível extrair dados de série temporal de vendas para o produto.", "type": "error"}

        # Ordenar por data
        sales_timeseries.sort(key=lambda x: x['date'])

        total_vendas = sum(item['vendas'] for item in sales_timeseries)

        return {
            "type": "evolucao_vendas_produto",
            "title": f"Evolução de Vendas - {produto_nome} ({produto_codigo})",
            "result": {
                "produto_codigo": produto_codigo,
                "produto_nome": produto_nome,
                "vendas_timeseries": sales_timeseries,
                "total_vendas": total_vendas
            },
            "summary": f"O produto '{produto_nome}' teve um total de {total_vendas:,.0f} vendas no período analisado.",
            "tokens_used": 0
        }

    def _query_produto_vendas_une_barras(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Query: Gráfico de barras para produto específico em UNE específica."""
        ddf = self._get_base_dask_df()
        produto_codigo = params.get('produto_codigo')
        une_codigo = params.get('une_codigo')

        try:
            produto_codigo = int(produto_codigo)
            une_codigo = int(une_codigo)
        except (ValueError, TypeError):
            return {"error": f"Código de produto ou UNE inválido: {produto_codigo}, {une_codigo}", "type": "error"}

        # Verificar se produto existe
        produto_data = ddf[ddf['codigo'] == produto_codigo].compute()
        if produto_data.empty:
            return {"error": f"Produto {produto_codigo} não encontrado", "type": "error"}

        # Verificar se UNE existe
        une_data = ddf[ddf['une'] == une_codigo].compute()
        if une_data.empty:
            unes_disponiveis = sorted(ddf['une'].unique()).compute()
            return {
                "error": f"UNE {une_codigo} não encontrada. UNEs disponíveis: {unes_disponiveis[:10]}...",
                "type": "error"
            }

        # Verificar se produto existe na UNE específica
        produto_une_data = ddf[(ddf['codigo'] == produto_codigo) & (ddf['une'] == une_codigo)].compute()
        if produto_une_data.empty:
            produto_unes = produto_data['une'].unique()
            return {
                "error": f"Produto {produto_codigo} não está disponível na UNE {une_codigo}. Está disponível nas UNEs: {list(produto_unes)}",
                "type": "error"
            }

        produto_nome = produto_data.iloc[0]['nome_produto']
        une_nome = produto_une_data.iloc[0].get('une_nome', f'UNE {une_codigo}')

        # Extrair vendas por mês
        vendas_meses = [f'mes_{i:02d}' for i in range(1, 13)]
        vendas_data = produto_une_data[vendas_meses].iloc[0]

        # Criar dados para gráfico de barras
        chart_data = {
            "x": [f"Mês {i:02d}" for i in range(1, 13)],
            "y": [float(vendas_data[col]) if pd.notna(vendas_data[col]) else 0 for col in vendas_meses],
            "type": "bar"
        }

        total_vendas = sum(chart_data["y"])

        return {
            "type": "chart",
            "title": f"Vendas Mensais - {produto_nome} na {une_nome}",
            "result": {
                "chart_data": chart_data,
                "produto_codigo": produto_codigo,
                "produto_nome": produto_nome,
                "une_codigo": une_codigo,
                "une_nome": une_nome,
                "total_vendas": total_vendas
            },
            "summary": f"Gráfico de barras gerado para {produto_nome} (código {produto_codigo}) na {une_nome}. Total de vendas: {total_vendas:,.0f} unidades.",
            "tokens_used": 0
        }

    def _query_produto_vendas_todas_unes(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Query: Gráfico de barras para produto específico em todas as UNEs."""
        ddf = self._get_base_dask_df()
        produto_codigo = params.get('produto_codigo')

        try:
            produto_codigo = int(produto_codigo)
        except (ValueError, TypeError):
            return {"error": f"Código de produto inválido: {produto_codigo}", "type": "error"}

        # Verificar se produto existe
        produto_data = ddf[ddf['codigo'] == produto_codigo].compute()
        if produto_data.empty:
            return {"error": f"Produto {produto_codigo} não encontrado", "type": "error"}

        produto_nome = produto_data.iloc[0]['nome_produto']

        # Agrupar por UNE e somar vendas
        vendas_meses = [f'mes_{i:02d}' for i in range(1, 13)]
        vendas_por_une = produto_data.groupby(['une', 'une_nome'])[vendas_meses].sum()
        vendas_por_une['vendas_total'] = vendas_por_une.sum(axis=1)

        # Ordenar por vendas totais (decrescente)
        vendas_por_une = vendas_por_une.sort_values('vendas_total', ascending=False)

        # Preparar dados para gráfico com melhorias visuais
        if len(vendas_por_une) > 20:
            # Se muitas UNEs, pegar apenas as top 20 para evitar gráfico muito largo
            vendas_por_une_top = vendas_por_une.head(20)
            titulo_extra = f" (Top 20 de {len(vendas_por_une)} UNEs)"
        else:
            vendas_por_une_top = vendas_por_une
            titulo_extra = ""

        # Criar labels melhorados
        x_labels = []
        y_values = []
        for (une_codigo, une_nome), row in vendas_por_une_top.iterrows():
            label = f"{une_nome}\n(UNE {une_codigo})"
            x_labels.append(label)
            y_values.append(float(row['vendas_total']))

        # Cores baseadas na performance (verde para altas vendas, amarelo para médias, vermelho para baixas)
        max_vendas = max(y_values) if y_values else 1
        colors = []
        for valor in y_values:
            if valor >= max_vendas * 0.7:
                colors.append('#2E8B57')  # Verde escuro para top performers
            elif valor >= max_vendas * 0.3:
                colors.append('#FFD700')  # Dourado para performance média
            else:
                colors.append('#CD5C5C')  # Vermelho suave para baixa performance

        total_vendas = sum(y_values)

        # Criar dados otimizados para gráfico
        chart_data = {
            "x": x_labels,
            "y": y_values,
            "type": "bar",
            "colors": colors,
            "show_values": True,  # Mostrar valores nas barras
            "height": max(400, min(800, len(x_labels) * 40)),  # Altura responsiva
            "margin": {"l": 80, "r": 80, "t": 100, "b": 120}  # Margens maiores para labels
        }

        return {
            "type": "chart",
            "title": f"Vendas por UNE - {produto_nome}{titulo_extra}",
            "result": {
                "chart_data": chart_data,
                "produto_codigo": produto_codigo,
                "produto_nome": produto_nome,
                "total_unes": len(vendas_por_une),
                "unes_exibidas": len(vendas_por_une_top),
                "total_vendas": total_vendas,
                "maior_une": vendas_por_une.index[0] if len(vendas_por_une) > 0 else None,
                "maior_vendas": vendas_por_une.iloc[0]['vendas_total'] if len(vendas_por_une) > 0 else 0
            },
            "summary": f"Gráfico de barras gerado para {produto_nome} (código {produto_codigo}) em {len(vendas_por_une_top)} UNEs. Total de vendas: {total_vendas:,.0f} unidades.",
            "tokens_used": 0
        }

    def _query_ranking_geral(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Ranking genérico - detecta automaticamente tipo (produtos/UNEs/segmentos)
        baseado na query original do usuário.
        """
        ddf = self._get_base_dask_df()
        user_query = params.get('user_query', params.get('matched_keywords', '')).lower()
        limite = self._safe_get_int(params, 'limite', 10)

        logger.info(f"[>] Processando ranking_geral - query: '{user_query[:50]}'")

        # Detectar tipo de ranking
        if any(word in user_query for word in ['produto', 'item', 'mercadoria']):
            return self._ranking_produtos(limite)
        elif any(word in user_query for word in ['une', 'filial', 'loja', 'unidade']):
            return self._ranking_unes(limite)
        elif any(word in user_query for word in ['segmento', 'categoria']):
            return self._ranking_segmentos(limite)
        else:
            # Default: ranking de produtos
            logger.info("[i] Tipo não detectado, usando ranking de produtos como padrão")
            return self._ranking_produtos(limite)

    def _ranking_produtos(self, limite: int = 10) -> Dict[str, Any]:
        """Ranking de produtos mais vendidos."""
        ddf = self._get_base_dask_df()
        # Agrupar por produto e somar vendas
        produtos = ddf.groupby('codigo').agg({
            'vendas_total': 'sum',
            'nome_produto': 'first',
            'preco_38_percent': 'first',
            'nomesegmento': 'first'
        }).compute().reset_index()

        # Top N
        top_produtos = produtos.nlargest(limite, 'vendas_total')

        if top_produtos.empty:
            return {"error": "Nenhum produto encontrado", "type": "error"}

        # Preparar chart
        chart_data = {
            "x": [p['nome_produto'][:40] for _, p in top_produtos.iterrows()],
            "y": [float(p['vendas_total']) for _, p in top_produtos.iterrows()],
            "type": "bar",
            "show_values": True
        }

        produtos_list = [{
            "codigo": int(p['codigo']),
            "nome": p['nome_produto'],
            "vendas": float(p['vendas_total']),
            "segmento": p['nomesegmento']
        } for _, p in top_produtos.iterrows()]

        return {
            "type": "chart",
            "title": f"Top {limite} Produtos Mais Vendidos",
            "result": {
                "chart_data": chart_data,
                "produtos": produtos_list,
                "total_produtos": len(produtos_list)
            },
            "summary": f"Top {len(produtos_list)} produtos. Líder: {produtos_list[0]['nome']} ({produtos_list[0]['vendas']:,.0f} vendas)",
            "tokens_used": 0
        }

    def _ranking_unes(self, limite: int = 10) -> Dict[str, Any]:
        """Ranking de UNEs por volume de vendas."""
        ddf = self._get_base_dask_df()
        # Agrupar por UNE
        unes = ddf.groupby('une_nome').agg({
            'vendas_total': 'sum',
            'une': 'first'
        }).compute().reset_index()

        # Top N
        top_unes = unes.nlargest(limite, 'vendas_total')

        if top_unes.empty:
            return {"error": "Nenhuma UNE encontrada", "type": "error"}

        # Preparar chart
        chart_data = {
            "x": [une['une_nome'] for _, une in top_unes.iterrows()],
            "y": [float(une['vendas_total']) for _, une in top_unes.iterrows()],
            "type": "bar",
            "show_values": True
        }

        unes_list = [{
            "une_codigo": int(une['une']),
            "une_nome": une['une_nome'],
            "vendas": float(une['vendas_total'])
        } for _, une in top_unes.iterrows()]

        return {
            "type": "chart",
            "title": f"Top {limite} UNEs por Volume de Vendas",
            "result": {
                "chart_data": chart_data,
                "unes": unes_list,
                "total_unes": len(unes_list)
            },
            "summary": f"Top {len(unes_list)} UNEs. Líder: {unes_list[0]['une_nome']} ({unes_list[0]['vendas']:,.0f} vendas)",
            "tokens_used": 0
        }

    def _ranking_segmentos(self, limite: int = 10) -> Dict[str, Any]:
        """Ranking de segmentos por volume de vendas."""
        ddf = self._get_base_dask_df()
        # Agrupar por segmento
        segmentos = ddf.groupby('nomesegmento').agg({
            'vendas_total': 'sum'
        }).compute().reset_index()

        # Top N
        top_segmentos = segmentos.nlargest(limite, 'vendas_total')

        if top_segmentos.empty:
            return {"error": "Nenhum segmento encontrado", "type": "error"}

        # Preparar chart
        chart_data = {
            "x": [seg['nomesegmento'] for _, seg in top_segmentos.iterrows()],
            "y": [float(seg['vendas_total']) for _, seg in top_segmentos.iterrows()],
            "type": "bar",
            "show_values": True
        }

        segmentos_list = [{
            "segmento": seg['nomesegmento'],
            "vendas": float(seg['vendas_total'])
        } for _, seg in top_segmentos.iterrows()]

        return {
            "type": "chart",
            "title": f"Top {limite} Segmentos por Volume de Vendas",
            "result": {
                "chart_data": chart_data,
                "segmentos": segmentos_list,
                "total_segmentos": len(segmentos_list)
            },
            "summary": f"Top {len(segmentos_list)} segmentos. Líder: {segmentos_list[0]['segmento']} ({segmentos_list[0]['vendas']:,.0f} vendas)",
            "tokens_used": 0
        }

    def _query_consulta_une_especifica(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Consulta informações sobre uma UNE específica.
        Retorna vendas totais, produtos mais vendidos, segmentos, etc.
        """
        ddf = self._get_base_dask_df()
        une_nome = self._safe_get_str(params, 'une_nome', '').upper()

        logger.info(f"[>] Consultando informações da UNE: '{une_nome}'")

        if not une_nome:
            return {"error": "Nome da UNE não especificado", "type": "error"}

        # Aplicar filtros no Dask (lazy) ANTES do compute
        une_upper = une_nome.strip()
        ddf_filtered = ddf[
            (ddf['une_nome'].str.upper() == une_upper) |
            (ddf['une'].astype(str) == une_upper)
        ]

        # Se input numérico, tentar como int
        if une_upper.isdigit():
            try:
                ddf_filtered_int = ddf[ddf['une'] == int(une_upper)]
                check_df = ddf_filtered.head(1).compute()
                if check_df.empty:
                    ddf_filtered = ddf_filtered_int
            except:
                pass

        # Compute apenas dados filtrados
        une_data = ddf_filtered.compute()

        if une_data.empty:
            unes_disponiveis = sorted(ddf['une_nome'].unique().compute())[:10]
            return {
                "error": f"UNE '{une_nome}' não encontrada",
                "type": "error",
                "suggestion": f"UNEs disponíveis: {', '.join(unes_disponiveis)}"
            }

        # Calcular métricas
        total_vendas = une_data['vendas_total'].sum()
        total_produtos = une_data['codigo'].nunique()
        segmentos = une_data.groupby('nomesegmento')['vendas_total'].sum().nlargest(5)

        # Top 5 produtos da UNE
        top_produtos = une_data.groupby('codigo').agg({
            'vendas_total': 'sum',
            'nome_produto': 'first'
        }).nlargest(5, 'vendas_total')

        return {
            "type": "table",
            "title": f"Informações da UNE {une_nome}",
            "result": {
                "une": une_nome,
                "total_vendas": float(total_vendas),
                "total_produtos": int(total_produtos),
                "top_segmentos": [{"nome": seg, "vendas": float(val)} for seg, val in segmentos.items()],
                "top_produtos": [
                    {
                        "codigo": int(cod),
                        "nome": row['nome_produto'],
                        "vendas": float(row['vendas_total'])
                    } for cod, row in top_produtos.iterrows()
                ]
            },
            "summary": f"UNE {une_nome}: {total_vendas:,.0f} vendas totais, {total_produtos} produtos diferentes",
            "tokens_used": 0
        }

    def _query_ranking_fabricantes(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Ranking de fabricantes por volume de vendas.
        """
        ddf = self._get_base_dask_df()
        limite = self._safe_get_int(params, 'limite', 10)

        logger.info(f"[>] Gerando ranking de fabricantes (top {limite})")

# Agrupar por fabricante
        fabricantes = ddf.groupby('nome_fabricante').agg({
            'vendas_total': 'sum',
            'codigo': 'nunique'  # Conta produtos únicos
        }).compute().reset_index()

        fabricantes.columns = ['fabricante', 'vendas_total', 'produtos_unicos']

        # Top N
        top_fabricantes = fabricantes.nlargest(limite, 'vendas_total')

        if top_fabricantes.empty:
            return {"error": "Nenhum fabricante encontrado", "type": "error"}

        # Preparar chart
        chart_data = {
            "x": [fab['fabricante'][:30] for _, fab in top_fabricantes.iterrows()],
            "y": [float(fab['vendas_total']) for _, fab in top_fabricantes.iterrows()],
            "type": "bar",
            "show_values": True
        }

        fabricantes_list = [{
            "fabricante": fab['fabricante'],
            "vendas": float(fab['vendas_total']),
            "produtos_unicos": int(fab['produtos_unicos'])
        } for _, fab in top_fabricantes.iterrows()]

        return {
            "type": "chart",
            "title": f"Top {limite} Fabricantes por Volume de Vendas",
            "result": {
                "chart_data": chart_data,
                "fabricantes": fabricantes_list,
                "total_fabricantes": len(fabricantes_list)
            },
            "summary": f"Top {len(fabricantes_list)} fabricantes. Líder: {fabricantes_list[0]['fabricante']} ({fabricantes_list[0]['vendas']:,.0f} vendas, {fabricantes_list[0]['produtos_unicos']} produtos)",
            "tokens_used": 0
        }

    # ============================================================
    # FASE 2: ANÁLISES ESSENCIAIS
    # ============================================================

    def _query_comparacao_segmentos(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Compara vendas entre 2 ou mais segmentos.

        Args:
            df: DataFrame com dados
            params: {'segmento1': str, 'segmento2': str, ...}

        Returns:
            Dict com comparação de vendas entre segmentos
        """
        ddf = self._get_base_dask_df()
        logger.info(f"[>] Processando comparacao_segmentos - params: {params}")

        # Extrair segmentos dos parâmetros ou da query original
        segmentos_list = []
        segmentos_conhecidos = ddf['nomesegmento'].unique().compute()

        # SEMPRE tentar extrair da query original primeiro (mais confiável)
        user_query = params.get('user_query', '').upper()

        # Buscar todos os segmentos conhecidos mencionados na query
        for seg in segmentos_conhecidos:
            if seg.upper() in user_query:
                if seg.upper() not in segmentos_list:
                    segmentos_list.append(seg.upper())

        # Se não encontrou pelo menos 2, tentar pelos parâmetros do regex (com validação)
        if len(segmentos_list) < 2:
            for key in ['segmento1', 'segmento2', 'segmento3', 'segmento4']:
                seg = self._safe_get_str(params, key, '').strip()  # TRIM aqui!
                if seg and len(seg) >= 2:  # Reduzir para 2 caracteres mínimo
                    # Buscar match parcial nos segmentos conhecidos
                    seg_upper = seg.upper().strip()  # TRIM novamente para garantir

                    # Primeiro tentar match exato
                    for seg_conhecido in segmentos_conhecidos:
                        if seg_conhecido.upper() == seg_upper:
                            if seg_conhecido.upper() not in segmentos_list:
                                segmentos_list.append(seg_conhecido.upper())
                            break
                    else:
                        # Match parcial: o segmento conhecido deve CONTER o texto extraído
                        # (não o contrário, para evitar "C" dar match em "CONFECÇÃO")
                        for seg_conhecido in segmentos_conhecidos:
                            if seg_upper in seg_conhecido.upper() and len(seg_upper) >= 5:
                                if seg_conhecido.upper() not in segmentos_list:
                                    segmentos_list.append(seg_conhecido.upper())
                                break

        if len(segmentos_list) < 2:
            # Fallback: não conseguimos extrair 2 segmentos
            logger.warning(f"[!] Não foi possível extrair 2 segmentos da query. Encontrados: {segmentos_list}")
            return {
                "type": "fallback",
                "error": "Não foi possível identificar 2 segmentos para comparação",
                "summary": "Acionando fallback para processamento com IA.",
                "tokens_used": 0
            }

        logger.info(f"[i] Comparando segmentos: {segmentos_list}")

        # Filtrar dados por segmentos
        df_filtrado = ddf[ddf['nomesegmento'].str.upper().isin(segmentos_list)].compute()

        if df_filtrado.empty:
            # Dataset atual (amostra) não contém esses segmentos
            # Retornar mensagem informativa em vez de erro
            return {
                "type": "text",
                "title": f"Comparação: {' vs '.join(segmentos_list)}",
                "result": {
                    "message": f"Os segmentos {', '.join(segmentos_list)} não foram encontrados na amostra atual de dados.",
                    "segmentos_solicitados": segmentos_list,
                    "segmentos_disponiveis": ddf['nomesegmento'].unique().compute().tolist()[:10]
                },
                "summary": f"Segmentos {', '.join(segmentos_list)} não disponíveis. Tente com: {', '.join(ddf['nomesegmento'].unique().compute()[:5])}",
                "tokens_used": 0
            }

        # Agrupar por segmento e calcular métricas
        comparacao = df_filtrado.groupby('nomesegmento').agg({
            'vendas_total': 'sum',
            'codigo': 'nunique',  # Produtos únicos
            'une': 'nunique'  # UNEs com vendas
        }).reset_index()

        comparacao.columns = ['segmento', 'vendas_total', 'produtos_unicos', 'unes_ativas']
        comparacao = comparacao.sort_values('vendas_total', ascending=False)

        # Calcular percentuais
        total_vendas = comparacao['vendas_total'].sum()
        comparacao['percentual'] = (comparacao['vendas_total'] / total_vendas * 100).round(2)

        # Preparar chart (barras comparativas)
        chart_data = {
            "x": comparacao['segmento'].tolist(),
            "y": comparacao['vendas_total'].tolist(),
            "type": "bar",
            "show_values": True
        }

        # Preparar lista de resultados
        resultados = [{
            "segmento": row['segmento'],
            "vendas_total": float(row['vendas_total']),
            "produtos_unicos": int(row['produtos_unicos']),
            "unes_ativas": int(row['unes_ativas']),
            "percentual": float(row['percentual'])
        } for _, row in comparacao.iterrows()]

        # Gerar resumo
        lider = resultados[0]
        summary = f"Comparação de {len(resultados)} segmentos. Líder: {lider['segmento']} ({lider['percentual']:.1f}% das vendas, {lider['produtos_unicos']} produtos)"

        return {
            "type": "chart",
            "title": f"Comparação de Vendas - {len(resultados)} Segmentos",
            "result": {
                "chart_data": chart_data,
                "comparacao": resultados,
                "total_vendas": float(total_vendas)
            },
            "summary": summary,
            "tokens_used": 0
        }

    def _query_analise_abc(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Classificação ABC de produtos (80-15-5).

        Args:
            df: DataFrame com dados
            params: {'classe_abc': 'A'|'B'|'C' (opcional)}

        Returns:
            Dict com análise ABC
        """
        ddf = self._get_base_dask_df()
        logger.info(f"[>] Processando analise_abc - params: {params}")

        # Verificar se existe coluna ABC no dataset
        if 'abc_une_mes_01' in ddf.columns:
            # Usar classificação existente
            logger.info("[i] Usando classificação ABC existente (abc_une_mes_01)")

            # Agrupar por classe ABC
            abc_dist = ddf.groupby('abc_une_mes_01').agg({
                'vendas_total': 'sum',
                'codigo': 'nunique'
            }).compute().reset_index()
            abc_dist.columns = ['classe', 'vendas_total', 'produtos']

        else:
            # Calcular classificação ABC
            logger.info("[i] Calculando classificação ABC (80-15-5)")

            # Agrupar por produto e somar vendas
            produtos_vendas = ddf.groupby('codigo').agg({
                'vendas_total': 'sum',
                'nome_produto': 'first'
            }).compute().reset_index()

            # Ordenar por vendas decrescentes
            produtos_vendas = produtos_vendas.sort_values('vendas_total', ascending=False)

            # Calcular percentual acumulado
            produtos_vendas['vendas_acumuladas'] = produtos_vendas['vendas_total'].cumsum()
            total_vendas = produtos_vendas['vendas_total'].sum()
            produtos_vendas['percentual_acumulado'] = (produtos_vendas['vendas_acumuladas'] / total_vendas * 100)

            # Classificar ABC
            produtos_vendas['classe'] = produtos_vendas['percentual_acumulado'].apply(
                lambda x: 'A' if x <= 80 else ('B' if x <= 95 else 'C')
            )

            # Agrupar por classe
            abc_dist = produtos_vendas.groupby('classe').agg({
                'vendas_total': 'sum',
                'codigo': 'count'
            }).reset_index()
            abc_dist.columns = ['classe', 'vendas_total', 'produtos']

        # Calcular percentuais
        total_vendas = abc_dist['vendas_total'].sum()
        total_produtos = abc_dist['produtos'].sum()
        abc_dist['percentual_vendas'] = (abc_dist['vendas_total'] / total_vendas * 100).round(2)
        abc_dist['percentual_produtos'] = (abc_dist['produtos'] / total_produtos * 100).round(2)

        # Ordenar A, B, C
        ordem_abc = {'A': 0, 'B': 1, 'C': 2}
        abc_dist['ordem'] = abc_dist['classe'].map(ordem_abc)
        abc_dist = abc_dist.sort_values('ordem').drop('ordem', axis=1)

        # Preparar chart
        chart_data = {
            "labels": abc_dist['classe'].tolist(),
            "datasets": [
                {
                    "label": "% Vendas",
                    "data": abc_dist['percentual_vendas'].tolist(),
                    "backgroundColor": ["#4CAF50", "#FFC107", "#F44336"]
                },
                {
                    "label": "% Produtos",
                    "data": abc_dist['percentual_produtos'].tolist(),
                    "backgroundColor": ["#81C784", "#FFD54F", "#EF5350"]
                }
            ],
            "type": "bar"
        }

        # Preparar resultados
        resultados = [{
            "classe": row['classe'],
            "vendas_total": float(row['vendas_total']),
            "produtos": int(row['produtos']),
            "percentual_vendas": float(row['percentual_vendas']),
            "percentual_produtos": float(row['percentual_produtos'])
        } for _, row in abc_dist.iterrows()]

        # Gerar resumo
        classe_a = resultados[0] if resultados else None
        if classe_a:
            summary = f"Classe A: {classe_a['percentual_vendas']:.1f}% das vendas com {classe_a['percentual_produtos']:.1f}% dos produtos ({classe_a['produtos']} itens)"
        else:
            summary = "Análise ABC concluída"

            return {
            "type": "chart",
            "title": "Análise ABC de Produtos",
            "result": {
                "chart_data": chart_data,
                "distribuicao": resultados,
                "total_vendas": float(total_vendas),
                "total_produtos": int(total_produtos)
            },
            "summary": summary,
            "tokens_used": 0
        }

    def _query_estoque_alto(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Produtos com baixa rotação de vendas (vendas baixas = estoque parado implícito).

        Args:
            df: DataFrame com dados
            params: {'threshold': float (opcional, padrão 2.0)}

        Returns:
            Dict com produtos com baixa rotação
        """
        ddf = self._get_base_dask_df()
        logger.info(f"[>] Processando estoque_alto - params: {params}")

        # Calcular média de vendas
        media_vendas = ddf['vendas_total'].mean().compute()

        # Produtos com vendas muito abaixo da média (< 30% da média)
        threshold_percentual = 0.3
        df_baixa_rotacao = ddf[ddf['vendas_total'] < (media_vendas * threshold_percentual)].copy().compute()
        df_baixa_rotacao = df_baixa_rotacao.sort_values('vendas_total', ascending=True)

        limite = self._safe_get_int(params, 'limite', 20)
        top_produtos = df_baixa_rotacao.head(limite)

        if top_produtos.empty:
            return {
                "type": "text",
                "title": "Análise de Produtos com Baixa Rotação",
                "result": {"message": "Todos os produtos têm vendas normais"},
                "summary": "Nenhum produto com vendas significativamente abaixo da média",
                "tokens_used": 0
            }

        # Preparar dados para visualização
        chart_data = {
            "x": top_produtos['nome_produto'].str[:30].tolist(),
            "y": top_produtos['vendas_total'].tolist(),
            "labels": top_produtos['nome_produto'].tolist()
        }

        # Preparar tabela
        tabela = []
        for _, prod in top_produtos.iterrows():
            tabela.append({
                "codigo": str(prod['codigo']),
                "produto": prod['nome_produto'][:50],
                "vendas_total": float(prod['vendas_total']),
                "percentual_media": float((prod['vendas_total'] / media_vendas * 100)),
                "segmento": prod['nomesegmento']
            })

        # Resumo
        summary = f"Identificados {len(top_produtos)} produtos com baixa rotação (vendas < {threshold_percentual*100:.0f}% da média de R$ {media_vendas:,.2f})"

        return {
            "type": "chart",
            "title": "Produtos com Baixa Rotação de Vendas",
            "result": {
                "produtos": tabela,
                "total_produtos": len(tabela),
                "media_vendas": float(media_vendas),
                "chart_data": chart_data
            },
            "summary": summary,
            "tokens_used": 0
        }

    def _query_top_produtos_por_segmento(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Top N produtos mais vendidos em um segmento específico.

        Args:
            df: DataFrame com dados
            params: {'segmento': str, 'limite': int}

        Returns:
            Dict com top produtos do segmento
        """
        ddf = self._get_base_dask_df()
        logger.info(f"[>] Processando top_produtos_por_segmento - params: {params}")

        # Extrair segmento
        segmento = self._safe_get_str(params, 'segmento', '').strip().upper()
        limite = self._safe_get_int(params, 'limite', 10)

        # Se não veio nos params, buscar na user_query
        if not segmento or segmento == 'TODOS':
            user_query = params.get('user_query', '').upper()
            segmentos_conhecidos = ddf['nomesegmento'].unique().compute()
            for seg in segmentos_conhecidos:
                if seg.upper() in user_query:
                    segmento = seg.upper()
                    break

        # Se ainda não tem segmento, usar TODOS (ranking geral)
        if not segmento or segmento == 'TODOS':
            logger.info(f"[i] Buscando top {limite} produtos GERAL (todos os segmentos)")
            df_segmento = ddf.compute()
            titulo_segmento = "Geral"
        else:
            logger.info(f"[i] Buscando top {limite} produtos no segmento: {segmento}")
            # Filtrar por segmento
            df_segmento = ddf[ddf['nomesegmento'].str.upper() == segmento].compute()
            titulo_segmento = segmento

            if df_segmento.empty:
                # Segmento não encontrado, tentar ranking geral
                logger.warning(f"[!] Segmento '{segmento}' não encontrado - usando ranking geral")
                df_segmento = ddf.compute()
                titulo_segmento = "Geral"

        # Agrupar por produto e somar vendas
        top_produtos = df_segmento.groupby('codigo', as_index=False).agg({
            'nome_produto': 'first',
            'vendas_total': 'sum'
        })

        top_produtos = top_produtos.nlargest(limite, 'vendas_total')

        # Preparar chart
        chart_data = {
            "x": top_produtos['nome_produto'].str[:30].tolist(),
            "y": top_produtos['vendas_total'].tolist(),
            "type": "bar",
            "show_values": True
        }

        produtos_list = [{
            "codigo": str(row['codigo']),
            "nome": row['nome_produto'],
            "vendas": float(row['vendas_total'])
        } for _, row in top_produtos.iterrows()]

        return {
            "type": "chart",
            "title": f"Top {limite} Produtos - {titulo_segmento}",
            "result": {
                "chart_data": chart_data,
                "produtos": produtos_list,
                "total_produtos": len(produtos_list),
                "segmento": titulo_segmento
            },
            "summary": f"Top {len(produtos_list)} produtos{' no segmento ' + titulo_segmento if titulo_segmento != 'Geral' else ' (ranking geral)'}. Líder: {produtos_list[0]['nome'][:40]} ({produtos_list[0]['vendas']:,.0f} vendas)",
            "tokens_used": 0
        }

    def _query_distribuicao_categoria(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Distribuição de vendas por categoria (opcionalmente dentro de um segmento).

        Args:
            df: DataFrame com dados
            params: {'segmento': str (opcional)}

        Returns:
            Dict com distribuição por categoria
        """
        ddf = self._get_base_dask_df()
        logger.info(f"[>] Processando distribuicao_categoria - params: {params}")

        # Extrair segmento se especificado
        segmento = self._safe_get_str(params, 'segmento', '').strip().upper()

        # Se não veio nos params, buscar na user_query
        if not segmento:
            user_query = params.get('user_query', '').upper()
            segmentos_conhecidos = ddf['nomesegmento'].unique().compute()
            for seg in segmentos_conhecidos:
                if seg.upper() in user_query:
                    segmento = seg.upper()
                    break

        # Filtrar por segmento se especificado
        if segmento:
            df_filtrado = ddf[ddf['nomesegmento'].str.upper() == segmento].compute()
            titulo_sufixo = f" - {segmento}"
        else:
            df_filtrado = ddf.compute()
            titulo_sufixo = ""

        if df_filtrado.empty:
            return {
                "type": "fallback",
                "error": f"Nenhum dado encontrado para o segmento {segmento}" if segmento else "Dados vazios",
                "summary": "Acionando fallback para processamento com IA.",
                "tokens_used": 0
            }

        # Agrupar por categoria
        categorias = df_filtrado.groupby('nome_categoria').agg({
            'vendas_total': 'sum',
            'codigo': 'nunique'
        }).reset_index()

        categorias.columns = ['categoria', 'vendas_total', 'produtos_unicos']
        categorias = categorias.sort_values('vendas_total', ascending=False)

        # Calcular percentuais
        total_vendas = categorias['vendas_total'].sum()
        categorias['percentual'] = (categorias['vendas_total'] / total_vendas * 100).round(2)

        # Preparar chart
        chart_data = {
            "labels": categorias['categoria'].tolist(),
            "data": categorias['vendas_total'].tolist(),
            "type": "pie",
            "show_percentages": True
        }

        categorias_list = [{
            "categoria": row['categoria'],
            "vendas": float(row['vendas_total']),
            "produtos": int(row['produtos_unicos']),
            "percentual": float(row['percentual'])
        } for _, row in categorias.iterrows()]

        return {
            "type": "chart",
            "title": f"Distribuição de Vendas por Categoria{titulo_sufixo}",
            "result": {
                "chart_data": chart_data,
                "categorias": categorias_list,
                "total_categorias": len(categorias_list),
                "total_vendas": float(total_vendas)
            },
            "summary": f"{len(categorias_list)} categorias. Líder: {categorias_list[0]['categoria']} ({categorias_list[0]['percentual']:.1f}% das vendas)",
            "tokens_used": 0
        }

    def _query_diversidade_produtos(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Análise de diversidade de produtos por UNE ou segmento.

        Args:
            df: DataFrame com dados
            params: {}

        Returns:
            Dict com análise de diversidade
        """
        ddf = self._get_base_dask_df()
        logger.info(f"[>] Processando diversidade_produtos - params: {params}")

        user_query = params.get('user_query', '').lower()

        # Detectar se é por UNE ou por segmento
        if 'une' in user_query or 'loja' in user_query or 'filial' in user_query:
            # Diversidade por UNE
            agrupamento = ddf.groupby('une_nome').agg({
                'codigo': 'nunique',  # Diversidade de produtos
                'vendas_total': 'sum',
                'nomesegmento': 'nunique'  # Diversidade de segmentos
            }).compute().reset_index()

            agrupamento.columns = ['une', 'produtos_unicos', 'vendas_total', 'segmentos_ativos']
            agrupamento = agrupamento.sort_values('produtos_unicos', ascending=False).head(15)

            titulo = "UNEs com Maior Diversidade de Produtos"
            label_col = 'une'

        else:
            # Diversidade por segmento
            agrupamento = ddf.groupby('nomesegmento').agg({
                'codigo': 'nunique',
                'vendas_total': 'sum',
                'nome_categoria': 'nunique'
            }).compute().reset_index()

            agrupamento.columns = ['segmento', 'produtos_unicos', 'vendas_total', 'categorias']
            agrupamento = agrupamento.sort_values('produtos_unicos', ascending=False)

            titulo = "Segmentos com Maior Diversidade de Produtos"
            label_col = 'segmento'

        # Preparar chart
        chart_data = {
            "x": agrupamento[label_col].tolist(),
            "y": agrupamento['produtos_unicos'].tolist(),
            "type": "bar",
            "show_values": True
        }

        resultados = [{
            label_col: row[label_col],
            "produtos_unicos": int(row['produtos_unicos']),
            "vendas_total": float(row['vendas_total'])
        } for _, row in agrupamento.iterrows()]

        lider = resultados[0]
        summary = f"{titulo.split()[0]} com maior diversidade: {lider[label_col]} ({lider['produtos_unicos']} produtos únicos)"

        return {
            "type": "chart",
            "title": titulo,
            "result": {
                "chart_data": chart_data,
                "resultados": resultados,
                "total": len(resultados)
            },
            "summary": summary,
            "tokens_used": 0
        }

    def _query_crescimento_segmento(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Análise de crescimento percentual de vendas por segmento.

        Args:
            df: DataFrame com dados
            params: {}

        Returns:
            Dict com análise de crescimento
        """
        ddf = self._get_base_dask_df()
        logger.info(f"[>] Processando crescimento_segmento - params: {params}")

        # Verificar se temos dados mensais
        meses_cols = [f'mes_{i:02d}' for i in range(1, 13)]
        if not all(col in ddf.columns for col in meses_cols[:2]):
            return {
                "type": "fallback",
                "error": "Dados mensais não disponíveis para cálculo de crescimento",
                "summary": "Acionando fallback para processamento com IA.",
                "tokens_used": 0
            }

        # Calcular vendas do primeiro e último trimestre
        df_crescimento = ddf.groupby('nomesegmento').agg({
            'mes_01': 'sum',
            'mes_02': 'sum',
            'mes_03': 'sum',
            'mes_10': 'sum',
            'mes_11': 'sum',
            'mes_12': 'sum'
        }).compute().reset_index()

        df_crescimento['primeiro_tri'] = df_crescimento[['mes_01', 'mes_02', 'mes_03']].sum(axis=1)
        df_crescimento['ultimo_tri'] = df_crescimento[['mes_10', 'mes_11', 'mes_12']].sum(axis=1)

        # Calcular crescimento percentual
        df_crescimento['crescimento_pct'] = ((df_crescimento['ultimo_tri'] - df_crescimento['primeiro_tri']) / (df_crescimento['primeiro_tri'] + 1) * 100).round(2)

        df_crescimento = df_crescimento.sort_values('crescimento_pct', ascending=False)

        # Preparar chart
        chart_data = {
            "x": df_crescimento['nomesegmento'].tolist(),
            "y": df_crescimento['crescimento_pct'].tolist(),
            "type": "bar",
            "show_values": True
        }

        resultados = [{
            "segmento": row['nomesegmento'],
            "crescimento_percentual": float(row['crescimento_pct']),
            "vendas_primeiro_tri": float(row['primeiro_tri']),
            "vendas_ultimo_tri": float(row['ultimo_tri'])
        } for _, row in df_crescimento.iterrows()]

        lider = resultados[0]
        summary = f"Segmento com maior crescimento: {lider['segmento']} ({lider['crescimento_percentual']:+.1f}%)"

        return {
            "type": "chart",
            "title": "Crescimento Percentual por Segmento",
            "result": {
                "chart_data": chart_data,
                "segmentos": resultados,
                "total_segmentos": len(resultados)
            },
            "summary": summary,
            "tokens_used": 0
        }

    def _query_sazonalidade(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Análise de sazonalidade de vendas.

        Args:
            df: DataFrame com dados
            params: {'segmento': str (opcional)}

        Returns:
            Dict com análise de sazonalidade
        """
        ddf = self._get_base_dask_df()
        logger.info(f"[>] Processando sazonalidade - params: {params}")

        # Verificar se temos dados mensais
        meses_cols = [f'mes_{i:02d}' for i in range(1, 13)]
        if not all(col in ddf.columns for col in meses_cols):
            return {
                "type": "fallback",
                "error": "Dados mensais não disponíveis",
                "summary": "Acionando fallback para processamento com IA.",
                "tokens_used": 0
            }

        # Extrair segmento se especificado
        segmento = self._safe_get_str(params, 'segmento', '').strip().upper()

        if not segmento:
            user_query = params.get('user_query', '').upper()
            segmentos_conhecidos = ddf['nomesegmento'].unique().compute()
            for seg in segmentos_conhecidos:
                if seg.upper() in user_query:
                    segmento = seg.upper()
                    break

        # Filtrar por segmento se especificado
        if segmento:
            df_filtrado = ddf[ddf['nomesegmento'].str.upper() == segmento].compute()
            titulo_sufixo = f" - {segmento}"
        else:
            df_filtrado = ddf.compute()
            titulo_sufixo = ""

        if df_filtrado.empty:
            return {
                "type": "fallback",
                "error": f"Segmento '{segmento}' não encontrado" if segmento else "Dados vazios",
                "summary": "Acionando fallback para processamento com IA.",
                "tokens_used": 0
            }

        # Somar vendas por mês
        vendas_mensais = {f'Mês {i}': df_filtrado[f'mes_{i:02d}'].sum() for i in range(1, 13)}

        # Calcular média e desvio
        valores = list(vendas_mensais.values())
        media = sum(valores) / len(valores)
        variacao = [(v - media) / media * 100 for v in valores]

        # Identificar picos (variação > 20%)
        meses_pico = [mes for mes, var in zip(vendas_mensais.keys(), variacao) if var > 20]

        # Preparar chart
        chart_data = {
            "x": list(vendas_mensais.keys()),
            "y": list(vendas_mensais.values()),
            "type": "line",
            "show_values": True
        }

        summary = f"Sazonalidade{titulo_sufixo}. Média mensal: {media:,.0f}. " + (f"Picos em: {', '.join(meses_pico)}" if meses_pico else "Vendas estáveis ao longo do ano")

        return {
            "type": "chart",
            "title": f"Análise de Sazonalidade{titulo_sufixo}",
            "result": {
                "chart_data": chart_data,
                "vendas_mensais": vendas_mensais,
                "media_mensal": float(media),
                "meses_pico": meses_pico
            },
            "summary": summary,
            "tokens_used": 0
        }

    def _query_ranking_unes_por_segmento(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Ranking de UNEs por volume de vendas em um segmento específico.

        Args:
            df: DataFrame com dados
            params: {'segmento': str, 'limite': int}

        Returns:
            Dict com ranking de UNEs
        """
        ddf = self._get_base_dask_df()
        logger.info(f"[>] Processando ranking_unes_por_segmento - params: {params}")

        # Extrair segmento
        segmento = self._safe_get_str(params, 'segmento', '').strip().upper()
        limite = self._safe_get_int(params, 'limite', 10)

        # Se não veio nos params, buscar na user_query
        if not segmento:
            user_query = params.get('user_query', '').upper()
            segmentos_conhecidos = ddf['nomesegmento'].unique().compute()
            for seg in segmentos_conhecidos:
                if seg.upper() in user_query:
                    segmento = seg.upper()
                    break

        if not segmento:
            # Se não encontrou segmento, retornar ranking geral de UNEs
            logger.info("[i] Segmento não especificado, retornando ranking geral de UNEs")
            return self._ranking_unes(limite)

        logger.info(f"[i] Ranking de UNEs no segmento: {segmento}")

        # Filtrar por segmento
        df_segmento = ddf[ddf['nomesegmento'].str.upper() == segmento].compute()

        if df_segmento.empty:
            return {
                "type": "fallback",
                "error": f"Segmento '{segmento}' não encontrado",
                "summary": "Acionando fallback para processamento com IA.",
                "tokens_used": 0
            }

        # Agrupar por UNE
        ranking = df_segmento.groupby('une_nome', as_index=False).agg({
            'vendas_total': 'sum',
            'codigo': 'nunique'  # Produtos únicos
        })

        ranking.columns = ['une', 'vendas_total', 'produtos_unicos']
        ranking = ranking.nlargest(limite, 'vendas_total')

        # Preparar chart
        chart_data = {
            "x": ranking['une'].tolist(),
            "y": ranking['vendas_total'].tolist(),
            "type": "bar",
            "show_values": True
        }

        unes_list = [{
            "une": row['une'],
            "vendas": float(row['vendas_total']),
            "produtos": int(row['produtos_unicos'])
        } for _, row in ranking.iterrows()]

        lider = unes_list[0] if unes_list else None
        summary = f"UNE que mais vende em {segmento}: {lider['une']} ({lider['vendas']:,.0f} vendas)" if lider else "Sem dados"

        return {
            "type": "chart",
            "title": f"Ranking de UNEs - {segmento}",
            "result": {
                "chart_data": chart_data,
                "unes": unes_list,
                "total_unes": len(unes_list),
                "segmento": segmento
            },
            "summary": summary,
            "tokens_used": 0
        }

    def _query_vendas_produto_une(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Vendas de um produto específico em uma UNE específica.

        Args:
            df: DataFrame com dados
            params: {'produto': str, 'une': str}

        Returns:
            Dict com vendas do produto na UNE
        """
        ddf = self._get_base_dask_df()
        logger.info(f"[>] Processando vendas_produto_une - params: {params}")

        produto_codigo = self._safe_get_str(params, 'produto', '').strip()
        une_nome = self._safe_get_str(params, 'une', '').strip().upper()

        if not produto_codigo or not une_nome:
            return {
                "type": "fallback",
                "error": "Produto ou UNE não especificados",
                "summary": "Acionando fallback para processamento com IA.",
                "tokens_used": 0
            }

        logger.info(f"[i] Buscando vendas do produto {produto_codigo} na UNE {une_nome}")

        # Filtrar por UNE primeiro (lazy)
        une_upper = une_nome.strip()
        ddf_une = ddf[
            (ddf['une_nome'].str.upper() == une_upper) |
            (ddf['une'].astype(str) == une_upper)
        ]

        # Se input numérico, tentar como int
        if une_upper.isdigit():
            try:
                ddf_une_int = ddf[ddf['une'] == int(une_upper)]
                check_df = ddf_une.head(1).compute()
                if check_df.empty:
                    ddf_une = ddf_une_int
            except:
                pass

        # Depois filtrar por produto no subset da UNE (lazy)
        ddf_filtered = ddf_une[ddf_une['codigo'].astype(str) == produto_codigo]

        # Compute apenas o resultado final filtrado (1 produto em 1 UNE = muito pequeno)
        produto_une = ddf_filtered.compute()

        if produto_une.empty:
            return {
                "type": "fallback",
                "message": f"Produto {produto_codigo} não encontrado na UNE {une_nome}"
            }

        # Pegar primeira linha (deveria ser única)
        prod = produto_une.iloc[0]

        # Preparar vendas mensais
        meses_cols = [f'mes_{i:02d}' for i in range(1, 13)]
        vendas_mensais = {f'Mês {i}': float(prod[col]) for i, col in enumerate(meses_cols, 1) if col in prod.index}

        # Preparar chart
        chart_data = {
            "x": list(vendas_mensais.keys()),
            "y": list(vendas_mensais.values()),
            "type": "line",
            "show_values": True
        }

        summary = f"{prod['nome_produto'][:50]} na UNE {une_nome}: {prod['vendas_total']:,.0f} vendas totais"

        return {
            "type": "chart",
            "title": f"Vendas de {prod['nome_produto'][:40]} - UNE {une_nome}",
            "result": {
                "chart_data": chart_data,
                "produto": {
                    "codigo": str(prod['codigo']),
                    "nome": prod['nome_produto'],
                    "vendas_total": float(prod['vendas_total']),
                    "segmento": prod['nomesegmento']
                },
                "une": une_nome,
                "vendas_mensais": vendas_mensais
            },
            "summary": summary,
            "tokens_used": 0
        }

    def _query_evolucao_mes_a_mes(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Evolução de vendas mês a mês (geral ou por produto/segmento).

        Args:
            df: DataFrame com dados
            params: {'produto': str (opcional), 'segmento': str (opcional)}

        Returns:
            Dict com evolução mensal
        """
        ddf = self._get_base_dask_df()
        logger.info(f"[>] Processando evolucao_mes_a_mes - params: {params}")

        # Verificar se temos dados mensais
        meses_cols = [f'mes_{i:02d}' for i in range(1, 13)]
        if not all(col in ddf.columns for col in meses_cols):
            return {
                "type": "fallback",
                "error": "Dados mensais não disponíveis",
                "summary": "Acionando fallback para processamento com IA.",
                "tokens_used": 0
            }

        produto_codigo = self._safe_get_str(params, 'produto', '').strip()
        segmento = self._safe_get_str(params, 'segmento', '').strip().upper()

        # Se não veio nos params, buscar na user_query
        if not produto_codigo and not segmento:
            user_query = params.get('user_query', '').upper()
            # Tentar extrair código de produto (números)
            import re
            match_produto = re.search(r'\b(\d{5,})\b', user_query)
            if match_produto:
                produto_codigo = match_produto.group(1)

        # Filtrar dados
        if produto_codigo:
            df_filtrado = ddf[ddf['codigo'].astype(str) == produto_codigo].compute()
            titulo_sufixo = f" - Produto {produto_codigo}"
        elif segmento:
            df_filtrado = ddf[ddf['nomesegmento'].str.upper() == segmento].compute()
            titulo_sufixo = f" - {segmento}"
        else:
            df_filtrado = ddf.compute()
            titulo_sufixo = ""

        if df_filtrado.empty:
            return {
                "type": "fallback",
                "error": "Nenhum dado encontrado para os filtros especificados",
                "summary": "Acionando fallback para processamento com IA.",
                "tokens_used": 0
            }

        # Somar vendas por mês
        vendas_mensais = {f'Mês {i}': df_filtrado[col].sum() for i, col in enumerate(meses_cols, 1)}

        # Preparar chart
        chart_data = {
            "x": list(vendas_mensais.keys()),
            "y": list(vendas_mensais.values()),
            "type": "line",
            "show_values": True
        }

        total = sum(vendas_mensais.values())
        summary = f"Evolução mensal{titulo_sufixo}. Total: {total:,.0f} vendas"

        return {
            "type": "chart",
            "title": f"Evolução de Vendas Mês a Mês{titulo_sufixo}",
            "result": {
                "chart_data": chart_data,
                "vendas_mensais": vendas_mensais,
                "total_vendas": float(total)
            },
            "summary": summary,
            "tokens_used": 0
        }

    def _query_pico_vendas(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Produtos com pico de vendas no último mês.

        Args:
            df: DataFrame com dados
            params: {'limite': int}

        Returns:
            Dict com produtos que tiveram pico
        """
        ddf = self._get_base_dask_df()
        logger.info(f"[>] Processando pico_vendas - params: {params}")

        limite = self._safe_get_int(params, 'limite', 15)

        # Verificar se temos dados mensais
        
        return {
                "type": "fallback",
                "error": "Dados mensais não disponíveis",
                "summary": "Acionando fallback para processamento com IA.",
                "tokens_used": 0
            }

        # Calcular variação entre último mês e média dos 11 anteriores
        df_pico = ddf.copy()
        colunas_anteriores = [f'mes_{i:02d}' for i in range(1, 12)]
        df_pico['media_anterior'] = df_pico[colunas_anteriores].mean(axis=1)
        df_pico['variacao_pct'] = ((df_pico['mes_12'] - df_pico['media_anterior']) / (df_pico['media_anterior'] + 1) * 100)

        # Filtrar produtos com pico (variação > 50%)
        produtos_pico = df_pico[df_pico['variacao_pct'] > 50].nlargest(limite, 'variacao_pct')

        if produtos_pico.empty:
            return {
                "type": "text",
                "title": "Produtos com Pico de Vendas",
                "result": {
                    "message": "Nenhum produto com pico significativo no último mês"
                },
                "summary": "Não foram encontrados produtos com pico de vendas no último mês",
                "tokens_used": 0
            }

        # Preparar chart
        chart_data = {
            "x": produtos_pico['nome_produto'].str[:30].tolist(),
            "y": produtos_pico['variacao_pct'].tolist(),
            "type": "bar",
            "show_values": True
        }

        produtos_list = [{
            "codigo": str(row['codigo']),
            "nome": row['nome_produto'],
            "vendas_ultimo_mes": float(row['mes_12']),
            "media_anterior": float(row['media_anterior']),
            "variacao_pct": float(row['variacao_pct'])
        } for _, row in produtos_pico.iterrows()]

        lider = produtos_list[0] if produtos_list else None
        summary = f"{len(produtos_list)} produtos com pico. Destaque: {lider['nome'][:40]} ({lider['variacao_pct']:+.0f}%)" if lider else "Sem picos"

        return {
            "type": "chart",
            "title": "Produtos com Pico de Vendas no Último Mês",
            "result": {
                "chart_data": chart_data,
                "produtos": produtos_list,
                "total_produtos": len(produtos_list)
            },
            "summary": summary,
            "tokens_used": 0
        }

    def _query_tendencia_vendas(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Tendência de vendas por categoria nos últimos meses.

        Args:
            df: DataFrame com dados
            params: {'meses': int}

        Returns:
            Dict com tendência por categoria
        """
        ddf = self._get_base_dask_df()
        logger.info(f"[>] Processando tendencia_vendas - params: {params}")

        meses = self._safe_get_int(params, 'meses', 6)

        # Verificar dados mensais
        meses_cols = [f'mes_{i:02d}' for i in range(13-meses, 13)]
        if not all(col in ddf.columns for col in meses_cols):
            return {
                "type": "fallback",
                "error": "Dados mensais insuficientes",
                "summary": "Acionando fallback para processamento com IA.",
                "tokens_used": 0
            }

        # Agrupar por categoria e somar vendas mensais
        tendencia = ddf.groupby('nome_categoria')[meses_cols].sum().compute()

        # Calcular tendência (comparar primeiros vs últimos meses do período)
        metade = len(meses_cols) // 2
        tendencia['periodo_inicial'] = tendencia[meses_cols[:metade]].sum(axis=1)
        tendencia['periodo_final'] = tendencia[meses_cols[metade:]].sum(axis=1)
        tendencia['tendencia_pct'] = ((tendencia['periodo_final'] - tendencia['periodo_inicial']) / (tendencia['periodo_inicial'] + 1) * 100)

        tendencia = tendencia.reset_index().sort_values('tendencia_pct', ascending=False)

        # Preparar chart
        chart_data = {
            "x": tendencia['nome_categoria'].tolist(),
            "y": tendencia['tendencia_pct'].tolist(),
            "type": "bar",
            "show_values": True
        }

        categorias_list = [{
            "categoria": row['nome_categoria'],
            "tendencia_pct": float(row['tendencia_pct']),
            "periodo_inicial": float(row['periodo_inicial']),
            "periodo_final": float(row['periodo_final'])
        } for _, row in tendencia.iterrows()]

        lider = categorias_list[0] if categorias_list else None
        summary = f"Tendência de {len(categorias_list)} categorias. Maior crescimento: {lider['categoria']} ({lider['tendencia_pct']:+.1f}%)" if lider else "Sem dados"

        return {
            "type": "chart",
            "title": f"Tendência de Vendas - Últimos {meses} Meses",
            "result": {
                "chart_data": chart_data,
                "categorias": categorias_list,
                "total_categorias": len(categorias_list)
            },
            "summary": summary,
            "tokens_used": 0
        }

    def _query_produtos_acima_media(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Produtos com vendas acima da média (opcionalmente por segmento).

        Args:
            df: DataFrame com dados
            params: {'segmento': str (opcional), 'limite': int}

        Returns:
            Dict com produtos acima da média
        """
        ddf = self._get_base_dask_df()
        logger.info(f"[>] Processando produtos_acima_media - params: {params}")

        segmento = self._safe_get_str(params, 'segmento', '').strip().upper()
        limite = self._safe_get_int(params, 'limite', 20)

        # Se não veio nos params, buscar na user_query
        if not segmento:
            user_query = params.get('user_query', '').upper()
            segmentos_conhecidos = ddf['nomesegmento'].unique().compute()
            for seg in segmentos_conhecidos:
                if seg.upper() in user_query:
                    segmento = seg.upper()
                    break

        # Filtrar por segmento se especificado
        if segmento:
            df_filtrado = ddf[ddf['nomesegmento'].str.upper() == segmento].compute()
            titulo_sufixo = f" - {segmento}"
        else:
            df_filtrado = ddf.compute()
            titulo_sufixo = ""

        if df_filtrado.empty:
            return {
                "type": "fallback",
                "error": f"Segmento '{segmento}' não encontrado" if segmento else "Dados vazios",
                "summary": "Acionando fallback para processamento com IA.",
                "tokens_used": 0
            }

        # Calcular média de vendas
        media_vendas = df_filtrado['vendas_total'].mean()

        # Filtrar produtos acima da média
        produtos_acima = df_filtrado[df_filtrado['vendas_total'] > media_vendas].nlargest(limite, 'vendas_total')

        # Preparar chart
        chart_data = {
            "x": produtos_acima['nome_produto'].str[:30].tolist(),
            "y": produtos_acima['vendas_total'].tolist(),
            "type": "bar",
            "show_values": True
        }

        produtos_list = [{
            "codigo": str(row['codigo']),
            "nome": row['nome_produto'],
            "vendas": float(row['vendas_total']),
            "vs_media": float((row['vendas_total'] / media_vendas - 1) * 100)
        } for _, row in produtos_acima.iterrows()]

        summary = f"{len(produtos_list)} produtos acima da média{titulo_sufixo} ({media_vendas:,.0f} vendas)"

        return {
            "type": "chart",
            "title": f"Produtos Acima da Média{titulo_sufixo}",
            "result": {
                "chart_data": chart_data,
                "produtos": produtos_list,
                "media_vendas": float(media_vendas),
                "total_produtos": len(produtos_list)
            },
            "summary": summary,
            "tokens_used": 0
        }

    def _query_performance_categoria(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Performance de vendas por categoria (opcionalmente dentro de um segmento).

        Args:
            df: DataFrame com dados
            params: {'segmento': str (opcional)}

        Returns:
            Dict com performance por categoria
        """
        ddf = self._get_base_dask_df()
        logger.info(f"[>] Processando performance_categoria - params: {params}")

        # Extrair segmento se especificado
        user_query = params.get('user_query', '').upper()
        segmentos_conhecidos = ddf['nomesegmento'].unique().compute()
        segmento = None

        for seg in segmentos_conhecidos:
            if seg.upper() in user_query:
                segmento = seg.upper()
                break

        # Filtrar por segmento se especificado
        if segmento:
            df_filtrado = ddf[ddf['nomesegmento'].str.upper() == segmento].compute()
            titulo_sufixo = f" - {segmento}"
            logger.info(f"[i] Analisando categorias do segmento: {segmento}")
        else:
            df_filtrado = ddf.compute()
            titulo_sufixo = ""
            logger.info("[i] Analisando todas as categorias")

        if df_filtrado.empty:
            return {
                "type": "text",
                "title": "Performance por Categoria",
                "result": {"message": f"Segmento '{segmento}' não encontrado"},
                "summary": f"Segmento '{segmento}' não disponível na amostra",
                "tokens_used": 0
            }

        # Agrupar por categoria
        performance = df_filtrado.groupby('nome_categoria').agg({
            'vendas_total': 'sum',
            'codigo': 'nunique',  # Produtos únicos
            'une': 'nunique'  # UNEs com vendas
        }).reset_index()

        performance.columns = ['categoria', 'vendas_total', 'produtos_unicos', 'unes_ativas']
        performance = performance.sort_values('vendas_total', ascending=False)

        # Calcular percentuais
        total_vendas = performance['vendas_total'].sum()
        performance['percentual'] = (performance['vendas_total'] / total_vendas * 100).round(2)

        # Top 15 categorias
        top_categorias = performance.head(15)

        # Chart data
        chart_data = {
            "x": top_categorias['categoria'].tolist(),
            "y": top_categorias['vendas_total'].tolist(),
            "type": "bar",
            "show_values": True
        }

        # Tabela
        tabela = []
        for _, cat in top_categorias.iterrows():
            tabela.append({
                "categoria": cat['categoria'],
                "vendas_total": float(cat['vendas_total']),
                "produtos_unicos": int(cat['produtos_unicos']),
                "unes_ativas": int(cat['unes_ativas']),
                "percentual": float(cat['percentual'])
            })

        # Resumo
        top_cat = tabela[0] if tabela else None
        summary = f"Performance por Categoria{titulo_sufixo}:\n\n"
        summary += f"Líder: {top_cat['categoria']} (R$ {top_cat['vendas_total']:,.2f} - {top_cat['percentual']:.1f}%)\n"
        summary += f"Total de categorias: {len(performance)}\n"
        summary += f"Top 3: {', '.join(top_categorias['categoria'].head(3).tolist())}"

        return {
            "type": "chart",
            "title": f"Performance por Categoria{titulo_sufixo}",
            "result": {
                "chart_data": chart_data,
                "categorias": tabela,
                "total_categorias": len(performance),
                "segmento": segmento
            },
            "summary": summary,
            "tokens_used": 0
        }

    def _query_comparativo_unes_similares(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Compara eficiência de vendas entre UNEs com características similares.
        Usa volume total de vendas como proxy para similaridade.

        Args:
            df: DataFrame com dados
            params: {}

        Returns:
            Dict com comparativo de UNEs
        """
        ddf = self._get_base_dask_df()
        logger.info(f"[>] Processando comparativo_unes_similares - params: {params}")

        # Agrupar por UNE
        unes = ddf.groupby('une_nome').agg({
            'vendas_total': 'sum',
            'codigo': 'nunique',  # Diversidade de produtos
            'nomesegmento': 'nunique'  # Diversidade de segmentos
        }).compute().reset_index()

        unes.columns = ['une', 'vendas_total', 'produtos_unicos', 'segmentos_unicos']
        unes = unes.sort_values('vendas_total', ascending=False)

        # Calcular eficiência (vendas / produto)
        unes['eficiencia'] = (unes['vendas_total'] / unes['produtos_unicos']).round(2)

        # Top 10 UNEs
        top_unes = unes.head(10)

        # Chart data
        chart_data = {
            "x": top_unes['une'].tolist(),
            "y": top_unes['eficiencia'].tolist(),
            "type": "bar",
            "show_values": True
        }

        # Tabela
        tabela = []
        for _, une in top_unes.iterrows():
            tabela.append({
                "une": une['une'],
                "vendas_total": float(une['vendas_total']),
                "produtos_unicos": int(une['produtos_unicos']),
                "segmentos_unicos": int(une['segmentos_unicos']),
                "eficiencia": float(une['eficiencia'])
            })

        # Resumo
        media_eficiencia = unes['eficiencia'].mean()
        summary = f"Comparativo de Eficiência entre UNEs:\n\n"
        summary += f"Eficiência média: R$ {media_eficiencia:,.2f} por produto\n"
        summary += f"Mais eficiente: {tabela[0]['une']} (R$ {tabela[0]['eficiencia']:,.2f}/produto)"
        summary += f"\nTotal de UNEs analisadas: {len(unes)}"

        return {
            "type": "chart",
            "title": "Eficiência de Vendas por UNE",
            "result": {
                "chart_data": chart_data,
                "unes": tabela,
                "total_unes": len(unes),
                "media_eficiencia": float(media_eficiencia)
            },
            "summary": summary,
            "tokens_used": 0
        }

    def _query_fabricantes_novos_vs_estabelecidos(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Compara performance entre fabricantes novos (baixo volume) vs estabelecidos (alto volume).
        Usa volume de vendas como proxy para classificar fabricantes.

        Args:
            df: DataFrame com dados
            params: {}

        Returns:
            Dict com comparação fabricantes
        """
        ddf = self._get_base_dask_df()
        logger.info(f"[>] Processando fabricantes_novos_vs_estabelecidos - params: {params}")

        # Agrupar por fabricante
        fabricantes = ddf.groupby('nome_fabricante').agg({
            'vendas_total': 'sum',
            'codigo': 'nunique'
        }).compute().reset_index()

        fabricantes.columns = ['fabricante', 'vendas_total', 'produtos_unicos']

        # Classificar: top 30% = estabelecidos, bottom 30% = novos
        threshold_estabelecidos = fabricantes['vendas_total'].quantile(0.70)
        threshold_novos = fabricantes['vendas_total'].quantile(0.30)

        estabelecidos = fabricantes[fabricantes['vendas_total'] >= threshold_estabelecidos].copy()
        novos = fabricantes[fabricantes['vendas_total'] <= threshold_novos].copy()

        # Estatísticas
        stats = {
            "estabelecidos": {
                "count": len(estabelecidos),
                "vendas_media": float(estabelecidos['vendas_total'].mean()),
                "vendas_total": float(estabelecidos['vendas_total'].sum()),
                "produtos_media": float(estabelecidos['produtos_unicos'].mean())
            },
            "novos": {
                "count": len(novos),
                "vendas_media": float(novos['vendas_total'].mean()),
                "vendas_total": float(novos['vendas_total'].sum()),
                "produtos_media": float(novos['produtos_unicos'].mean())
            }
        }

        # Resumo
        summary = f"Fabricantes: Novos vs Estabelecidos\n\n"
        summary += f"📊 Estabelecidos (top 30%):\n"
        summary += f"  - Quantidade: {stats['estabelecidos']['count']}\n"
        summary += f"  - Vendas médias: R$ {stats['estabelecidos']['vendas_media']:,.2f}\n"
        summary += f"  - Produtos médios: {stats['estabelecidos']['produtos_media']:.0f}\n\n"
        summary += f"🆕 Novos (bottom 30%):\n"
        summary += f"  - Quantidade: {stats['novos']['count']}\n"
        summary += f"  - Vendas médias: R$ {stats['novos']['vendas_media']:,.2f}\n"
        summary += f"  - Produtos médios: {stats['novos']['produtos_media']:.0f}"

        return {
            "type": "text",
            "title": "Fabricantes: Novos vs Estabelecidos",
            "result": stats,
            "summary": summary,
            "tokens_used": 0
        }

    def _query_fabricantes_exclusivos_multimarca(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Compara fabricantes exclusivos de uma UNE vs fabricantes presentes em múltiplas UNEs.

        Args:
            df: DataFrame com dados
            params: {}

        Returns:
            Dict com análise exclusividade fabricantes
        """
        ddf = self._get_base_dask_df()
        logger.info(f"[>] Processando fabricantes_exclusivos_multimarca - params: {params}")

        # Contar em quantas UNEs cada fabricante está presente
        fabricantes_unes = ddf.groupby('nome_fabricante')['une'].nunique().compute().reset_index()
        fabricantes_unes.columns = ['nome_fabricante', 'unes_count']

        # Pegar também volume de vendas
        fabricantes_vendas = ddf.groupby('nome_fabricante')['vendas_total'].sum().compute().reset_index()
        fabricantes = fabricantes_unes.merge(fabricantes_vendas, on='nome_fabricante')

        # Classificar
        exclusivos = fabricantes[fabricantes['unes_count'] == 1].copy()
        multimarca = fabricantes[fabricantes['unes_count'] > 1].copy()

        # Estatísticas
        stats = {
            "exclusivos": {
                "count": len(exclusivos),
                "vendas_media": float(exclusivos['vendas_total'].mean()) if len(exclusivos) > 0 else 0,
                "vendas_total": float(exclusivos['vendas_total'].sum()) if len(exclusivos) > 0 else 0
            },
            "multimarca": {
                "count": len(multimarca),
                "vendas_media": float(multimarca['vendas_total'].mean()) if len(multimarca) > 0 else 0,
                "vendas_total": float(multimarca['vendas_total'].sum()) if len(multimarca) > 0 else 0,
                "unes_media": float(multimarca['unes_count'].mean()) if len(multimarca) > 0 else 0
            }
        }

        # Top fabricantes multimarca
        top_multimarca = multimarca.nlargest(10, 'unes_count')[['nome_fabricante', 'unes_count', 'vendas_total']].to_dict('records')

        # Resumo
        summary = f"Fabricantes: Exclusivos vs Multimarca\n\n"
        summary += f"🏪 Exclusivos (1 UNE):\n"
        summary += f"  - Quantidade: {stats['exclusivos']['count']}\n"
        summary += f"  - Vendas médias: R$ {stats['exclusivos']['vendas_media']:,.2f}\n\n"
        summary += f"🌐 Multimarca (2+ UNEs):\n"
        summary += f"  - Quantidade: {stats['multimarca']['count']}\n"
        summary += f"  - Vendas médias: R$ {stats['multimarca']['vendas_media']:,.2f}\n"
        summary += f"  - UNEs médias: {stats['multimarca']['unes_media']:.1f}"

        return {
            "type": "text",
            "title": "Fabricantes: Exclusivos vs Multimarca",
            "result": {
                **stats,
                "top_multimarca": top_multimarca
            },
            "summary": summary,
            "tokens_used": 0
        }

    def _query_ciclo_vendas_consistente(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Identifica produtos com ciclo de vendas consistente vs irregular.
        Usa desvio padrão das frequências semanais.
        """
        ddf = self._get_base_dask_df()
        logger.info(f"[>] Processando ciclo_vendas_consistente - params: {params}")

        # Colunas de frequência semanal
        freq_cols = ['freq_semana_anterior_5', 'freq_semana_anterior_4', 'freq_semana_anterior_3',
                     'freq_semana_anterior_2', 'freq_semana_atual']

        # Verificar se colunas existem
        if not all(col in ddf.columns for col in freq_cols):
            return {
                "type": "fallback",
                "error": "Dados de frequência semanal não disponíveis",
                "summary": "Acionando fallback para processamento com IA.",
                "tokens_used": 0
            }

        # Calcular desvio padrão das frequências (consistência)
        df_temp = ddf[freq_cols].copy().compute()
        ddf['freq_std'] = df_temp.std(axis=1).compute()

        # Produtos com vendas (pelo menos em alguma semana)
        df_vendas = ddf[ddf[freq_cols].sum(axis=1) > 0].copy().compute()

        # Classificar: std baixo = consistente, std alto = irregular
        threshold = df_vendas['freq_std'].quantile(0.50)

        consistentes = df_vendas[df_vendas['freq_std'] <= threshold].nlargest(15, 'vendas_total')
        irregulares = df_vendas[df_vendas['freq_std'] > threshold].nlargest(15, 'vendas_total')

        # Resumo
        summary = f"Análise de Ciclo de Vendas:\n\n"
        summary += f"📊 Produtos Consistentes: {len(consistentes)} (desvio padrão ≤ {threshold:.2f})\n"
        summary += f"📈 Produtos Irregulares: {len(irregulares)} (desvio padrão > {threshold:.2f})\n\n"
        summary += f"Top 3 Consistentes: {', '.join(consistentes['nome_produto'].head(3).str[:30])}"

        return {
            "type": "text",
            "title": "Produtos: Ciclo Consistente vs Irregular",
            "result": {
                "consistentes": consistentes[['nome_produto', 'vendas_total', 'freq_std']].head(10).to_dict('records'),
                "irregulares": irregulares[['nome_produto', 'vendas_total', 'freq_std']].head(10).to_dict('records'),
                "threshold": float(threshold)
            },
            "summary": summary,
            "tokens_used": 0
        }

    def _query_estoque_baixo_alta_demanda(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Produtos com estoque baixo mas alta demanda (venda_30d alta).
        """
        ddf = self._get_base_dask_df()
        logger.info(f"[>] Processando estoque_baixo_alta_demanda - params: {params}")

        
        return {
                "type": "fallback",
                "error": "Dados de estoque não disponíveis",
                "summary": "Acionando fallback para processamento com IA.",
                "tokens_used": 0
            }

        # Produtos com vendas nos últimos 30 dias
        df_vendas = ddf[ddf['venda_30_d'] > 0].copy().compute()

        # Calcular dias de estoque (estoque / média diária)
        df_vendas['media_diaria'] = df_vendas['venda_30_d'] / 30
        df_vendas['dias_estoque'] = (df_vendas['estoque_atual'] / (df_vendas['media_diaria'] + 0.01)).fillna(0)

        # Estoque baixo = menos de 15 dias + demanda alta (acima da mediana)
        mediana_demanda = df_vendas['venda_30_d'].quantile(0.50)

        produtos_risco = df_vendas[
            (df_vendas['dias_estoque'] < 15) &
            (df_vendas['venda_30_d'] >= mediana_demanda)
        ].nlargest(20, 'venda_30_d')

        # Tabela
        tabela = []
        for _, prod in produtos_risco.iterrows():
            tabela.append({
                "codigo": str(prod['codigo']),
                "produto": prod['nome_produto'][:50],
                "estoque": float(prod.get('estoque_atual', 0)),
                "venda_30d": float(prod['venda_30_d']),
                "dias_estoque": float(prod['dias_estoque']),
                "segmento": prod['nomesegmento']
            })

        summary = f"Produtos com Estoque Baixo e Alta Demanda:\n\n"
        summary += f"Total identificado: {len(produtos_risco)}\n"
        summary += f"Critério: Estoque < 15 dias + Demanda ≥ {mediana_demanda:.0f} (mediana)"
        if tabela:
            summary += f"\nMaior risco: {tabela[0]['produto']} ({tabela[0]['dias_estoque']:.1f} dias)"

            return {
            "type": "table",
            "title": "Produtos com Estoque Baixo e Alta Demanda",
            "result": {
                "produtos": tabela,
                "total": len(tabela),
                "mediana_demanda": float(mediana_demanda)
            },
            "summary": summary,
            "tokens_used": 0
        }

    def _query_leadtime_vs_performance(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Relação entre leadtime e performance de vendas.
        """
        ddf = self._get_base_dask_df()
        logger.info(f"[>] Processando leadtime_vs_performance - params: {params}")

        
        return {
                "type": "fallback",
                "error": "Dados de leadtime não disponíveis",
                "summary": "Acionando fallback para processamento com IA.",
                "tokens_used": 0
            }

        # Produtos com leadtime definido e vendas
        df_lead = ddf[(ddf['leadtime_lv'].notna()) & (ddf['leadtime_lv'] > 0) & (ddf['vendas_total'] > 0)].copy().compute()

        if df_lead.empty:
            return {
                "type": "text",
                "title": "Leadtime vs Performance",
                "result": {"message": "Sem dados de leadtime disponíveis"},
                "summary": "Dados de leadtime não encontrados na amostra",
                "tokens_used": 0
            }

        # Classificar por leadtime
        df_lead['leadtime_categoria'] = pd.cut(df_lead['leadtime_lv'], bins=[0, 7, 15, 30, 999],
                                                labels=['Rápido (0-7d)', 'Médio (8-15d)', 'Lento (16-30d)', 'Muito Lento (30+d)'])

        # Agrupar por categoria
        analise = df_lead.groupby('leadtime_categoria', observed=True).agg({
            'vendas_total': ['mean', 'sum', 'count'],
            'leadtime_lv': 'mean'
        }).reset_index()

        analise.columns = ['categoria', 'vendas_media', 'vendas_total', 'count', 'leadtime_medio']

        summary = f"Relação Leadtime vs Performance:\n\n"
        for _, row in analise.iterrows():
            summary += f"{row['categoria']}: {row['count']} produtos, Vendas médias: R$ {row['vendas_media']:,.2f}\n"

            return {
            "type": "text",
            "title": "Leadtime vs Performance de Vendas",
            "result": {
                "analise": analise.to_dict('records'),
                "correlacao": "Análise por categoria de leadtime"
            },
            "summary": summary,
            "tokens_used": 0
        }

    def _query_rotacao_estoque_avancada(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Produtos com maior rotação de estoque (venda_30d / estoque)."""
        ddf = self._get_base_dask_df()
        logger.info(f"[>] Processando rotacao_estoque_avancada - params: {params}")

        
        return {
                "type": "fallback",
                "error": "Dados de estoque não disponíveis",
                "summary": "Acionando fallback para processamento com IA.",
                "tokens_used": 0
            }

        # Produtos com estoque e vendas
        df_rot = ddf[(ddf['estoque_atual'] > 0) & (ddf['venda_30_d'] > 0)].copy().compute()

        # Calcular rotação mensal (vendas / estoque)
        df_rot['rotacao'] = (df_rot['venda_30_d'] / df_rot['estoque_atual']).round(2)

        # Top 20 produtos com maior rotação
        top_rotacao = df_rot.nlargest(20, 'rotacao')

        # Tabela
        tabela = []
        for _, prod in top_rotacao.iterrows():
            tabela.append({
                "codigo": str(prod['codigo']),
                "produto": prod['nome_produto'][:50],
                "estoque": float(prod['estoque_atual']),
                "venda_30d": float(prod['venda_30_d']),
                "rotacao": float(prod['rotacao']),
                "segmento": prod['nomesegmento']
            })

        summary = f"Top 20 Produtos com Maior Rotação de Estoque:\n\n"
        if tabela:
            summary += f"Líder: {tabela[0]['produto']} (rotação: {tabela[0]['rotacao']:.2f}x/mês)\n"
            summary += f"Média de rotação: {top_rotacao['rotacao'].mean():.2f}x/mês"

            return {
            "type": "table",
            "title": "Produtos com Maior Rotação de Estoque",
            "result": {
                "produtos": tabela,
                "total": len(tabela)
            },
            "summary": summary,
            "tokens_used": 0
        }

    def _query_exposicao_vs_vendas(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Análise de exposição mínima vs vendas.
        """
        ddf = self._get_base_dask_df()
        logger.info(f"[>] Processando exposicao_vs_vendas - params: {params}")

        
        return {
                "type": "fallback",
                "error": "Dados de exposição não disponíveis",
                "summary": "Acionando fallback para processamento com IA.",
                "tokens_used": 0
            }

        # Produtos com exposição definida e vendas
        df_exp = ddf[(ddf['exposicao_minima_une'].notna()) & (ddf['vendas_total'] > 0)].copy().compute()

        if df_exp.empty:
            return {
                "type": "text",
                "title": "Exposição vs Vendas",
                "result": {"message": "Sem dados de exposição disponíveis"},
                "summary": "Dados de exposição não encontrados",
                "tokens_used": 0
            }

        # Converter exposição para numérico
        df_exp['exposicao_num'] = pd.to_numeric(df_exp['exposicao_minima_une'], errors='coerce')
        df_exp = df_exp[df_exp['exposicao_num'].notna()]

        # Produtos com exposição mínima mas boas vendas
        mediana_exp = df_exp['exposicao_num'].quantile(0.30)
        mediana_vendas = df_exp['vendas_total'].quantile(0.70)

        produtos_destaque = df_exp[
            (df_exp['exposicao_num'] <= mediana_exp) &
            (df_exp['vendas_total'] >= mediana_vendas)
        ].nlargest(15, 'vendas_total')

        tabela = []
        for _, prod in produtos_destaque.iterrows():
            tabela.append({
                "codigo": str(prod['codigo']),
                "produto": prod['nome_produto'][:50],
                "exposicao": float(prod['exposicao_num']),
                "vendas_total": float(prod['vendas_total']),
                "segmento": prod['nomesegmento']
            })

        summary = f"Produtos com Exposição Mínima mas Alto Desempenho:\n\n"
        summary += f"Total identificado: {len(produtos_destaque)}\n"
        summary += f"Critério: Exposição ≤ {mediana_exp:.0f} + Vendas ≥ {mediana_vendas:,.0f}"

        return {
            "type": "table",
            "title": "Exposição Mínima vs Alto Desempenho",
            "result": {
                "produtos": tabela,
                "total": len(tabela)
            },
            "summary": summary,
            "tokens_used": 0
        }

    def _query_estoque_cd_vs_vendas(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Eficiência logística: relação entre estoque CD vs vendas.
        """
        ddf = self._get_base_dask_df()
        logger.info(f"[>] Processando estoque_cd_vs_vendas - params: {params}")

        
        return {
                "type": "fallback",
                "error": "Dados de estoque CD não disponíveis",
                "summary": "Acionando fallback para processamento com IA.",
                "tokens_used": 0
            }

        # Produtos com estoque CD e vendas
        df_cd = ddf[(ddf['estoque_cd'] > 0) & (ddf['vendas_total'] > 0)].copy().compute()

        # Calcular ratio CD/vendas
        df_cd['ratio_cd_vendas'] = (df_cd['estoque_cd'] / df_cd['vendas_total']).round(3)

        # Análise por quartis
        q1 = df_cd['ratio_cd_vendas'].quantile(0.25)
        q3 = df_cd['ratio_cd_vendas'].quantile(0.75)

        # Produtos eficientes (ratio baixo = pouco estoque, muita venda)
        eficientes = df_cd[df_cd['ratio_cd_vendas'] <= q1].nlargest(15, 'vendas_total')

        # Produtos com excesso CD (ratio alto)
        excesso_cd = df_cd[df_cd['ratio_cd_vendas'] >= q3].nlargest(15, 'estoque_cd')

        summary = f"Eficiência Logística - Estoque CD vs Vendas:\n\n"
        summary += f"📦 Eficientes (CD/Vendas ≤ {q1:.3f}): {len(eficientes)} produtos\n"
        summary += f"⚠️ Excesso CD (CD/Vendas ≥ {q3:.3f}): {len(excesso_cd)} produtos"

        return {
            "type": "text",
            "title": "Eficiência Logística: Estoque CD vs Vendas",
            "result": {
                "eficientes": eficientes[['nome_produto', 'estoque_cd', 'vendas_total', 'ratio_cd_vendas']].head(10).to_dict('records'),
                "excesso_cd": excesso_cd[['nome_produto', 'estoque_cd', 'vendas_total', 'ratio_cd_vendas']].head(10).to_dict('records'),
                "quartis": {"q1": float(q1), "q3": float(q3)}
            },
            "summary": summary,
            "tokens_used": 0
        }

    def _query_analise_geral(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Router inteligente para análises gerais.
        Sub-classifica queries genéricas baseado em keywords e roteia para métodos específicos.
        """
        ddf = self._get_base_dask_df()
        # Pegar query original do usuário
        user_query = params.get('user_query', '').lower()

        logger.info(f"[ANALISE_GERAL ROUTER] Query original: {user_query}")

        # Sub-classificação por keywords - ordem de prioridade

        # 1. ABC Analysis
        if any(kw in user_query for kw in ['abc', 'curva abc', 'classificação abc', 'classe a', 'classe b', 'classe c']):
            logger.info("[ANALISE_GERAL ROUTER] -> Roteando para _query_analise_abc")
            return self._query_analise_abc(params)

        # 2. Sazonalidade
        if any(kw in user_query for kw in ['sazonalidade', 'sazonal', 'sazonais', 'padrão sazonal', 'variação mensal']):
            logger.info("[ANALISE_GERAL ROUTER] -> Roteando para _query_sazonalidade")
            return self._query_sazonalidade(params)

        # 3. Crescimento
        if any(kw in user_query for kw in ['crescimento', 'cresceu', 'aumentou', 'evolução', 'crescente']):
            logger.info("[ANALISE_GERAL ROUTER] -> Roteando para _query_crescimento_segmento")
            return self._query_crescimento_segmento(params)

        # 4. Tendência
        if any(kw in user_query for kw in ['tendência', 'tendencia', 'trend', 'projeção']):
            logger.info("[ANALISE_GERAL ROUTER] -> Roteando para _query_tendencia_vendas")
            return self._query_tendencia_vendas(params)

        # 5. Pico de vendas
        if any(kw in user_query for kw in ['pico', 'máximo', 'maximo', 'maior venda', 'record']):
            logger.info("[ANALISE_GERAL ROUTER] -> Roteando para _query_pico_vendas")
            return self._query_pico_vendas(params)

        # 6. Concentração/Dependência
        if any(kw in user_query for kw in ['concentração', 'concentracao', 'dependência', 'dependencia', 'diversificação', 'diversificacao']):
            logger.info("[ANALISE_GERAL ROUTER] -> Roteando para _query_diversidade_produtos")
            return self._query_diversidade_produtos(params)

        # 7. Distribuição por categoria
        if any(kw in user_query for kw in ['distribuição', 'distribuicao', 'categoria', 'categorias']):
            logger.info("[ANALISE_GERAL ROUTER] -> Roteando para _query_distribuicao_categoria")
            return self._query_distribuicao_categoria(params)

        # 8. Estoque
        if any(kw in user_query for kw in ['estoque alto', 'excesso de estoque', 'estoque parado', 'muito estoque']):
            logger.info("[ANALISE_GERAL ROUTER] -> Roteando para _query_estoque_alto")
            return self._query_estoque_alto(params)

        # 9. Produtos acima da média
        if any(kw in user_query for kw in ['acima da média', 'acima da media', 'superam', 'ultrapassam']):
            logger.info("[ANALISE_GERAL ROUTER] -> Roteando para _query_produtos_acima_media")
            return self._query_produtos_acima_media(params)

        # 10. Ranking/Top produtos
        if any(kw in user_query for kw in ['top', 'ranking', 'melhores', 'maiores', 'principais']):
            logger.info("[ANALISE_GERAL ROUTER] -> Roteando para _query_ranking_geral")
            return self._query_ranking_geral(params)

        # 11. Comparação de segmentos
        if any(kw in user_query for kw in ['comparar', 'comparação', 'comparacao', 'versus', 'vs', 'entre']):
            logger.info("[ANALISE_GERAL ROUTER] -> Roteando para _query_comparacao_segmentos")
            return self._query_comparacao_segmentos(params)

        # 12. Evolução mês a mês
        if any(kw in user_query for kw in ['evolução', 'evolucao', 'mês a mês', 'mes a mes', 'mensal']):
            logger.info("[ANALISE_GERAL ROUTER] -> Roteando para _query_evolucao_mes_a_mes")
            return self._query_evolucao_mes_a_mes(params)

        # 13. Análise geral de vendas - padrão fallback com informações básicas
        logger.info("[ANALISE_GERAL ROUTER] -> Gerando análise geral padrão")

        # Calcular métricas gerais
        total_vendas = ddf['vendas_total'].sum().compute()
        total_produtos = ddf['nome_produto'].nunique().compute()
        total_unes = ddf['une'].nunique().compute() if 'une' in ddf.columns else 0

        # CORREÇÃO: Média de vendas POR PRODUTO (agrupar antes de calcular média)
        # Antes: calculava média de todas as linhas (errado)
        # Agora: agrupa por produto, soma vendas, depois calcula média (correto)
        vendas_por_produto = ddf.groupby('codigo')['vendas_total'].sum()
        media_vendas = vendas_por_produto.mean().compute()

        # Top 5 produtos
        top_5 = ddf.nlargest(5, 'vendas_total')[['nome_produto', 'vendas_total']].compute()

        summary = f"Análise Geral do Período:\n📊 Métricas Principais:\n- Vendas Totais: R$ {total_vendas:,.2f}\n- Total de Produtos: {total_produtos}\n- Total de UNEs: {total_unes}\n- Média de Vendas por Produto: R$ {media_vendas:,.2f}\n\n🏆 Top 5 Produtos:"
        for idx, row in top_5.iterrows():
            summary += f"\n{idx+1}. {row['nome_produto']}: R$ {row['vendas_total']:,.2f}"

            return {
            "type": "text",
            "title": "Análise Geral de Vendas",
            "result": {
                "total_vendas": float(total_vendas),
                "total_produtos": int(total_produtos),
                "total_unes": int(total_unes),
                "media_vendas": float(media_vendas),
                "top_5_produtos": top_5.to_dict('records')
            },
            "summary": summary,
            "tokens_used": 0
        }

    def _query_fallback(self, query_type: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Fallback para queries não implementadas, sinalizando para usar o grafo principal."""
        logger.warning(f"Consulta não implementada ou não compreendida no DirectQueryEngine: {query_type}. Acionando fallback para o agent_graph.")
        return {
            "type": "fallback",
            "error": "Consulta não compreendida pelo motor de busca rápida. Usando IA avançada.",
            "summary": "Acionando fallback para processamento com IA.",
            "title": "Necessário Processamento Avançado"
        }

    def process_query(self, user_query: str) -> Dict[str, Any]:
        """Processa query completa: classifica + executa SEM usar LLM."""
        start_time = datetime.now()

        # Classificar intenção SEM LLM
        query_type, params = self.classify_intent_direct(user_query)

        # Adicionar user_query aos params para o router inteligente
        params['user_query'] = user_query

        # Executar consulta direta
        result = self.execute_direct_query(query_type, params)

        # Adicionar metadados
        result['query_original'] = user_query
        result['query_type'] = query_type
        result['processing_time'] = (datetime.now() - start_time).total_seconds()
        result['method'] = 'direct_query'  # Indica que NÃO usou LLM

        logger.info(f"Query processada em {result['processing_time']:.2f}s - ZERO tokens LLM")

        return result

    def get_available_queries(self) -> List[Dict[str, str]]:
        """Retorna lista de consultas disponíveis para sugestões."""
        return [
            {"keyword": keyword, "description": f"Executa consulta: {query_type}"}
            for keyword, query_type in list(self.keywords_map.items())[:20]
        ]
