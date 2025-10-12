"""
Módulo para generate_project_report.py. Fornece as funções: get_python_summary, get_file_summary, generate_report.
"""

# generate_project_report.py
import os
import ast
from pathlib import Path

# --- Configuração ---
ROOT_DIR = Path(__file__).parent
OUTPUT_FILE = ROOT_DIR / "relatorio_arquitetura_atual.md"

# Diretórios e ficheiros a serem ignorados na análise
IGNORED_DIRS = {
    ".git",
    ".venv",
    "venv",
    "__pycache__",
    ".mypy_cache",
    ".pytest_cache",
    ".devcontainer",
    ".github",
    "node_modules",
    "build",
    "dist",
}

IGNORED_FILES = {
    ".gitignore",
    "desktop.ini",
    "nul",
    "CACHEDIR.TAG",
    "py.typed",
    "poetry.lock",
    "pdm.lock",
    "Pipfile.lock",
}

# Mapeamento de extensões para descrições genéricas
FILE_TYPE_SUMMARIES = {
    ".md": "Ficheiro de documentação em Markdown.",
    ".json": "Ficheiro de configuração ou dados em formato JSON.",
    ".yml": "Ficheiro de configuração em formato YAML.",
    ".yaml": "Ficheiro de configuração em formato YAML.",
    ".toml": "Ficheiro de configuração em formato TOML.",
    ".in": "Ficheiro de definição de dependências (pip-tools).",
    ".txt": "Ficheiro de texto, provavelmente dependências ou documentação.",
    ".env": "Ficheiro de variáveis de ambiente.",
    ".env.example": "Ficheiro de exemplo para variáveis de ambiente.",
    ".sql": "Script SQL para operações de base de dados.",
    ".bat": "Script de automação para ambiente Windows.",
    ".sh": "Script de automação para ambientes Unix-like (Linux, macOS).",
    ".css": "Ficheiro de estilos CSS para a interface.",
    ".html": "Ficheiro de estrutura HTML.",
    ".parquet": "Ficheiro de dados em formato Parquet, otimizado para análise colunar.",
    ".pkl": "Ficheiro de objeto Python serializado (pickle).",
    ".log": "Ficheiro de registo de logs.",
    ".ini": "Ficheiro de configuração em formato INI.",
    ".mako": "Template Mako, provavelmente para Alembic.",
    ".png": "Ficheiro de imagem PNG.",
}

def get_python_summary(file_path: Path) -> str:
    """
    Extrai o docstring de um módulo Python de forma segura.
    """
    try:
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read()
            tree = ast.parse(content)
            docstring = ast.get_docstring(tree)
            if docstring:
                # Retorna a primeira linha não vazia do docstring
                first_line = next((line for line in docstring.strip().splitlines() if line.strip()), "")
                return first_line.strip()
            return "Script Python com funcionalidade não documentada."
    except Exception:
        return "Não foi possível analisar o ficheiro Python (pode conter erros de sintaxe)."

def get_file_summary(file_path: Path) -> str:
    """
    Determina a finalidade de um ficheiro com base na sua extensão ou conteúdo.
    """
    if file_path.suffix == ".py":
        return get_python_summary(file_path)
    
    summary = FILE_TYPE_SUMMARIES.get(file_path.suffix.lower())
    if summary:
        return summary
    
    return f"Ficheiro de tipo desconhecido ({file_path.suffix})."


def generate_report():
    """
    Gera o relatório de arquitetura do projeto em formato Markdown.
    """
    report_content = ["# Relatório de Arquitetura do Projeto Agent_Solution_BI\n"]
    report_content.append("Este documento foi gerado automaticamente para fornecer uma visão completa da estrutura de diretórios e ficheiros do projeto.\n")

    # Ordena os diretórios para uma apresentação consistente
    paths_to_walk = sorted([p for p in ROOT_DIR.rglob("*") if p.is_dir()])
    
    # Adiciona o diretório raiz no início
    all_dirs = [ROOT_DIR] + paths_to_walk

    processed_dirs = set()

    for current_dir in all_dirs:
        # Garante que não processamos diretórios ignorados ou seus filhos
        if any(ignored in current_dir.parts for ignored in IGNORED_DIRS):
            continue
        
        if current_dir in processed_dirs:
            continue
        
        processed_dirs.add(current_dir)

        report_content.append(f"## Diretório: `{current_dir}`\n")
        
        files = sorted([f for f in current_dir.iterdir() if f.is_file() and f.name not in IGNORED_FILES])
        
        if not files:
            report_content.append("*(Diretório vazio ou contém apenas subdiretórios)*\n")
            continue

        report_content.append("| Ficheiro | Resumo da Finalidade |")
        report_content.append("| :--- | :--- |")

        for file_path in files:
            summary = get_file_summary(file_path)
            report_content.append(f"| `{file_path.name}` | {summary} |")
        
        report_content.append("\n")

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write("\n".join(report_content))

    print(f"✅ Relatório de arquitetura gerado com sucesso em: '{OUTPUT_FILE}'")


if __name__ == "__main__":
    generate_report()