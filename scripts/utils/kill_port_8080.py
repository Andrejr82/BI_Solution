"""
Script para matar processos na porta 8080
"""
import subprocess
import sys
import re

def kill_process_on_port(port=8080):
    """Mata processo usando a porta especificada"""
    try:
        # Windows
        if sys.platform == 'win32':
            # Encontrar PID usando netstat
            result = subprocess.run(
                ['netstat', '-ano'],
                capture_output=True,
                text=True,
                shell=True
            )

            # Procurar pela porta
            for line in result.stdout.split('\n'):
                if f':{port}' in line and 'LISTENING' in line:
                    # Extrair PID (última coluna)
                    parts = line.split()
                    if parts:
                        pid = parts[-1]
                        print(f"Encontrado processo {pid} usando porta {port}")

                        # Matar processo
                        try:
                            subprocess.run(['taskkill', '/PID', pid, '/F'], shell=True)
                            print(f"[OK] Processo {pid} encerrado!")
                        except Exception as e:
                            print(f"[ERRO] Erro ao matar processo {pid}: {e}")

            print(f"\n[OK] Porta {port} liberada!")
            return True

        else:
            # Linux/Mac
            result = subprocess.run(
                ['lsof', '-ti', f':{port}'],
                capture_output=True,
                text=True
            )

            if result.stdout.strip():
                pid = result.stdout.strip()
                subprocess.run(['kill', '-9', pid])
                print(f"[OK] Processo {pid} encerrado!")
                return True
            else:
                print(f"Nenhum processo encontrado na porta {port}")
                return False

    except Exception as e:
        print(f"Erro: {e}")
        return False

if __name__ == "__main__":
    kill_process_on_port(8080)
