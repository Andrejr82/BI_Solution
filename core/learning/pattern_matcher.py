"""
Módulo para identificar padrões de queries e injetar exemplos relevantes.
"""

import json
import os
import logging
from typing import Dict, List, Optional, Tuple


class PatternMatcher:
    """
    Identifica qual padrão de query melhor se encaixa na pergunta do usuário
    e retorna exemplos relevantes para guiar o LLM.
    """

    def __init__(self, patterns_file: str = None):
        """
        Inicializa o matcher com arquivo de padrões.

        Args:
            patterns_file: Caminho para query_patterns.json (opcional)
        """
        self.logger = logging.getLogger(__name__)

        if patterns_file is None:
            patterns_file = os.path.join(os.getcwd(), "data", "query_patterns.json")

        try:
            with open(patterns_file, 'r', encoding='utf-8') as f:
                self.patterns = json.load(f)
            self.logger.info(f"✅ {len(self.patterns)} padrões de query carregados")
        except Exception as e:
            self.logger.error(f"❌ Erro ao carregar padrões: {e}")
            self.patterns = {}

    def match_pattern(self, user_query: str) -> Optional[Dict]:
        """
        Identifica qual padrão a query se encaixa melhor.

        Args:
            user_query: Query do usuário

        Returns:
            Dicionário com padrão identificado e exemplos, ou None
        """
        query_lower = user_query.lower()

        # Calcular score para cada padrão
        scores = {}

        for pattern_name, pattern_data in self.patterns.items():
            score = 0

            # Verificar keywords positivas
            for keyword in pattern_data.get('keywords', []):
                if keyword.lower() in query_lower:
                    score += 1

            # Verificar keywords de exclusão (reduz score)
            for exclude_kw in pattern_data.get('exclude_keywords', []):
                if exclude_kw.lower() in query_lower:
                    score -= 2

            if score > 0:
                scores[pattern_name] = score

        # Retornar padrão com maior score
        if scores:
            best_pattern_name = max(scores, key=scores.get)
            best_pattern = self.patterns[best_pattern_name].copy()
            best_pattern['pattern_name'] = best_pattern_name
            best_pattern['score'] = scores[best_pattern_name]

            self.logger.info(
                f"🎯 Padrão identificado: '{best_pattern_name}' (score: {scores[best_pattern_name]})"
            )

            return best_pattern

        self.logger.debug("⚠️ Nenhum padrão identificado para a query")
        return None

    def get_all_matches(self, user_query: str, top_k: int = 3) -> List[Tuple[str, Dict, int]]:
        """
        Retorna os top K padrões mais relevantes.

        Args:
            user_query: Query do usuário
            top_k: Número de padrões a retornar

        Returns:
            Lista de tuplas (pattern_name, pattern_data, score)
        """
        query_lower = user_query.lower()
        scores = []

        for pattern_name, pattern_data in self.patterns.items():
            score = 0

            # Calcular score
            for keyword in pattern_data.get('keywords', []):
                if keyword.lower() in query_lower:
                    score += 1

            for exclude_kw in pattern_data.get('exclude_keywords', []):
                if exclude_kw.lower() in query_lower:
                    score -= 2

            if score > 0:
                scores.append((pattern_name, pattern_data, score))

        # Ordenar por score e retornar top K
        scores.sort(key=lambda x: x[2], reverse=True)
        return scores[:top_k]

    def build_examples_context(self, user_query: str, max_examples: int = 2) -> str:
        """
        Constrói contexto com exemplos relevantes para adicionar ao prompt.

        Args:
            user_query: Query do usuário
            max_examples: Número máximo de exemplos por padrão

        Returns:
            String formatada com exemplos prontos para o prompt
        """
        matched_pattern = self.match_pattern(user_query)

        if not matched_pattern:
            return ""

        context = "**📚 EXEMPLOS RELEVANTES PARA SUA QUERY:**\n\n"
        context += f"**Padrão identificado:** {matched_pattern['pattern_name']}\n"
        context += f"**Descrição:** {matched_pattern['description']}\n\n"

        examples = matched_pattern.get('examples', [])[:max_examples]

        for i, example in enumerate(examples, 1):
            context += f"**Exemplo {i}:**\n"
            context += f"Query: \"{example['user_query']}\"\n"
            context += f"Código:\n```python\n{example['code']}\n```\n"
            context += f"Resultado esperado: {example['expected_output']}\n\n"

        context += "**⚡ USE OS EXEMPLOS ACIMA COMO REFERÊNCIA para gerar código similar!**\n"
        context += "Adapte a lógica dos exemplos para responder à query do usuário.\n\n"

        return context

    def get_validation_hints(self, user_query: str) -> List[str]:
        """
        Retorna dicas de validação específicas para o padrão identificado.

        Args:
            user_query: Query do usuário

        Returns:
            Lista de hints para validação
        """
        matched_pattern = self.match_pattern(user_query)

        if not matched_pattern:
            return []

        hints = []
        pattern_name = matched_pattern.get('pattern_name', '')

        # Hints específicos por padrão
        if pattern_name == 'top_n':
            hints.append("DEVE usar .head(N) para limitar resultados")
            hints.append("DEVE ter agregação com groupby()")

        elif pattern_name == 'ranking_completo':
            hints.append("NÃO deve ter .head() - mostrar todos os resultados")
            hints.append("DEVE ordenar com sort_values()")

        elif pattern_name == 'comparacao':
            hints.append("DEVE usar .isin() para múltiplos valores")
            hints.append("DEVE ter exatamente N linhas no resultado (N = itens comparados)")

        elif pattern_name == 'agregacao_simples':
            hints.append("Resultado pode ser um valor único, não necessariamente DataFrame")
            hints.append("Usar sum(), mean(), count(), etc.")

        elif pattern_name == 'estoque_baixo':
            hints.append("Filtrar por ESTOQUE_UNE == 0 ou < threshold")
            hints.append("Incluir coluna VENDA_30DD para contexto")

        elif pattern_name == 'distribuicao':
            hints.append("DEVE agrupar por categoria/segmento")
            hints.append("Ordenar por valor descendente")

        elif pattern_name == 'percentual':
            hints.append("Calcular total primeiro")
            hints.append("Criar coluna 'Percentual' com (valor/total * 100)")

        return hints

    def suggest_columns(self, user_query: str) -> List[str]:
        """
        Sugere colunas relevantes baseadas no padrão identificado.

        Args:
            user_query: Query do usuário

        Returns:
            Lista de nomes de colunas sugeridas
        """
        query_lower = user_query.lower()
        suggested = ['NOME']  # Sempre incluir nome do produto

        # Análise de keywords para sugerir colunas
        if any(kw in query_lower for kw in ['venda', 'vendas', 'faturamento', 'receita']):
            suggested.append('VENDA_30DD')

        if any(kw in query_lower for kw in ['estoque', 'inventário', 'disponível']):
            suggested.append('ESTOQUE_UNE')

        if any(kw in query_lower for kw in ['preço', 'valor', 'custo']):
            suggested.append('LIQUIDO_38')

        if any(kw in query_lower for kw in ['segmento']):
            suggested.append('NOMESEGMENTO')

        if any(kw in query_lower for kw in ['categoria']):
            suggested.append('NomeCategoria')

        if any(kw in query_lower for kw in ['grupo']):
            suggested.append('NOMEGRUPO')

        if any(kw in query_lower for kw in ['fabricante', 'marca', 'fornecedor']):
            suggested.append('NomeFabricante')

        if any(kw in query_lower for kw in ['une', 'loja', 'unidade']):
            suggested.append('UNE_NOME')

        return list(dict.fromkeys(suggested))  # Remove duplicatas mantendo ordem
