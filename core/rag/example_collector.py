"""
ExampleCollector - Coleta automática de queries bem-sucedidas
"""
import json
import os
from datetime import datetime
from typing import Dict, Any, List, Optional
import logging

logger = logging.getLogger(__name__)

# Lazy import
try:
    from sentence_transformers import SentenceTransformer
    SENTENCE_TRANSFORMERS_AVAILABLE = True
except ImportError:
    logger.warning("sentence-transformers not available - ExampleCollector will work in fallback mode")
    SENTENCE_TRANSFORMERS_AVAILABLE = False
    SentenceTransformer = None


class ExampleCollector:
    """Coleta queries bem-sucedidas para alimentar o RAG"""

    def __init__(self, model_name: str = 'paraphrase-multilingual-MiniLM-L12-v2'):
        """
        Args:
            model_name: Nome do modelo sentence-transformers
        """
        self.model_name = model_name
        self.model: Optional[Any] = None  # Lazy loading
        self.examples_file = os.path.join(os.getcwd(), "data", "query_examples.json")
        logger.info("ExampleCollector inicializado (lazy load)")

    def _ensure_model_loaded(self):
        """Carrega o modelo sob demanda"""
        if self.model is None and SENTENCE_TRANSFORMERS_AVAILABLE:
            try:
                logger.info(f"Carregando modelo {self.model_name}...")
                self.model = SentenceTransformer(self.model_name)
                logger.info("Modelo carregado com sucesso")
            except Exception as e:
                logger.error(f"Erro ao carregar modelo: {e}")
                self.model = None

    def collect_successful_query(
        self,
        user_query: str,
        code_generated: str,
        result_rows: int,
        intent: str = "python_analysis",
        tags: List[str] = None
    ) -> Dict[str, Any]:
        """
        Salva query bem-sucedida como exemplo

        Args:
            user_query: Query original do usuário
            code_generated: Código Python gerado
            result_rows: Número de linhas retornadas
            intent: Tipo de intenção
            tags: Tags para categorização

        Returns:
            Dicionário com o exemplo criado
        """
        # Garantir modelo carregado
        self._ensure_model_loaded()

        # Gerar embedding (ou None se modelo indisponível)
        embedding = None
        if self.model is not None:
            embedding = self.model.encode([user_query])[0].tolist()
        else:
            logger.warning("Modelo não disponível - salvando sem embedding")

        # Normalizar query (simplificar)
        normalized = self._normalize_query(user_query)

        # Extrair tags automaticamente se não fornecidas
        if not tags:
            tags = self._extract_tags(user_query, code_generated)

        # Criar exemplo
        example = {
            "query_user": user_query,
            "query_normalized": normalized,
            "intent": intent,
            "code_generated": code_generated,
            "success": True,
            "rows_returned": result_rows,
            "embedding": embedding,
            "tags": tags,
            "timestamp": datetime.now().isoformat()
        }

        # Adicionar ao banco de exemplos
        self._append_to_database(example)

        logger.info(f"Query coletada: '{user_query[:50]}...' ({result_rows} linhas)")
        return example

    def _normalize_query(self, query: str) -> str:
        """Normaliza query removendo acentos e palavras comuns"""
        import unicodedata
        import re

        # Remover acentos
        normalized = ''.join(
            c for c in unicodedata.normalize('NFD', query.lower())
            if unicodedata.category(c) != 'Mn'
        )

        # Remover palavras comuns
        stop_words = ['o', 'a', 'de', 'da', 'do', 'em', 'para', 'com', 'por', 'me', 'mostre', 'qual', 'quais']
        words = normalized.split()
        filtered = [w for w in words if w not in stop_words]

        return ' '.join(filtered)

    def _extract_tags(self, user_query: str, code: str) -> List[str]:
        """Extrai tags automaticamente da query e código"""
        tags = []

        query_lower = user_query.lower()

        # Tags de tipo de query
        if any(w in query_lower for w in ['ranking', 'top', 'maior', 'melhor']):
            tags.append('ranking')
        if any(w in query_lower for w in ['total', 'soma', 'somar']):
            tags.append('agregacao')
        if 'gráfico' in query_lower or 'grafico' in query_lower:
            tags.append('grafico')
        if any(w in query_lower for w in ['comparar', 'versus', 'vs']):
            tags.append('comparacao')
        if any(w in query_lower for w in ['estoque', 'inventário']):
            tags.append('estoque')
        if any(w in query_lower for w in ['venda', 'vendas']):
            tags.append('vendas')

        # Tags de código
        if 'groupby' in code:
            tags.append('groupby')
        if '.head(' in code:
            tags.append('limite')
        if 'plotly' in code or 'px.' in code:
            tags.append('visualizacao')

        return tags if tags else ['geral']

    def _append_to_database(self, example: Dict[str, Any]):
        """Adiciona exemplo ao arquivo de banco de dados"""
        # Carregar exemplos existentes
        if os.path.exists(self.examples_file):
            try:
                with open(self.examples_file, 'r', encoding='utf-8') as f:
                    examples = json.load(f)
            except:
                examples = []
        else:
            examples = []

        # Adicionar novo exemplo
        examples.append(example)

        # Salvar
        os.makedirs(os.path.dirname(self.examples_file), exist_ok=True)
        with open(self.examples_file, 'w', encoding='utf-8') as f:
            json.dump(examples, f, ensure_ascii=False, indent=2)

        logger.info(f"Exemplo adicionado ao banco ({len(examples)} total)")

    def get_collection_stats(self) -> Dict[str, Any]:
        """Retorna estatísticas da coleta"""
        if not os.path.exists(self.examples_file):
            return {"total_examples": 0}

        with open(self.examples_file, 'r', encoding='utf-8') as f:
            examples = json.load(f)

        # Contar por tags
        tag_counts = {}
        for ex in examples:
            for tag in ex.get('tags', []):
                tag_counts[tag] = tag_counts.get(tag, 0) + 1

        return {
            "total_examples": len(examples),
            "tag_distribution": tag_counts,
            "latest_timestamp": examples[-1].get('timestamp') if examples else None
        }
