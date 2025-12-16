"""
Code RAG Service - Semantic Code Search with LlamaIndex + Gemini
================================================================

Provides semantic search and analysis of the entire codebase using:
- LlamaIndex for RAG (Retrieval-Augmented Generation)
- Gemini 2.5 Flash for LLM
- GeminiEmbedding for semantic search
- FAISS for vector storage

Author: Antigravity AI
Date: 2025-12-15
"""

import os
import json
import logging
from pathlib import Path
from typing import Optional, Dict, Any, List
from datetime import datetime

from app.config.settings import settings

logger = logging.getLogger(__name__)


class CodeRAGService:
    """
    Service for semantic code search and analysis using RAG.
    
    Features:
    - Semantic search across entire codebase
    - Context-aware code analysis
    - Intelligent code suggestions
    - Multi-language support (Python, TypeScript, etc.)
    """
    
    def __init__(self):
        """Initialize the RAG service with lazy loading."""
        # Melhor prática Context7: Usar caminho absoluto baseado no arquivo, não no CWD
        # ./backend/app/core/code_rag_service.py -> ../../../storage
        self._storage_path = Path(__file__).resolve().parents[3] / "storage"
        self._initialized = False
        
    def _ensure_initialized(self) -> bool:
        """
        Lazy initialization of the RAG engine.
        Only loads when first query is made.
        
        Returns:
            bool: True if initialized successfully
        """
        if self._initialized:
            return True
            
        try:
            logger.info("🔧 Initializing Code RAG Service...")
            logger.info(f"📁 Storage Path: {self._storage_path}")
            
            # Check if storage exists
            if not self._storage_path.exists():
                logger.error(f"❌ Storage path does not exist: {self._storage_path}")
                logger.error("Please run: python scripts/index_codebase.py")
                return False

            # Check if Gemini API key is configured
            if not settings.GEMINI_API_KEY:
                logger.error("❌ GEMINI_API_KEY not configured")
                return False
            
            # Import LlamaIndex components (lazy import)
            try:
                from llama_index.core import (
                    VectorStoreIndex,
                    Settings,
                    load_index_from_storage,
                )
                from llama_index.core.storage import StorageContext
                from llama_index.llms.gemini import Gemini
                from llama_index.embeddings.gemini import GeminiEmbedding
            except ImportError as e:
                logger.error(f"❌ Missing dependencies (ImportError): {e}")
                logger.error("Install with: pip install llama-index llama-index-vector-stores-faiss llama-index-llms-gemini llama-index-embeddings-gemini")
                return False
            
            # Configure LlamaIndex Settings
            # Usando modelos estáveis: gemini-1.5-flash e text-embedding-004
            Settings.llm = Gemini(
                model_name="models/gemini-2.0-flash", 
                api_key=settings.GEMINI_API_KEY,
                temperature=0.1,
            )
            
            Settings.embed_model = GeminiEmbedding(
                model_name="models/text-embedding-004",
                api_key=settings.GEMINI_API_KEY,
            )
            
            # Load FAISS index
            logger.info("Loading index from storage...")
            storage_context = StorageContext.from_defaults(
                persist_dir=str(self._storage_path)
            )
            
            self._index = load_index_from_storage(storage_context)
            self._query_engine = self._index.as_query_engine(
                similarity_top_k=5,
                response_mode="tree_summarize"
            )
            
            # Load index statistics
            stats_file = self._storage_path / "index_stats.json"
            if stats_file.exists():
                with open(stats_file, 'r', encoding='utf-8') as f:
                    self._index_stats = json.load(f)
            
            self._initialized = True
            logger.info("✅ Code RAG Service initialized successfully")
            return True
            
        except Exception as e:
            # CRITICAL: Log the full traceback to understand why it fails
            import traceback
            trace = traceback.format_exc()
            logger.error(f"❌ Failed to initialize RAG service: {e}\n{trace}")
            return False
    
    def get_index_stats(self) -> Dict[str, Any]:
        """
        Get statistics about the code index.
        
        Returns:
            Dict with index statistics
        """
        if self._index_stats:
            return self._index_stats
        
        # Default stats if not loaded
        return {
            "status": "not_indexed",
            "total_files": 0,
            "total_functions": 0,
            "total_classes": 0,
            "total_lines": 0,
            "indexed_at": None,
            "languages": []
        }
    
    def query(
        self,
        message: str,
        history: Optional[List[Dict[str, str]]] = None,
        filters: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Query the codebase with semantic search.
        
        Args:
            message: User's question about the code
            history: Previous conversation history
            filters: Optional filters (language, directory, etc.)
            
        Returns:
            Dict with response, code references, and metadata
        """
        # Ensure service is initialized
        if not self._ensure_initialized():
            return {
                "response": (
                    "❌ **Serviço RAG não disponível**\n\n"
                    "O índice de código não foi encontrado ou o serviço não pôde ser inicializado.\n\n"
                    "**Possíveis causas:**\n"
                    "1. GEMINI_API_KEY não configurada\n"
                    "2. Dependências faltando (llama-index, faiss)\n"
                    "3. Índice não gerado (execute `python scripts/index_codebase.py`)\n\n"
                    "Verifique os logs para mais detalhes."
                ),
                "code_references": [],
                "metadata": {
                    "response_time": 0,
                    "sources_count": 0,
                    "error": "Service not initialized"
                }
            }
        
        try:
            start_time = datetime.now()
            
            # Build context from history if provided
            context_messages = []
            if history:
                for msg in history[-5:]:  # Last 5 messages for context
                    role = msg.get("role", "user")
                    content = msg.get("content", "")
                    context_messages.append(f"{role}: {content}")
            
            # Construct query with context
            full_query = message
            if context_messages:
                context_str = "\n".join(context_messages)
                full_query = f"Contexto da conversa:\n{context_str}\n\nPergunta atual: {message}"
            
            # Query the RAG engine
            logger.info(f"🔍 Querying codebase: {message[:100]}...")
            response = self._query_engine.query(full_query)
            
            # Extract source nodes (code references)
            code_references = []
            if hasattr(response, 'source_nodes'):
                for node in response.source_nodes[:5]:  # Top 5 sources
                    metadata = node.node.metadata
                    code_references.append({
                        "file": metadata.get("file_path", "unknown"),
                        "score": node.score,
                        "content": node.node.text[:500],  # First 500 chars
                        "lines": str(metadata.get("lines", "")),  # Convert to string
                    })
            
            end_time = datetime.now()
            response_time = (end_time - start_time).total_seconds()
            
            return {
                "response": str(response),
                "code_references": code_references,
                "metadata": {
                    "response_time": round(response_time, 2),
                    "sources_count": len(code_references),
                    "timestamp": datetime.now().isoformat()
                }
            }
            
        except Exception as e:
            logger.error(f"Error querying codebase: {e}", exc_info=True)
            return {
                "response": f"❌ **Erro ao processar consulta**\n\n{str(e)}",
                "code_references": [],
                "metadata": {
                    "response_time": 0,
                    "sources_count": 0,
                    "error": str(e)
                }
            }


# Singleton instance
_code_rag_service: Optional[CodeRAGService] = None


def get_code_rag_service() -> CodeRAGService:
    """
    Get or create the singleton CodeRAGService instance.
    
    Returns:
        CodeRAGService instance
    """
    global _code_rag_service
    if _code_rag_service is None:
        _code_rag_service = CodeRAGService()
    return _code_rag_service
