"""
Script para popular banco de exemplos RAG com queries históricas bem-sucedidas
Migra dados de successful_queries_*.jsonl para query_examples.json
"""
import json
import os
import sys
from pathlib import Path
from datetime import datetime

# Adicionar core ao path
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.rag.example_collector import ExampleCollector


def load_historical_queries():
    """Carrega queries históricas dos arquivos JSONL"""
    learning_dir = Path(__file__).parent.parent / "data" / "learning"
    queries = []

    # Procurar todos os arquivos de queries bem-sucedidas
    for file_path in learning_dir.glob("successful_queries_*.jsonl"):
        print(f"  Lendo {file_path.name}...")
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                for line_num, line in enumerate(f, 1):
                    try:
                        entry = json.loads(line.strip())
                        if entry.get('success') and entry.get('rows', 0) > 0:
                            queries.append(entry)
                    except json.JSONDecodeError:
                        print(f"    [!] Linha {line_num} invalida em {file_path.name}")
        except Exception as e:
            print(f"    [X] Erro ao ler {file_path.name}: {e}")

    return queries


def deduplicate_queries(queries):
    """Remove queries duplicadas baseado em similaridade"""
    seen_queries = {}
    unique_queries = []

    for entry in queries:
        # Normalizar query para detectar duplicatas
        normalized = entry['query'].lower().strip()

        # Remover duplicatas exatas
        if normalized not in seen_queries:
            seen_queries[normalized] = True
            unique_queries.append(entry)

    print(f"  Remocao de duplicatas: {len(queries)} -> {len(unique_queries)} queries unicas")
    return unique_queries


def filter_quality_queries(queries, min_rows=1, max_rows=10000):
    """Filtra queries de qualidade (não vazias, não muito grandes)"""
    quality_queries = []

    for entry in queries:
        rows = entry.get('rows', 0)
        query = entry.get('query', '')

        # Filtros de qualidade
        if (min_rows <= rows <= max_rows and
            len(query) >= 10 and  # Query mínima de 10 caracteres
            'PRODUTO' not in query.upper() or len(query) > 20):  # Evitar queries triviais
            quality_queries.append(entry)

    print(f"  Filtro de qualidade: {len(queries)} -> {len(quality_queries)} queries")
    return quality_queries


def populate_rag_database(queries, max_examples=100):
    """Popula banco RAG com queries selecionadas"""
    print(f"  Populando banco RAG com ate {max_examples} exemplos...")

    # Inicializar collector
    collector = ExampleCollector()

    # Ordenar por número de linhas (queries mais interessantes primeiro)
    queries_sorted = sorted(queries, key=lambda x: x.get('rows', 0), reverse=True)

    # Limitar ao máximo
    queries_to_add = queries_sorted[:max_examples]

    added = 0
    skipped = 0

    for i, entry in enumerate(queries_to_add, 1):
        try:
            # Detectar intenção baseado no código
            code = entry.get('code', '')
            intent = "python_analysis"

            if 'plotly' in code or 'px.' in code:
                intent = "visualization"
            elif '.groupby' in code:
                intent = "aggregation"
            elif '.nlargest' in code or '.nsmallest' in code:
                intent = "ranking"

            # Coletar exemplo
            collector.collect_successful_query(
                user_query=entry['query'],
                code_generated=code,
                result_rows=entry.get('rows', 0),
                intent=intent
            )
            added += 1

            if i % 10 == 0:
                print(f"    {i}/{len(queries_to_add)} exemplos processados...")

        except Exception as e:
            print(f"    [!] Erro ao adicionar exemplo {i}: {e}")
            skipped += 1

    # Estatísticas finais
    stats = collector.get_collection_stats()

    print(f"\nOK - Banco RAG populado com sucesso!")
    print(f"  Total de exemplos: {stats['total_examples']}")
    print(f"  Adicionados: {added}")
    print(f"  Ignorados: {skipped}")
    print(f"  Distribuicao de tags: {stats['tag_distribution']}")

    return stats


def main():
    """Função principal"""
    print("=" * 60)
    print("POPULACAO INICIAL DO BANCO RAG")
    print("=" * 60)

    # 1. Carregar queries históricas
    print("\nEtapa 1: Carregando queries historicas...")
    queries = load_historical_queries()
    print(f"OK - {len(queries)} queries carregadas")

    # 2. Remover duplicatas
    print("\nEtapa 2: Removendo duplicatas...")
    unique_queries = deduplicate_queries(queries)

    # 3. Filtrar qualidade
    print("\nEtapa 3: Filtrando queries de qualidade...")
    quality_queries = filter_quality_queries(unique_queries)

    # 4. Popular banco
    print("\nEtapa 4: Populando banco RAG...")
    stats = populate_rag_database(quality_queries, max_examples=100)

    print("\n" + "=" * 60)
    print("PROCESSO CONCLUIDO!")
    print("=" * 60)


if __name__ == '__main__':
    main()
