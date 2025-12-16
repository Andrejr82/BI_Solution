import sys
import os
sys.path.insert(0, os.path.join(os.getcwd(), "backend"))

from app.core.utils.session_manager import SessionManager
import shutil
import os

# Setup
test_dir = "test_sessions"
if os.path.exists(test_dir):
    shutil.rmtree(test_dir)
    
manager = SessionManager(storage_dir=test_dir)
session_id = "test_session_123"

# 1. Add User Message
print("1. Adicionando mensagem do usuário...")
manager.add_message(session_id, "user", "Qual o produto mais vendido?")

# 2. Add Assistant Message
print("2. Adicionando resposta do assistente...")
manager.add_message(session_id, "assistant", "O produto mais vendido é X.")

# 3. Retrieve History
print("3. Recuperando histórico...")
history = manager.get_history(session_id)
print(f"Histórico recuperado ({len(history)} itens):")
for msg in history:
    print(f" - {msg['role']}: {msg['content']}")

if len(history) != 2:
    print("❌ ERRO: Histórico deveria ter 2 mensagens.")
else:
    print("✅ Sucesso: Histórico persistido corretamente.")

# 4. Check formatting
if history[0]['role'] != 'user' or history[1]['role'] != 'assistant':
    print("❌ ERRO: Roles incorretos.")
else:
    print("✅ Sucesso: Roles corretos.")
