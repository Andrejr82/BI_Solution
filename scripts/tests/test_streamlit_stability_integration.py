"""
Script de Teste: Integração da Solução 3 (Estabilidade Streamlit)
==================================================================

Valida que todas as modificações foram aplicadas corretamente.

Uso:
    python scripts/tests/test_streamlit_stability_integration.py

Autor: Claude Code
Data: 2025-10-27
"""

import sys
import os
import re

# Adicionar path do projeto
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

STREAMLIT_APP_PATH = "streamlit_app.py"

def read_file(filepath):
    """Lê arquivo com encoding UTF-8."""
    with open(filepath, "r", encoding="utf-8") as f:
        return f.read()

def test_imports():
    """Testa se imports foram adicionados corretamente."""
    print("\n[Teste 1] Verificando imports...")

    content = read_file(STREAMLIT_APP_PATH)

    # Verificar imports
    required_imports = [
        "from core.utils.streamlit_stability import",
        "safe_rerun,",
        "stable_component,",
        "init_rerun_monitor,",
        "check_memory_usage,",
        "cleanup_old_session_data,",
        "run_health_check"
    ]

    all_found = True
    for imp in required_imports:
        if imp not in content:
            print(f"  [FAIL] Import não encontrado: {imp}")
            all_found = False

    if all_found:
        print("  [PASS] Todos os imports presentes")
        return True
    else:
        return False

def test_init_monitor():
    """Testa se init_rerun_monitor() foi adicionado."""
    print("\n[Teste 2] Verificando init_rerun_monitor()...")

    content = read_file(STREAMLIT_APP_PATH)

    if "init_rerun_monitor()" in content and "check_memory_usage()" in content:
        print("  [PASS] Monitor inicializado corretamente")
        return True
    else:
        print("  [FAIL] init_rerun_monitor() ou check_memory_usage() não encontrado")
        return False

def test_safe_rerun_replacement():
    """Testa se st.rerun() foi substituído por safe_rerun()."""
    print("\n[Teste 3] Verificando substituição st.rerun() -> safe_rerun()...")

    content = read_file(STREAMLIT_APP_PATH)

    # Contar ocorrências de safe_rerun()
    safe_rerun_count = len(re.findall(r'\bsafe_rerun\(\)', content))

    # Contar ocorrências restantes de st.rerun() (não deve haver)
    st_rerun_count = len(re.findall(r'\bst\.rerun\(\)', content))

    print(f"  - safe_rerun() encontrado: {safe_rerun_count} vezes")
    print(f"  - st.rerun() restante: {st_rerun_count} vezes")

    if safe_rerun_count >= 5 and st_rerun_count == 0:
        print(f"  [PASS] Substituição completa ({safe_rerun_count} chamadas ativas)")
        return True
    else:
        print("  [FAIL] Substituição incompleta")
        return False

def test_stable_component():
    """Testa se @stable_component foi adicionado ao query_backend."""
    print("\n[Teste 4] Verificando @stable_component no query_backend...")

    content = read_file(STREAMLIT_APP_PATH)

    # Verificar padrão: @stable_component(...) seguido de def query_backend
    pattern = r'@stable_component\([^)]+\)\s+def query_backend'

    if re.search(pattern, content):
        print("  [PASS] Decorator @stable_component presente")
        return True
    else:
        print("  [FAIL] Decorator não encontrado")
        return False

def test_cleanup():
    """Testa se cleanup periódico foi adicionado."""
    print("\n[Teste 5] Verificando cleanup periódico...")

    content = read_file(STREAMLIT_APP_PATH)

    if "cleanup_old_session_data()" in content:
        print("  [PASS] Cleanup periódico adicionado")
        return True
    else:
        print("  [FAIL] cleanup_old_session_data() não encontrado")
        return False

def test_health_check():
    """Testa se health check foi adicionado para admin."""
    print("\n[Teste 6] Verificando health check (admin)...")

    content = read_file(STREAMLIT_APP_PATH)

    if "run_health_check()" in content and "health['status']" in content:
        print("  [PASS] Health check adicionado")
        return True
    else:
        print("  [FAIL] run_health_check() não encontrado")
        return False

def test_module_import():
    """Testa se o módulo streamlit_stability pode ser importado."""
    print("\n[Teste 7] Testando import do módulo streamlit_stability...")

    try:
        from core.utils.streamlit_stability import (
            safe_rerun,
            stable_component,
            init_rerun_monitor,
            check_memory_usage,
            cleanup_old_session_data,
            run_health_check
        )
        print("  [PASS] Módulo importado com sucesso")
        return True
    except Exception as e:
        print(f"  [FAIL] Erro ao importar: {e}")
        return False

def main():
    """Função principal."""
    print("=" * 70)
    print("TESTE: Integração da Solução 3 (Estabilidade Streamlit)")
    print("=" * 70)

    # Verificar se arquivo existe
    if not os.path.exists(STREAMLIT_APP_PATH):
        print(f"\n[ERRO] Arquivo não encontrado: {STREAMLIT_APP_PATH}")
        print("Execute este script da raiz do projeto")
        return 1

    # Executar testes
    tests = [
        test_imports,
        test_init_monitor,
        test_safe_rerun_replacement,
        test_stable_component,
        test_cleanup,
        test_health_check,
        test_module_import
    ]

    results = []
    for test in tests:
        try:
            results.append(test())
        except Exception as e:
            print(f"  [ERRO] Exceção no teste: {e}")
            results.append(False)

    # Resumo
    print("\n" + "=" * 70)
    print("RESUMO DOS TESTES")
    print("=" * 70)

    passed = sum(results)
    total = len(results)

    print(f"\nTotal de testes: {total}")
    print(f"Testes passados: {passed}")
    print(f"Testes falhados: {total - passed}")

    if all(results):
        print("\n[SUCESSO] Todas as modificações foram aplicadas corretamente!")
        print("\nPróximos passos:")
        print("  1. Iniciar Streamlit: streamlit run streamlit_app.py")
        print("  2. Testar comportamento:")
        print("     - Fazer login")
        print("     - Executar queries")
        print("     - Verificar métricas (admin)")
        print("     - Testar health check (admin)")
        return 0
    else:
        print("\n[FALHA] Algumas modificações estão faltando.")
        print("Consulte a documentação: docs/SOLUCAO_FECHAMENTO_NAVEGADOR.md")
        return 1

if __name__ == "__main__":
    sys.exit(main())
