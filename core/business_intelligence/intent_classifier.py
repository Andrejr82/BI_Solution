"""
Intent Classifier usando Gemini com Structured Output.
Classifica intenções de queries em linguagem natural e extrai parâmetros estruturados.

ZERO RISCO: Este arquivo é NOVO e não afeta o sistema atual.
O sistema antigo continua funcionando normalmente.
"""

import os
import json
from typing import Dict, Any, Optional, List
from datetime import datetime

# Imports opcionais - não quebra se não tiver
try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False
    # Nota: logger ainda não está disponível aqui, então apenas skip

from core.utils.logger_config import get_logger

logger = get_logger('agent_bi.intent_classifier')


class IntentClassifier:
    """
    Classifica intenções de queries usando Gemini com Structured Output.

    Funcionalidades:
    - Entende perguntas em linguagem natural
    - Extrai operações, filtros, agregações
    - Retorna JSON estruturado para execução
    - Cache de respostas para economia de tokens
    """

    def __init__(self, gemini_api_key: Optional[str] = None):
        """
        Inicializa o classificador.

        Args:
            gemini_api_key: API key do Gemini (se None, pega do .env)
        """
        self.enabled = False
        self.model = None
        self.cache_hits = 0
        self.cache_misses = 0
        self.total_tokens_used = 0

        # Tentar inicializar Gemini
        if GEMINI_AVAILABLE:
            api_key = gemini_api_key or os.getenv('GEMINI_API_KEY')
            if api_key:
                try:
                    genai.configure(api_key=api_key)
                    self.model = genai.GenerativeModel('gemini-2.0-flash-exp')
                    self.enabled = True
                    logger.info("[OK] IntentClassifier inicializado com Gemini 2.0 Flash")
                except Exception as e:
                    logger.error(f"[ERRO] Erro ao inicializar Gemini: {e}")
                    self.enabled = False
            else:
                logger.warning("[AVISO] GEMINI_API_KEY não encontrada. IntentClassifier desabilitado.")
        else:
            logger.warning("[AVISO] google-generativeai não disponível. IntentClassifier desabilitado.")

    def get_schema_info(self) -> str:
        """Retorna informações sobre o schema do DataFrame para o LLM."""
        return """
# SCHEMA DO DATAFRAME

## Colunas Principais:
- **codigo**: Código do produto (int)
- **nome_produto**: Nome do produto (str)
- **une_nome**: Nome da UNE/filial (str: SCR, CFR, MAD, TIJ, etc.)
- **une**: Código numérico da UNE (int: 261, 2720, etc.)
- **nomesegmento**: Segmento do produto (str: TECIDOS, ARMARINHO, PAPELARIA, etc.)
- **NOMECATEGORIA**: Categoria do produto (str)
- **nomegrupo**: Grupo do produto (str)
- **NOMESUBGRUPO**: Subgrupo do produto (str)
- **NOMEFABRICANTE**: Fabricante (str)
- **vendas_total**: Total de vendas (float)
- **preco_38_percent**: Preço com 38% de margem (float)
- **estoque_atual**: Estoque atual (int)
- **estoque_cd**: Estoque no CD (int)
- **mes_01** até **mes_12**: Vendas mensais (float)

## Sinônimos aceitos:
- UNE = filial = loja = unidade
- Categoria = segmento (podem ser usados intercambiavelmente)
- Produto = item = mercadoria
"""

    def classify_intent(self, user_query: str, dataframe_columns: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Classifica a intenção da query do usuário.

        Args:
            user_query: Pergunta do usuário em linguagem natural
            dataframe_columns: Lista de colunas disponíveis no DataFrame (opcional)

        Returns:
            Dict com estrutura:
            {
                "operation": str,  # tipo de operação
                "filters": dict,   # filtros a aplicar
                "aggregations": dict,  # agregações
                "sort_by": str,    # coluna para ordenar
                "limit": int,      # limite de resultados
                "group_by": str,   # agrupar por
                "confidence": float,  # confiança (0-1)
                "raw_response": str  # resposta do LLM
            }
        """
        if not self.enabled:
            logger.warning("[AVISO] IntentClassifier desabilitado. Use sistema de fallback.")
            return {
                "operation": "unknown",
                "confidence": 0.0,
                "error": "IntentClassifier não disponível"
            }

        try:
            # Criar prompt estruturado
            prompt = self._build_prompt(user_query, dataframe_columns)

            # Chamar Gemini
            logger.info(f"[INFO] Classificando intent: '{user_query[:50]}...'")
            response = self.model.generate_content(
                prompt,
                generation_config=genai.GenerationConfig(
                    temperature=0.1,  # Baixa temperatura para respostas consistentes
                    top_p=0.95,
                    top_k=40,
                    max_output_tokens=1024,
                    response_mime_type="application/json"
                )
            )

            # Parsear resposta
            result = self._parse_response(response.text)

            # Contabilizar tokens
            if hasattr(response, 'usage_metadata'):
                tokens = response.usage_metadata.total_token_count
                self.total_tokens_used += tokens
                logger.info(f"[STATS] Tokens usados: {tokens} (total: {self.total_tokens_used})")

            result['raw_response'] = response.text
            result['user_query'] = user_query

            logger.info(f"[OK] Intent classificado: {result['operation']} (confiança: {result.get('confidence', 0):.2f})")

            return result

        except Exception as e:
            logger.error(f"[ERRO] Erro ao classificar intent: {e}")
            import traceback
            traceback.print_exc()
            return {
                "operation": "unknown",
                "confidence": 0.0,
                "error": str(e)
            }

    def _build_prompt(self, user_query: str, dataframe_columns: Optional[List[str]] = None) -> str:
        """Constrói o prompt para o LLM."""

        schema_info = self.get_schema_info()

        columns_info = ""
        if dataframe_columns:
            columns_info = f"\n## Colunas disponíveis no DataFrame:\n{', '.join(dataframe_columns)}\n"

        prompt = f"""Você é um especialista em análise de dados e SQL. Analise a pergunta do usuário e extraia a intenção e parâmetros estruturados.

{schema_info}
{columns_info}

# PERGUNTA DO USUÁRIO:
"{user_query}"

# SUA TAREFA:
Retorne um JSON estruturado com:

1. **operation**: Tipo de operação (escolha UMA):
   - "ranking_produtos": Top N produtos por vendas
   - "ranking_unes": Top N UNEs por vendas
   - "ranking_segmentos": Top N segmentos por vendas
   - "ranking_categorias": Top N categorias por vendas
   - "distribuicao_categoria": Distribuição por categoria
   - "consulta_une": Informações de uma UNE específica
   - "analise_estoque": Análise de estoque (baixo, zero, alto)
   - "evolucao_temporal": Evolução ao longo do tempo
   - "comparacao": Comparar entre entidades
   - "agregacao": Agregação de valores
   - "filtro_complexo": Múltiplos filtros combinados

2. **filters**: Dicionário de filtros a aplicar:
   - "une_nome": Nome da UNE (str)
   - "segmento": Nome do segmento (str)
   - "categoria": Nome da categoria (str)
   - "codigo": Código do produto (int)
   - "estoque_maior_que": Valor (int)
   - "estoque_menor_que": Valor (int)
   - "estoque_igual_a": Valor (int)
   - "preco_maior_que": Valor (float)
   - "preco_menor_que": Valor (float)

3. **aggregations**: Dicionário de agregações:
   - "sum": Coluna para somar
   - "avg": Coluna para média
   - "count": Contar registros
   - "min": Valor mínimo
   - "max": Valor máximo

4. **sort_by**: Coluna para ordenar (str)

5. **sort_order**: Ordem ("asc" ou "desc")

6. **limit**: Número de resultados (int, padrão: 10)

7. **group_by**: Agrupar por coluna (str)

8. **confidence**: Sua confiança na classificação (0.0 a 1.0)

# EXEMPLOS:

**Pergunta**: "top 10 tecidos une cfr"
**JSON**:
{{
  "operation": "ranking_produtos",
  "filters": {{"segmento": "TECIDOS", "une_nome": "CFR"}},
  "aggregations": {{"sum": "vendas_total"}},
  "sort_by": "vendas_total",
  "sort_order": "desc",
  "limit": 10,
  "group_by": "codigo",
  "confidence": 0.95
}}

**Pergunta**: "quais categorias de tecidos com estoque zero?"
**JSON**:
{{
  "operation": "distribuicao_categoria",
  "filters": {{"segmento": "TECIDOS", "estoque_igual_a": 0}},
  "aggregations": {{"count": "codigo"}},
  "sort_by": "count",
  "sort_order": "desc",
  "limit": 100,
  "group_by": "NOMECATEGORIA",
  "confidence": 0.9
}}

**Pergunta**: "vendas totais de cada une"
**JSON**:
{{
  "operation": "ranking_unes",
  "filters": {{}},
  "aggregations": {{"sum": "vendas_total"}},
  "sort_by": "vendas_total",
  "sort_order": "desc",
  "limit": 100,
  "group_by": "une_nome",
  "confidence": 0.95
}}

# IMPORTANTE:
- Use EXATAMENTE os nomes de colunas do schema
- Normalize valores: "tecidos" → "TECIDOS", "cfr" → "CFR"
- Se não tiver certeza, retorne confidence < 0.7
- Sempre retorne um JSON válido

Retorne APENAS o JSON, sem texto adicional.
"""
        return prompt

    def _parse_response(self, response_text: str) -> Dict[str, Any]:
        """Parseia a resposta do LLM."""
        try:
            # Tentar parsear JSON
            result = json.loads(response_text)

            # Validar campos obrigatórios
            if 'operation' not in result:
                result['operation'] = 'unknown'

            if 'filters' not in result:
                result['filters'] = {}

            if 'confidence' not in result:
                result['confidence'] = 0.5

            if 'limit' not in result:
                result['limit'] = 10

            if 'aggregations' not in result:
                result['aggregations'] = {}

            return result

        except json.JSONDecodeError as e:
            logger.error(f"[ERRO] Erro ao parsear JSON: {e}")
            logger.error(f"Resposta recebida: {response_text}")
            return {
                "operation": "unknown",
                "confidence": 0.0,
                "error": f"JSON inválido: {e}",
                "raw_text": response_text
            }

    def get_stats(self) -> Dict[str, Any]:
        """Retorna estatísticas de uso."""
        return {
            "enabled": self.enabled,
            "total_tokens_used": self.total_tokens_used,
            "cache_hits": self.cache_hits,
            "cache_misses": self.cache_misses,
            "cache_hit_rate": self.cache_hits / max(self.cache_hits + self.cache_misses, 1)
        }
