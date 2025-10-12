"""
Módulo para gerar_inventario_projeto.py. Fornece as funções: get_file_summary, map_project_structure.
"""

import os
import ast
import logging
from pathlib import Path

# --- Configuração ---
PROJECT_ROOT = Path(__file__).parent
OUTPUT_FILE = PROJECT_ROOT / "relatorio_codigo_completo.md"
EXCLUDED_DIRS = {'.venv', '.git', '.vscode', '.idea', '__pycache__', 'logs', 'dist', 'build'}
EXCLUDED_FILES = {'relatorio_codigo_completo.md', 'gerar_inventario_projeto.py'}

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def get_file_summary(file_path: Path) -> str:
    """
    Tenta extrair um resumo inteligente de um ficheiro Python.
    - Prioridade 1: O docstring do módulo.
    - Prioridade 2: Um comentário de bloco no topo do ficheiro.
    - Prioridade 3: Uma descrição genérica.
    """
    if file_path.suffix == '.py':
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
                # Tenta analisar o docstring do módulo
                tree = ast.parse(content)
                docstring = ast.get_docstring(tree)
                if docstring:
                    return docstring.strip().split('\n')[0]

                # Se não houver docstring, procura por um comentário inicial
                lines = content.splitlines()
                if lines and lines[0].strip().startswith(('#', '"""', "'''")):
                    comment = lines[0].strip().lstrip('# "').rstrip('"\'')
                    return comment.strip()

        except Exception as e:
            logging.warning(f"Não foi possível analisar o ficheiro {file_path}: {e}")
            return "Script Python com funcionalidade não documentada."
            
    # Para outros tipos de ficheiro, retorna a extensão
    return f"Ficheiro de {file_path.suffix.lstrip('.').upper()}."


def map_project_structure(root_dir: Path, output_file: Path):
    """
    Varre a estrutura do projeto e gera um relatório em Markdown.
    """
    logging.info(f"A iniciar o mapeamento do projeto em: {root_dir}")
    structure = {}

    for dirpath, dirnames, filenames in os.walk(root_dir):
        # Remove diretórios excluídos da exploração
        dirnames[:] = [d for d in dirnames if d not in EXCLUDED_DIRS]
        
        current_dir = Path(dirpath)
        relative_dir_path = current_dir.relative_to(root_dir)

        # Ignora o diretório raiz na chave do dicionário
        dir_key = str(relative_dir_path) if str(relative_dir_path) != '.' else 'Raiz'
        
        if dir_key not in structure:
            structure[dir_key] = []
            
        for filename in sorted(filenames):
            if filename in EXCLUDED_FILES:
                continue
            
            file_path = current_dir / filename
            summary = get_file_summary(file_path)
            structure[dir_key].append({'file': filename, 'summary': summary})

    logging.info(f"Mapeamento concluído. A gerar o relatório em: {output_file}")
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("# Relatório Completo de Ficheiros do Projeto Agent_BI\n\n")
        f.write("Este documento fornece um inventário de cada ficheiro no projeto, organizado por diretório, gerado automaticamente para análise de arquitetura.\n\n")

        # Processa a raiz primeiro
        if 'Raiz' in structure:
            f.write(f"## Diretório Raiz: `{root_dir}`\n\n")
            f.write("| Ficheiro | Resumo da Finalidade |\n")
            f.write("| --- | --- |\n")
            for item in structure['Raiz']:
                f.write(f"| `{item['file']}` | {item['summary']} |\n")
            f.write("\n")
        
        # Processa os outros diretórios
        for dir_key, files in sorted(structure.items()):
            if dir_key == 'Raiz' or not files:
                continue
            
            full_dir_path = root_dir / dir_key
            f.write(f"## Diretório: `{full_dir_path}`\n\n")
            f.write("| Ficheiro | Resumo da Finalidade |\n")
            f.write("| --- | --- |\n")
            for item in files:
                f.write(f"| `{item['file']}` | {item['summary']} |\n")
            f.write("\n")

    logging.info("Relatório gerado com sucesso!")

if __name__ == "__main__":
    map_project_structure(PROJECT_ROOT, OUTPUT_FILE)