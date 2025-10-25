"""
🎨 TESTE COMPLETO DE GERAÇÃO DE GRÁFICOS

Foca em queries que EXPLICITAMENTE pedem gráficos.
Objetivo: Validar se sistema está gerando visualizações corretamente.
"""

import sys
import os
import io
import time
import json
from pathlib import Path
from datetime import datetime

# Fix encoding Windows
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

# Add root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from core.config.safe_settings import get_safe_settings
from core.connectivity.hybrid_adapter import HybridDataAdapter
from core.llm_adapter import GeminiLLMAdapter
from core.agents.code_gen_agent import CodeGenAgent
from core.graph.graph_builder import GraphBuilder

# 🎨 QUERIES DE GRÁFICOS - 15 variações
QUERIES_GRAFICOS = [
    # Gráficos de Barras - Rankings
    "Gere um gráfico de barras mostrando o ranking dos 10 produtos mais vendidos no segmento TECIDOS",
    "Crie um gráfico de barras com os 5 produtos mais vendidos na UNE SCR",
    "Mostre um gráfico de barras comparando as vendas por segmento",
    "Gere um gráfico de barras do top 10 produtos do segmento FESTAS",

    # Gráficos de Pizza - Distribuições
    "Crie um gráfico de pizza mostrando a distribuição de vendas por segmento",
    "Gere um gráfico de pizza com a participação de cada UNE nas vendas totais",
    "Mostre um gráfico de pizza da distribuição de vendas por categoria no segmento PAPELARIA",

    # Gráficos de Linha - Evolução/Tendências
    "Mostre a evolução de vendas mensais em um gráfico de linha",
    "Gere um gráfico de linha mostrando a tendência de vendas dos últimos 6 meses",

    # Comparações Visuais
    "Compare visualmente as vendas entre UNE SCR e UNE MAD",
    "Mostre graficamente a comparação de vendas por segmento",

    # Análises Temporais/Sazonais
    "Análise de sazonalidade em formato de gráfico para o segmento FESTAS",
    "Visualize a distribuição de vendas ao longo do tempo",

    # Palavras-chave analíticas
    "Ranking visual dos produtos mais vendidos",
    "Distribuição gráfica por categoria de produtos"
]

def test_grafico(query_text, idx):
    """Testa uma query de gráfico."""
    print(f"\n{'='*80}")
    print(f"[{idx+1}/{len(QUERIES_GRAFICOS)}] {query_text}")
    print(f"{'='*80}")

    try:
        # Inicializar (rápido com cache)
        settings = get_safe_settings()
        llm_adapter = GeminiLLMAdapter(
            api_key=settings.GEMINI_API_KEY,
            model_name=settings.GEMINI_MODEL_NAME
        )
        data_adapter = HybridDataAdapter()
        code_gen_agent = CodeGenAgent(
            llm_adapter=llm_adapter,
            data_adapter=data_adapter
        )
        graph_builder = GraphBuilder(
            llm_adapter=llm_adapter,
            parquet_adapter=data_adapter,
            code_gen_agent=code_gen_agent
        )
        grafo = graph_builder.build()

        # Executar
        start_time = time.time()
        result_state = grafo.invoke({
            "messages": [{"role": "user", "content": query_text}]
        })
        elapsed = time.time() - start_time

        # Analisar
        resultado = result_state.get("final_response", {})
        tipo = resultado.get("type", "unknown")
        sucesso = resultado.get("success", False)

        # Resultado
        status = "CHART" if tipo == "chart" else f"{tipo.upper()}"
        emoji = "✅" if tipo == "chart" else "❌"

        print(f"{emoji} Tipo: {status} | Tempo: {elapsed:.2f}s")

        return {
            "query": query_text,
            "type": tipo,
            "success": sucesso,
            "time": elapsed,
            "is_chart": tipo == "chart"
        }

    except Exception as e:
        print(f"❌ ERRO: {e}")
        return {
            "query": query_text,
            "type": "error",
            "success": False,
            "time": 0,
            "error": str(e),
            "is_chart": False
        }

