"""
Remove método duplicado _query_top_produtos_por_segmento (versão antiga sem filtros).
"""

def remove_duplicate():
    file_path = r"C:\Users\André\Documents\Agent_Solution_BI\core\business_intelligence\direct_query_engine.py"

    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    # Remover linhas 1044-1118 (75 linhas do método duplicado)
    # Índices são base-0, então linha 1044 = índice 1043
    new_lines = lines[:1043] + lines[1118:]

    # Salvar
    with open(file_path, 'w', encoding='utf-8') as f:
        f.writelines(new_lines)

    print(f"[OK] Metodo duplicado removido (linhas 1044-1118)")
    print(f"[OK] Total de linhas removidas: 75")
    print(f"[OK] Arquivo atualizado: {file_path}")

if __name__ == "__main__":
    remove_duplicate()
