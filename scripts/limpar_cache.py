"""
Script Automatico de Limpeza de Cache - Streamlit
Versao Python (multiplataforma)
"""

import os
import shutil
import sys
from pathlib import Path
import subprocess

# Configurar encoding para Windows
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')

def print_header(title):
    """Imprime cabecalho formatado"""
    print("\n" + "=" * 60)
    print(f"  {title}")
    print("=" * 60 + "\n")

def limpar_cache_streamlit_cli():
    """Limpa cache via comando streamlit"""
    print("[1/5] Limpando cache via Streamlit CLI...")
    try:
        result = subprocess.run(
            ["streamlit", "cache", "clear"],
            capture_output=True,
            text=True,
            timeout=10
        )
        if result.returncode == 0:
            print("      OK Cache limpo via CLI")
            return True
        else:
            print("      AVISO Streamlit CLI nao respondeu")
            return False
    except FileNotFoundError:
        print("      AVISO Comando streamlit nao encontrado")
        return False
    except Exception as e:
        print(f"      AVISO Erro: {e}")
        return False

def limpar_pasta_cache():
    """Remove pasta de cache do Streamlit"""
    print("\n[2/5] Deletando pasta de cache...")

    # Localização do cache (Windows/Linux/Mac)
    home = Path.home()
    cache_path = home / ".streamlit" / "cache"

    try:
        if cache_path.exists():
            shutil.rmtree(cache_path)
            print(f"      OK Pasta deletada: {cache_path}")
            return True
        else:
            print(f"      INFO Pasta nao existe: {cache_path}")
            return False
    except Exception as e:
        print(f"      ERRO ao deletar: {e}")
        return False

def limpar_arquivos_python():
    """Remove arquivos .pyc e pastas __pycache__"""
    print("\n[3/5] Limpando arquivos .pyc e __pycache__...")

    base_dir = Path(__file__).parent
    count_pyc = 0
    count_pycache = 0

    # Remover .pyc
    for pyc_file in base_dir.rglob("*.pyc"):
        try:
            pyc_file.unlink()
            count_pyc += 1
        except:
            pass

    # Remover __pycache__
    for pycache_dir in base_dir.rglob("__pycache__"):
        try:
            shutil.rmtree(pycache_dir)
            count_pycache += 1
        except:
            pass

    print(f"      OK {count_pyc} arquivos .pyc removidos")
    print(f"      OK {count_pycache} pastas __pycache__ removidas")
    return count_pyc + count_pycache > 0

def limpar_session_state():
    """Remove session state do Streamlit"""
    print("\n[4/5] Limpando session state...")

    home = Path.home()
    session_path = home / ".streamlit" / "session_state"

    try:
        if session_path.exists():
            shutil.rmtree(session_path)
            print(f"      OK Session state removido")
            return True
        else:
            print(f"      INFO Session state nao existe")
            return False
    except Exception as e:
        print(f"      AVISO Erro: {e}")
        return False

def limpar_cache_adapter():
    """Remove cache do HybridAdapter no session_state"""
    print("\n[5/5] Limpando cache do HybridAdapter...")
    print("      INFO Cache do adapter sera limpo ao reiniciar Streamlit")
    return True

def main():
    """Função principal"""
    print_header("LIMPEZA DE CACHE - STREAMLIT")

    print("Iniciando limpeza completa...\n")

    # Executar limpezas
    results = []
    results.append(limpar_cache_streamlit_cli())
    results.append(limpar_pasta_cache())
    results.append(limpar_arquivos_python())
    results.append(limpar_session_state())
    results.append(limpar_cache_adapter())

    # Resumo
    print_header("LIMPEZA CONCLUÍDA")

    total = len(results)
    success = sum(results)

    print(f"OK {success}/{total} operacoes bem-sucedidas\n")

    print("PROXIMOS PASSOS:\n")
    print("1. Reiniciar o Streamlit:")
    print("   streamlit run streamlit_app.py\n")
    print("2. Fazer login na aplicacao\n")
    print("3. Testar pagina Transferencias\n")
    print("4. Verificar se os produtos aparecem\n")

    print("=" * 60)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nAVISO Limpeza cancelada pelo usuario")
        sys.exit(1)
    except Exception as e:
        print(f"\n\nERRO inesperado: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