def main():
    print("="*80)
    print("🎨 TESTE COMPLETO DE GERAÇÃO DE GRÁFICOS")
    print("="*80)
    print(f"Total de queries: {len(QUERIES_GRAFICOS)}")
    print(f"Objetivo: Validar taxa de geração de gráficos")
    print("="*80)

    resultados = []

    for idx, query in enumerate(QUERIES_GRAFICOS):
        resultado = test_grafico(query, idx)
        resultados.append(resultado)

        # Pausa entre queries para evitar sobrecarga
        time.sleep(1)

    # Análise Final
    print("\n" + "="*80)
    print("📊 ANÁLISE FINAL")
    print("="*80)

    total = len(resultados)
    charts = sum(1 for r in resultados if r["is_chart"])
    data_responses = sum(1 for r in resultados if r["type"] == "data")
    text_responses = sum(1 for r in resultados if r["type"] == "text")
    errors = sum(1 for r in resultados if r["type"] == "error")

    tempo_total = sum(r["time"] for r in resultados)
    tempo_medio = tempo_total / total if total > 0 else 0

    taxa_graficos = (charts / total * 100) if total > 0 else 0

    print(f"\n📈 Métricas:")
    print(f"  Total de queries: {total}")
    print(f"  Gráficos gerados: {charts} ({taxa_graficos:.1f}%)")
    print(f"  Respostas data: {data_responses} ({data_responses/total*100:.1f}%)")
    print(f"  Respostas text: {text_responses} ({text_responses/total*100:.1f}%)")
    print(f"  Erros: {errors} ({errors/total*100:.1f}%)")
    print(f"\n⏱️  Performance:")
    print(f"  Tempo total: {tempo_total:.2f}s")
    print(f"  Tempo médio: {tempo_medio:.2f}s")

    # Avaliação
    print(f"\n🎯 Avaliação:")
    if taxa_graficos >= 80:
        print(f"  ✅ EXCELENTE! Taxa de {taxa_graficos:.1f}% está acima da meta (80%)")
    elif taxa_graficos >= 60:
        print(f"  ⚠️  BOM. Taxa de {taxa_graficos:.1f}% está próxima da meta (60-80%)")
    elif taxa_graficos >= 40:
        print(f"  ⚠️  REGULAR. Taxa de {taxa_graficos:.1f}% precisa melhorar (40-60%)")
    else:
        print(f"  ❌ RUIM. Taxa de {taxa_graficos:.1f}% está abaixo do esperado (<40%)")

    # Detalhamento de falhas
    falhas = [r for r in resultados if not r["is_chart"]]
    if falhas:
        print(f"\n❌ Queries que NÃO geraram gráficos ({len(falhas)}):")
        for i, r in enumerate(falhas[:5], 1):  # Mostrar até 5
            print(f"  {i}. \"{r['query'][:60]}...\" → {r['type']}")

    # Salvar relatório JSON
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    relatorio_json = {
        "timestamp": timestamp,
        "total_queries": total,
        "metricas": {
            "graficos_gerados": charts,
            "taxa_graficos": taxa_graficos,
            "data_responses": data_responses,
            "text_responses": text_responses,
            "errors": errors,
            "tempo_total": tempo_total,
            "tempo_medio": tempo_medio
        },
        "resultados": resultados
    }

    json_path = f"tests/relatorio_teste_graficos_{timestamp}.json"
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(relatorio_json, f, indent=2, ensure_ascii=False)

    print(f"\n💾 Relatório salvo: {json_path}")

    # Status final
    print("\n" + "="*80)
    if taxa_graficos >= 60:
        print("✅ TESTE PASSOU - Sistema está gerando gráficos adequadamente!")
    else:
        print("❌ TESTE FALHOU - Taxa de gráficos abaixo do esperado")
    print("="*80)

if __name__ == "__main__":
    main()
