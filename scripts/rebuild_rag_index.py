"""
Script para rebuild automático do índice FAISS do RAG
Recria índice a partir de query_examples.json
"""
import sys
from pathlib import Path

# Adicionar core ao path
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.rag.query_retriever import QueryRetriever


def main():
    """Reconstroi o índice FAISS"""
    print("=" * 60)
    print("REBUILD DO INDICE FAISS - RAG")
    print("=" * 60)

    # Inicializar retriever
    print("\nInicializando QueryRetriever...")
    retriever = QueryRetriever()

    # Estatísticas ANTES
    stats_before = retriever.get_stats()
    print(f"\nESTATISTICAS ANTES DO REBUILD:")
    print(f"  Total de exemplos: {stats_before['total_examples']}")
    print(f"  Tamanho do indice: {stats_before['index_size']}")
    print(f"  Modelo: {stats_before.get('model_name', 'MiniLM')}")

    # Rebuild
    print("\nReconstruindo indice FAISS...")
    retriever.rebuild_index()

    # Estatísticas DEPOIS
    stats_after = retriever.get_stats()
    print(f"\nESTATISTICAS DEPOIS DO REBUILD:")
    print(f"  Total de exemplos: {stats_after['total_examples']}")
    print(f"  Tamanho do indice: {stats_after['index_size']}")

    # Validação
    if stats_after['index_size'] == stats_after['total_examples']:
        print("\nOK - Indice reconstruido com sucesso!")
    else:
        print("\n[!] AVISO - Discrepancia entre exemplos e indice!")

    print("=" * 60)


if __name__ == '__main__':
    main()
