"""
Script para adicionar código de carregamento de dados em métodos _query_* refatorados.
"""

import re
from pathlib import Path

def add_data_loading_to_methods(file_path: str):
    """Adiciona código de carregamento de dados após a definição de cada método."""

    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Código a ser inserido
    loading_code = """data = adapter.execute_query({})
        if not data or ('error' in data[0] and data[0]['error']):
            return {"error": f"Falha ao carregar dados: {data[0].get('error') if data else 'Unknown error'}", "type": "error"}
        df = pd.DataFrame(data)

        """

    # Padrão: encontrar métodos que recebem adapter mas ainda não têm o código de carregamento
    # Procurar por: def _query_*(...adapter...) seguido de docstring e então código que usa 'df'
    pattern = r'(def _query_\w+\(self, adapter: ParquetAdapter, params: Dict\[str, Any\]\) -> Dict\[str, Any\]:)\n(\s+)(""".*?""")\n(\s+)(if |return |[a-z_]+\s*=\s*df)'

    matches_found = 0

    def replace_with_loading(match):
        nonlocal matches_found
        method_def = match.group(1)
        indent1 = match.group(2)
        docstring = match.group(3)
        indent2 = match.group(4)
        first_line = match.group(5)

        # Verificar se já tem o código de carregamento
        # (verificando os próximos 500 caracteres)
        next_content = content[match.end()-50:match.end()+500]
        if 'adapter.execute_query' in next_content:
            return match.group(0)  # Já tem, não adicionar

        matches_found += 1
        return f"{method_def}\n{indent1}{docstring}\n{indent2}{loading_code}{indent2}{first_line}"

    modified_content = re.sub(pattern, replace_with_loading, content, flags=re.DOTALL)

    if matches_found == 0:
        # Tentar padrão alternativo: sem docstring
        pattern2 = r'(def _query_\w+\(self, adapter: ParquetAdapter, params: Dict\[str, Any\]\) -> Dict\[str, Any\]:)\n(\s+)(if |return |[a-z_]+\s*=\s*df)'

        def replace_no_docstring(match):
            nonlocal matches_found
            method_def = match.group(1)
            indent = match.group(2)
            first_line = match.group(3)

            # Verificar se já tem o código de carregamento
            next_content = content[match.end()-50:match.end()+500]
            if 'adapter.execute_query' in next_content:
                return match.group(0)

            matches_found += 1
            return f"{method_def}\n{indent}{loading_code}{indent}{first_line}"

        modified_content = re.sub(pattern2, replace_no_docstring, modified_content)

    # Salvar arquivo modificado
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(modified_content)

    print(f"[OK] Arquivo atualizado: {file_path}")
    print(f"[STATS] Metodos com codigo de carregamento adicionado: {matches_found}")

    return modified_content

if __name__ == "__main__":
    file_path = r"C:\Users\André\Documents\Agent_Solution_BI\core\business_intelligence\direct_query_engine.py"
    add_data_loading_to_methods(file_path)
    print("\n[OK] Adicao de codigo de carregamento concluida!")
