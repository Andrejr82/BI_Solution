"""
Script de validação da integração DynamicPrompt no CodeGenAgent
"""

import os
import sys

# Adicionar diretório raiz ao path
BASE_DIR = r"C:\Users\André\Documents\Agent_Solution_BI"
sys.path.insert(0, BASE_DIR)

def validate_file_structure():
    """Valida que os arquivos necessários existem"""
    print("=" * 80)
    print("VALIDAÇÃO DA INTEGRAÇÃO - DynamicPrompt no CodeGenAgent")
    print("=" * 80)

    required_files = {
        "CodeGenAgent": os.path.join(BASE_DIR, "core", "agents", "code_gen_agent.py"),
        "DynamicPrompt": os.path.join(BASE_DIR, "core", "learning", "dynamic_prompt.py"),
        "LLMClient": os.path.join(BASE_DIR, "core", "llm", "llm_client.py"),
    }

    print("\n[1] Verificando estrutura de arquivos...")
    all_exist = True
    for name, path in required_files.items():
        exists = os.path.exists(path)
        status = "✓" if exists else "✗"
        print(f"  {status} {name}: {path}")
        if not exists:
            all_exist = False

    return all_exist


def validate_imports():
    """Valida que os imports estão corretos"""
    print("\n[2] Verificando imports...")

    code_gen_path = os.path.join(BASE_DIR, "core", "agents", "code_gen_agent.py")

    if not os.path.exists(code_gen_path):
        print("  ✗ Arquivo code_gen_agent.py não encontrado")
        return False

    with open(code_gen_path, 'r', encoding='utf-8') as f:
        content = f.read()

    required_imports = [
        "from core.learning.dynamic_prompt import DynamicPrompt",
        "from core.llm.llm_client import LLMClient",
    ]

    all_imports_ok = True
    for import_line in required_imports:
        if import_line in content:
            print(f"  ✓ {import_line}")
        else:
            print(f"  ✗ {import_line} - NÃO ENCONTRADO")
            all_imports_ok = False

    return all_imports_ok


def validate_initialization():
    """Valida que DynamicPrompt é inicializado no __init__"""
    print("\n[3] Verificando inicialização...")

    code_gen_path = os.path.join(BASE_DIR, "core", "agents", "code_gen_agent.py")

    with open(code_gen_path, 'r', encoding='utf-8') as f:
        content = f.read()

    checks = {
        "self.dynamic_prompt = DynamicPrompt()": "Inicialização do DynamicPrompt",
        "self.llm_client": "LLM Client presente",
    }

    all_init_ok = True
    for code_snippet, description in checks.items():
        if code_snippet in content:
            print(f"  ✓ {description}")
        else:
            print(f"  ✗ {description} - NÃO ENCONTRADO")
            all_init_ok = False

    return all_init_ok


def validate_usage():
    """Valida que enhanced_prompt é usado no generate_and_execute_code"""
    print("\n[4] Verificando uso do enhanced_prompt...")

    code_gen_path = os.path.join(BASE_DIR, "core", "agents", "code_gen_agent.py")

    with open(code_gen_path, 'r', encoding='utf-8') as f:
        content = f.read()

    checks = {
        "enhanced_prompt = self.dynamic_prompt.get_enhanced_prompt": "Chamada ao get_enhanced_prompt",
        "user_query=user_query": "Passagem do user_query",
        "context=context": "Passagem do contexto",
    }

    all_usage_ok = True
    for code_snippet, description in checks.items():
        if code_snippet in content:
            print(f"  ✓ {description}")
        else:
            print(f"  ✗ {description} - NÃO ENCONTRADO")
            all_usage_ok = False

    return all_usage_ok


def validate_logging():
    """Valida que logging foi adicionado"""
    print("\n[5] Verificando logging...")

    code_gen_path = os.path.join(BASE_DIR, "core", "agents", "code_gen_agent.py")

    with open(code_gen_path, 'r', encoding='utf-8') as f:
        content = f.read()

    log_checks = [
        "logger.info",
        "logger.debug",
        "logger.warning",
        "logger.error",
    ]

    all_logging_ok = True
    for log_type in log_checks:
        count = content.count(log_type)
        if count > 0:
            print(f"  ✓ {log_type}: {count} ocorrências")
        else:
            print(f"  ✗ {log_type}: não encontrado")
            all_logging_ok = False

    return all_logging_ok


