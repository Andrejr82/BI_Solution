"""
Script para limpar cache antigo após atualização v2.1.4

Executa:
1. Remove todos os arquivos JSON do cache (força regeneração)
2. Atualiza arquivos de versão

Uso: python scripts/clear_old_cache.py
"""
import os
import glob
import logging

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

def clear_cache():
    """Remove todos os arquivos de cache antigos"""
    cache_dir = os.path.join(os.getcwd(), "data", "cache")

    if not os.path.exists(cache_dir):
        logger.info(f"✅ Diretório de cache não existe: {cache_dir}")
        return 0

    # Listar todos os arquivos JSON
    cache_files = glob.glob(os.path.join(cache_dir, "*.json"))

    if not cache_files:
        logger.info("✅ Cache já está vazio")
        return 0

    # Remover cada arquivo
    removed_count = 0
    for cache_file in cache_files:
        try:
            os.remove(cache_file)
            removed_count += 1
        except Exception as e:
            logger.error(f"❌ Erro ao remover {cache_file}: {e}")

    logger.info(f"✅ Cache limpo: {removed_count} arquivos removidos")
    return removed_count

def update_version_files():
    """Atualiza arquivos de versão do cache e código"""
    version = "v2.1.4"

    # Atualizar .cache_version
    cache_version_file = os.path.join(os.getcwd(), "data", ".cache_version")
    try:
        with open(cache_version_file, 'w') as f:
            f.write(version)
        logger.info(f"✅ Versão de cache atualizada: {version}")
    except Exception as e:
        logger.error(f"❌ Erro ao atualizar .cache_version: {e}")

    # Atualizar .code_version
    code_version_file = os.path.join(os.getcwd(), "data", "cache", ".code_version")
    try:
        os.makedirs(os.path.dirname(code_version_file), exist_ok=True)
        with open(code_version_file, 'w') as f:
            f.write(version)
        logger.info(f"✅ Versão de código atualizada: {version}")
    except Exception as e:
        logger.error(f"❌ Erro ao atualizar .code_version: {e}")

def main():
    """Função principal"""
    logger.info("=" * 60)
    logger.info("🧹 LIMPEZA DE CACHE - Versão 2.1.4")
    logger.info("=" * 60)

    # Limpar cache
    removed = clear_cache()

    # Atualizar versões
    update_version_files()

    logger.info("=" * 60)
    logger.info(f"✅ Limpeza concluída!")
    logger.info(f"   - {removed} arquivos de cache removidos")
    logger.info(f"   - Cache será regenerado automaticamente")
    logger.info(f"   - TTL reduzido de 24-48h para 1h")
    logger.info("=" * 60)

if __name__ == "__main__":
    main()
