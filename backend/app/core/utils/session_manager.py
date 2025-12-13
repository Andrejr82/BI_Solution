import json
import os
import logging
from typing import List, Dict, Any
from pathlib import Path

logger = logging.getLogger(__name__)

class SessionManager:
    def __init__(self, storage_dir: str = "data/sessions"):
        self.storage_dir = Path(storage_dir)
        self.storage_dir.mkdir(parents=True, exist_ok=True)

    def _get_file_path(self, session_id: str) -> Path:
        return self.storage_dir / f"{session_id}.json"

    def get_history(self, session_id: str) -> List[Dict[str, str]]:
        """Retrieves chat history for a given session ID."""
        file_path = self._get_file_path(session_id)
        if not file_path.exists():
            return []
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return data.get("history", [])
        except Exception as e:
            logger.error(f"Error reading session {session_id}: {e}")
            return []

    def add_message(self, session_id: str, role: str, content: str):
        """Adds a message to the session history."""
        file_path = self._get_file_path(session_id)
        history = self.get_history(session_id)
        
        history.append({"role": role, "content": content})
        
        # Limit history length to prevent context window explosion (e.g., last 20 messages)
        # This is a basic optimization. RAG/Summarization would be better for long term.
        if len(history) > 20:
            history = history[-20:]

        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump({"history": history}, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"Error saving session {session_id}: {e}")

    def clear_session(self, session_id: str):
        """Deletes a session file."""
        file_path = self._get_file_path(session_id)
        if file_path.exists():
            try:
                os.remove(file_path)
            except Exception as e:
                logger.error(f"Error clearing session {session_id}: {e}")
