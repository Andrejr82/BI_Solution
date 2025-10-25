"""
🧹 UTILITÁRIO DE LIMPEZA DE CACHE
=================================

Limpa todos os caches do sistema Agent_Solution_BI.

USO:
    python clear_cache.py

QUANDO USAR:
    - Após modificar code_gen_agent.py
    - Após adicionar/remover colunas no Parquet
    - Após corrigir bugs em código gerado
    - Quando queries começarem a dar erro inesperado
    - Quando suspeitar que cache está desatualizado

SEGURO: Não afeta dados ou configurações, apenas limpa código em cache.
"""

import os
import sys
from pathlib import Path
from datetime import datetime

# Fix encoding para Windows
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

def clear_all_caches():
    """Limpa todos os caches do sistema"""

    print("=" * 80)
    print("🧹 LIMPEZA DE CACHE - Agent_Solution_BI")
    print("=" * 80)
    print(f"\n📅 Data: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

    # Diretórios de cache
    cache_dirs = [
        Path('data/cache'),
        Path('data/cache_agent_graph')
    ]

    total_removed = 0
    total_size = 0

    for cache_dir in cache_dirs:
        if not cache_dir.exists():
            print(f"⚠️  Diretório não existe: {cache_dir}")
            continue

        print(f"\n📁 Limpando: {cache_dir}")

        removed_count = 0
        dir_size = 0

        for cache_file in cache_dir.glob('*'):
            if cache_file.is_file():
                # Calcular tamanho
                file_size = cache_file.stat().st_size
                dir_size += file_size

                # Remover arquivo
                try:
                    cache_file.unlink()
                    removed_count += 1
                except Exception as e:
                    print(f"   ❌ Erro ao remover {cache_file.name}: {e}")

        total_removed += removed_count
        total_size += dir_size

        if removed_count > 0:
            print(f"   ✅ {removed_count} arquivos removidos ({dir_size / 1024:.2f} KB)")
        else:
            print(f"   ℹ️  Nenhum arquivo para remover")

    # Limpar arquivo de versão do prompt
    version_file = Path('data/cache/.prompt_version')
    if version_file.exists():
        try:
            version_file.unlink()
            print(f"\n🔄 Versão do prompt resetada")
        except Exception as e:
            print(f"\n⚠️  Erro ao remover versão do prompt: {e}")

    # Resumo
    print("\n" + "=" * 80)
    print("📊 RESUMO")
    print("=" * 80)
    print(f"\n✅ Total de arquivos removidos: {total_removed}")
    print(f"💾 Espaço liberado: {total_size / 1024:.2f} KB ({total_size / 1024 / 1024:.2f} MB)")

    if total_removed > 0:
        print("\n✅ Cache limpo com sucesso!")
        print("\n🔄 PRÓXIMOS PASSOS:")
        print("   1. Reiniciar a aplicação (se estiver rodando)")
        print("   2. Testar queries que estavam falhando")
        print("   3. Código será regenerado com o prompt atualizado")
    else:
        print("\nℹ️  Cache já estava vazio")

    print("\n" + "=" * 80)


def main():
    """Função principal"""

    # Verificar se está no diretório correto
    if not Path('data').exists():
        print("❌ ERRO: Execute este script do diretório raiz do projeto!")
        print("   cd C:\\Users\\André\\Documents\\Agent_Solution_BI")
        print("   python clear_cache.py")
        sys.exit(1)

    # Confirmar antes de limpar (se chamado interativamente)
    if sys.stdout.isatty():  # Se é um terminal interativo
        print("⚠️  Isto irá limpar TODO o cache de código gerado.")
        print("   Código será regenerado na próxima execução (pode demorar mais).")
        confirm = input("\n❓ Confirma a limpeza? (s/N): ")

        if confirm.lower() not in ['s', 'sim', 'y', 'yes']:
            print("\n❌ Operação cancelada.")
            sys.exit(0)

    # Executar limpeza
    try:
        clear_all_caches()
    except Exception as e:
        print(f"\n❌ ERRO ao limpar cache: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
