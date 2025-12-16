import sys
import os
from pathlib import Path
import logging

# Config logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Add backend to path
sys.path.append(str(Path.cwd() / "backend"))

# Mock settings
class Settings:
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

from llama_index.core import StorageContext, load_index_from_storage
from llama_index.vector_stores.faiss import FaissVectorStore
import faiss

def debug_load():
    storage_path = Path("./storage")
    print(f"Testing load from: {storage_path.resolve()}")
    
    if not storage_path.exists():
        print("❌ Storage path does not exist!")
        return

    try:
        print("Attempting to load storage context...")
        # Try loading strictly what we have
        storage_context = StorageContext.from_defaults(
            persist_dir=str(storage_path)
        )
        print("✅ Storage context loaded.")
        
        print("Attempting to load index...")
        index = load_index_from_storage(storage_context)
        print("✅ Index loaded successfully!")
        
    except Exception as e:
        print(f"❌ Error loading index: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv("backend/.env")
    debug_load()
