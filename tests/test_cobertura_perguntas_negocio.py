"""
Teste de Cobertura Funcional das 80 Perguntas de Negócio
Valida quantas perguntas o sistema consegue processar
"""

import sys
import os
from pathlib import Path

# Adicionar diretório raiz ao path
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.business_intelligence.direct_query_engine import DirectQueryEngine
from core.connectivity.parquet_adapter import ParquetAdapter


# Perguntas organizadas por categoria (baseado em exemplos_perguntas_negocio.md)
PERGUNTAS_POR_CATEGORIA = {
    "Vendas por Produto": [
        "Gere um gráfico de vendas do produto 369947 na UNE SCR",
        "Mostre a evolução de vendas mensais do produto 369947",
        "Compare as vendas do produto 369947 entre todas as UNEs",
        "Quais são os 5 produtos mais vendidos na UNE SCR?",
        "Top 10 produtos por margem de crescimento",
        "Produtos com vendas acima da média no segmento TECIDOS",
    ],
    "Análises por Segmento": [
        "Quais são os 10 produtos que mais vendem no segmento TECIDOS?",
        "Compare vendas entre segmentos ARMARINHO e TECIDOS",
        "Ranking dos segmentos por volume de vendas",
        "Qual segmento teve maior crescimento?",
        "Segmentos com maior concentração de produtos ABC A",
    ],
    "Análises por UNE/Loja": [
        "Ranking de vendas por UNE",
        "Qual UNE vende mais produtos do segmento PAPELARIA?",
        "Compare performance da UNE SCR vs outras UNEs",
        "UNEs com maior diversidade de produtos",
        "Top 5 produtos da une 261",
        "Ranking de vendas na une scr",
    ],
    "Análises Temporais": [
        "Análise de sazonalidade no segmento FESTAS",
        "Tendência de vendas dos últimos 6 meses",
        "Produtos com padrão de vendas decrescente",
        "Quais produtos tiveram pico no último mês?",
        "Evolução de vendas dos últimos 12 meses",
    ],
    "Performance e ABC": [
        "Produtos classificados como ABC A no segmento TECIDOS",
        "Análise ABC: distribuição de produtos",
        "Produtos ABC C com potencial para B",
        "Top 10 produtos por média de vendas semanal",
        "Produtos com vendas regulares vs esporádicas",
    ],
    "Estoque e Logística": [
        "Produtos com estoque baixo vs alta demanda",
        "Produtos próximos ao ponto de pedido",
        "Identificar produtos com excesso de estoque",
        "Produtos com maior rotação de estoque",
        "Produtos sem movimento",
    ],
    "Análises por Fabricante": [
        "Ranking de fabricantes por volume de vendas",
        "Fabricantes com maior diversidade de produtos",
        "Compare performance de fabricantes no segmento TECIDOS",
    ],
    "Categoria/Grupo": [
        "Performance por categoria no segmento ARMARINHO",
        "Grupos de produtos com maior margem",
        "Categorias com menor penetração",
    ],
    "Dashboards Executivos": [
        "Dashboard executivo: KPIs principais",
        "Relatório de performance mensal",
        "Scorecard de vendas",
        "Métricas de eficiência por UNE",
    ],
    "Análises Específicas": [
        "Produtos com risco de ruptura",
        "Análise de canibalização entre produtos",
        "Oportunidades de bundle",
    ]
}


