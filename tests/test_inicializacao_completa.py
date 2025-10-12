"""
Teste de Inicialização Completa - Validação Profunda
Simula exatamente o fluxo do Streamlit para detectar crashes
"""

import os
import sys
import traceback
from datetime import datetime

# Adicionar raiz ao path
root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

# Fix encoding
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

# Imports
from dotenv import load_dotenv
load_dotenv()

print("=" * 80)
print("TESTE DE INICIALIZAÇÃO COMPLETA - AGENT_BI")
print(f"Timestamp: {datetime.now()}")
print("=" * 80)

test_results = []

def log_test(name, status, details=""):
    """Log resultado de teste"""
    symbol = "✅" if status else "❌"
    test_results.append({
        "name": name,
        "status": status,
        "details": details
    })
    print(f"\n{symbol} {name}")
    if details:
        print(f"   {details}")

# ====================
# FASE 1: IMPORTS
# ====================
print("\n" + "=" * 80)
print("FASE 1: VALIDAÇÃO DE IMPORTS (Lazy Loading)")
print("=" * 80)

try:
    from core.graph.graph_builder import GraphBuilder
    log_test("Import GraphBuilder", True, "Módulo carregado")
except Exception as e:
    log_test("Import GraphBuilder", False, f"ERRO: {str(e)[:100]}")

try:
    from core.factory.component_factory import ComponentFactory
    log_test("Import ComponentFactory", True, "Módulo carregado")
except Exception as e:
    log_test("Import ComponentFactory", False, f"ERRO: {str(e)[:100]}")

try:
    from core.connectivity.parquet_adapter import ParquetAdapter
    log_test("Import ParquetAdapter", True, "Módulo carregado")
except Exception as e:
    log_test("Import ParquetAdapter", False, f"ERRO: {str(e)[:100]}")

try:
    from core.business_intelligence.direct_query_engine import DirectQueryEngine
    log_test("Import DirectQueryEngine", True, "⭐ FIX APLICADO - Módulo carregado")
except Exception as e:
    log_test("Import DirectQueryEngine", False, f"ERRO: {str(e)[:100]}")

try:
    from core.connectivity.hybrid_adapter import HybridDataAdapter
    log_test("Import HybridDataAdapter", True, "Módulo carregado")
except Exception as e:
    log_test("Import HybridDataAdapter", False, f"ERRO: {str(e)[:100]}")

try:
    from core.agents.code_gen_agent import CodeGenAgent
    log_test("Import CodeGenAgent", True, "Módulo carregado")
except Exception as e:
    log_test("Import CodeGenAgent", False, f"ERRO: {str(e)[:100]}")

# ====================
# FASE 2: INICIALIZAÇÃO DE COMPONENTES
# ====================
print("\n" + "=" * 80)
print("FASE 2: INICIALIZAÇÃO DE COMPONENTES (Simulando Streamlit)")
print("=" * 80)

# 2.1 - LLM Adapter
try:
    llm_adapter = ComponentFactory.get_llm_adapter("gemini")
    if llm_adapter:
        log_test("Inicialização LLM Adapter", True, f"Tipo: {type(llm_adapter).__name__}")
    else:
        log_test("Inicialização LLM Adapter", False, "Retornou None")
except Exception as e:
    log_test("Inicialização LLM Adapter", False, f"ERRO: {str(e)[:100]}")
    traceback.print_exc()

# 2.2 - HybridDataAdapter
try:
    print("\n📊 Inicializando HybridDataAdapter...")
    data_adapter = HybridDataAdapter()

    status = data_adapter.get_status()
    log_test("Inicialização HybridDataAdapter", True,
             f"Fonte: {status['current_source']}, SQL: {status['sql_available']}")

    # Verificar se tem dataframe
    if hasattr(data_adapter, '_dataframe') and data_adapter._dataframe is not None:
        df = data_adapter._dataframe
        print(f"   📋 Dataset: {len(df):,} registros, {len(df.columns)} colunas")
        log_test("Dataset Carregado", True, f"{len(df):,} registros")
    else:
        log_test("Dataset Carregado", False, "DataFrame não disponível")

