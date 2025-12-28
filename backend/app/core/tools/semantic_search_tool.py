"""
Ferramenta de busca semântica para produtos usando RAG (Retrieval-Augmented Generation).

Implementa hybrid search combinando:
- Semantic search via Google Generative AI Embeddings
- Keyword search tradicional
- Reciprocal Rank Fusion (RRF) para merge de resultados

Author: Context7 2025
Status: POC (Proof of Concept)
"""

import logging
import os
from typing import Dict, Any, List, Optional
from langchain_core.tools import tool
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_community.vectorstores import FAISS
import polars as pl

logger = logging.getLogger(__name__)

# Singleton instance para cache do vector store
_VECTOR_STORE_CACHE = None
_EMBEDDINGS_MODEL = None


def _get_embeddings_model():
    """Retorna o modelo de embeddings (singleton)"""
    global _EMBEDDINGS_MODEL
    if _EMBEDDINGS_MODEL is None:
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY not found in environment")

        _EMBEDDINGS_MODEL = GoogleGenerativeAIEmbeddings(
            model="models/embedding-001",
            google_api_key=api_key
        )
        logger.info("Google Generative AI Embeddings initialized")
    return _EMBEDDINGS_MODEL


def _initialize_vector_store() -> FAISS:
    """
    Inicializa o vector store FAISS com embeddings de produtos.
    Executa apenas uma vez e cacheia o resultado (lazy loading).
    """
    global _VECTOR_STORE_CACHE

    if _VECTOR_STORE_CACHE is not None:
        logger.debug("Using cached vector store")
        return _VECTOR_STORE_CACHE

    logger.info("Initializing FAISS vector store with product embeddings...")

    # OTIMIZAÇÃO 2025-12-28: Cache persistente para evitar recomputação de embeddings
    try:
        from pathlib import Path

        cache_dir = Path("backend/data/cache/embeddings")
        cache_dir.mkdir(parents=True, exist_ok=True)
        cache_index = cache_dir / "product_embeddings_faiss.index"

        # Tentar carregar do cache primeiro
        if cache_index.exists():
            logger.info(f"Loading cached embeddings from {cache_index}...")
            try:
                embeddings_model = _get_embeddings_model()
                _VECTOR_STORE_CACHE = FAISS.load_local(
                    str(cache_dir),
                    embeddings_model,
                    index_name="product_embeddings_faiss"
                )
                logger.info(f"Successfully loaded cached vector store")
                return _VECTOR_STORE_CACHE
            except Exception as e:
                logger.warning(f"Failed to load cache: {e}. Regenerating embeddings...")

        # Se cache não existe ou falhou, criar novos embeddings
        # Carregar dados de produtos
        parquet_path = "C:/Agente_BI/BI_Solution/backend/data/parquet/admmat.parquet"
        df = pl.read_parquet(parquet_path)

        # Extrair nomes únicos de produtos
        products_df = df.select([
            pl.col("PRODUTO").cast(pl.Utf8).alias("codigo"),
            pl.col("NOME").fill_null("").alias("nome")
        ]).unique()

        texts = [
            f"{row['codigo']} | {row['nome']}"
            for row in products_df.iter_rows(named=True)
        ]

        logger.info(f"Creating embeddings for {len(texts)} unique products...")
        logger.warning(f"This will consume API quota. Future runs will use cache.")

        # Criar embeddings e vector store
        embeddings_model = _get_embeddings_model()

        _VECTOR_STORE_CACHE = FAISS.from_texts(
            texts=texts,
            embedding=embeddings_model
        )

        # Salvar cache para uso futuro
        try:
            _VECTOR_STORE_CACHE.save_local(
                str(cache_dir),
                index_name="product_embeddings_faiss"
            )
            logger.info(f"Embeddings cached to {cache_dir} for future use")
        except Exception as e:
            logger.warning(f"Failed to save cache: {e}")

        logger.info(f"Vector store initialized with {len(texts)} product embeddings")
        return _VECTOR_STORE_CACHE

    except Exception as e:
        logger.error(f"Failed to initialize vector store: {e}", exc_info=True)
        raise


def _reciprocal_rank_fusion(
    semantic_results: List[str],
    keyword_results: List[str],
    limit: int = 10,
    k: int = 60
) -> List[str]:
    """
    Combina resultados de semantic e keyword search usando Reciprocal Rank Fusion.

    RRF Formula: score(d) = Σ 1 / (k + rank(d))
    onde k é uma constante (default=60) e rank(d) é a posição do documento.

    Args:
        semantic_results: Resultados da busca semântica
        keyword_results: Resultados da busca por palavra-chave
        limit: Número máximo de resultados
        k: Constante RRF (default=60)

    Returns:
        Lista mesclada e ranqueada de resultados
    """
    scores = {}

    # Score semantic results
    for rank, doc in enumerate(semantic_results, start=1):
        scores[doc] = scores.get(doc, 0) + (1 / (k + rank))

    # Score keyword results
    for rank, doc in enumerate(keyword_results, start=1):
        scores[doc] = scores.get(doc, 0) + (1 / (k + rank))

    # Sort by score descending
    sorted_docs = sorted(scores.items(), key=lambda x: x[1], reverse=True)

    # Return top N document IDs
    return [doc for doc, score in sorted_docs[:limit]]


