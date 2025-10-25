"""
QueryRetriever - Sistema RAG para busca semântica de queries similares
"""
import json
import os
import numpy as np
from typing import List, Dict, Any
from sentence_transformers import SentenceTransformer
import faiss
import logging

logger = logging.getLogger(__name__)


class QueryRetriever:
    """Busca exemplos similares usando embeddings + FAISS"""

    def __init__(self, examples_file: str = None, model_name: str = 'paraphrase-multilingual-MiniLM-L12-v2'):
        """
        Args:
            examples_file: Path do arquivo de exemplos JSON
            model_name: Nome do modelo sentence-transformers
        """
        self.examples_file = examples_file or os.path.join(
            os.getcwd(), "data", "query_examples.json"
        )

        logger.info(f"Inicializando QueryRetriever com modelo {model_name}")

        # Carregar modelo de embeddings
        self.model = SentenceTransformer(model_name)
        self.dimension = 384  # Dimensão do modelo MiniLM

        # Carregar exemplos
        self.examples = self._load_examples()

        # Criar índice FAISS
        self.index = self._build_faiss_index()

        logger.info(f"QueryRetriever inicializado com {len(self.examples)} exemplos")

    def _load_examples(self) -> List[Dict]:
        """Carrega exemplos do arquivo JSON"""
        if not os.path.exists(self.examples_file):
            logger.warning(f"Arquivo de exemplos não encontrado: {self.examples_file}")
            return []

        try:
            with open(self.examples_file, 'r', encoding='utf-8') as f:
                examples = json.load(f)
            logger.info(f"Carregados {len(examples)} exemplos de {self.examples_file}")
            return examples
        except Exception as e:
            logger.error(f"Erro ao carregar exemplos: {e}")
            return []

    def _build_faiss_index(self) -> faiss.Index:
        """Cria índice FAISS para busca rápida"""
        if not self.examples:
            logger.warning("Nenhum exemplo para indexar, criando índice vazio")
            index = faiss.IndexFlatL2(self.dimension)
            return index

        # Extrair ou gerar embeddings
        embeddings = []
        for i, example in enumerate(self.examples):
            if 'embedding' in example and example['embedding']:
                # Usar embedding existente
                embeddings.append(example['embedding'])
            else:
                # Gerar embedding
                logger.info(f"Gerando embedding para exemplo {i+1}/{len(self.examples)}")
                query = example.get('query_user', '')
                emb = self.model.encode(query)
                embeddings.append(emb.tolist())
                # Atualizar exemplo com embedding
                example['embedding'] = emb.tolist()

        # Salvar exemplos atualizados com embeddings
        self._save_examples()

        # Criar índice FAISS
        embeddings_array = np.array(embeddings, dtype='float32')
        index = faiss.IndexFlatL2(self.dimension)
        index.add(embeddings_array)

        logger.info(f"Índice FAISS criado com {index.ntotal} vetores")
        return index

    def _save_examples(self):
        """Salva exemplos de volta no arquivo"""
        try:
            os.makedirs(os.path.dirname(self.examples_file), exist_ok=True)
            with open(self.examples_file, 'w', encoding='utf-8') as f:
                json.dump(self.examples, f, ensure_ascii=False, indent=2)
            logger.info(f"Exemplos salvos em {self.examples_file}")
        except Exception as e:
            logger.error(f"Erro ao salvar exemplos: {e}")

    def find_similar_queries(self, user_query: str, top_k: int = 3) -> List[Dict]:
        """
        Busca as K queries mais similares

        Args:
            user_query: Query do usuário
            top_k: Número de exemplos a retornar

        Returns:
            Lista de dicionários com exemplos similares e scores
        """
        if not self.examples:
            logger.warning("Nenhum exemplo disponível para busca")
            return []

        # Gerar embedding da query
        query_embedding = self.model.encode([user_query])[0]

        # Buscar no FAISS
        distances, indices = self.index.search(
            query_embedding.reshape(1, -1).astype('float32'),
            min(top_k, len(self.examples))
        )

        # Preparar resultados
        similar = []
        for idx, dist in zip(indices[0], distances[0]):
            if idx < len(self.examples):
                example = self.examples[idx].copy()
                # Converter distância L2 em score de similaridade (0-1)
                example['similarity_score'] = float(1 / (1 + dist))
                example['distance'] = float(dist)
                similar.append(example)

        logger.info(f"Encontrados {len(similar)} exemplos similares para '{user_query[:50]}...'")
        return similar

    def add_example(self, query_user: str, code: str, success: bool = True,
                    rows_returned: int = 0, intent: str = "python_analysis", tags: List[str] = None):
        """
        Adiciona novo exemplo ao banco

        Args:
            query_user: Query original do usuário
            code: Código Python gerado
            success: Se a query foi bem-sucedida
            rows_returned: Número de linhas retornadas
            intent: Tipo de intenção
            tags: Tags para categorização
        """
        # Gerar embedding
        embedding = self.model.encode(query_user).tolist()

        # Criar exemplo
        example = {
            "query_user": query_user,
            "code_generated": code,
            "success": success,
            "rows_returned": rows_returned,
            "intent": intent,
            "embedding": embedding,
            "tags": tags or []
        }

        # Adicionar à lista
        self.examples.append(example)

        # Atualizar índice FAISS
        embedding_array = np.array([embedding], dtype='float32')
        self.index.add(embedding_array)

        # Salvar
        self._save_examples()

        logger.info(f"Exemplo adicionado: '{query_user[:50]}...' (total: {len(self.examples)})")

    def rebuild_index(self):
        """Reconstroi o índice FAISS do zero"""
        logger.info("Reconstruindo índice FAISS...")
        self.examples = self._load_examples()
        self.index = self._build_faiss_index()
        logger.info("Índice reconstruído com sucesso")

    def get_stats(self) -> Dict[str, Any]:
        """Retorna estatísticas do retriever"""
        return {
            "total_examples": len(self.examples),
            "index_size": self.index.ntotal if self.index else 0,
            "model_name": self.model._model_card_vars.get('model_name', 'unknown') if hasattr(self.model, '_model_card_vars') else 'MiniLM',
            "dimension": self.dimension,
            "examples_file": self.examples_file
        }
