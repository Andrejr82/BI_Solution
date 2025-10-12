"""
Script completo para refatorar TODOS os métodos _query_* de uma vez.
"""

import re

def refactor_complete(file_path: str):
    """Refatora assinatura E adiciona código de carregamento em UMA passagem."""

    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Fazer backup
    backup_path = file_path.replace('.py', '_backup2.py')
    with open(backup_path, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"[OK] Backup criado: {backup_path}")

    # Padrão para encontrar métodos que ainda usam DataFrame
    # Captura a assinatura completa e a primeira linha do código após a docstring
    pattern = r'(def _query_\w+\(self,\s*)df: pd\.DataFrame(,\s*params: Dict\[str, Any\]\s*->\s*Dict\[str, Any\]:\s*\n)(\s+)("""[^"]*""")\n(\s+)'

    def replace_method(match):
        """Substitui a assinatura e adiciona código de carregamento."""
        prefix = match.group(1)  # "def _query_xxx(self, "
        suffix = match.group(2)  # ", params...) -> Dict...:\n"
        indent_docstring = match.group(3)  # espaços antes da docstring
        docstring = match.group(4)  # docstring
        indent_code = match.group(5)  # espaços antes do código

        # Nova assinatura
        new_signature = f"{prefix}adapter: ParquetAdapter{suffix}"

        # Código de carregamento
        loading_code = f'{indent_code}data = adapter.execute_query({{}})\n'
        loading_code += f'{indent_code}if not data or (\'error\' in data[0] and data[0][\'error\']):\n'
        loading_code += f'{indent_code}    return {{"error": f"Falha ao carregar dados: {{data[0].get(\'error\') if data else \'Unknown error\'}}", "type": "error"}}\n'
        loading_code += f'{indent_code}df = pd.DataFrame(data)\n\n'

        return f"{new_signature}{indent_docstring}{docstring}\n{loading_code}{indent_code}"

    # Aplicar refatoração
    modified_content = re.sub(pattern, replace_method, content, flags=re.DOTALL)

    # Contar quantos foram modificados
    original_count = len(re.findall(r'def _query_\w+\(self,\s*df: pd\.DataFrame', content))
    modified_count = len(re.findall(r'def _query_\w+\(self, adapter: ParquetAdapter', modified_content))
    refactored = modified_count - len(re.findall(r'def _query_\w+\(self, adapter: ParquetAdapter', content))

    # Salvar
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(modified_content)

    print(f"[OK] Arquivo refatorado: {file_path}")
    print(f"[STATS] Metodos originais com DataFrame: {original_count}")
    print(f"[STATS] Metodos refatorados nesta execucao: {refactored}")

    return modified_content

if __name__ == "__main__":
    file_path = r"C:\Users\André\Documents\Agent_Solution_BI\core\business_intelligence\direct_query_engine.py"
    refactor_complete(file_path)
    print("\n[OK] Refatoracao completa concluida!")
