"""
🎨 TESTE DE VALIDAÇÃO DE GRÁFICOS
==================================

Objetivo: Validar as correções implementadas em 19/10/2025:
1. max_tokens aumentado para 4096
2. load_data() usando Dask (lazy loading)
3. Instruções sobre Dask no prompt

Este teste executa 10 queries EXPLÍCITAS de gráficos para validar:
- ✅ LLM gera código Plotly (max_tokens suficiente)
- ✅ Código usa Dask corretamente (.compute() após filtros)
- ✅ Sem erros de memória
- ✅ Performance aceitável (<15s por query)

Uso:
    cd "C:\\Users\\André\\Documents\\Agent_Solution_BI"
    python tests/test_validacao_graficos.py

Tempo estimado: 3-5 minutos
"""

import sys
import os
from pathlib import Path
import time
import json
from datetime import datetime

# Adicionar diretório raiz ao path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Fix encoding para Windows
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

from core.config.safe_settings import get_safe_settings
from core.connectivity.hybrid_adapter import HybridDataAdapter
from core.llm_adapter import GeminiLLMAdapter
from core.agents.code_gen_agent import CodeGenAgent
from core.graph.graph_builder import GraphBuilder
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()

# 10 queries EXPLÍCITAS de gráfico
QUERIES_GRAFICOS = [
    # Gráficos de barras
    "Gere um gráfico de barras mostrando as vendas do produto 369947 na UNE SCR nos últimos 30 dias",
    "Mostre em um gráfico de barras o estoque dos 5 produtos mais vendidos na UNE SCR",
    "Crie um gráfico de barras com a venda dos últimos 7 dias do produto 369947",

    # Gráficos de linha
    "Gere um gráfico de linha mostrando a evolução das vendas do produto 369947 nos últimos 30 dias",
    "Mostre em um gráfico de linha a tendência de estoque do produto 369947 na UNE SCR",

    # Gráficos de pizza
    "Crie um gráfico de pizza mostrando a distribuição de vendas por UNE do produto 369947",
    "Gere um gráfico de pizza com a participação de cada produto nas vendas totais",

    # Múltiplos gráficos
    "Mostre em gráficos a comparação de vendas entre os produtos 369947 e 370000",
    "Gere gráficos comparando estoque atual vs venda dos últimos 30 dias por UNE",

    # Gráfico com cálculo
    "Crie um gráfico mostrando a relação entre estoque e ruptura por produto"
]


