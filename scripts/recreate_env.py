import os
import shutil
from datetime import datetime

# Backup do arquivo atual
env_path = ".env"
backup_path = f".env.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

if os.path.exists(env_path):
    try:
        shutil.copy2(env_path, backup_path)
        print(f"Backup criado: {backup_path}")
    except Exception as e:
        print(f"Aviso: Não foi possível criar backup: {e}")

# Criar novo .env
env_content = """# Configurações do SQL Server
MSSQL_SERVER=FAMILIA\\SQLJR,1433
MSSQL_DATABASE=Projeto_Caculinha
MSSQL_USER=AgenteVirtual
MSSQL_PASSWORD=Cacula@2020

# Driver ODBC
DB_DRIVER=ODBC Driver 17 for SQL Server

# API Keys (SUBSTITUA A CHAVE DO GEMINI POR UMA NOVA)
GEMINI_API_KEY=COLE_SUA_NOVA_CHAVE_AQUI
DEEPSEEK_API_KEY=sk-deepseek-sua-chave

# Modelos Híbridos (Gemini 2.5 Flash + Gemini 3 Pro)
INTENT_CLASSIFICATION_MODEL=models/gemini-2.5-flash
CODE_GENERATION_MODEL=models/gemini-3-pro

# Cache
CACHE_AUTO_CLEAN=false
USE_QUERY_CACHE=true
"""

try:
    # Tentar remover arquivo antigo se existir
    if os.path.exists(env_path):
        os.remove(env_path)
        print(f"Arquivo antigo removido")
except Exception as e:
    print(f"Aviso ao remover arquivo antigo: {e}")

try:
    # Criar novo arquivo
    with open(env_path, "w", encoding="utf-8") as f:
        f.write(env_content)
    print(f"\n✅ Novo arquivo .env criado com sucesso!")
    print("\n⚠️  IMPORTANTE: Edite o arquivo .env e substitua 'COLE_SUA_NOVA_CHAVE_AQUI' pela sua nova chave do Gemini")
except Exception as e:
    print(f"❌ Erro ao criar .env: {e}")
