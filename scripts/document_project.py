"""
Módulo para document_project.py. Fornece as funções: get_suggested_docstring, process_file, main.
"""

# document_project.py
import os
import ast
import argparse
from pathlib import Path
from typing import List, Optional, Tuple

# --- Configuração ---
ROOT_DIR = Path(__file__).parent
IGNORED_DIRS = {
    ".git", ".venv", "venv", "__pycache__", ".mypy_cache", 
    ".pytest_cache", "backup_lint", "backup_unused"
}

def get_suggested_docstring(file_path: Path, content: str) -> Optional[str]:
    """
    Analisa o conteúdo de um ficheiro Python e sugere um docstring de módulo.
    """
    try:
        tree = ast.parse(content)
    except SyntaxError:
        return "Ficheiro com erro de sintaxe, não foi possível gerar docstring."

    # Se já existe um docstring, não faz nada
    if ast.get_docstring(tree):
        return None

    # Tenta inferir a finalidade a partir de nomes de classes e funções
    class_names = [node.name for node in ast.walk(tree) if isinstance(node, ast.ClassDef)]
    func_names = [node.name for node in ast.walk(tree) if isinstance(node, ast.FunctionDef) and not node.name.startswith("_")]

    # Tenta inferir a partir de imports importantes
    imports = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                imports.add(alias.name.split('.')[0])
        elif isinstance(node, ast.ImportFrom):
            if node.module:
                imports.add(node.module.split('.')[0])

    # Constrói a docstring com base nas informações recolhidas
    parts = []
    relative_path = file_path.relative_to(ROOT_DIR).as_posix()
    parts.append(f"Módulo para {relative_path}.")

    if class_names:
        if len(class_names) > 1:
            parts.append(f"Define as classes: {', '.join(class_names)}.")
        else:
            parts.append(f"Define a classe principal '{class_names[0]}'.")
    
    if func_names:
        if len(func_names) > 3:
             parts.append(f"Fornece funções utilitárias, incluindo '{func_names[0]}' e outras.")
        else:
            parts.append(f"Fornece as funções: {', '.join(func_names)}.")

    if "fastapi" in imports:
        parts.append("Responsável por endpoints da API.")
    elif "streamlit" in imports:
        parts.append("Define componentes da interface de utilizador (UI).")
    elif "dask" in imports:
        parts.append("Realiza operações de processamento de dados com Dask.")
    elif "sqlalchemy" in imports:
        parts.append("Interage com a base de dados usando SQLAlchemy.")

    if len(parts) == 1: # Se não encontrou nada relevante
        return f"Script Python para a finalidade de '{file_path.stem.replace('_', ' ')}'."

    return " ".join(parts)


def process_file(file_path: Path, apply_changes: bool):
    """
    Processa um único ficheiro, adicionando o docstring se necessário.
    """
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            original_content = f.read()

        # Ignora ficheiros vazios
        if not original_content.strip():
            return

        suggested_docstring = get_suggested_docstring(file_path, original_content)

        if suggested_docstring:
            docstring_block = f'"""\n{suggested_docstring}\n"""\n\n'
            
            if apply_changes:
                new_content = docstring_block + original_content
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(new_content)
                print(f"✅ Docstring adicionado a: {file_path.relative_to(ROOT_DIR)}")
            else:
                print(f"📄 [DRY RUN] Propondo docstring para: {file_path.relative_to(ROOT_DIR)}")
                print(f'    """\n    {suggested_docstring}\n    """\n')

    except Exception as e:
        print(f"❌ Erro ao processar {file_path}: {e}")


def main():
    parser = argparse.ArgumentParser(
        description="Adiciona automaticamente docstrings de módulo a ficheiros Python num projeto."
    )
    parser.add_argument(
        "--apply",
        action="store_true",
        help="Aplica as alterações aos ficheiros. Por defeito, executa em modo de simulação (Dry Run)."
    )
    args = parser.parse_args()

    if not args.apply:
        print("--- 🏃 EXECUTANDO EM MODO SIMULAÇÃO (DRY RUN) 🏃 ---")
        print("Nenhum ficheiro será modificado. Para aplicar as alterações, use --apply.\n")
    else:
        print("--- ✍️ APLICANDO ALTERAÇÕES ✍️ ---")
        print("As docstrings serão adicionadas aos ficheiros.\n")

    for root, dirs, files in os.walk(ROOT_DIR, topdown=True):
        # Remove diretórios ignorados da exploração
        dirs[:] = [d for d in dirs if d not in IGNORED_DIRS]
        
        for name in files:
            if name.endswith(".py"):
                process_file(Path(root) / name, args.apply)

    print("\n--- ✨ Processo Concluído ✨ ---")

if __name__ == "__main__":
    main()