"""
Análise Rápida de Cache
Agent_Solution_BI - BI Agent (Caçulinha BI)

Script para análise rápida de métricas de cache.
"""

import os
import json
from pathlib import Path
from datetime import datetime
from collections import defaultdict

# Configuração de caminhos
BASE_DIR = Path(r"C:\Users\André\Documents\Agent_Solution_BI")
CACHE_DIR = BASE_DIR / "data" / "cache"
CACHE_AGENT_DIR = BASE_DIR / "data" / "cache_agent_graph"


def analyze_cache_hit_rate():
    """Analisa hit rate do cache baseado em timestamps"""
    print("\n=== Análise de Hit Rate do Cache ===\n")

    if not CACHE_DIR.exists():
        print("Diretório de cache não existe")
        return

    cache_files = list(CACHE_DIR.glob("*.json"))

    if not cache_files:
        print("Nenhum arquivo em cache")
        return

    # Agrupar por idade
    now = datetime.now()
    age_groups = {
        "< 1 hora": 0,
        "1-6 horas": 0,
        "6-24 horas": 0,
        "> 24 horas": 0
    }

    access_times = []

    for cache_file in cache_files:
        modified = datetime.fromtimestamp(cache_file.stat().st_mtime)
        age_hours = (now - modified).total_seconds() / 3600

        if age_hours < 1:
            age_groups["< 1 hora"] += 1
        elif age_hours < 6:
            age_groups["1-6 horas"] += 1
        elif age_hours < 24:
            age_groups["6-24 horas"] += 1
        else:
            age_groups["> 24 horas"] += 1

        access_times.append(age_hours)

    print(f"Total de arquivos em cache: {len(cache_files)}")
    print(f"\nDistribuição por idade:")
    for group, count in age_groups.items():
        percentage = (count / len(cache_files)) * 100
        print(f"  {group}: {count} ({percentage:.1f}%)")

    if access_times:
        avg_age = sum(access_times) / len(access_times)
        print(f"\nIdade média do cache: {avg_age:.2f} horas")

    # Estimar hit rate
    recent_cache = age_groups["< 1 hora"] + age_groups["1-6 horas"]
    if len(cache_files) > 0:
        estimated_hit_rate = (recent_cache / len(cache_files)) * 100
        print(f"\nHit Rate estimado (cache recente): {estimated_hit_rate:.1f}%")


def analyze_cache_patterns():
    """Analisa padrões de uso do cache"""
    print("\n=== Análise de Padrões de Cache ===\n")

    if not CACHE_DIR.exists():
        print("Diretório de cache não existe")
        return

    cache_files = list(CACHE_DIR.glob("*.json"))

    if not cache_files:
        print("Nenhum arquivo em cache")
        return

    query_types = defaultdict(int)
    total_size = 0
    sizes_by_type = defaultdict(list)

    for cache_file in cache_files:
        try:
            size = cache_file.stat().st_size
            total_size += size

            with open(cache_file, 'r', encoding='utf-8') as f:
                content = json.load(f)

            # Tentar identificar tipo de query baseado no conteúdo
            query_type = "unknown"
            if isinstance(content, dict):
                query = content.get("query", "").lower()
                if "transferencia" in query or "transfer" in query:
                    query_type = "transferencias"
                elif "estoque" in query:
                    query_type = "estoque"
                elif "venda" in query:
                    query_type = "vendas"
                elif "produto" in query:
                    query_type = "produtos"

            query_types[query_type] += 1
            sizes_by_type[query_type].append(size)

        except Exception as e:
            query_types["error"] += 1

    print(f"Padrões de cache identificados:")
    for qtype, count in sorted(query_types.items(), key=lambda x: x[1], reverse=True):
        percentage = (count / len(cache_files)) * 100
        avg_size = sum(sizes_by_type[qtype]) / len(sizes_by_type[qtype]) if sizes_by_type[qtype] else 0
        print(f"  {qtype}: {count} ({percentage:.1f}%) - Tamanho médio: {avg_size/1024:.2f} KB")


def analyze_cache_efficiency():
    """Analisa eficiência do cache"""
    print("\n=== Análise de Eficiência do Cache ===\n")

    if not CACHE_DIR.exists():
        print("Diretório de cache não existe")
        return

    cache_files = list(CACHE_DIR.glob("*.json"))

    if not cache_files:
        print("Nenhum arquivo em cache")
        return

    empty_cache = 0
    small_cache = 0  # < 1 KB
    medium_cache = 0  # 1-10 KB
    large_cache = 0  # > 10 KB

    total_size = 0

    for cache_file in cache_files:
        try:
            size = cache_file.stat().st_size
            total_size += size

            if size == 0:
                empty_cache += 1
            elif size < 1024:
                small_cache += 1
            elif size < 10240:
                medium_cache += 1
            else:
                large_cache += 1

        except Exception as e:
            pass

    print(f"Distribuição por tamanho:")
    print(f"  Vazios (0 bytes): {empty_cache}")
    print(f"  Pequenos (< 1 KB): {small_cache}")
    print(f"  Médios (1-10 KB): {medium_cache}")
    print(f"  Grandes (> 10 KB): {large_cache}")

    print(f"\nTamanho total: {total_size / (1024*1024):.2f} MB")
    print(f"Tamanho médio: {total_size / len(cache_files) / 1024:.2f} KB")

    # Calcular eficiência
    useful_cache = len(cache_files) - empty_cache
    if len(cache_files) > 0:
        efficiency = (useful_cache / len(cache_files)) * 100
        print(f"\nEficiência do cache: {efficiency:.1f}%")

    # Recomendar limpeza
    if empty_cache > 0:
        print(f"\n⚠️ Encontrados {empty_cache} arquivos vazios que podem ser removidos")

    old_cache_threshold = 24 * 7  # 7 dias
    now = datetime.now()
    old_cache = 0

    for cache_file in cache_files:
        modified = datetime.fromtimestamp(cache_file.stat().st_mtime)
        age_hours = (now - modified).total_seconds() / 3600
        if age_hours > old_cache_threshold:
            old_cache += 1

    if old_cache > 0:
        print(f"⚠️ Encontrados {old_cache} arquivos com mais de 7 dias")


def main():
    """Função principal"""
    print("=" * 60)
    print("ANÁLISE RÁPIDA DE CACHE")
    print("Agent_Solution_BI - BI Agent (Caçulinha BI)")
    print("=" * 60)

    analyze_cache_hit_rate()
    analyze_cache_patterns()
    analyze_cache_efficiency()

    print("\n" + "=" * 60)
    print("ANÁLISE CONCLUÍDA")
    print("=" * 60)


if __name__ == "__main__":
    main()