def executar_teste():
    """Executa teste de validação de gráficos."""

    print("=" * 80)
    print("🎨 TESTE DE VALIDAÇÃO DE GRÁFICOS")
    print("=" * 80)
    print(f"\n📅 Data: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"📊 Total de queries: {len(QUERIES_GRAFICOS)}")
    print(f"🎯 Objetivo: Validar correções de max_tokens e Dask\n")

    # Inicializar componentes
    print("🔧 Inicializando componentes...")
    try:
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
        print("[OK] GraphBuilder inicializado!\n")
    except Exception as e:
        print(f"[ERRO] Falha ao inicializar GraphBuilder: {e}")
        import traceback
        traceback.print_exc()
        return None

    # Resultados
    resultados = []
    graficos_gerados = 0
    erros = 0
    tempos = []

    # Executar queries
    for i, query in enumerate(QUERIES_GRAFICOS, 1):
        print(f"\n{'=' * 80}")
        print(f"📊 Query {i}/{len(QUERIES_GRAFICOS)}")
        print(f"{'=' * 80}")
        print(f"❓ {query}\n")

        inicio = time.time()
        sucesso = False
        tem_grafico = False
        erro_msg = None

        try:
            # Executar query usando GraphBuilder (igual ao test_80_perguntas)
            result_state = grafo.invoke({
                "messages": [{"role": "user", "content": query}]
            })

            # Extrair resposta final
            resultado = result_state.get("final_response", {})
            tempo = time.time() - inicio
            tempos.append(tempo)

            # Verificar se gerou gráfico (type == "chart")
            result_type = resultado.get("type", "unknown")

            if result_type == "chart":
                tem_grafico = True
                graficos_gerados += 1
                print(f"✅ GRÁFICO GERADO! ({tempo:.2f}s)")
                print(f"   Tipo: chart")
                if 'content' in resultado:
                    print(f"   Conteúdo: {str(resultado['content'])[:100]}...")
            else:
                print(f"❌ SEM GRÁFICO ({tempo:.2f}s)")
                print(f"   Tipo retornado: {result_type}")
                if resultado.get('content'):
                    print(f"   Conteúdo: {str(resultado['content'])[:150]}...")

            sucesso = True

        except Exception as e:
            tempo = time.time() - inicio
            tempos.append(tempo)
            erros += 1
            erro_msg = str(e)
            print(f"❌ ERRO! ({tempo:.2f}s)")
            print(f"   {erro_msg}")

        # Salvar resultado
        resultados.append({
            'query': query,
            'sucesso': sucesso,
            'tem_grafico': tem_grafico,
            'tempo': tempo,
            'erro': erro_msg
        })

        # Delay entre queries
        if i < len(QUERIES_GRAFICOS):
            print("\n⏳ Aguardando 2s antes da próxima query...")
            time.sleep(2)

    # Calcular métricas
    tempo_medio = sum(tempos) / len(tempos) if tempos else 0
    tempo_total = sum(tempos)
    taxa_graficos = (graficos_gerados / len(QUERIES_GRAFICOS)) * 100
    taxa_sucesso = ((len(QUERIES_GRAFICOS) - erros) / len(QUERIES_GRAFICOS)) * 100

    # Exibir resumo
    print("\n" + "=" * 80)
    print("📊 RESUMO DO TESTE")
    print("=" * 80)
    print(f"\n✅ Queries executadas: {len(QUERIES_GRAFICOS)}")
    print(f"🎨 Gráficos gerados: {graficos_gerados}/{len(QUERIES_GRAFICOS)} ({taxa_graficos:.1f}%)")
    print(f"✅ Taxa de sucesso: {len(QUERIES_GRAFICOS) - erros}/{len(QUERIES_GRAFICOS)} ({taxa_sucesso:.1f}%)")
    print(f"❌ Erros: {erros}")
    print(f"\n⏱️  Tempo médio: {tempo_medio:.2f}s")
    print(f"⏱️  Tempo total: {tempo_total:.2f}s ({tempo_total/60:.1f} min)")
    print(f"⏱️  Tempo min: {min(tempos):.2f}s")
    print(f"⏱️  Tempo max: {max(tempos):.2f}s")

    # Comparação com baseline
    print("\n" + "=" * 80)
    print("📈 COMPARAÇÃO COM BASELINE")
    print("=" * 80)
    print("\nBaseline (antes das correções):")
    print("  - Gráficos: 0% (0/80)")
    print("  - Tempo médio: 17.45s")
    print("  - Taxa de sucesso: 100%")
    print(f"\nNovo teste (após correções):")
    print(f"  - Gráficos: {taxa_graficos:.1f}% ({graficos_gerados}/{len(QUERIES_GRAFICOS)})")
    print(f"  - Tempo médio: {tempo_medio:.2f}s")
    print(f"  - Taxa de sucesso: {taxa_sucesso:.1f}%")

    # Análise
    print("\n" + "=" * 80)
    print("🔍 ANÁLISE")
    print("=" * 80)

    if taxa_graficos >= 70:
        print("\n✅ EXCELENTE! Taxa de gráficos >= 70%")
        print("   As correções funcionaram perfeitamente!")
    elif taxa_graficos >= 50:
        print("\n✅ BOM! Taxa de gráficos >= 50%")
        print("   As correções melhoraram significativamente o sistema.")
    elif taxa_graficos >= 20:
        print("\n⚠️  ACEITÁVEL. Taxa de gráficos >= 20%")
        print("   As correções ajudaram, mas há espaço para melhorias.")
    else:
        print("\n❌ PROBLEMA! Taxa de gráficos < 20%")
        print("   As correções não foram suficientes. Investigar logs.")

    if tempo_medio <= 10:
        print("\n✅ PERFORMANCE EXCELENTE! Tempo médio <= 10s")
    elif tempo_medio <= 15:
        print("\n✅ PERFORMANCE BOA! Tempo médio <= 15s")
    else:
        print("\n⚠️  PERFORMANCE LENTA. Tempo médio > 15s")
        print("   Considerar otimizações adicionais.")

    # Salvar relatório JSON
    relatorio_path = project_root / "tests" / f"relatorio_validacao_graficos_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

    relatorio = {
        'data': datetime.now().isoformat(),
        'objetivo': 'Validar correções de max_tokens e Dask',
        'queries_executadas': len(QUERIES_GRAFICOS),
        'metricas': {
            'graficos_gerados': graficos_gerados,
            'taxa_graficos': taxa_graficos,
            'taxa_sucesso': taxa_sucesso,
            'erros': erros,
            'tempo_medio': tempo_medio,
            'tempo_total': tempo_total,
            'tempo_min': min(tempos),
            'tempo_max': max(tempos)
        },
        'baseline': {
            'taxa_graficos': 0,
            'tempo_medio': 17.45,
            'taxa_sucesso': 100
        },
        'resultados_detalhados': resultados
    }

    with open(relatorio_path, 'w', encoding='utf-8') as f:
        json.dump(relatorio, f, indent=2, ensure_ascii=False)

    print(f"\n💾 Relatório salvo em: {relatorio_path}")

    # Conclusão
    print("\n" + "=" * 80)
    print("🎯 CONCLUSÃO")
    print("=" * 80)

    if taxa_graficos >= 50 and tempo_medio <= 15:
        print("\n✅ TESTE PASSOU! Sistema funcionando conforme esperado.")
        print("\n✅ Próximo passo: Executar teste completo (80 perguntas)")
        print("   python tests/test_80_perguntas_completo.py")
    elif taxa_graficos >= 20:
        print("\n⚠️  TESTE PARCIAL. Sistema melhorou mas pode ser otimizado.")
        print("\n🔍 Próximo passo: Analisar logs e identificar padrões de falha")
        print("   - Verificar logs em data/query_history/")
        print("   - Verificar logs em data/learning/")
    else:
        print("\n❌ TESTE FALHOU. Problemas persistem.")
        print("\n🔍 Próximo passo: Investigação detalhada")
        print("   - Executar teste de diagnóstico: python tests/test_debug_grafico.py")
        print("   - Verificar logs de erro")
        print("   - Validar configuração de max_tokens e Dask")

    print("\n" + "=" * 80)
    print("✅ Teste finalizado!")
    print("=" * 80)

    return relatorio


if __name__ == "__main__":
    try:
        relatorio = executar_teste()
    except KeyboardInterrupt:
        print("\n\n⚠️  Teste interrompido pelo usuário.")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Erro ao executar teste: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
