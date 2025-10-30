"""
Script de Patch: Corrigir Estabilidade do Streamlit
====================================================

Aplica correções automáticas no streamlit_app.py para prevenir:
1. Loops infinitos de st.rerun()
2. MemoryError não tratados
3. Session state corruption
4. Crashes do navegador

USO:
    python patches/fix_streamlit_stability.py

Autor: Claude Code
Data: 2025-10-27
"""

import re
import os
import shutil
from datetime import datetime

BACKUP_DIR = "backups"
STREAMLIT_APP = "streamlit_app.py"


def create_backup():
    """Cria backup do arquivo original."""
    if not os.path.exists(BACKUP_DIR):
        os.makedirs(BACKUP_DIR)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_file = os.path.join(BACKUP_DIR, f"{STREAMLIT_APP}.backup_{timestamp}")

    shutil.copy2(STREAMLIT_APP, backup_file)
    print(f"✅ Backup criado: {backup_file}")

    return backup_file


def read_file(filepath):
    """Lê arquivo com encoding UTF-8."""
    with open(filepath, "r", encoding="utf-8") as f:
        return f.read()


def write_file(filepath, content):
    """Escreve arquivo com encoding UTF-8."""
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(content)


def apply_patches(content):
    """Aplica todos os patches no conteúdo."""
    patches_applied = []

    # PATCH 1: Adicionar import do streamlit_stability
    if "from core.utils.streamlit_stability import" not in content:
        # Encontrar linha de imports
        import_section = re.search(r"(import streamlit as st.*?)(\n\n|\nimport)", content, re.DOTALL)

        if import_section:
            new_import = (
                import_section.group(1) +
                "\nfrom core.utils.streamlit_stability import (\n"
                "    safe_rerun,\n"
                "    stable_component,\n"
                "    init_rerun_monitor,\n"
                "    check_memory_usage,\n"
                "    cleanup_old_session_data,\n"
                "    run_health_check\n"
                ")\n" +
                import_section.group(2)
            )

            content = content.replace(import_section.group(0), new_import)
            patches_applied.append("✅ Adicionado import streamlit_stability")

    # PATCH 2: Substituir st.rerun() por safe_rerun()
    rerun_count = len(re.findall(r'\bst\.rerun\(\)', content))

    if rerun_count > 0:
        content = re.sub(r'\bst\.rerun\(\)', 'safe_rerun()', content)
        patches_applied.append(f"✅ Substituídas {rerun_count} chamadas st.rerun() → safe_rerun()")

    # PATCH 3: Adicionar inicialização do monitor no início
    if "init_rerun_monitor()" not in content:
        # Encontrar primeira linha depois das configurações
        match = re.search(r"(# --- Estado da Sessão ---)", content)

        if match:
            new_section = (
                "# --- Inicialização do Monitor de Estabilidade ---\n"
                "init_rerun_monitor()\n"
                "check_memory_usage()\n\n" +
                match.group(1)
            )

            content = content.replace(match.group(0), new_section)
            patches_applied.append("✅ Adicionado init_rerun_monitor() no início")

    # PATCH 4: Adicionar cleanup periódico
    if "cleanup_old_session_data" not in content:
        # Adicionar cleanup antes do chat input
        match = re.search(r"(if prompt := st\.chat_input)", content)

        if match:
            new_section = (
                "    # Cleanup periódico (a cada 10 mensagens)\n"
                "    if len(st.session_state.get('messages', [])) % 10 == 0:\n"
                "        cleanup_old_session_data()\n\n"
                "    " + match.group(1)
            )

            content = content.replace(match.group(0), new_section)
            patches_applied.append("✅ Adicionado cleanup_old_session_data()")

    # PATCH 5: Wrapper de erro no query_backend
    if "# --- Quick Actions" in content and "@stable_component" not in content:
        # Adicionar decorator no query_backend
        match = re.search(r"(def query_backend\(user_input\):)", content)

        if match:
            new_function = (
                "@stable_component(\"Erro ao processar consulta\")\n"
                "    " + match.group(1)
            )

            content = content.replace(match.group(0), new_function)
            patches_applied.append("✅ Adicionado @stable_component no query_backend")

    # PATCH 6: Health check para admins
    if "run_health_check" not in content:
        # Adicionar health check no sidebar para admins
        match = re.search(r"(# --- Painel de Controle \(Admin\) ---)", content)

        if match:
            health_check_section = (
                match.group(1) + "\n"
                "    # 🏥 Health Check\n"
                "    health = run_health_check()\n"
                "    if health['status'] != 'healthy':\n"
                "        with st.sidebar.expander(f\"⚠️ Status: {health['status'].upper()}\", expanded=False):\n"
                "            if health['issues']:\n"
                "                st.error(\"**Problemas:**\")\n"
                "                for issue in health['issues']:\n"
                "                    st.write(f\"- {issue}\")\n"
                "            if health['warnings']:\n"
                "                st.warning(\"**Avisos:**\")\n"
                "                for warning in health['warnings']:\n"
                "                    st.write(f\"- {warning}\")\n\n"
            )

            content = content.replace(match.group(0), health_check_section)
            patches_applied.append("✅ Adicionado health check no sidebar")

    return content, patches_applied


def main():
    """Função principal."""
    print("="*60)
    print("PATCH: Estabilidade do Streamlit")
    print("="*60)

    # Verificar se arquivo existe
    if not os.path.exists(STREAMLIT_APP):
        print(f"❌ Arquivo não encontrado: {STREAMLIT_APP}")
        print(f"   Execute este script da raiz do projeto")
        return 1

    # Criar backup
    print("\n[1/4] Criando backup...")
    backup_file = create_backup()

    # Ler arquivo
    print("\n[2/4] Lendo arquivo original...")
    original_content = read_file(STREAMLIT_APP)
    print(f"   Tamanho: {len(original_content)} caracteres")

    # Aplicar patches
    print("\n[3/4] Aplicando patches...")
    patched_content, patches_applied = apply_patches(original_content)

    if not patches_applied:
        print("   ℹ️ Nenhum patch necessário. Arquivo já está atualizado.")
        return 0

    for patch in patches_applied:
        print(f"   {patch}")

    # Salvar arquivo patched
    print("\n[4/4] Salvando arquivo corrigido...")
    write_file(STREAMLIT_APP, patched_content)

    print("\n" + "="*60)
    print("✅ PATCH APLICADO COM SUCESSO!")
    print("="*60)

    print("\n📋 RESUMO:")
    print(f"   Total de patches: {len(patches_applied)}")
    print(f"   Backup salvo em: {backup_file}")

    print("\n🚀 PRÓXIMOS PASSOS:")
    print("   1. Revisar mudanças: git diff streamlit_app.py")
    print("   2. Testar aplicação: streamlit run streamlit_app.py")
    print("   3. Se tudo OK, commitar mudanças")
    print("   4. Se houver problemas, restaurar backup:")
    print(f"      cp {backup_file} {STREAMLIT_APP}")

    return 0


if __name__ == "__main__":
    import sys
    sys.exit(main())
