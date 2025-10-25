"""
🕒 TESTE DE GRÁFICOS TEMPORAIS
==============================

Objetivo: Validar geração de gráficos de evolução temporal usando colunas mes_01 a mes_12

Testa especificamente as correções implementadas:
- ✅ Colunas mes_01 a mes_12 documentadas no prompt
- ✅ Instruções sobre como criar gráficos de evolução temporal
- ✅ Exemplos de código para gráficos de linha temporais

Uso:
    cd "C:\\Users\\André\\Documents\\Agent_Solution_BI"
    python tests\\test_graficos_temporais.py

Tempo estimado: 2-3 minutos
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

# Queries específicas de evolução temporal
QUERIES_TEMPORAIS = [
    # Gráficos de evolução - 6 meses
    "Gere um gráfico de linha mostrando a tendência de vendas dos últimos 6 meses",
    "Mostre a evolução de vendas mensais em um gráfico de linha",

    # Gráficos de evolução - 12 meses
    "Crie um gráfico mostrando a evolução das vendas nos últimos 12 meses",
    "Mostre um gráfico de linha com as vendas mensais do último ano",

    # Gráficos de evolução por produto
    "Gere um gráfico de linha mostrando a evolução de vendas do produto 369947 nos últimos 6 meses",

    # Gráficos de evolução por segmento
    "Mostre um gráfico de linha com a evolução de vendas do segmento TECIDOS nos últimos 12 meses",
]


def executar_teste():
    """Executa teste de validação de gráficos temporais."""

    print("=" * 80)
    print("🕒 TESTE DE GRÁFICOS TEMPORAIS")
    print("=" * 80)
    print(f"\n📅 Data: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"📊 Total de queries: {len(QUERIES_TEMPORAIS)}")
    print(f"🎯 Objetivo: Validar geração de gráficos de evolução temporal\n")

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
    for i, query in enumerate(QUERIES_TEMPORAIS, 1):
        print(f"\n{'=' * 80}")
        print(f"🕒 Query {i}/{len(QUERIES_TEMPORAIS)}")
        print(f"{'=' * 80}")
        print(f"❓ {query}\n")

        inicio = time.time()
        sucesso = False
        tem_grafico = False
        erro_msg = None

        try:
            # Executar query usando GraphBuilder
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
                print(f"✅ GRÁFICO TEMPORAL GERADO! ({tempo:.2f}s)")
                print(f"   Tipo: chart")
                if 'content' in resultado:
                    print(f"   Conteúdo: {str(resultado['content'])[:100]}...")
            else:
                print(f"❌ SEM GRÁFICO ({tempo:.2f}s)")
                print(f"   Tipo retornado: {result_type}")
                if resultado.get('content'):
                    content_str = str(resultado['content'])
                    print(f"   Conteúdo: {content_str[:200]}...")
                    # Verificar se há erro específico sobre coluna de data
                    if 'data' in content_str.lower() or 'date' in content_str.lower():
                        print(f"   ⚠️  ERRO RELACIONADO A COLUNA DE DATA!")

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
        if i < len(QUERIES_TEMPORAIS):
            print("\n⏳ Aguardando 2s antes da próxima query...")
            time.sleep(2)

    # Calcular métricas
    tempo_medio = sum(tempos) / len(tempos) if tempos else 0
    tempo_total = sum(tempos)
    taxa_graficos = (graficos_gerados / len(QUERIES_TEMPORAIS)) * 100
    taxa_sucesso = ((len(QUERIES_TEMPORAIS) - erros) / len(QUERIES_TEMPORAIS)) * 100

    # Exibir resumo
    print("\n" + "=" * 80)
    print("📊 RESUMO DO TESTE")
    print("=" * 80)
    print(f"\n✅ Queries executadas: {len(QUERIES_TEMPORAIS)}")
    print(f"🕒 Gráficos temporais gerados: {graficos_gerados}/{len(QUERIES_TEMPORAIS)} ({taxa_graficos:.1f}%)")
    print(f"✅ Taxa de sucesso: {len(QUERIES_TEMPORAIS) - erros}/{len(QUERIES_TEMPORAIS)} ({taxa_sucesso:.1f}%)")
    print(f"❌ Erros: {erros}")
    print(f"\n⏱️  Tempo médio: {tempo_medio:.2f}s")
    print(f"⏱️  Tempo total: {tempo_total:.2f}s ({tempo_total/60:.1f} min)")
    if tempos:
        print(f"⏱️  Tempo min: {min(tempos):.2f}s")
        print(f"⏱️  Tempo max: {max(tempos):.2f}s")

    # Análise
    print("\n" + "=" * 80)
    print("🔍 ANÁLISE")
    print("=" * 80)

    if taxa_graficos >= 80:
        print("\n✅ EXCELENTE! Taxa de gráficos temporais >= 80%")
        print("   A correção funcionou perfeitamente!")
        print("   LLM entendeu como usar colunas mes_01 a mes_12.")
    elif taxa_graficos >= 50:
        print("\n✅ BOM! Taxa de gráficos temporais >= 50%")
        print("   A correção melhorou o sistema.")
        print("   Algumas queries podem precisar de ajuste no prompt.")
    elif taxa_graficos >= 20:
        print("\n⚠️  PARCIAL. Taxa de gráficos temporais >= 20%")
        print("   A correção teve algum efeito, mas ainda há problemas.")
        print("   Verificar se LLM está usando as colunas corretas.")
    else:
        print("\n❌ PROBLEMA! Taxa de gráficos temporais < 20%")
        print("   A correção NÃO funcionou como esperado.")
        print("   Possíveis causas:")
        print("   - Prompt pode precisar ser mais explícito")
        print("   - Exemplos podem estar confusos")
        print("   - LLM pode estar interpretando de forma diferente")

    # Salvar relatório JSON
    relatorio_path = project_root / "tests" / f"relatorio_graficos_temporais_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

    relatorio = {
        'data': datetime.now().isoformat(),
        'objetivo': 'Validar geração de gráficos de evolução temporal',
        'queries_executadas': len(QUERIES_TEMPORAIS),
        'metricas': {
            'graficos_gerados': graficos_gerados,
            'taxa_graficos': taxa_graficos,
            'taxa_sucesso': taxa_sucesso,
            'erros': erros,
            'tempo_medio': tempo_medio,
            'tempo_total': tempo_total,
            'tempo_min': min(tempos) if tempos else 0,
            'tempo_max': max(tempos) if tempos else 0
        },
        'correcoes_implementadas': {
            'colunas_documentadas': 'mes_01 a mes_12 adicionadas ao column_descriptions',
            'instrucoes_adicionadas': 'Seção completa sobre gráficos de evolução temporal',
            'exemplos_adicionados': 'Exemplos de código para 6 e 12 meses'
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

    if taxa_graficos >= 80:
        print("\n✅ CORREÇÃO BEM-SUCEDIDA!")
        print("\nPróximo passo: Executar teste completo de 80 perguntas")
        print("   python tests\\test_80_perguntas_completo.py")
    elif taxa_graficos >= 50:
        print("\n⚠️  CORREÇÃO PARCIAL. Ajustes adicionais podem ser necessários.")
        print("\n🔍 Próximo passo: Analisar queries que falharam")
        print("   - Verificar logs de erro")
        print("   - Ajustar prompt se necessário")
    else:
        print("\n❌ CORREÇÃO INSUFICIENTE.")
        print("\n🔧 Próximo passo: Revisar implementação")
        print("   - Verificar se colunas mes_XX estão sendo passadas corretamente")
        print("   - Verificar se prompt está sendo usado pela LLM")
        print("   - Considerar adicionar mais exemplos")

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
