"""
Script para sincronizar usuários do SQL Server local para Streamlit Cloud.
Gera automaticamente os arquivos Python com usuários marcados como cloud_enabled.

Uso:
    python dev_tools/scripts/sync_users_to_cloud.py

Resultado:
    - Atualiza core/auth.py com CLOUD_USERS
    - Atualiza core/database/sql_server_auth_db.py com _local_users
    - Mostra resumo das alterações
"""

import os
import sys
from pathlib import Path

# Adicionar root do projeto ao path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from core.database import sql_server_auth_db
from core.utils.db_connection import get_db_connection
from sqlalchemy import text
from datetime import datetime


def get_cloud_enabled_users():
    """Busca usuários com cloud_enabled=1 no banco SQL Server"""
    try:
        conn = get_db_connection()
        if conn is None:
            print("❌ Erro: Banco de dados não disponível")
            return []

        with conn:
            result = conn.execute(
                text("""
                    SELECT username, role
                    FROM usuarios
                    WHERE cloud_enabled = 1 AND ativo = 1
                    ORDER BY username
                """)
            ).fetchall()

            users = []
            for row in result:
                users.append({
                    "username": row[0],
                    "role": row[1]
                })

            return users
    except Exception as e:
        print(f"❌ Erro ao buscar usuários: {e}")
        return []


def generate_cloud_users_dict(users):
    """Gera código Python para CLOUD_USERS em core/auth.py"""
    if not users:
        return """CLOUD_USERS = {
    "admin": {"password": "admin", "role": "admin"}
}"""

    lines = ["CLOUD_USERS = {"]
    for user in users:
        username = user["username"]
        role = user["role"]
        # Nota: senha é a mesma que o username para simplificar
        # Você pode alterar manualmente depois se necessário
        lines.append(f'    "{username}": {{"password": "{username}", "role": "{role}"}},')

    # Remover vírgula da última linha
    if lines[-1].endswith(','):
        lines[-1] = lines[-1][:-1]

    lines.append("}")
    return "\n".join(lines)


def generate_local_users_dict(users):
    """Gera código Python para _local_users em sql_server_auth_db.py"""
    if not users:
        return """_local_users = {
    "admin": {
        "password_hash": get_password_hash("admin"),
        "role": "admin",
        "ativo": True,
        "tentativas_invalidas": 0,
        "bloqueado_ate": None,
        "ultimo_login": None
    }
}"""

    lines = ["_local_users = {"]
    for user in users:
        username = user["username"]
        role = user["role"]
        lines.append(f'    "{username}": {{')
        lines.append(f'        "password_hash": get_password_hash("{username}"),')
        lines.append(f'        "role": "{role}",')
        lines.append('        "ativo": True,')
        lines.append('        "tentativas_invalidas": 0,')
        lines.append('        "bloqueado_ate": None,')
        lines.append('        "ultimo_login": None')
        lines.append('    },')

    # Remover vírgula da última linha
    if lines[-1].endswith(','):
        lines[-1] = lines[-1][:-1]

    lines.append("}")
    return "\n".join(lines)


def update_core_auth_py(cloud_users_code):
    """Atualiza core/auth.py com novos CLOUD_USERS"""
    file_path = project_root / "core" / "auth.py"

    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # Encontrar o bloco CLOUD_USERS e substituir
        import re
        pattern = r'CLOUD_USERS = \{[^}]*\}'

        if not re.search(pattern, content):
            print(f"⚠️ Aviso: Padrão CLOUD_USERS não encontrado em {file_path}")
            return False

        new_content = re.sub(pattern, cloud_users_code.replace('\n', '\n'), content, flags=re.DOTALL)

        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(new_content)

        print(f"✅ Atualizado: {file_path}")
        return True

    except Exception as e:
        print(f"❌ Erro ao atualizar core/auth.py: {e}")
        return False


def update_sql_server_auth_db_py(local_users_code):
    """Atualiza core/database/sql_server_auth_db.py com novos _local_users"""
    file_path = project_root / "core" / "database" / "sql_server_auth_db.py"

    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # Encontrar o bloco _local_users e substituir
        import re
        pattern = r'_local_users = \{[^}]*(?:\{[^}]*\}[^}]*)*\}'

        if not re.search(pattern, content):
            print(f"⚠️ Aviso: Padrão _local_users não encontrado em {file_path}")
            return False

        new_content = re.sub(pattern, local_users_code.replace('\n', '\n'), content, flags=re.DOTALL)

        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(new_content)

        print(f"✅ Atualizado: {file_path}")
        return True

    except Exception as e:
        print(f"❌ Erro ao atualizar sql_server_auth_db.py: {e}")
        return False


def main():
    print("=" * 60)
    print("🔄 SINCRONIZAÇÃO DE USUÁRIOS: LOCAL → CLOUD")
    print("=" * 60)
    print()

    # Buscar usuários habilitados para cloud
    print("📊 Buscando usuários com cloud_enabled=1...")
    users = get_cloud_enabled_users()

    if not users:
        print("⚠️ Nenhum usuário encontrado com cloud_enabled=1")
        print()
        print("💡 Dica: No Painel Admin, marque o checkbox 'Acesso Cloud' para os usuários")
        return

    print(f"✅ Encontrados {len(users)} usuários:")
    for user in users:
        print(f"   - {user['username']} ({user['role']})")
    print()

    # Gerar código Python
    print("🔧 Gerando código Python...")
    cloud_users_code = generate_cloud_users_dict(users)
    local_users_code = generate_local_users_dict(users)
    print()

    # Atualizar arquivos
    print("📝 Atualizando arquivos...")
    success1 = update_core_auth_py(cloud_users_code)
    success2 = update_sql_server_auth_db_py(local_users_code)
    print()

    if success1 and success2:
        print("=" * 60)
        print("✅ SINCRONIZAÇÃO CONCLUÍDA COM SUCESSO!")
        print("=" * 60)
        print()
        print("📋 Próximos passos:")
        print("   1. Revisar as alterações:")
        print("      - core/auth.py")
        print("      - core/database/sql_server_auth_db.py")
        print()
        print("   2. Fazer commit e push:")
        print("      git add core/auth.py core/database/sql_server_auth_db.py")
        print("      git commit -m 'sync: Atualizar usuários cloud'")
        print("      git push")
        print()
        print("   3. Aguardar redeploy do Streamlit Cloud (~2-3 min)")
        print()
        print(f"👥 {len(users)} usuários estarão disponíveis no Streamlit Cloud!")
    else:
        print("❌ Erro durante a sincronização. Verifique os logs acima.")


if __name__ == "__main__":
    main()
