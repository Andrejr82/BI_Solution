"""
TESTE DE DIAGNOSTICO - Por que graficos nao sao gerados?

Este script testa UMA UNICA query que explicitamente pede grafico
e mostra os logs detalhados da classificacao de intent.

Objetivo: Entender se o problema eh na classificacao ou na geracao.
"""

import sys
import os
import io
import logging
from pathlib import Path

# Fix encoding para Windows
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

# Adicionar o diretório raiz ao path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Configurar logging VERBOSE
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)

# Imports do sistema
from core.config.safe_settings import get_safe_settings
from core.connectivity.hybrid_adapter import HybridDataAdapter
from core.llm_adapter import GeminiLLMAdapter
from core.agents.code_gen_agent import CodeGenAgent
from core.graph.graph_builder import GraphBuilder

def main():
    print("=" * 80)
    print("🔍 TESTE DE DIAGNÓSTICO - Classificação de Intent para Gráficos")
    print("=" * 80)
    print()

    # Inicializar componentes
    print("📦 Inicializando componentes...")
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
    print("✅ Componentes inicializados\n")

    # Query de teste que EXPLICITAMENTE pede gráfico
    query_teste = "Gere um gráfico de barras mostrando as vendas do produto 369947 na UNE SCR nos últimos 30 dias"

    print("=" * 80)
    print(f"📝 Query de teste: \"{query_teste}\"")
    print("=" * 80)
    print("\n🔍 LOGS DETALHADOS:\n")

    # Executar query
    result_state = grafo.invoke({
        "messages": [{"role": "user", "content": query_teste}]
    })

    # Analisar resultado
    print("\n" + "=" * 80)
    print("📊 RESULTADO DO TESTE")
    print("=" * 80)

    resultado = result_state.get("final_response", {})
    tipo = resultado.get("type", "unknown")
    sucesso = resultado.get("success", False)

    print(f"\n✅ Sucesso: {sucesso}")
    print(f"📋 Tipo retornado: {tipo}")

    if tipo == "chart":
        print("🎉 SUCESSO! Gráfico foi gerado corretamente!")
    elif tipo == "data":
        print("⚠️ PROBLEMA: Retornou dados tabulares em vez de gráfico")
    elif tipo == "text":
        print("❌ PROBLEMA CRÍTICO: Retornou texto em vez de gráfico")
    else:
        print(f"❓ Tipo inesperado: {tipo}")

    # Mostrar resposta
    if "response" in resultado:
        response_preview = str(resultado["response"])[:500]
        print(f"\n📄 Preview da resposta:\n{response_preview}...")

    print("\n" + "=" * 80)
    print("🔍 ANÁLISE:")
    print("=" * 80)
    print("""
Verifique nos logs acima:

1. [CLASSIFY_INTENT] 📝 Query original - A query foi capturada corretamente?
2. [CLASSIFY_INTENT] 🤖 Resposta LLM raw - O que a LLM respondeu?
3. [CLASSIFY_INTENT] ✅ Intent classificada - Qual intent foi detectada?
4. [CLASSIFY_INTENT] ⚠️ POSSÍVEL ERRO - Houve warning sobre classificação incorreta?

Se intent != 'gerar_grafico', o problema está na CLASSIFICAÇÃO.
Se intent == 'gerar_grafico' mas tipo != 'chart', o problema está na GERAÇÃO.
    """)

if __name__ == "__main__":
    main()
