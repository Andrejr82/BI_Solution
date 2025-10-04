"""
Script de Teste Completo das 80 Perguntas de Negócio
Testa cada pergunta e gera relatório detalhado de cobertura
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import time
import json
from datetime import datetime
from core.business_intelligence.direct_query_engine import DirectQueryEngine
from core.connectivity.parquet_adapter import ParquetAdapter

# 80 Perguntas organizadas por categoria
PERGUNTAS = {
    "🎯 Vendas por Produto": [
        "Gere um gráfico de vendas do produto 369947 na UNE SCR",
        "Mostre a evolução de vendas mensais do produto 369947 nos últimos 12 meses",
        "Compare as vendas do produto 369947 entre todas as UNEs",
        "Quais são os 5 produtos mais vendidos na UNE SCR no último mês?",
        "Análise de performance: produtos com vendas acima da média no segmento TECIDOS",
        "Identifique produtos com variação de vendas superior a 20% mês a mês",
        "Top 10 produtos por margem de crescimento nos últimos 3 meses",
        "Produtos com padrão de vendas sazonal no segmento FESTAS"
    ],
    "🏪 Análises por Segmento": [
        "Quais são os 10 produtos que mais vendem no segmento TECIDOS?",
        "Compare as vendas entre os segmentos ARMARINHO E CONFECÇÃO vs TECIDOS",
        "Ranking dos segmentos por volume de vendas no último trimestre",
        "Qual segmento teve maior crescimento percentual mês a mês?",
        "Distribuição de vendas por categoria dentro do segmento PAPELARIA",
        "Segmentos com maior concentração de produtos ABC 'A'",
        "Análise de penetração: quantos produtos únicos vendidos por segmento",
        "Segmentos mais afetados por sazonalidade"
    ],
    "🏬 Análises por UNE/Loja": [
        "Ranking de performance de vendas por UNE no segmento TECIDOS",
        "Qual UNE vende mais produtos do segmento PAPELARIA?",
        "Compare a performance da UNE SCR vs outras UNEs principais",
        "Identifique UNEs com maior potencial de crescimento",
        "UNEs com maior diversidade de produtos vendidos",
        "Análise de concentração: dependência de produtos específicos por UNE",
        "UNEs com melhor desempenho em produtos promocionais",
        "Comparativo de eficiência de vendas entre UNEs similares"
    ],
    "📈 Análises Temporais": [
        "Análise de sazonalidade: quais meses vendem mais no segmento FESTAS?",
        "Tendência de vendas dos últimos 6 meses por categoria",
        "Identifique produtos com padrão de vendas decrescente",
        "Quais produtos tiveram pico de vendas no último mês?",
        "Produtos com ciclo de vendas consistente vs irregular",
        "Impacto sazonal por segmento: comparativo ano vs ano",
        "Previsão de vendas baseada no histórico dos últimos 12 meses",
        "Produtos que precisam de ação comercial urgente (tendência negativa)"
    ],
    "💰 Performance e ABC": [
        "Produtos classificados como ABC 'A' no segmento TECIDOS",
        "Análise ABC: distribuição de produtos por classificação",
        "Migração ABC: produtos que mudaram de classificação",
        "Produtos ABC 'C' com potencial para 'B'",
        "Produtos com maior frequency de vendas nas últimas 5 semanas",
        "Top 10 produtos por média de vendas semanal",
        "Produtos com vendas regulares vs esporádicas",
        "Análise de consistência: produtos vendidos em todas as semanas"
    ],
    "📦 Estoque e Logística": [
        "Produtos com estoque baixo vs alta demanda",
        "Análise de ponto de pedido: produtos próximos ao limite",
        "Produtos com maior leadtime vs performance de vendas",
        "Identificar produtos com excesso de estoque",
        "Produtos com maior rotação de estoque",
        "Análise de exposição: produtos com exposição mínima vs vendas",
        "Produtos pendentes de solicitação há mais de X dias",
        "Eficiência logística: relação entre estoque CD vs vendas"
    ],
    "🏭 Análises por Fabricante": [
        "Ranking de fabricantes por volume de vendas",
        "Compare performance de diferentes fabricantes no segmento TECIDOS",
        "Fabricantes com maior diversidade de produtos",
        "Análise de concentração: dependência de fabricantes específicos",
        "Fabricantes com produtos de maior margem",
        "Novos fabricantes vs estabelecidos: performance comparativa",
        "Fabricantes exclusivos vs multimarca por UNE",
        "Oportunidades de cross-selling por fabricante"
    ],
    "🎨 Categoria/Grupo": [
        "Performance por categoria dentro do segmento ARMARINHO E CONFECÇÃO",
        "Grupos de produtos com maior margem de crescimento",
        "Análise cross-selling: produtos frequentemente vendidos juntos",
        "Subgrupos mais rentáveis por segmento",
        "Categorias com menor penetração que têm potencial",
        "Gap analysis: categorias ausentes em UNEs específicas",
        "Produtos complementares com baixa correlação de vendas",
        "Oportunidades de expansão de linha por categoria"
    ],
    "📊 Dashboards Executivos": [
        "Dashboard executivo: KPIs principais por segmento",
        "Relatório de performance mensal consolidado",
        "Scorecard de vendas: top/bottom performers",
        "Métricas de eficiência operacional por UNE",
        "Alertas: produtos que precisam de atenção (baixa rotação, estoque alto)",
        "Monitor de tendências: produtos em ascensão vs declínio",
        "Relatório de exceções: performance fora do padrão",
        "Indicadores de saúde do negócio por segmento"
    ],
    "🔍 Análises Específicas": [
        "Análise de canibalização: produtos que competem entre si",
        "Impacto de promoções: antes vs durante vs depois",
        "Produtos fora de linha: análise de descontinuação",
        "Oportunidades de bundle: produtos com sinergia de vendas",
        "Produtos com risco de ruptura baseado em tendências",
        "Previsão de demanda para próximos 3 meses",
        "Simulação: impacto de mudanças de preço/exposição",
        "Análise de cenários: melhor/pior caso por produto"
    ]
}

def classificar_resultado(resultado):
    """Classifica o resultado do teste"""
    if not resultado:
        return "ERROR", "Resultado vazio ou None"

    result_type = resultado.get("type", "unknown")

    if result_type == "error":
        return "ERROR", resultado.get("error", "Erro desconhecido")
    elif result_type == "fallback":
        return "FALLBACK", "DirectQueryEngine não processou - necessário fallback"
    elif result_type in ["chart", "table", "text", "product_info"]:
        return "SUCCESS", f"Processado como {result_type}"
    else:
        return "UNKNOWN", f"Tipo desconhecido: {result_type}"

def executar_teste():
    """Executa o teste completo das 80 perguntas"""
    print("=" * 80)
    print("TESTE COMPLETO DAS 80 PERGUNTAS DE NEGÓCIO")
    print("=" * 80)
    print(f"Início: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

    # Inicializar DirectQueryEngine
    print("Inicializando DirectQueryEngine...")
    adapter = ParquetAdapter('data/parquet/admmat.parquet')
    engine = DirectQueryEngine(adapter)
    print("[OK] Engine inicializada\n")

    # Resultados
    resultados = []
    stats = {
        "SUCCESS": 0,
        "ERROR": 0,
        "FALLBACK": 0,
        "UNKNOWN": 0
    }

    total_perguntas = sum(len(perguntas) for perguntas in PERGUNTAS.values())
    contador = 0

    # Processar cada categoria
    for categoria, perguntas in PERGUNTAS.items():
        # Remover emojis do nome da categoria para print
        categoria_clean = categoria.encode('ascii', 'ignore').decode('ascii').strip()
        if not categoria_clean:
            categoria_clean = "Categoria sem nome"

        print(f"\n{'=' * 80}")
        print(f"[CATEGORIA] {categoria_clean}")
        print(f"{'=' * 80}")

        for idx, pergunta in enumerate(perguntas, 1):
            contador += 1
            print(f"\n[{contador}/{total_perguntas}] Testando: {pergunta[:70]}...")

            start_time = time.time()
            try:
                resultado = engine.process_query(pergunta)
                elapsed = time.time() - start_time

                status, mensagem = classificar_resultado(resultado)
                stats[status] += 1

                # Exibir resultado
                icon = "[OK]" if status == "SUCCESS" else "[ERROR]" if status == "ERROR" else "[FALLBACK]" if status == "FALLBACK" else "[?]"
                print(f"{icon} {status}: {mensagem} ({elapsed:.2f}s)")

                # Armazenar resultado
                resultados.append({
                    "id": contador,
                    "categoria": categoria,
                    "pergunta": pergunta,
                    "status": status,
                    "mensagem": mensagem,
                    "tipo_resultado": resultado.get("type") if resultado else None,
                    "tempo_processamento": elapsed,
                    "timestamp": datetime.now().isoformat()
                })

            except Exception as e:
                elapsed = time.time() - start_time
                stats["ERROR"] += 1
                print(f"[ERROR] EXCEPTION: {str(e)[:100]} ({elapsed:.2f}s)")

                resultados.append({
                    "id": contador,
                    "categoria": categoria,
                    "pergunta": pergunta,
                    "status": "ERROR",
                    "mensagem": str(e),
                    "tipo_resultado": None,
                    "tempo_processamento": elapsed,
                    "timestamp": datetime.now().isoformat()
                })

    # Estatísticas finais
    print(f"\n\n{'=' * 80}")
    print("ESTATÍSTICAS FINAIS")
    print(f"{'=' * 80}")
    print(f"Total de perguntas testadas: {total_perguntas}")
    print(f"[OK] Sucesso (SUCCESS):        {stats['SUCCESS']} ({stats['SUCCESS']/total_perguntas*100:.1f}%)")
    print(f"[>>] Fallback necessario:      {stats['FALLBACK']} ({stats['FALLBACK']/total_perguntas*100:.1f}%)")
    print(f"[XX] Erros (ERROR):            {stats['ERROR']} ({stats['ERROR']/total_perguntas*100:.1f}%)")
    print(f"[??] Desconhecido (UNKNOWN):   {stats['UNKNOWN']} ({stats['UNKNOWN']/total_perguntas*100:.1f}%)")

    # Salvar relatório JSON
    relatorio = {
        "metadata": {
            "timestamp": datetime.now().isoformat(),
            "total_perguntas": total_perguntas,
            "total_categorias": len(PERGUNTAS)
        },
        "estatisticas": stats,
        "resultados": resultados
    }

    output_file = f"tests/relatorio_teste_80_perguntas_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(relatorio, f, ensure_ascii=False, indent=2)

    print(f"\n[SAVE] Relatorio salvo em: {output_file}")

    # Mostrar perguntas que falharam
    if stats['ERROR'] > 0:
        print(f"\n\n{'=' * 80}")
        print("PERGUNTAS COM ERRO")
        print(f"{'=' * 80}")
        for r in resultados:
            if r['status'] == 'ERROR':
                print(f"\n[ERROR] [{r['id']}] {r['pergunta']}")
                print(f"   Erro: {r['mensagem'][:100]}")

    # Mostrar perguntas que precisam fallback
    if stats['FALLBACK'] > 0:
        print(f"\n\n{'=' * 80}")
        print("PERGUNTAS QUE PRECISAM FALLBACK (LLM)")
        print(f"{'=' * 80}")
        for r in resultados:
            if r['status'] == 'FALLBACK':
                print(f"\n[FALLBACK] [{r['id']}] {r['pergunta']}")

    print(f"\n{'=' * 80}")
    print(f"Fim: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'=' * 80}\n")

    return relatorio

if __name__ == "__main__":
    relatorio = executar_teste()
