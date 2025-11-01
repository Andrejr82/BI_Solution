"""
Few-Shot Pattern Matcher
FASE 2.1 - Sistema de matching de padrões para Few-Shot Learning

Funcionalidades:
1. Busca padrões similares à query do usuário
2. Ranking por relevância (keywords + prioridade)
3. Geração de prompt Few-Shot para LLM
4. Substituição de placeholders em templates
"""

import json
import re
from pathlib import Path
from typing import Dict, List, Tuple
from dataclasses import dataclass


@dataclass
class PatternMatch:
    """Representa um padrão matched"""
    pattern_id: str
    pattern: Dict
    score: float
    keyword_matches: int


class FewShotPatternMatcher:
    """Sistema de matching de padrões para Few-Shot Learning"""

    def __init__(self, patterns_file: str):
        self.patterns_file = Path(patterns_file)
        self.patterns_data = None
        self.patterns = []
        self.load_patterns()

    def load_patterns(self):
        """Carrega biblioteca de padrões"""
        with open(self.patterns_file, 'r', encoding='utf-8') as f:
            self.patterns_data = json.load(f)
            self.patterns = self.patterns_data.get('patterns', [])
        print(f"[INFO] {len(self.patterns)} padrões carregados")

    def normalize_text(self, text: str) -> str:
        """Normaliza texto para matching"""
        return text.lower().strip()

    def find_matching_patterns(
        self,
        user_query: str,
        top_n: int = 3,
        min_score: float = 0.0
    ) -> List[PatternMatch]:
        """
        Encontra padrões que fazem match com a query do usuário

        Args:
            user_query: Query do usuário
            top_n: Número de padrões a retornar
            min_score: Score mínimo para considerar

        Returns:
            Lista de PatternMatch ordenada por relevância
        """
        query_normalized = self.normalize_text(user_query)
        matches = []

        for pattern in self.patterns:
            pattern_id = pattern.get('id')
            keywords = pattern.get('keywords', [])
            priority = pattern.get('priority', 'medium')
            frequency = pattern.get('usage_frequency', 'media')

            # Contar keywords presentes na query
            keyword_matches = sum(
                1 for keyword in keywords
                if self.normalize_text(keyword) in query_normalized
            )

            if keyword_matches == 0:
                continue

            # Calcular score
            score = self._calculate_score(
                keyword_matches,
                len(keywords),
                priority,
                frequency
            )

            if score >= min_score:
                matches.append(PatternMatch(
                    pattern_id=pattern_id,
                    pattern=pattern,
                    score=score,
                    keyword_matches=keyword_matches
                ))

        # Ordenar por score (descendente)
        matches.sort(key=lambda x: x.score, reverse=True)

        return matches[:top_n]

    def _calculate_score(
        self,
        keyword_matches: int,
        total_keywords: int,
        priority: str,
        frequency: str
    ) -> float:
        """
        Calcula score de relevância do padrão

        Fatores:
        - Keywords matched (50%)
        - Priority (30%)
        - Frequency (20%)
        """
        # Keyword coverage (0-50 pontos)
        keyword_score = (keyword_matches / total_keywords) * 50

        # Priority score (0-30 pontos)
        priority_weights = {'high': 30, 'medium': 20, 'low': 10}
        priority_score = priority_weights.get(priority, 15)

        # Frequency score (0-20 pontos)
        frequency_weights = {
            'muito_alta': 20,
            'alta': 15,
            'media': 10,
            'baixa': 5
        }
        frequency_score = frequency_weights.get(frequency, 10)

        return keyword_score + priority_score + frequency_score

    def generate_few_shot_prompt(
        self,
        user_query: str,
        matches: List[PatternMatch],
        include_all_examples: bool = False
    ) -> str:
        """
        Gera prompt Few-Shot para o LLM

        Args:
            user_query: Query do usuário
            matches: Lista de padrões matched
            include_all_examples: Se True, inclui todos os exemplos

        Returns:
            Prompt formatado para Few-Shot Learning
        """
        prompt_parts = []

        # Header
        prompt_parts.append("Você é um especialista em Polars que gera código para análise de dados.")
        prompt_parts.append("\nAqui estão exemplos de queries similares bem-sucedidas:\n")

        # Adicionar exemplos dos padrões matched
        for idx, match in enumerate(matches, 1):
            pattern = match.pattern
            examples = pattern.get('examples', [])

            prompt_parts.append(f"\n--- Padrão {idx}: {pattern.get('description')} ---")

            # Pegar 1 ou todos os exemplos
            examples_to_use = examples if include_all_examples else examples[:1]

            for example in examples_to_use:
                query_text = example.get('query')
                code_text = example.get('code')
                prompt_parts.append(f"\nQuery: {query_text}")
                prompt_parts.append(f"Código Polars:\n{code_text}\n")

        # User query
        prompt_parts.append("\n" + "="*70)
        prompt_parts.append(f"\nAgora gere código Polars para a seguinte query:")
        prompt_parts.append(f"\nQuery do Usuário: {user_query}")
        prompt_parts.append("\nInstruções:")
        prompt_parts.append("1. Analise os exemplos acima")
        prompt_parts.append("2. Identifique o padrão similar")
        prompt_parts.append("3. Adapte o código para a query do usuário")
        prompt_parts.append("4. Retorne APENAS o código Polars válido, sem explicações")
        prompt_parts.append("\nCódigo Polars:")

        return "\n".join(prompt_parts)

    def extract_parameters_from_query(self, query: str) -> Dict[str, str]:
        """
        Extrai parâmetros da query do usuário

        Exemplos:
        - "Top 10 produtos" -> {n: 10}
        - "UNE FORTALEZA" -> {une_nome: 'FORTALEZA'}
        - "vendas acima de 5000" -> {valor: 5000}
        """
        params = {}

        # Extrair números (para Top N, valores, etc)
        numbers = re.findall(r'\b(\d+)\b', query)
        if numbers:
            params['n'] = int(numbers[0])
            if len(numbers) > 1:
                params['valor'] = int(numbers[1])

        # Extrair UNE
        une_match = re.search(r'une\s+([A-Z]+(?:\s+[A-Z]+)*)', query, re.IGNORECASE)
        if une_match:
            params['une_nome'] = une_match.group(1).upper()

        # Extrair segmento
        segmento_match = re.search(r'segmento\s+(\w+)', query, re.IGNORECASE)
        if segmento_match:
            params['segmento'] = segmento_match.group(1).upper()

        # Extrair produto
        produto_match = re.search(r'produto\s+(\w+)', query, re.IGNORECASE)
        if produto_match:
            params['produto_nome'] = produto_match.group(1).upper()

        return params

    def generate_code_from_template(
        self,
        pattern: Dict,
        parameters: Dict[str, any]
    ) -> str:
        """
        Gera código a partir do template e parâmetros

        Args:
            pattern: Padrão selecionado
            parameters: Parâmetros extraídos da query

        Returns:
            Código Polars com placeholders substituídos
        """
        template = pattern.get('code_template', '')

        # Substituir placeholders
        for key, value in parameters.items():
            placeholder = f'{{{key}}}'
            if isinstance(value, str):
                replacement = f"'{value}'"
            else:
                replacement = str(value)

            template = template.replace(placeholder, replacement)

        return template

    def process_query(
        self,
        user_query: str,
        return_prompt: bool = True,
        return_code: bool = False
    ) -> Dict:
        """
        Processa query do usuário e retorna prompt/código

        Args:
            user_query: Query do usuário
            return_prompt: Se True, retorna prompt Few-Shot
            return_code: Se True, tenta gerar código direto

        Returns:
            Dict com resultados do processamento
        """
        # Encontrar padrões
        matches = self.find_matching_patterns(user_query, top_n=3)

        if not matches:
            return {
                'success': False,
                'message': 'Nenhum padrão encontrado para a query',
                'matches': []
            }

        result = {
            'success': True,
            'query': user_query,
            'matches': [
                {
                    'pattern_id': m.pattern_id,
                    'score': m.score,
                    'description': m.pattern.get('description')
                }
                for m in matches
            ]
        }

        # Gerar prompt Few-Shot
        if return_prompt:
            result['few_shot_prompt'] = self.generate_few_shot_prompt(
                user_query,
                matches
            )

        # Tentar gerar código direto
        if return_code:
            best_match = matches[0]
            parameters = self.extract_parameters_from_query(user_query)
            code = self.generate_code_from_template(
                best_match.pattern,
                parameters
            )
            result['generated_code'] = code
            result['parameters'] = parameters

        return result

    def print_match_results(self, results: Dict):
        """Imprime resultados de forma formatada"""
        print("\n" + "="*70)
        print("RESULTADOS DO PATTERN MATCHING")
        print("="*70)

        if not results['success']:
            print(f"\n[ERRO] {results['message']}")
            return

        print(f"\nQuery: {results['query']}")
        print(f"\nPadrões encontrados: {len(results['matches'])}")

        for idx, match in enumerate(results['matches'], 1):
            print(f"\n{idx}. {match['pattern_id']}")
            print(f"   Score: {match['score']:.2f}")
            print(f"   Descrição: {match['description']}")

        if 'generated_code' in results:
            print("\n" + "-"*70)
            print("CÓDIGO GERADO:")
            print("-"*70)
            print(results['generated_code'])

        if 'few_shot_prompt' in results:
            print("\n" + "-"*70)
            print("FEW-SHOT PROMPT:")
            print("-"*70)
            print(results['few_shot_prompt'][:500] + "...")  # Primeiros 500 chars


def main():
    """Função principal para testes"""
    import sys

    patterns_file = "C:\\Users\\André\\Documents\\Agent_Solution_BI\\query_patterns_complete.json"

    if not Path(patterns_file).exists():
        print(f"[ERRO] Arquivo não encontrado: {patterns_file}")
        return 1

    # Criar matcher
    matcher = FewShotPatternMatcher(patterns_file)

    # Exemplos de queries para testar
    test_queries = [
        "Top 10 produtos mais vendidos da UNE FORTALEZA",
        "Total de vendas por UNE",
        "Produtos com estoque abaixo de 100",
        "Ranking das UNEs por vendas",
        "Média de vendas por produto"
    ]

    print("\n" + "="*70)
    print("TESTANDO FEW-SHOT PATTERN MATCHER")
    print("="*70)

    for query in test_queries:
        results = matcher.process_query(
            query,
            return_prompt=False,
            return_code=True
        )
        matcher.print_match_results(results)
        print("\n")

    return 0


if __name__ == "__main__":
    exit(main())
