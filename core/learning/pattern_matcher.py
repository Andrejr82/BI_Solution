"""
Pattern Matcher - Few-Shot Learning System

Este módulo implementa o sistema de Few-Shot Learning que identifica padrões
de queries similares e injeta exemplos relevantes no prompt do LLM.

Parte do Pilar 2: Few-Shot Learning
"""

import json
import re
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass


@dataclass
class MatchedPattern:
    """Representa um padrão identificado com seus exemplos"""
    pattern_name: str
    description: str
    score: int
    keywords_matched: List[str]
    examples: List[Dict[str, str]]


class PatternMatcher:
    """
    Identifica automaticamente qual padrão a query do usuário se encaixa
    e retorna exemplos relevantes para injeção no prompt.

    Exemplo de uso:
        matcher = PatternMatcher()
        matched = matcher.match_pattern("top 10 produtos mais vendidos")
        if matched:
            print(f"Padrão: {matched.pattern_name}")
            print(f"Exemplos: {len(matched.examples)}")
    """

    def __init__(self, patterns_file: Optional[str] = None):
        """
        Inicializa o PatternMatcher carregando os padrões de queries.

        Args:
            patterns_file: Caminho para o arquivo JSON com padrões.
                          Se None, usa o caminho padrão.
        """
        if patterns_file is None:
            # Caminho padrão relativo ao diretório raiz do projeto
            base_dir = Path(__file__).parent.parent.parent
            patterns_file = base_dir / "data" / "query_patterns.json"

        self.patterns_file = Path(patterns_file)
        self.patterns = self._load_patterns()

    def _load_patterns(self) -> Dict[str, Any]:
        """Carrega os padrões do arquivo JSON"""
        try:
            with open(self.patterns_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"⚠️ Arquivo de padrões não encontrado: {self.patterns_file}")
            return {}
        except json.JSONDecodeError as e:
            print(f"⚠️ Erro ao decodificar JSON: {e}")
            return {}

    def match_pattern(self, user_query: str, top_k: int = 1) -> Optional[MatchedPattern]:
        """
        Identifica qual padrão a query se encaixa melhor.

        Args:
            user_query: Query do usuário em linguagem natural
            top_k: Número de padrões a retornar (default: 1, melhor match)

        Returns:
            MatchedPattern com o padrão identificado e seus exemplos,
            ou None se nenhum padrão corresponder
        """
        if not self.patterns:
            return None

        query_lower = user_query.lower()

        # Calcular scores para cada padrão
        pattern_scores = []

        for pattern_name, pattern_data in self.patterns.items():
            score = 0
            matched_keywords = []

            # Verificar keywords do padrão
            for keyword in pattern_data.get('keywords', []):
                keyword_lower = keyword.lower()

                # Match exato de palavra inteira (mais pontos)
                if re.search(r'\b' + re.escape(keyword_lower) + r'\b', query_lower):
                    score += 3
                    matched_keywords.append(keyword)
                # Match parcial (menos pontos)
                elif keyword_lower in query_lower:
                    score += 1
                    matched_keywords.append(keyword)

            # Adicionar score baseado no número de palavras em comum
            pattern_words = set(pattern_data.get('description', '').lower().split())
            query_words = set(query_lower.split())
            common_words = pattern_words.intersection(query_words)
            score += len(common_words) * 0.5

            if score > 0:
                pattern_scores.append({
                    'pattern_name': pattern_name,
                    'pattern_data': pattern_data,
                    'score': score,
                    'keywords_matched': matched_keywords
                })

        # Ordenar por score decrescente
        pattern_scores.sort(key=lambda x: x['score'], reverse=True)

        if not pattern_scores:
            return None

        # Retornar o melhor match
        best_match = pattern_scores[0]

        return MatchedPattern(
            pattern_name=best_match['pattern_name'],
            description=best_match['pattern_data'].get('description', ''),
            score=best_match['score'],
            keywords_matched=best_match['keywords_matched'],
            examples=best_match['pattern_data'].get('examples', [])
        )

    def get_all_matches(self, user_query: str, min_score: float = 1.0) -> List[MatchedPattern]:
        """
        Retorna todos os padrões que correspondem à query.

        Args:
            user_query: Query do usuário
            min_score: Score mínimo para considerar um match

        Returns:
            Lista de MatchedPattern ordenada por score
        """
        if not self.patterns:
            return []

        query_lower = user_query.lower()
        matches = []

        for pattern_name, pattern_data in self.patterns.items():
            score = 0
            matched_keywords = []

            for keyword in pattern_data.get('keywords', []):
                keyword_lower = keyword.lower()
                if re.search(r'\b' + re.escape(keyword_lower) + r'\b', query_lower):
                    score += 3
                    matched_keywords.append(keyword)
                elif keyword_lower in query_lower:
                    score += 1
                    matched_keywords.append(keyword)

            if score >= min_score:
                matches.append(MatchedPattern(
                    pattern_name=pattern_name,
                    description=pattern_data.get('description', ''),
                    score=score,
                    keywords_matched=matched_keywords,
                    examples=pattern_data.get('examples', [])
                ))

        # Ordenar por score
        matches.sort(key=lambda x: x.score, reverse=True)
        return matches

    def format_examples_for_prompt(self, matched_pattern: MatchedPattern, max_examples: int = 3) -> str:
        """
        Formata os exemplos do padrão para injeção no prompt do LLM.

        Args:
            matched_pattern: Padrão identificado
            max_examples: Número máximo de exemplos a incluir

        Returns:
            String formatada com exemplos prontos para o prompt
        """
        if not matched_pattern or not matched_pattern.examples:
            return ""

        examples_text = "**EXEMPLOS DE QUERIES SIMILARES:**\n\n"
        examples_text += f"*Padrao identificado: {matched_pattern.description}*\n\n"

        # Limitar número de exemplos
        examples = matched_pattern.examples[:max_examples]

        for i, example in enumerate(examples, 1):
            user_query = example.get('user_query', '')
            code = example.get('code', '')
            expected_output = example.get('expected_output', '')

            examples_text += f"**Exemplo {i}:**\n"
            examples_text += f"Query: \"{user_query}\"\n\n"
            examples_text += f"Codigo gerado:\n```python\n{code}\n```\n"
            examples_text += f"Resultado esperado: {expected_output}\n\n"
            examples_text += "---\n\n"

        examples_text += "**IMPORTANTE:**\n"
        examples_text += "- Use os exemplos acima como REFERENCIA para estruturar seu codigo\n"
        examples_text += "- Mantenha o mesmo padrao de agrupamento, filtragem e ordenacao\n"
        examples_text += "- Sempre use `load_data()` e salve o resultado em `result`\n"
        examples_text += "- Se a query pedir 'top N', use `.head(N)`\n\n"

        return examples_text

    def get_pattern_statistics(self) -> Dict[str, Any]:
        """
        Retorna estatísticas sobre os padrões carregados.

        Returns:
            Dicionário com estatísticas
        """
        if not self.patterns:
            return {
                'total_patterns': 0,
                'total_examples': 0,
                'patterns': []
            }

        stats = {
            'total_patterns': len(self.patterns),
            'total_examples': sum(len(p.get('examples', [])) for p in self.patterns.values()),
            'patterns': []
        }

        for pattern_name, pattern_data in self.patterns.items():
            stats['patterns'].append({
                'name': pattern_name,
                'description': pattern_data.get('description', ''),
                'keywords_count': len(pattern_data.get('keywords', [])),
                'examples_count': len(pattern_data.get('examples', []))
            })

        return stats

    def test_query(self, user_query: str, verbose: bool = True) -> Optional[MatchedPattern]:
        """
        Testa uma query e imprime informações de debug.

        Args:
            user_query: Query a testar
            verbose: Se True, imprime informações detalhadas

        Returns:
            MatchedPattern se encontrado
        """
        matched = self.match_pattern(user_query)

        if verbose:
            print(f"\n{'='*60}")
            print(f"Query testada: \"{user_query}\"")
            print(f"{'='*60}\n")

            if matched:
                print(f"[OK] Padrao identificado: {matched.pattern_name}")
                print(f"Descricao: {matched.description}")
                print(f"Score: {matched.score}")
                print(f"Keywords matched: {', '.join(matched.keywords_matched)}")
                print(f"Exemplos disponiveis: {len(matched.examples)}")
                print(f"\n--- Primeiro exemplo ---")
                if matched.examples:
                    ex = matched.examples[0]
                    print(f"Query: {ex.get('user_query', 'N/A')}")
                    print(f"Codigo:\n{ex.get('code', 'N/A')[:200]}...")
            else:
                print("[ERRO] Nenhum padrao identificado")
                print("Sugestao: Adicione mais padroes ou keywords ao arquivo de padroes")

        return matched


# Função auxiliar para uso rápido
def quick_match(user_query: str) -> Optional[str]:
    """
    Função auxiliar para match rápido de padrão.

    Args:
        user_query: Query do usuário

    Returns:
        String com exemplos formatados ou None
    """
    matcher = PatternMatcher()
    matched = matcher.match_pattern(user_query)

    if matched:
        return matcher.format_examples_for_prompt(matched)

    return None


# Exemplo de uso standalone
if __name__ == "__main__":
    # Teste básico
    matcher = PatternMatcher()

    # Estatísticas
    stats = matcher.get_pattern_statistics()
    print(f"[STATS] Estatisticas dos Padroes:")
    print(f"Total de padroes: {stats['total_patterns']}")
    print(f"Total de exemplos: {stats['total_examples']}\n")

    # Teste com queries de exemplo
    test_queries = [
        "top 10 produtos mais vendidos",
        "ranking de vendas no segmento tecidos",
        "comparar vendas entre perfumaria e alimentar",
        "quantos produtos temos em estoque",
        "produtos sem estoque na une 1"
    ]

    print("[TEST] Testando queries de exemplo:\n")
    for query in test_queries:
        matched = matcher.test_query(query, verbose=True)
        print()
