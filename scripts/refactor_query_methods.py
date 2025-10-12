"""
Script para refatorar métodos _query_* para usar ParquetAdapter ao invés de DataFrame.
"""

import re
from pathlib import Path

def refactor_query_methods(file_path: str):
    """Refatora todos os métodos _query_* que ainda usam DataFrame."""

    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Padrão para encontrar métodos que usam DataFrame
    pattern = r'(def _query_\w+\(self,\s*)df: pd\.DataFrame(,\s*params: Dict\[str, Any\]\s*\)\s*->\s*Dict\[str, Any\]:)'

    # Código a ser inserido após a definição do método
    data_loading_code = '''
        data = adapter.execute_query({})
        if not data or ('error' in data[0] and data[0]['error']):
            return {"error": f"Falha ao carregar dados: {data[0].get('error') if data else 'Unknown error'}", "type": "error"}
        df = pd.DataFrame(data)
'''

    def replace_method(match):
        """Substitui a assinatura do método e adiciona código de carregamento."""
        method_def = match.group(1)
        method_end = match.group(2)

        # Nova assinatura com adapter
        new_signature = f"{method_def}adapter: ParquetAdapter{method_end}"

        return new_signature

    # Substituir assinaturas
    modified_content = re.sub(pattern, replace_method, content)

    # Agora precisamos adicionar o código de carregamento após cada método refatorado
    # Padrão para encontrar o início do corpo do método (após docstring se houver)
    method_pattern = r'(def _query_\w+\(self, adapter: ParquetAdapter, params: Dict\[str, Any\]\) -> Dict\[str, Any\]:)\n(\s+""".*?"""\n)?(\s+)'

    def add_loading_code(match):
        """Adiciona código de carregamento de dados."""
        method_def = match.group(1)
        docstring = match.group(2) if match.group(2) else ""
        indent = match.group(3)

        # Verificar se o código de carregamento já existe
        # (para não duplicar em métodos já refatorados)
        if 'adapter.execute_query' in match.string[match.end():match.end()+500]:
            return match.group(0)  # Já tem o código, não adicionar

        return f"{method_def}\n{docstring}{indent}data = adapter.execute_query({{}})\n{indent}if not data or ('error' in data[0] and data[0]['error']):\n{indent}    return {{\"error\": f\"Falha ao carregar dados: {{data[0].get('error') if data else 'Unknown error'}}\", \"type\": \"error\"}}\n{indent}df = pd.DataFrame(data)\n{indent}"

    # modified_content = re.sub(method_pattern, add_loading_code, modified_content, flags=re.DOTALL)

    # Salvar arquivo modificado
    backup_path = file_path.replace('.py', '_backup.py')

    # Fazer backup
    with open(backup_path, 'w', encoding='utf-8') as f:
        f.write(content)

    print(f"[OK] Backup criado: {backup_path}")

    # Salvar arquivo refatorado
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(modified_content)

    print(f"[OK] Arquivo refatorado: {file_path}")

    # Contar quantos métodos foram modificados
    original_count = len(re.findall(r'def _query_\w+\(self,\s*df: pd\.DataFrame', content))
    modified_count = len(re.findall(r'def _query_\w+\(self, adapter: ParquetAdapter', modified_content))
    original_adapter_count = len(re.findall(r'def _query_\w+\(self, adapter: ParquetAdapter', content))
    refactored_count = modified_count - original_adapter_count

    print(f"\n[STATS] Estatisticas:")
    print(f"   - Metodos com DataFrame (antes): {original_count}")
    print(f"   - Metodos com ParquetAdapter (depois): {modified_count}")
    print(f"   - Metodos refatorados: {refactored_count}")

    return modified_content

if __name__ == "__main__":
    file_path = r"C:\Users\André\Documents\Agent_Solution_BI\core\business_intelligence\direct_query_engine.py"
    refactor_query_methods(file_path)
    print("\n[OK] Refatoracao concluida!")
