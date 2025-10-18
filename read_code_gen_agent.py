"""Script para ler o arquivo code_gen_agent.py"""

file_path = r"C:\Users\André\Documents\Agent_Solution_BI\core\agents\code_gen_agent.py"

try:
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    print("=" * 80)
    print(f"ARQUIVO: {file_path}")
    print("=" * 80)
    print(content)
    print("=" * 80)
    print(f"Total de linhas: {len(content.splitlines())}")
except FileNotFoundError:
    print(f"ERRO: Arquivo não encontrado: {file_path}")
except Exception as e:
    print(f"ERRO ao ler arquivo: {e}")
