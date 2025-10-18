"""
FewShotManager - Gerenciador de Exemplos Few-Shot para LLM

Módulo responsável por:
1. Carregar queries bem-sucedidas do histórico
2. Encontrar exemplos relevantes para cada nova consulta
3. Formatar exemplos para inclusão no prompt da LLM

Autor: Code Agent
Data: 2025-10-18
Versão: 1.0.0
"""

import json
import os
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


class FewShotManager:
    """
    Gerencia exemplos few-shot para alimentar a LLM com casos de sucesso anteriores.

    Attributes:
        learning_dir (Path): Diretório onde ficam os logs de aprendizado
        max_examples (int): Número máximo de exemplos a retornar
    """

    def __init__(self, learning_dir: str = "data/learning", max_examples: int = 5):
        """
        Inicializa o gerenciador few-shot

        Args:
            learning_dir: Diretório com logs de queries bem-sucedidas
            max_examples: Máximo de exemplos por consulta
        """
        self.learning_dir = Path(learning_dir)
        self.max_examples = max_examples

        # Criar diretório se não existir
        self.learning_dir.mkdir(parents=True, exist_ok=True)

        logger.info(f"FewShotManager inicializado - Dir: {self.learning_dir}")

    def load_successful_queries(self, days: int = 7) -> List[Dict]:
        """
        Carrega queries bem-sucedidas dos últimos N dias

        Args:
            days: Número de dias para buscar histórico

        Returns:
            Lista de dicionários com queries bem-sucedidas
        """
        queries = []
        cutoff_date = datetime.now() - timedelta(days=days)

        logger.info(f"Buscando queries dos últimos {days} dias...")

        # Buscar arquivos JSONL recentes
        pattern = "successful_queries_*.jsonl"
        files_found = list(self.learning_dir.glob(pattern))

        logger.info(f"Arquivos encontrados: {len(files_found)}")

        for file in files_found:
            try:
                with open(file, 'r', encoding='utf-8') as f:
                    line_count = 0
                    for line in f:
                        try:
                            query = json.loads(line.strip())

                            # Verificar se tem timestamp válido
                            timestamp_str = query.get('timestamp', '')
                            if timestamp_str:
                                try:
                                    query_date = datetime.fromisoformat(timestamp_str)
                                    if query_date >= cutoff_date:
                                        queries.append(query)
                                        line_count += 1
                                except ValueError:
                                    # Timestamp inválido, pular
                                    continue
                        except json.JSONDecodeError:
                            # Linha JSON inválida, pular
                            continue

                    logger.info(f"Carregadas {line_count} queries de {file.name}")

            except Exception as e:
                logger.warning(f"Erro ao ler {file.name}: {e}")
                continue

        logger.info(f"Total de queries carregadas: {len(queries)}")
        return queries

    def find_relevant_examples(
        self,
        user_query: str,
        intent: Optional[str] = None,
        min_score: float = 0.1
    ) -> List[Dict]:
        """
        Encontra exemplos relevantes para a query do usuário

        Estratégia de similaridade simples (sem embeddings):
        1. Buscar por palavras-chave em comum
        2. Bonus se intent corresponder
        3. Ordenar por score de similaridade
        4. Retornar top N

        Args:
            user_query: Pergunta do usuário
            intent: Intent detectado (opcional)
            min_score: Score mínimo para incluir exemplo

        Returns:
            Lista de exemplos ordenados por relevância
        """
        all_queries = self.load_successful_queries()

        if not all_queries:
            logger.warning("Nenhuma query bem-sucedida encontrada no histórico")
            return []

        # Normalizar query do usuário
        user_words = set(user_query.lower().split())

        # Calcular score de similaridade para cada exemplo
        scored = []
        for example in all_queries:
            example_query = example.get('query', '')
            example_words = set(example_query.lower().split())

            # Palavras em comum (similaridade de Jaccard simplificada)
            common_words = user_words & example_words
            if not user_words:
                score = 0.0
            else:
                score = len(common_words) / len(user_words)

            # Bonus se intent corresponder
            if intent and example.get('intent') == intent:
                score += 0.3

            # Bonus se tiver código e resultado
            if example.get('code') and example.get('rows', 0) > 0:
                score += 0.1

            # Apenas incluir se score mínimo
            if score >= min_score:
                example['similarity_score'] = score
                scored.append(example)

        # Ordenar por score decrescente e limitar
        scored.sort(key=lambda x: x['similarity_score'], reverse=True)
        top_examples = scored[:self.max_examples]

        logger.info(f"Encontrados {len(top_examples)} exemplos relevantes para '{user_query[:50]}...'")

        return top_examples

    def format_examples_for_prompt(self, examples: List[Dict]) -> str:
        """
        Formata exemplos para inclusão no prompt da LLM

        Args:
            examples: Lista de exemplos relevantes

        Returns:
            String formatada para adicionar ao prompt do sistema
        """
        if not examples:
            return ""

        context = "\n" + "="*80 + "\n"
        context += "## EXEMPLOS DE QUERIES BEM-SUCEDIDAS (Few-Shot Learning)\n"
        context += "="*80 + "\n\n"
        context += "Use estes exemplos como referência para gerar código similar e de qualidade.\n"
        context += "Adapte os padrões abaixo para a pergunta atual do usuário.\n\n"

        for i, ex in enumerate(examples, 1):
            score = ex.get('similarity_score', 0)
            rows = ex.get('rows', 0)
            intent = ex.get('intent', 'N/A')

            context += f"{'─'*80}\n"
            context += f"### EXEMPLO {i} (Relevância: {score:.0%})\n"
            context += f"{'─'*80}\n"
            context += f"**Pergunta do Usuário:** {ex.get('query', 'N/A')}\n"
            context += f"**Intent:** {intent}\n"
            context += f"**Resultado:** {rows} linhas retornadas com sucesso\n\n"
            context += f"**Código Python Gerado:**\n"
            context += f"```python\n{ex.get('code', 'N/A')}\n```\n\n"

        context += "="*80 + "\n"
        context += "IMPORTANTE: Use os padrões acima mas adapte para a pergunta ATUAL.\n"
        context += "="*80 + "\n\n"

        return context

    def get_statistics(self) -> Dict:
        """
        Retorna estatísticas sobre o histórico de queries

        Returns:
            Dicionário com métricas do histórico
        """
        queries = self.load_successful_queries(days=30)

        if not queries:
            return {
                "total_queries": 0,
                "intents": {},
                "avg_rows": 0,
                "oldest_query": None,
                "newest_query": None
            }

        # Agrupar por intent
        intents = {}
        total_rows = 0
        timestamps = []

        for q in queries:
            intent = q.get('intent', 'unknown')
            intents[intent] = intents.get(intent, 0) + 1
            total_rows += q.get('rows', 0)

            ts = q.get('timestamp')
            if ts:
                timestamps.append(ts)

        timestamps.sort()

        return {
            "total_queries": len(queries),
            "intents": intents,
            "avg_rows": total_rows / len(queries) if queries else 0,
            "oldest_query": timestamps[0] if timestamps else None,
            "newest_query": timestamps[-1] if timestamps else None
        }


# Funções auxiliares para uso direto

def get_few_shot_examples(user_query: str, intent: str = None, max_examples: int = 5) -> str:
    """
    Função de conveniência para obter exemplos formatados rapidamente

    Args:
        user_query: Pergunta do usuário
        intent: Intent detectado
        max_examples: Número máximo de exemplos

    Returns:
        String formatada com exemplos para o prompt
    """
    manager = FewShotManager(max_examples=max_examples)
    examples = manager.find_relevant_examples(user_query, intent)
    return manager.format_examples_for_prompt(examples)


if __name__ == "__main__":
    # Teste rápido
    logging.basicConfig(level=logging.INFO)

    manager = FewShotManager()
    stats = manager.get_statistics()

    print("\n" + "="*80)
    print("ESTATÍSTICAS DO FEW-SHOT LEARNING")
    print("="*80)
    print(f"Total de queries: {stats['total_queries']}")
    print(f"Intents: {stats['intents']}")
    print(f"Média de linhas: {stats['avg_rows']:.1f}")
    print("="*80)
