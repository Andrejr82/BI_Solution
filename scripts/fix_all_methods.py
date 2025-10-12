"""
Script robusto para adicionar código de carregamento em TODOS os métodos _query_*.
"""

import re

def fix_all_query_methods(file_path: str):
    """Adiciona código de carregamento de dados em todos os métodos que precisam."""

    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    modified_lines = []
    i = 0
    methods_fixed = 0

    while i < len(lines):
        line = lines[i]
        modified_lines.append(line)

        # Detectar início de método _query_ com adapter
        if re.match(r'\s*def _query_\w+\(self, adapter: ParquetAdapter, params:', line):
            method_name = re.search(r'def (_query_\w+)', line).group(1)
            i += 1

            # Pular docstring se existir
            if i < len(lines) and '"""' in lines[i]:
                modified_lines.append(lines[i])
                i += 1
                # Procurar fim da docstring
                while i < len(lines) and '"""' not in lines[i]:
                    modified_lines.append(lines[i])
                    i += 1
                if i < len(lines):
                    modified_lines.append(lines[i])  # Linha de fechamento da docstring
                    i += 1

            # Verificar se as próximas 10 linhas têm 'adapter.execute_query'
            has_loading = False
            for j in range(i, min(i + 10, len(lines))):
                if 'adapter.execute_query' in lines[j]:
                    has_loading = True
                    break

            # Se não tem código de carregamento, adicionar
            if not has_loading:
                indent = '        '  # 8 espaços (padrão para corpo de método)
                loading_code = [
                    f"{indent}data = adapter.execute_query({{}})\n",
                    f"{indent}if not data or ('error' in data[0] and data[0]['error']):\n",
                    f'{indent}    return {{"error": f"Falha ao carregar dados: {{data[0].get(\'error\') if data else \'Unknown error\'}}", "type": "error"}}\n',
                    f"{indent}df = pd.DataFrame(data)\n",
                    f"\n"
                ]
                modified_lines.extend(loading_code)
                methods_fixed += 1
                print(f"[FIX] {method_name}")
            continue

        i += 1

    # Salvar arquivo modificado
    with open(file_path, 'w', encoding='utf-8') as f:
        f.writelines(modified_lines)

    print(f"\n[OK] Arquivo atualizado: {file_path}")
    print(f"[STATS] Metodos corrigidos: {methods_fixed}")

    return modified_lines

if __name__ == "__main__":
    file_path = r"C:\Users\André\Documents\Agent_Solution_BI\core\business_intelligence\direct_query_engine.py"
    fix_all_query_methods(file_path)
    print("\n[OK] Correcao concluida!")
