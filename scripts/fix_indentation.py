#!/usr/bin/env python
"""Script para corrigir indentação do streamlit_app.py"""

# Ler o arquivo
with open('streamlit_app.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Corrigir linhas 882-1094 (índice 881-1093)
# Remover 1 nível de indentação (4 espaços ou 1 tab)
fixed_lines = []
for i, line in enumerate(lines):
    # Linhas 882-1094 precisam de -4 espaços (ou -1 tab)
    if 881 <= i <= 1093:  # índice 0-based
        if line.startswith('                        '):  # 24 espaços (6 níveis)
            fixed_lines.append(line[4:])  # Remover 4 espaços
        elif line.startswith('\t\t\t\t\t\t'):  # 6 tabs
            fixed_lines.append(line[1:])  # Remover 1 tab
        else:
            # Já está correto ou é linha em branco
            fixed_lines.append(line)
    else:
        fixed_lines.append(line)

# Salvar
with open('streamlit_app.py', 'w', encoding='utf-8') as f:
    f.writelines(fixed_lines)

print("✅ Indentação corrigida!")
print(f"Total de linhas processadas: {len(lines)}")
