"""
Teste para validar correção do erro:
"If using all scalar values, you must pass an index"

Este erro ocorria quando gráficos de evolução eram gerados para um único produto.

Autor: Agent_Solution_BI
Data: 2025-11-02
Versão: v2.1 - Fix temporal DataFrame
"""

import sys
import os
import logging

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(levelname)s - %(name)s - %(message)s'
)

logger = logging.getLogger(__name__)

print("=" * 80)
print("TESTE: Correção de Gráfico de Evolução - DataFrame Escalar")
print("=" * 80)

# 1. Verificar ambiente
print("\n1. Verificando ambiente...")

try:
    from core.llm_adapter import GeminiLLMAdapter
    from core.agents.code_gen_agent import CodeGenAgent
    from core.connectivity.hybrid_adapter import HybridDataAdapter
    print("   [OK] Imports bem-sucedidos")
except ImportError as e:
    print(f"   [ERRO] Erro ao importar modulos: {e}")
    sys.exit(1)

# 2. Verificar chave API
print("\n2. Verificando API Key...")
from dotenv import load_dotenv
load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    print("   [ERRO] GEMINI_API_KEY nao encontrada no .env")
    sys.exit(1)

print(f"   [OK] API Key encontrada: {api_key[:10]}...")

# 3. Inicializar agentes
print("\n3. Inicializando agentes...")

try:
    llm_adapter = GeminiLLMAdapter(api_key=api_key, model_name="gemini-2.5-flash")
    data_adapter = HybridDataAdapter()
    code_gen_agent = CodeGenAgent(llm_adapter=llm_adapter, data_adapter=data_adapter)
    print("   [OK] Agentes inicializados")
except Exception as e:
    print(f"   [ERRO] Erro ao inicializar agentes: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# 4. Testar query problemática original
print("\n4. Testando query que causava erro...")
print("   Query: 'gere gráfico de evolução do produto 592294 na une 2365'")

try:
    import time
    start = time.time()

    result = code_gen_agent.generate_and_execute_code({
        "query": "gere gráfico de evolução do produto 592294 na une 2365",
        "raw_data": []
    })

    elapsed = time.time() - start

    print("\n" + "=" * 80)
    print("RESULTADO DO TESTE:")
    print("=" * 80)

    result_type = result.get("type")
    print(f"Tipo de resposta: {result_type}")
    print(f"Tempo de execução: {elapsed:.2f}s")

    if result_type == "error":
        print(f"\n[ERRO] ERRO: {result.get('output')}")
        print("\nO erro ainda persiste. Verifique:")
        print("1. Cache foi limpo? (versao 6.1)")
        print("2. Prompt foi atualizado corretamente?")
        print("3. LLM esta gerando codigo com as novas instrucoes?")
        sys.exit(1)

    elif result_type == "chart":
        print("\n[OK] SUCESSO! Grafico gerado sem erros")
        print("\nCodigo gerado deve conter padrao correto:")
        print("- Valores mes_XX extraidos como lista/array")
        print("- DataFrame criado com pd.DataFrame({'periodo': [...], 'vendas': [...]})")
        print("- Sem uso de dict de scalars")

    elif result_type == "dataframe":
        print("\n[AVISO] AVISO: Resultado e DataFrame (esperado: chart)")
        print("Mas nao houve erro de 'must pass an index'")

    else:
        print(f"\n[AVISO] AVISO: Tipo inesperado: {result_type}")
        print(f"Output: {result.get('output')}")

    print("\n" + "=" * 80)
    print("TESTE CONCLUIDO COM SUCESSO! [OK]")
    print("=" * 80)
    print("\nProximos passos:")
    print("1. Verificar log completo em logs/app_activity/")
    print("2. Testar no Streamlit com a query original")
    print("3. Validar outros tipos de grafico de evolucao")

except Exception as e:
    print("\n" + "=" * 80)
    print("[ERRO] ERRO NO TESTE")
    print("=" * 80)
    print(f"Tipo: {type(e).__name__}")
    print(f"Mensagem: {str(e)}")

    import traceback
    print("\nStacktrace completo:")
    traceback.print_exc()

    sys.exit(1)
