"""Script para ler code_gen_agent.py e preparar integração do DynamicPrompt"""

import os

# Tentar múltiplos caminhos possíveis
possible_paths = [
    r"C:\Users\André\Documents\Agent_Solution_BI\core\agents\code_gen_agent.py",
    r"C:\Users\André\Documents\Agent_Solution_BI\core\agents\code_gen_agent_new.py",
    "./core/agents/code_gen_agent.py",
]

for file_path in possible_paths:
    if os.path.exists(file_path):
        print(f"\n{'='*80}")
        print(f"ARQUIVO ENCONTRADO: {file_path}")
        print('='*80)

        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        print(content)
        print('='*80)
        print(f"Total de linhas: {len(content.splitlines())}")
        print(f"Total de caracteres: {len(content)}")
        print('='*80)

        # Análise do prompt atual
        if "prompt" in content.lower():
            print("\n[ANÁLISE] Encontradas referências a 'prompt' no arquivo:")
            for i, line in enumerate(content.splitlines(), 1):
                if "prompt" in line.lower():
                    print(f"  Linha {i}: {line.strip()}")

        break
else:
    print("\n[ERRO] Arquivo code_gen_agent.py não encontrado em nenhum dos caminhos:")
    for path in possible_paths:
        print(f"  - {path}")

    # Listar arquivos no diretório core/agents/
    agents_dir = r"C:\Users\André\Documents\Agent_Solution_BI\core\agents"
    if os.path.exists(agents_dir):
        print(f"\n[INFO] Arquivos em {agents_dir}:")
        for file in os.listdir(agents_dir):
            if file.endswith('.py'):
                print(f"  - {file}")
