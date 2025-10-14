"""
Script de Verificação - Streamlit App
Verifica se streamlit_app.py está OK antes de rodar
"""
import sys
import ast

def verify_syntax(filename):
    """Verifica sintaxe Python"""
    print(f"[1/4] Verificando sintaxe Python de {filename}...")
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            code = f.read()
        ast.parse(code)
        print("   [OK] Sintaxe Python válida")
        return True
    except SyntaxError as e:
        print(f"   [ERRO] Sintaxe inválida: {e}")
        return False

def verify_imports():
    """Verifica imports críticos"""
    print("\n[2/4] Verificando imports críticos...")
    critical_imports = [
        'streamlit',
        'pandas',
        'dotenv'
    ]

    all_ok = True
    for module in critical_imports:
        try:
            __import__(module.split('.')[0])
            print(f"   [OK] {module}")
        except ImportError:
            print(f"   [ERRO] {module} não encontrado")
            all_ok = False

    return all_ok

def verify_file_structure():
    """Verifica estrutura de arquivos"""
    print("\n[3/4] Verificando estrutura de arquivos...")
    import os

    required_files = [
        'streamlit_app.py',
        'data/parquet/admmat.parquet',
        '.env'
    ]

    all_ok = True
    for file_path in required_files:
        if os.path.exists(file_path):
            print(f"   [OK] {file_path}")
        else:
            print(f"   [AVISO] {file_path} não encontrado")
            if file_path == '.env':
                print(f"         (Se estiver no Streamlit Cloud, .env não é necessário)")
            else:
                all_ok = False

    return all_ok

def verify_specific_code():
    """Verifica código específico do sistema 100% IA"""
    print("\n[4/4] Verificando implementação 100% IA...")

    with open('streamlit_app.py', 'r', encoding='utf-8') as f:
        content = f.read()

    checks = [
        ('if True:  # Simplificado para sempre processar com IA', 'Fluxo 100% IA presente'),
        ('DirectQueryEngine desabilitado - 100% IA', 'Comentário explicativo presente'),
        ('Sistema 100% IA Ativo', 'UI atualizada'),
        ('🤖 Processando com IA...', 'Spinner atualizado')
    ]

    all_ok = True
    for code_snippet, description in checks:
        if code_snippet in content:
            print(f"   [OK] {description}")
        else:
            print(f"   [ERRO] {description} - NÃO ENCONTRADO")
            all_ok = False

    return all_ok

def main():
    print("="*60)
    print("VERIFICAÇÃO DO STREAMLIT APP - SISTEMA 100% IA")
    print("="*60)

    results = []

    results.append(("Sintaxe Python", verify_syntax('streamlit_app.py')))
    results.append(("Imports críticos", verify_imports()))
    results.append(("Estrutura de arquivos", verify_file_structure()))
    results.append(("Código 100% IA", verify_specific_code()))

    print("\n" + "="*60)
    print("RESULTADO FINAL")
    print("="*60)

    for name, success in results:
        status = "[PASS]" if success else "[FAIL]"
        print(f"{status} {name}")

    all_passed = all(success for _, success in results)

    if all_passed:
        print("\n[SUCCESS] Todos os testes passaram!")
        print("\nO arquivo está pronto para rodar:")
        print("  streamlit run streamlit_app.py")
        return 0
    else:
        print("\n[WARNING] Alguns testes falharam.")
        print("Verifique os erros acima antes de rodar o Streamlit.")
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
