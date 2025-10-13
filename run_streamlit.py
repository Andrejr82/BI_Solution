"""
Script de Inicialização do Agent_BI
Inicia o Streamlit com configurações otimizadas
"""
import os
import sys
import subprocess
import webbrowser
import time

def print_header():
    """Exibe cabeçalho"""
    print("=" * 50)
    print("   Agent_BI - Sistema 100% IA")
    print("=" * 50)
    print()

def check_streamlit():
    """Verifica se Streamlit está instalado"""
    try:
        import streamlit
        print("[OK] Streamlit encontrado")
        return True
    except ImportError:
        print("[ERRO] Streamlit não encontrado!")
        print("Execute: pip install -r requirements.txt")
        return False

def check_dependencies():
    """Verifica dependências críticas"""
    print("\n[1/3] Verificando dependências...")

    critical_modules = ['streamlit', 'pandas', 'dotenv']
    all_ok = True

    for module in critical_modules:
        try:
            __import__(module.split('.')[0])
            print(f"  [OK] {module}")
        except ImportError:
            print(f"  [ERRO] {module} não encontrado")
            all_ok = False

    return all_ok

def start_streamlit():
    """Inicia o servidor Streamlit"""
    print("\n[2/3] Iniciando servidor Streamlit...")
    print("\n" + "=" * 50)
    print("   URLs de Acesso:")
    print("=" * 50)
    print("   Local:    http://localhost:8501")
    print("   Network:  http://127.0.0.1:8501")
    print("=" * 50)
    print("\nO navegador abrirá automaticamente...")
    print("Pressione Ctrl+C para parar o servidor\n")

    # Aguardar um pouco e então abrir o navegador
    time.sleep(2)

    try:
        # Tentar abrir o navegador
        webbrowser.open('http://localhost:8501')
    except:
        print("[AVISO] Não foi possível abrir o navegador automaticamente")
        print("Abra manualmente: http://localhost:8501")

    # Executar Streamlit
    try:
        subprocess.run([
            sys.executable,
            '-m',
            'streamlit',
            'run',
            'streamlit_app.py'
        ], check=True)
    except KeyboardInterrupt:
        print("\n\nServidor Streamlit encerrado.")
    except Exception as e:
        print(f"\n[ERRO] Falha ao iniciar Streamlit: {e}")
        return False

    return True

def main():
    """Função principal"""
    print_header()

    # Verificar dependências
    if not check_dependencies():
        print("\n[ERRO] Dependências faltando. Instale com:")
        print("  pip install -r requirements.txt")
        input("\nPressione Enter para sair...")
        return 1

    print("[3/3] Tudo pronto!")

    # Iniciar Streamlit
    if not start_streamlit():
        input("\nPressione Enter para sair...")
        return 1

    return 0

if __name__ == "__main__":
    try:
        exit_code = main()
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n\nEncerrando...")
        sys.exit(0)