@tool
def buscar_produtos_inteligente(
    descricao: str,
    limite: int = 10,
    usar_hybrid: bool = True
) -> Dict[str, Any]:
    """
    Busca produtos usando IA semântica (RAG) com tolerância a typos e sinônimos.

    Esta ferramenta combina busca semântica (embeddings) com busca tradicional
    por palavra-chave, resultando em melhor recall e precisão.

    Exemplos de uso:
    - "cola para sapato" → encontra "Cola de Sapateiro"
    - "maquiagem rosto" → encontra "Base", "Pó Compacto", etc.
    - "tinta cabelo" → encontra "Tintura Capilar", "Coloração"

    Args:
        descricao: Descrição natural do produto que procura
        limite: Número máximo de resultados (default: 10)
        usar_hybrid: Se True, combina semantic + keyword (default: True)

    Returns:
        Dicionário com produtos encontrados e scores de relevância
    """
    logger.info(f"Busca inteligente: '{descricao}' (limite={limite}, hybrid={usar_hybrid})")

    try:
        # Carregar dados completos
        parquet_path = "C:/Agente_BI/BI_Solution/backend/data/parquet/admmat.parquet"
        df = pl.read_parquet(parquet_path)

        # 1. SEMANTIC SEARCH (sempre executado)
        vector_store = _initialize_vector_store()
        semantic_docs = vector_store.similarity_search(descricao, k=limite * 2)

        # Extrair códigos de produto dos resultados semânticos
        semantic_product_codes = [
            doc.page_content.split(" | ")[0]
            for doc in semantic_docs
        ]

        if not usar_hybrid:
            # Apenas semantic search
            results_df = df.filter(
                pl.col("PRODUTO").cast(pl.Utf8).is_in(semantic_product_codes)
            ).unique(subset=["PRODUTO"])

            produtos = results_df.select([
                "PRODUTO",
                "NOME",
                "NOMESEGMENTO",
                "NOMECATEGORIA",
                "PRECO_VENDA",
                "ESTOQUE_UNE",
                "VENDA_30DD"
            ]).head(limite).to_dicts()

            return {
                "status": "success",
                "search_type": "semantic_only",
                "total_encontrados": len(produtos),
                "produtos": produtos,
                "message": f"Encontrados {len(produtos)} produtos via busca semântica"
            }

        # 2. KEYWORD SEARCH (fallback tradicional)
        keyword_results_df = df.filter(
            pl.col("NOME").str.to_lowercase().str.contains(descricao.lower())
        ).unique(subset=["PRODUTO"]).head(limite * 2)

        keyword_product_codes = keyword_results_df.select(
            pl.col("PRODUTO").cast(pl.Utf8)
        ).to_series().to_list()

        # 3. RECIPROCAL RANK FUSION (merge)
        merged_codes = _reciprocal_rank_fusion(
            semantic_results=semantic_product_codes,
            keyword_results=keyword_product_codes,
            limit=limite
        )

        # 4. Buscar detalhes completos dos produtos mesclados
        final_df = df.filter(
            pl.col("PRODUTO").cast(pl.Utf8).is_in(merged_codes)
        ).unique(subset=["PRODUTO"])

        # Preservar ordem do RRF
        final_df = final_df.sort(
            by=pl.col("PRODUTO").cast(pl.Utf8),
            maintain_order=True
        )

        produtos = final_df.select([
            "PRODUTO",
            "NOME",
            "NOMESEGMENTO",
            "NOMECATEGORIA",
            "PRECO_VENDA",
            "ESTOQUE_UNE",
            "VENDA_30DD",
            "UNE",
            "UNE_NOME"
        ]).head(limite).to_dicts()

        return {
            "status": "success",
            "search_type": "hybrid (semantic + keyword + RRF)",
            "total_encontrados": len(produtos),
            "produtos": produtos,
            "stats": {
                "semantic_matches": len(semantic_product_codes),
                "keyword_matches": len(keyword_product_codes),
                "merged_results": len(merged_codes)
            },
            "message": f"Encontrados {len(produtos)} produtos via busca híbrida inteligente"
        }

    except Exception as e:
        logger.error(f"Erro na busca inteligente: {e}", exc_info=True)
        return {
            "status": "error",
            "message": f"Erro ao buscar produtos: {str(e)}",
            "fallback": "Use consultar_dados_flexivel para busca tradicional"
        }


@tool
def reinicializar_vector_store() -> Dict[str, Any]:
    """
    Reinicializa o vector store (útil se dados foram atualizados).
    Use apenas quando necessário, pois recria todos os embeddings.

    Returns:
        Status da reinicialização
    """
    global _VECTOR_STORE_CACHE

    logger.warning("Reinicializando vector store (clearing cache)...")

    _VECTOR_STORE_CACHE = None

    try:
        _initialize_vector_store()
        return {
            "status": "success",
            "message": "Vector store reinicializado com sucesso"
        }
    except Exception as e:
        logger.error(f"Erro ao reinicializar vector store: {e}")
        return {
            "status": "error",
            "message": f"Erro: {str(e)}"
        }
