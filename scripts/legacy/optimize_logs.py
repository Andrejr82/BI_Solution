"""
Script para otimizar logs excessivos no DirectQueryEngine
Reduz logs de INFO para DEBUG onde apropriado
"""
import re
from pathlib import Path

def optimize_logs():
    """Otimiza logs no direct_query_engine.py"""

    file_path = Path("core/business_intelligence/direct_query_engine.py")

    if not file_path.exists():
        print(f"[ERRO] Arquivo nao encontrado: {file_path}")
        return

    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    original_content = content

    # Patterns para otimização
    optimizations = [
        # 1. Logs de tentativa/processamento -> DEBUG
        (r'logger\.info\("🤖 Tentando sistema LLM Classifier\.\.\."\)',
         r'logger.debug("🤖 Tentando sistema LLM Classifier...")'),

        (r'logger\.info\("\[OK\] Intent encontrado no CACHE \(0 tokens\)"\)',
         r'logger.debug("[OK] Intent encontrado no CACHE (0 tokens)")'),

        (r'logger\.info\("\[INFO\] Classificando com Gemini\.\.\."\)',
         r'logger.debug("[INFO] Classificando com Gemini...")'),

        (r'logger\.info\("\[INFO\] Intent salvo no cache"\)',
         r'logger.debug("[INFO] Intent salvo no cache")'),

        (r'logger\.info\("\[INFO\] Usando sistema de regex patterns \(ZERO tokens\)"\)',
         r'logger.debug("[INFO] Usando sistema de regex patterns (ZERO tokens)")'),

        # 2. Logs repetitivos de sucesso -> DEBUG ou remover
        (r'logger\.info\(f"\[OK\] Intent: \{intent\[\'operation\'\]\} \(confiança: \{intent\.get\(\'confidence\', 0\):.2f\}\)"\)',
         r'logger.debug(f"[OK] Intent: {intent[\'operation\']} (confiança: {intent.get(\'confidence\', 0):.2f})")'),

        (r'logger\.info\(f"\[OK\] Query processada com LLM Classifier em \{result\[\'processing_time\'\]:.2f\}s"\)',
         r'logger.debug(f"[OK] Query processada com LLM Classifier em {result[\'processing_time\']:.2f}s")'),

        (r'logger\.info\(f"Query processada em \{result\[\'processing_time\'\]:.2f\}s - ZERO tokens LLM"\)',
         r'logger.debug(f"Query processada em {result[\'processing_time\']:.2f}s - ZERO tokens LLM")'),

        # 3. Logs de inicialização -> apenas uma vez, no nível INFO
        # Estes ficam como estão, pois são informativos e acontecem só uma vez

        # 4. Logs de cache e performance -> DEBUG
        (r'logger\.info\(f"\[INFO\] Usando sistema de classificação direta"\)',
         r'logger.debug(f"[INFO] Usando sistema de classificação direta")'),
    ]

    changes_made = 0
    for pattern, replacement in optimizations:
        new_content = re.sub(pattern, replacement, content)
        if new_content != content:
            changes_made += len(re.findall(pattern, content))
            content = new_content

    # Salvar se houver mudanças
    if content != original_content:
        # Criar backup
        backup_path = file_path.with_suffix('.py.bak')
        with open(backup_path, 'w', encoding='utf-8') as f:
            f.write(original_content)

        # Salvar otimizado
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)

        print(f"[OK] Logs otimizados: {changes_made} mudancas")
        print(f"[INFO] Backup criado: {backup_path}")
    else:
        print("[INFO] Nenhuma mudanca necessaria")

if __name__ == "__main__":
    optimize_logs()
