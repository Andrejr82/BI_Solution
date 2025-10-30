"""
Script para corrigir os 102 exemplos de query_examples.json
Substitui nomes de colunas legados por nomes corretos do Parquet.
"""
import json
import re
import sys
import io
from pathlib import Path

# Configurar encoding
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Adicionar path do projeto
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.config.column_mapping import COLUMN_MAP

def fix_code(code: str) -> str:
    """
    Corrige nomes de colunas no código Python.

    Args:
        code: Código Python com colunas legadas

    Returns:
        Código corrigido com colunas reais
    """
    fixed_code = code

    # Substituir cada coluna legada pela real
    for legacy, real in COLUMN_MAP.items():
        # Padrões de uso de colunas
        patterns = [
            (f"['{legacy}']", f"['{real}']"),
            (f'["{legacy}"]', f'["{real}"]'),
            (f"'{legacy}'", f"'{real}'"),
            (f'"{legacy}"', f'"{real}"'),
        ]

        for old_pattern, new_pattern in patterns:
            fixed_code = fixed_code.replace(old_pattern, new_pattern)

    return fixed_code

def fix_query_examples():
    """Corrige arquivo query_examples.json"""

    file_path = Path("data/query_examples.json")
    backup_path = Path("data/query_examples.json.backup")

    print("="*60)
    print("CORRECAO DE QUERY EXAMPLES")
    print("="*60)
    print()

    # Carregar exemplos
    print(f"Carregando exemplos de: {file_path}")
    with open(file_path, 'r', encoding='utf-8') as f:
        examples = json.load(f)

    print(f"Total de exemplos: {len(examples)}\n")

    # Fazer backup
    print(f"Criando backup em: {backup_path}")
    with open(backup_path, 'w', encoding='utf-8') as f:
        json.dump(examples, f, indent=2, ensure_ascii=False)

    # Corrigir cada exemplo
    fixed_count = 0
    error_count = 0

    for i, example in enumerate(examples):
        try:
            original_code = example.get('code', '')

            if original_code:
                fixed_code = fix_code(original_code)

                if fixed_code != original_code:
                    example['code'] = fixed_code
                    fixed_count += 1

                    if fixed_count <= 3:  # Mostrar primeiros 3
                        print(f"\nExemplo {i+1} corrigido:")
                        print(f"  ANTES: {original_code[:80]}...")
                        print(f"  DEPOIS: {fixed_code[:80]}...")

        except Exception as e:
            error_count += 1
            print(f"\nERRO no exemplo {i+1}: {e}")

    # Salvar corrigidos
    print(f"\n{'='*60}")
    print(f"Exemplos corrigidos: {fixed_count}/{len(examples)}")
    print(f"Erros: {error_count}")
    print(f"{'='*60}\n")

    print(f"Salvando exemplos corrigidos em: {file_path}")
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(examples, f, indent=2, ensure_ascii=False)

    print("\nCORRECAO CONCLUIDA!")
    print(f"Backup salvo em: {backup_path}")

    return fixed_count, error_count

if __name__ == "__main__":
    try:
        fixed, errors = fix_query_examples()

        if errors > 0:
            print(f"\nAVISO: {errors} erros encontrados!")
            sys.exit(1)
        else:
            print(f"\nSUCESSO: {fixed} exemplos corrigidos!")
            sys.exit(0)

    except Exception as e:
        print(f"\nERRO FATAL: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
