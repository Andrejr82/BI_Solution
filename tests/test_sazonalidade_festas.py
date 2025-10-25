"""
Teste direto da query de sazonalidade para FESTAS
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

from core.config.safe_settings import get_safe_settings
from core.connectivity.hybrid_adapter import HybridDataAdapter
from core.llm_adapter import GeminiLLMAdapter
from core.agents.code_gen_agent import CodeGenAgent
from dotenv import load_dotenv

load_dotenv()

print("=" * 80)
print("TESTE: Análise de sazonalidade - FESTAS")
print("=" * 80)

query = "Análise de sazonalidade em formato de gráfico para o segmento FESTAS"
print(f"\n❓ Query: {query}\n")

try:
    print("🔧 Inicializando componentes...")
    settings = get_safe_settings()
    llm = GeminiLLMAdapter(settings.GEMINI_API_KEY, settings.GEMINI_MODEL_NAME)
    data = HybridDataAdapter()
    agent = CodeGenAgent(llm, data)
    print("[OK] Componentes inicializados!\n")

    print("⏳ Gerando e executando código...")
    result = agent.generate_and_execute_code({"query": query, "raw_data": []})

    print(f"\n📊 Resultado:")
    print(f"   Tipo: {result.get('type')}")

    if result['type'] == 'error':
        print(f"   ❌ ERRO: {result.get('output')}")
    else:
        print(f"   ✅ SUCESSO!")
        if 'output' in result:
            print(f"   Output: {str(result['output'])[:200]}")

except Exception as e:
    print(f"\n❌ ERRO EXCEPTION: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 80)
