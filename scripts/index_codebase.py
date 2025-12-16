"""
Code Indexer - Generate RAG Index for Entire Codebase
=====================================================

This script indexes the entire codebase (Python + TypeScript) using:
- LlamaIndex for document processing
- Gemini Embeddings for semantic search
- FAISS for vector storage

Usage:
    python scripts/index_codebase.py

Output:
    ./storage/ - FAISS index and metadata

Author: Antigravity AI
Date: 2025-12-15
"""

import os
import sys
from pathlib import Path
from datetime import datetime
import json
import logging

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from dotenv import load_dotenv
load_dotenv(project_root / "backend" / ".env")

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Import LlamaIndex components
try:
    from llama_index.core import (
        VectorStoreIndex,
        SimpleDirectoryReader,
        StorageContext,
        Document
    )
    from llama_index.core.settings import Settings
    from llama_index.llms.gemini import Gemini
    from llama_index.embeddings.gemini import GeminiEmbedding
except ImportError as e:
    import traceback
    logger.error(f"Missing dependencies: {e}")
    traceback.print_exc()
    logger.error("Install with: pip install llama-index llama-index-llms-gemini llama-index-embeddings-gemini")
    sys.exit(1)


def configure_llamaindex():
    """Configure LlamaIndex with Gemini models."""
    api_key = os.getenv("GEMINI_API_KEY")
    
    # Validar API key
    if not api_key:
        logger.error("GEMINI_API_KEY not found in environment")
        sys.exit(1)

    logger.info("Configuring LlamaIndex with Gemini...")
    
    try:
        # Usar modelo confirmado na lista
        Settings.llm = Gemini(
            model_name="models/gemini-2.0-flash",
            api_key=api_key,
            temperature=0.1,
        )
        
        Settings.embed_model = GeminiEmbedding(
            model_name="models/text-embedding-004",
            api_key=api_key,
        )
        
        logger.info("LlamaIndex configured (Gemini 2.0 Flash + Text Embedding 004)")
        
    except Exception as e:
        logger.error(f"❌ Failed to configure Gemini: {e}")
        logger.error("Please check your GEMINI_API_KEY and model availability.")
        sys.exit(1)


def load_code_documents(base_path: Path) -> list:
    """
    Load code documents from backend and frontend directories.
    
    Args:
        base_path: Project root path
        
    Returns:
        List of Document objects
    """
    documents = []
    stats = {
        "total_files": 0,
        "total_functions": 0,
        "total_classes": 0,
        "total_lines": 0,
        "languages": set()
    }
    
    # Directories to index
    code_dirs = [
        base_path / "backend" / "app",
        base_path / "frontend-solid" / "src",
    ]
    
    # File extensions to index
    extensions = {
        ".py": "python",
        ".tsx": "typescript",
        ".ts": "typescript",
        ".jsx": "javascript",
        ".js": "javascript"
    }
    
    logger.info("📂 Loading code files...")
    
    for code_dir in code_dirs:
        if not code_dir.exists():
            logger.warning(f"Directory not found: {code_dir}")
            continue
        
        logger.info(f"  Scanning: {code_dir}")
        
        for file_path in code_dir.rglob("*"):
            if file_path.suffix not in extensions:
                continue
            
            # Skip node_modules, __pycache__, etc.
            if any(skip in str(file_path) for skip in ["node_modules", "__pycache__", ".venv", "dist", "build"]):
                continue
            
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Count lines
                lines = content.count('\n') + 1
                stats["total_lines"] += lines
                stats["total_files"] += 1
                
                # Count functions and classes (simple heuristic)
                if file_path.suffix == ".py":
                    stats["total_functions"] += content.count('\ndef ')
                    stats["total_classes"] += content.count('\nclass ')
                    stats["languages"].add("Python")
                else:
                    stats["total_functions"] += content.count('function ') + content.count('const ') + content.count('export ')
                    stats["total_classes"] += content.count('class ')
                    stats["languages"].add("TypeScript/JavaScript")
                
                # Create document with metadata
                doc = Document(
                    text=content,
                    metadata={
                        "file_path": str(file_path.relative_to(base_path)),
                        "language": extensions[file_path.suffix],
                        "lines": lines,
                        "filename": file_path.name
                    }
                )
                documents.append(doc)
                
            except Exception as e:
                logger.warning(f"  Error reading {file_path}: {e}")
    
    logger.info(f"✅ Loaded {len(documents)} files")
    logger.info(f"   Total lines: {stats['total_lines']:,}")
    logger.info(f"   Functions: {stats['total_functions']:,}")
    logger.info(f"   Classes: {stats['total_classes']:,}")
    logger.info(f"   Languages: {', '.join(stats['languages'])}")
    
    return documents, stats


def create_index(documents: list, storage_path: Path):
    """
    Create FAISS index from documents.
    
    Args:
        documents: List of Document objects
        storage_path: Path to save index
    """
    logger.info("🔨 Creating Index...")
    
    # Create index (using default SimpleVectorStore which is JSON based)
    # This is more robust on Windows than FAISS for this scale
    Settings.embed_model = GeminiEmbedding(
        model_name="models/text-embedding-004",
        api_key=os.getenv("GEMINI_API_KEY")
    )

    logger.info("   Generating embeddings (this may take a while)...")
    index = VectorStoreIndex.from_documents(
        documents,
        show_progress=True
    )
    
    # Persist index
    storage_path.mkdir(parents=True, exist_ok=True)
    index.storage_context.persist(persist_dir=str(storage_path))
    
    logger.info(f"✅ Index saved to {storage_path}")


def save_stats(stats: dict, storage_path: Path):
    """Save index statistics to JSON."""
    stats_data = {
        "status": "ready",
        "total_files": stats["total_files"],
        "total_functions": stats["total_functions"],
        "total_classes": stats["total_classes"],
        "total_lines": stats["total_lines"],
        "indexed_at": datetime.now().isoformat(),
        "languages": list(stats["languages"])
    }
    
    stats_file = storage_path / "index_stats.json"
    with open(stats_file, 'w', encoding='utf-8') as f:
        json.dump(stats_data, f, indent=2)
    
    logger.info(f"✅ Stats saved to {stats_file}")


def main():
    """Main indexing function."""
    logger.info("=" * 60)
    logger.info("Code Indexer - Generating RAG Index")
    logger.info("=" * 60)
    
    # Configure LlamaIndex
    configure_llamaindex()
    
    # Load documents
    base_path = project_root
    documents, stats = load_code_documents(base_path)
    
    if not documents:
        logger.error("No documents found to index")
        sys.exit(1)
    
    # Create index
    storage_path = base_path / "storage"
    create_index(documents, storage_path)
    
    # Save stats
    save_stats(stats, storage_path)
    
    logger.info("=" * 60)
    logger.info("Indexing complete!")
    logger.info("=" * 60)
    logger.info(f"Index location: {storage_path}")
    logger.info(f"Total files indexed: {stats['total_files']}")
    logger.info(f"Total lines of code: {stats['total_lines']:,}")
    logger.info("")
    logger.info("You can now use the Code Chat feature!")


if __name__ == "__main__":
    main()
