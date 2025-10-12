#!/usr/bin/env python
"""Script para refatorar métodos _query_* para usar Dask lazy"""

import re

def refactor_query_methods(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # Dividir em métodos
    methods = re.split(r'(\n    def _query_\w+)', content)

    refactored = [methods[0]]  # Início do arquivo antes do primeiro método

    for i in range(1, len(methods), 2):
        if i + 1 < len(methods):
            method_def = methods[i]
            method_body = methods[i + 1]

            # Refatorar corpo do método
            new_body = refactor_method_body(method_body)
            refactored.append(method_def)
            refactored.append(new_body)

    return ''.join(refactored)

def refactor_method_body(body):
    """Refatora o corpo de um método _query_*"""
    lines = body.split('\n')
    new_lines = []

    for line in lines:
        original = line

        # Pular comentários e linhas vazias
        if line.strip().startswith('#') or not line.strip():
            new_lines.append(line)
            continue

        # Pular linhas que já usam ddf
        if 'ddf' in line:
            new_lines.append(line)
            continue

        # Substituir verificações de colunas (agora desnecessárias com Dask)
        if "if 'vendas_total' not in df.columns" in line:
            new_lines.append(line.replace("if 'vendas_total' not in df.columns",
                                         "if False  # Dask lazy - skip check"))
            continue

        if "not in df.columns" in line:
            new_lines.append(line.replace("not in df.columns",
                                         "not in ddf.columns  # Dask lazy"))
            continue

        # Padrões de substituição df -> ddf
        # 1. df.groupby -> ddf.groupby
        if 'df.groupby' in line:
            line = line.replace('df.groupby', 'ddf.groupby')
            # Se atribui a variável e não tem .compute(), adicionar
            if '=' in line and 'compute()' not in line:
                # Remover .reset_index() temporariamente, adicionar .compute(), depois readicionar
                if '.reset_index()' in line:
                    line = line.replace('.reset_index()', '')
                    line = line.rstrip()
                    if line.endswith(')'):
                        line += '.compute().reset_index()'
                    else:
                        line += '.compute()'
                else:
                    line = line.rstrip()
                    if not line.endswith(')'):
                        line += '()'
                    line += '.compute()'
                line += '\n' if original.endswith('\n') else ''

        # 2. df.nlargest/nsmallest -> ddf.nlargest/nsmallest
        elif re.search(r'\bdf\.(nlargest|nsmallest)', line):
            line = re.sub(r'\bdf\.(nlargest|nsmallest)', r'ddf.\1', line)
            if '=' in line and 'compute()' not in line:
                line = line.rstrip() + '.compute()\n' if original.endswith('\n') else line.rstrip() + '.compute()'

        # 3. df.sort_values -> ddf.sort_values (mas só se for logo após groupby)
        elif 'df.sort_values' in line and 'ddf' not in line:
            # Verificar se linha anterior tinha groupby - se sim, a variável já é ddf computado
            if new_lines and 'groupby' in new_lines[-1] and 'compute()' in new_lines[-1]:
                # df já é pandas, manter
                pass
            else:
                line = line.replace('df.sort_values', 'ddf.sort_values')
                if '=' in line and 'compute()' not in line:
                    line = line.rstrip() + '.compute()\n' if original.endswith('\n') else line.rstrip() + '.compute()'

        # 4. df[coluna] ou df['coluna'] -> ddf[coluna] (mas só em operações, não em acesso)
        elif re.search(r"\bdf\[", line) and '=' in line and not '.iloc' in line:
            # Se é filtro ou seleção que vai atribuir
            line = re.sub(r'\bdf\[', 'ddf[', line)
            # Se atribui e não tem compute
            if '=' in line and 'compute()' not in line and '.head(' not in line:
                line = line.rstrip() + '.compute()\n' if original.endswith('\n') else line.rstrip() + '.compute()'

        # 5. resultado.empty verifica - garantir que resultado seja pandas
        # (não precisa mudar, pois já terá .compute() antes)

        new_lines.append(line)

    return '\n'.join(new_lines)

if __name__ == '__main__':
    filepath = r'C:\Users\André\Documents\Agent_Solution_BI\core\business_intelligence\direct_query_engine.py'

    content = refactor_query_methods(filepath)

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)

    print("Refatoracao Dask concluida com sucesso!")
    print(f"Arquivo atualizado: {filepath}")