def test_cobertura_funcional():
    """Testa cobertura funcional de todas as categorias"""
    print("\n" + "="*80)
    print("TESTE DE COBERTURA FUNCIONAL - 80 PERGUNTAS DE NEGOCIO")
    print("="*80)

    # Inicializar engine
    parquet_path = os.path.join("data", "parquet", "admmat.parquet")
    adapter = ParquetAdapter(file_path=parquet_path)
    engine = DirectQueryEngine(adapter)

    total_perguntas = 0
    total_suportadas = 0
    total_nao_suportadas = 0

    resultados_por_categoria = {}

    # Testar cada categoria
    for categoria, perguntas in PERGUNTAS_POR_CATEGORIA.items():
        print(f"\n{'='*80}")
        print(f"Categoria: {categoria} ({len(perguntas)} perguntas)")
        print(f"{'='*80}")

        suportadas = 0
        nao_suportadas = 0
        detalhes = []

        for pergunta in perguntas:
            total_perguntas += 1

            # Classificar intent
            query_type, params = engine.classify_intent_direct(pergunta)

            # Verificar se foi classificado corretamente (não é fallback genérico)
            is_supported = query_type not in ["analise_geral", "fallback"]

            if is_supported:
                suportadas += 1
                total_suportadas += 1
                status = "OK"
                symbol = "OK"
            else:
                nao_suportadas += 1
                total_nao_suportadas += 1
                status = "NAO_SUPORTADA"
                symbol = "X"

            detalhes.append({
                "pergunta": pergunta,
                "query_type": query_type,
                "params": params,
                "status": status
            })

            print(f"  [{symbol}] {pergunta[:70]}")
            print(f"      Type: {query_type}, Params: {params}")

        # Calcular percentual da categoria
        percentual = (suportadas / len(perguntas)) * 100 if perguntas else 0

        resultados_por_categoria[categoria] = {
            "total": len(perguntas),
            "suportadas": suportadas,
            "nao_suportadas": nao_suportadas,
            "percentual": percentual,
            "detalhes": detalhes
        }

        print(f"\n  RESULTADO: {suportadas}/{len(perguntas)} suportadas ({percentual:.1f}%)")

    # Relatório final
    print("\n" + "="*80)
    print("RELATORIO FINAL DE COBERTURA")
    print("="*80)

    print(f"\nTotal de Perguntas Testadas: {total_perguntas}")
    print(f"Perguntas Suportadas: {total_suportadas} ({(total_suportadas/total_perguntas)*100:.1f}%)")
    print(f"Perguntas Nao Suportadas: {total_nao_suportadas} ({(total_nao_suportadas/total_perguntas)*100:.1f}%)")

    print("\n" + "-"*80)
    print("COBERTURA POR CATEGORIA:")
    print("-"*80)

    for categoria, resultado in resultados_por_categoria.items():
        simbolo = "OK" if resultado['percentual'] >= 70 else "!!" if resultado['percentual'] >= 50 else "X"
        print(f"[{simbolo}] {categoria:30s}: {resultado['suportadas']:2d}/{resultado['total']:2d} ({resultado['percentual']:5.1f}%)")

    # Identificar gaps críticos
    print("\n" + "-"*80)
    print("GAPS CRITICOS (categorias < 50%):")
    print("-"*80)

    gaps_criticos = [cat for cat, res in resultados_por_categoria.items() if res['percentual'] < 50]

    if gaps_criticos:
        for categoria in gaps_criticos:
            resultado = resultados_por_categoria[categoria]
            print(f"\n{categoria}:")
            for detalhe in resultado['detalhes']:
                if detalhe['status'] == "NAO_SUPORTADA":
                    print(f"  - {detalhe['pergunta']}")
    else:
        print("\nNenhum gap crítico identificado!")

    # Recomendações
    print("\n" + "="*80)
    print("RECOMENDACOES:")
    print("="*80)

    if (total_suportadas / total_perguntas) >= 0.8:
        print("EXCELENTE: Sistema cobre mais de 80% das perguntas!")
    elif (total_suportadas / total_perguntas) >= 0.6:
        print("BOM: Sistema cobre mais de 60% das perguntas.")
        print("Recomendacao: Implementar patterns para categorias com <70% de cobertura")
    else:
        print("ATENCAO: Sistema cobre menos de 60% das perguntas.")
        print("Recomendacao: Revisar e expandir patterns de classificacao de intents")

    print("\n" + "="*80)

    return {
        "total": total_perguntas,
        "suportadas": total_suportadas,
        "nao_suportadas": total_nao_suportadas,
        "percentual_geral": (total_suportadas / total_perguntas) * 100,
        "por_categoria": resultados_por_categoria
    }


if __name__ == "__main__":
    import logging
    logging.basicConfig(level=logging.WARNING)  # Reduzir verbosidade

    resultado = test_cobertura_funcional()

    # Salvar relatório
    import json
    from datetime import datetime

    relatorio = {
        "data_teste": datetime.now().isoformat(),
        "resultado": resultado
    }

    os.makedirs("reports", exist_ok=True)
    with open("reports/cobertura_perguntas_negocio.json", "w", encoding="utf-8") as f:
        json.dump(relatorio, f, indent=2, ensure_ascii=False)

    print("\nRelatorio salvo em: reports/cobertura_perguntas_negocio.json")