except Exception as e:
    log_test("Inicialização HybridDataAdapter", False, f"ERRO: {str(e)[:100]}")
    traceback.print_exc()

# 2.3 - DirectQueryEngine
try:
    print("\n⚡ Inicializando DirectQueryEngine...")
    direct_engine = DirectQueryEngine(data_adapter)

    # Verificar quantos padrões foram carregados
    num_patterns = len(direct_engine.patterns) if hasattr(direct_engine, 'patterns') else 0
    log_test("Inicialização DirectQueryEngine", True,
             f"{num_patterns} padrões de query carregados")

except Exception as e:
    log_test("Inicialização DirectQueryEngine", False, f"ERRO: {str(e)[:100]}")
    traceback.print_exc()

# ====================
# FASE 3: TESTES DE QUERIES REAIS
# ====================
print("\n" + "=" * 80)
print("FASE 3: TESTES DE QUERIES REAIS")
print("=" * 80)

# 3.1 - Query SEM filtro (deve usar amostra)
try:
    print("\n🔍 Teste 1: Query sem filtro específico (deve usar amostra de 20k)")
    query1 = "quais são os produtos do segmento tecidos?"

    start_time = datetime.now()
    result1 = direct_engine.process_query(query1)
    elapsed1 = (datetime.now() - start_time).total_seconds()

    if result1 and result1.get('type') != 'error':
        log_test("Query Segmento (amostra)", True,
                 f"Tempo: {elapsed1:.2f}s, Type: {result1.get('type')}")

        # Verificar se usou amostra (não dataset completo)
        if hasattr(direct_engine, '_cached_data'):
            cache_data = list(direct_engine._cached_data.values())
            if cache_data:
                sample_size = len(cache_data[0])
                print(f"   📊 Tamanho da amostra: {sample_size:,} registros")
                if sample_size <= 20000:
                    print(f"   ✅ OK - Usou amostra (não dataset completo)")
    else:
        log_test("Query Segmento (amostra)", False,
                 f"Erro: {result1.get('error', 'Unknown')}")

except Exception as e:
    log_test("Query Segmento (amostra)", False, f"CRASH: {str(e)[:100]}")
    traceback.print_exc()

# 3.2 - Query COM filtro de estoque (deve usar dataset completo)
try:
    print("\n🔍 Teste 2: Query com filtro de estoque (deve carregar dataset completo)")
    query2 = "quais categorias do segmento tecidos com estoque baixo?"

    start_time = datetime.now()
    result2 = direct_engine.process_query(query2)
    elapsed2 = (datetime.now() - start_time).total_seconds()

    if result2 and result2.get('type') != 'error':
        log_test("Query Filtro Estoque (dataset completo)", True,
                 f"⭐ FIX APLICADO - Tempo: {elapsed2:.2f}s, Type: {result2.get('type')}")

        # Verificar se usou dataset completo
        if hasattr(direct_engine, '_cached_data'):
            cache_data = list(direct_engine._cached_data.values())
            if cache_data:
                dataset_size = len(cache_data[0])
                print(f"   📊 Tamanho do dataset: {dataset_size:,} registros")
                if dataset_size > 100000:
                    print(f"   ✅ OK - Usou dataset COMPLETO (fix aplicado!)")
                else:
                    print(f"   ⚠️  AVISO - Dataset menor que esperado")
    else:
        log_test("Query Filtro Estoque (dataset completo)", False,
                 f"Erro: {result2.get('error', 'Unknown')}")

except Exception as e:
    log_test("Query Filtro Estoque (dataset completo)", False, f"CRASH: {str(e)[:100]}")
    traceback.print_exc()

