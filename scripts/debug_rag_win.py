
import sys
import os
import json
import logging
import traceback
from pathlib import Path

# Configure logging to console and file
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler("rag_debug_output.log", mode='w', encoding='utf-8')
    ]
)
logger = logging.getLogger(__name__)

def debug_rag():
    print("="*50)
    print("🚀 STARTING SURGICAL DEBUG")
    print("="*50)

    # 1. Path Resolution Debug
    print("\n[1] CHECKING PATH RESOLUTION")
    
    # Simulate code_rag_service.py location (backend/app/core/code_rag_service.py)
    # We are running from scripts/debug_rag_win.py (root/scripts)
    # So we need to calculate paths relative to root for simulation
    
    cwd = Path.cwd()
    print(f"CWD: {cwd}")
    
    # Expected storage path relative to ROOT
    storage_path = cwd / "storage"
    print(f"Target Storage Path: {storage_path}")
    print(f"Exists? {storage_path.exists()}")
    
    if storage_path.exists():
        print(f"Contents: {[str(p.name) for p in storage_path.glob('*')]}")
    else:
        print("❌ STORAGE PATH MISSING!")

    # 2. Check API Key
    print("\n[2] CHECKING API KEY")
    from dotenv import load_dotenv
    # Try loading from backend/.env
    env_path = cwd / "backend" / ".env"
    print(f"Loading env from: {env_path}")
    load_dotenv(env_path)
    
    api_key = os.getenv("GEMINI_API_KEY")
    if api_key:
        print(f"API Key found: {api_key[:5]}...{api_key[-5:]}")
    else:
        print("❌ GEMINI_API_KEY MISSING in env!")

    # 3. Import Dependencies
    print("\n[3] IMPORTING LLAMA-INDEX")
    try:
        from llama_index.core import (
            VectorStoreIndex,
            Settings,
            load_index_from_storage,
            StorageContext
        )
        # from llama_index.vector_stores.faiss import FaissVectorStore # DISABLED
        from llama_index.llms.gemini import Gemini
        from llama_index.embeddings.gemini import GeminiEmbedding
        print("✅ Imports successful")
    except Exception as e:
        print(f"❌ Import Failed: {e}")
        traceback.print_exc()
        return

    # 4. Configure Settings
    print("\n[4] CONFIGURING SETTINGS")
    try:
        if not api_key:
             print("Skipping settings config (no key)")
        else:
            Settings.llm = Gemini(
                model_name="models/gemini-2.0-flash", 
                api_key=api_key,
                temperature=0.1,
            )
            print("LLM Configured")
            
            Settings.embed_model = GeminiEmbedding(
                model_name="models/text-embedding-004",
                api_key=api_key,
            )
            print("Embeddings Configured")
    except Exception as e:
        print(f"❌ Configuration Failed: {e}")
        traceback.print_exc()

    # 5. Load Index
    print("\n[5] ATTEMPTING LOAD")
    try:
        if not storage_path.exists():
            print("Skipping load (no storage)")
            return

        print("Creating persistent storage context...")
        storage_context = StorageContext.from_defaults(
            persist_dir=str(storage_path)
        )
        print("✅ StorageContext created")
        
        print("Loading index from storage...")
        index = load_index_from_storage(storage_context)
        print("✅ INDEX LOADED SUCCESSFULLY!")
        
        print("Creating query engine...")
        engine = index.as_query_engine()
        print("✅ Engine created")

        # Test Query
        print("\n[6] TEST QUERY")
        response = engine.query("Como funciona a autenticação?")
        print(f"Response: {str(response)[:100]}...")

    except Exception as e:
        print(f"❌ LOAD FAILED: {e}")
        traceback.print_exc()

if __name__ == "__main__":
    try:
        debug_rag()
    except Exception as e:
        print(f"CRITICAL ERROR: {e}")
