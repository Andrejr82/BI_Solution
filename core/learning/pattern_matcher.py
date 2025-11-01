import json
import logging
from typing import Dict, Any, Optional, Tuple

logger = logging.getLogger(__name__)

class PatternMatcher:
    """Identifica o padrão de uma query de usuário e retorna exemplos relevantes."""

    def __init__(self, patterns_file: str = "data/query_patterns.json"):
        self.patterns = self._load_patterns(patterns_file)
        logger.info(f"{len(self.patterns)} padrões de query carregados de {patterns_file}")

    def _load_patterns(self, patterns_file: str) -> Dict[str, Any]:
        try:
            with open(patterns_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            logger.error(f"Arquivo de padrões não encontrado: {patterns_file}")
            return {}
        except json.JSONDecodeError:
            logger.error(f"Erro ao decodificar o JSON do arquivo: {patterns_file}")
            return {}

    def match_pattern(self, user_query: str) -> Optional[Tuple[str, Dict[str, Any]]]:
        """
        Identifica o melhor padrão para a query do usuário baseado em um score de keywords.

        Returns:
            Uma tupla (pattern_name, pattern_data) ou None.
        """
        if not self.patterns:
            return None

        query_lower = user_query.lower()
        scores = {}

        for pattern_name, pattern_data in self.patterns.items():
            score = 0
            for keyword in pattern_data.get("keywords", []):
                if keyword.lower() in query_lower:
                    score += 1
            if score > 0:
                scores[pattern_name] = score

        if not scores:
            logger.info(f"Nenhum padrão encontrado para a query: '{user_query}'")
            return None

        best_pattern_name = max(scores, key=scores.get)
        best_score = scores[best_pattern_name]
        logger.info(f"Melhor padrão encontrado para a query '{user_query}': '{best_pattern_name}' (Score: {best_score})")
        return best_pattern_name, self.patterns[best_pattern_name]

    def format_examples_for_prompt(self, pattern_data: Dict[str, Any], max_examples: int = 2) -> str:
        """Formata os exemplos de um padrão para serem injetados no prompt."""
        if not pattern_data or "examples" not in pattern_data:
            return ""

        examples = pattern_data.get("examples", [])
        if not examples:
            return ""

        few_shot_section = "\n\n# 📚 EXEMPLOS DE QUERIES SIMILARES (Few-Shot Learning)\n\n"
        few_shot_section += "Use os exemplos abaixo como referência para gerar código similar:\n\n"

        for i, ex in enumerate(examples[:max_examples], 1):
            few_shot_section += f"""## Exemplo {i}

**Query do Usuário:** "{ex.get('user_query', 'N/A')}"

**Código Python Gerado:**
```python
{ex.get('code', 'N/A')}
```
---
"""
        return few_shot_section

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    matcher = PatternMatcher()

    test_queries = [
        "quais são os 10 produtos mais vendidos?",
        "me dê o ranking completo de vendas do segmento aviamentos",
        "top 5 produtos na une bangu",
        "qual o faturamento total?"
    ]

    for query in test_queries:
        match_result = matcher.match_pattern(query)
        if match_result:
            name, data = match_result
            print(f"\nQuery: '{query}'")
            print(f"Padrão: {name} - {data.get('description')}")
            # Testar a formatação
            formatted_examples = matcher.format_examples_for_prompt(data)
            print(f"Exemplos Formatados:\n{formatted_examples}")
        else:
            print(f"\nQuery: '{query}' -> Nenhum padrão correspondente.")