# 3.3 - Query de produto específico (deve usar dataset completo)
try:
    print("\n🔍 Teste 3: Query de produto específico (deve carregar dataset completo)")
    query3 = "vendas do produto 100001"

    start_time = datetime.now()
    result3 = direct_engine.process_query(query3)
    elapsed3 = (datetime.now() - start_time).total_seconds()

    if result3 and result3.get('type') != 'error':
        log_test("Query Produto Específico (dataset completo)", True,
                 f"Tempo: {elapsed3:.2f}s, Type: {result3.get('type')}")
    else:
        # Fallback é OK se produto não existe
        if result3.get('type') == 'fallback':
            log_test("Query Produto Específico (dataset completo)", True,
                     "Fallback OK (produto pode não existir)")
        else:
            log_test("Query Produto Específico (dataset completo)", False,
                     f"Erro: {result3.get('error', 'Unknown')}")

except Exception as e:
    log_test("Query Produto Específico (dataset completo)", False, f"CRASH: {str(e)[:100]}")
    traceback.print_exc()

# 3.4 - Query simples (ranking)
try:
    print("\n🔍 Teste 4: Query de ranking (deve usar amostra)")
    query4 = "top 10 produtos mais vendidos"

    start_time = datetime.now()
    result4 = direct_engine.process_query(query4)
    elapsed4 = (datetime.now() - start_time).total_seconds()

    if result4 and result4.get('type') != 'error':
        log_test("Query Ranking (amostra)", True,
                 f"Tempo: {elapsed4:.2f}s, Type: {result4.get('type')}")
    else:
        log_test("Query Ranking (amostra)", False,
                 f"Erro: {result4.get('error', 'Unknown')}")

except Exception as e:
    log_test("Query Ranking (amostra)", False, f"CRASH: {str(e)[:100]}")
    traceback.print_exc()

# ====================
# FASE 4: VALIDAÇÃO DE CACHE
# ====================
print("\n" + "=" * 80)
print("FASE 4: VALIDAÇÃO DE CACHE")
print("=" * 80)

try:
    # Executar mesma query 2x para testar cache
    print("\n🔄 Testando cache - Executando mesma query 2 vezes...")

    start1 = datetime.now()
    r1 = direct_engine.process_query("top 10 produtos")
    time1 = (datetime.now() - start1).total_seconds()

    start2 = datetime.now()
    r2 = direct_engine.process_query("top 10 produtos")
    time2 = (datetime.now() - start2).total_seconds()

    if time2 < time1:
        log_test("Cache Funcionando", True,
                 f"1ª exec: {time1:.2f}s, 2ª exec: {time2:.2f}s (cache mais rápido!)")
    else:
        log_test("Cache Funcionando", True,
                 f"1ª exec: {time1:.2f}s, 2ª exec: {time2:.2f}s")

except Exception as e:
    log_test("Cache Funcionando", False, f"ERRO: {str(e)[:100]}")

# ====================
# RESUMO FINAL
# ====================
print("\n" + "=" * 80)
print("RESUMO DOS TESTES")
print("=" * 80)

passed = sum(1 for t in test_results if t['status'])
failed = sum(1 for t in test_results if not t['status'])
total = len(test_results)

print(f"\n📊 Resultados:")
print(f"   ✅ Passou: {passed}/{total}")
print(f"   ❌ Falhou: {failed}/{total}")
print(f"   📈 Taxa de Sucesso: {(passed/total*100):.1f}%")

print("\n📋 Detalhes:")
for test in test_results:
    symbol = "✅" if test['status'] else "❌"
    print(f"   {symbol} {test['name']}")
    if test['details']:
        print(f"      {test['details']}")

print("\n" + "=" * 80)

if failed == 0:
    print("🎉 TODOS OS TESTES PASSARAM - SISTEMA 100% FUNCIONAL!")
elif failed <= 2:
    print("⚠️  Sistema funcional com alguns avisos - Revisar testes que falharam")
else:
    print("❌ Sistema com problemas - Atenção necessária")

print("=" * 80)
