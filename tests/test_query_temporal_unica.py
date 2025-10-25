"""
Teste rápido de uma única query temporal para validar correção de f-string
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

from core.config.safe_settings import get_safe_settings
from core.connectivity.hybrid_adapter import HybridDataAdapter
from core.llm_adapter import GeminiLLMAdapter
from core.agents.code_gen_agent import CodeGenAgent
from core.graph.graph_builder import GraphBuilder
from dotenv import load_dotenv

load_dotenv()

print("=" * 80)
print("TESTE RÁPIDO - Query Temporal Única")
print("=" * 80)

query = "Gere um gráfico de linha mostrando a tendência de vendas dos últimos 6 meses"
print(f"\n❓ Query: {query}\n")

try:
    print("🔧 Inicializando componentes...")
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
    print("[OK] Inicializado!\n")

    print("⏳ Executando query...")
    result_state = grafo.invoke({
        "messages": [{"role": "user", "content": query}]
    })

    resultado = result_state.get("final_response", {})
    result_type = resultado.get("type", "unknown")

    print(f"\n📊 Resultado:")
    print(f"   Tipo: {result_type}")

    if result_type == "chart":
        print(f"   ✅ GRÁFICO GERADO COM SUCESSO!")
    else:
        print(f"   ❌ Não gerou gráfico")
        if 'content' in resultado:
            print(f"   Conteúdo: {str(resultado['content'])[:300]}")

except Exception as e:
    print(f"\n❌ ERRO: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 80)
print("Teste finalizado!")
print("=" * 80)