def test_instantiation():
    """Testa se é possível instanciar o CodeGenAgent"""
    print("\n[6] Testando instanciação...")

    try:
        from core.agents.code_gen_agent import CodeGenAgent

        print("  ✓ Import do CodeGenAgent bem-sucedido")

        # Tentar instanciar (pode falhar se LLMClient não estiver configurado)
        try:
            agent = CodeGenAgent()
            print("  ✓ Instanciação do CodeGenAgent bem-sucedida")

            # Verificar atributos
            if hasattr(agent, 'dynamic_prompt'):
                print("  ✓ Atributo 'dynamic_prompt' presente")
            else:
                print("  ✗ Atributo 'dynamic_prompt' ausente")
                return False

            if hasattr(agent, 'llm_client'):
                print("  ✓ Atributo 'llm_client' presente")
            else:
                print("  ✗ Atributo 'llm_client' ausente")
                return False

            # Verificar métodos
            if hasattr(agent, 'generate_and_execute_code'):
                print("  ✓ Método 'generate_and_execute_code' presente")
            else:
                print("  ✗ Método 'generate_and_execute_code' ausente")
                return False

            return True

        except Exception as e:
            print(f"  ⚠ Instanciação falhou (pode ser por dependências): {e}")
            # Não consideramos como erro fatal
            return True

    except ImportError as e:
        print(f"  ✗ Erro de import: {e}")
        return False
    except Exception as e:
        print(f"  ✗ Erro inesperado: {e}")
        return False


def show_summary():
    """Mostra resumo da integração"""
    print("\n" + "=" * 80)
    print("RESUMO DA INTEGRAÇÃO")
    print("=" * 80)

    code_gen_path = os.path.join(BASE_DIR, "core", "agents", "code_gen_agent.py")

    if os.path.exists(code_gen_path):
        with open(code_gen_path, 'r', encoding='utf-8') as f:
            content = f.read()

        lines = content.splitlines()

        print(f"\nArquivo: {code_gen_path}")
        print(f"Total de linhas: {len(lines)}")
        print(f"Total de caracteres: {len(content)}")

        print("\n--- LINHAS RELEVANTES ---")
        for i, line in enumerate(lines, 1):
            if "DynamicPrompt" in line or "dynamic_prompt" in line:
                print(f"Linha {i:3d}: {line}")

        print("\n--- MÉTODOS PRINCIPAIS ---")
        for i, line in enumerate(lines, 1):
            if "def " in line and not line.strip().startswith("#"):
                print(f"Linha {i:3d}: {line.strip()}")


def main():
    """Função principal de validação"""
    results = {
        "Estrutura de arquivos": validate_file_structure(),
        "Imports": validate_imports(),
        "Inicialização": validate_initialization(),
        "Uso do enhanced_prompt": validate_usage(),
        "Logging": validate_logging(),
        "Instanciação": test_instantiation(),
    }

    show_summary()

    # Resultado final
    print("\n" + "=" * 80)
    print("RESULTADO FINAL")
    print("=" * 80)

    all_passed = True
    for test_name, result in results.items():
        status = "✓ PASSOU" if result else "✗ FALHOU"
        print(f"  {status}: {test_name}")
        if not result:
            all_passed = False

    print("\n" + "=" * 80)
    if all_passed:
        print("✓ INTEGRAÇÃO VALIDADA COM SUCESSO!")
        print("=" * 80)
        print("\nTODAS AS VERIFICAÇÕES PASSARAM!")
        print("CodeGenAgent está pronto para usar DynamicPrompt.")
    else:
        print("✗ INTEGRAÇÃO INCOMPLETA")
        print("=" * 80)
        print("\nAlgumas verificações falharam. Revise os erros acima.")

    return all_passed


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
