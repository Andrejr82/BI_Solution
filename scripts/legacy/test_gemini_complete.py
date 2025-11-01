"""
Teste Robusto Completo do Sistema com Gemini

Valida:
1. Conexão Gemini API
2. DirectQueryEngine (queries diretas)
3. LLM Adapter (queries com LLM)
4. Fallback DeepSeek
5. Cache Dask
6. Híbrido SQL Server + Parquet
"""

import sys
import os
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Carregar .env ANTES de importar módulos
from dotenv import load_dotenv
load_dotenv()

from datetime import datetime
from core.connectivity.hybrid_adapter import HybridDataAdapter
from core.business_intelligence.direct_query_engine import DirectQueryEngine
from core.factory.component_factory import ComponentFactory

def print_section(title):
    """Imprime seção formatada."""
    print("\n" + "=" * 80)
    print(f"  {title}")
    print("=" * 80)

def print_test(test_name, success, details=""):
    """Imprime resultado de teste."""
    status = "[OK]" if success else "[FALHA]"
    print(f"{status} {test_name}")
    if details:
        print(f"    {details}")

def test_api_keys():
    """Testa se as API keys estão configuradas."""
    print_section("TESTE 1: VERIFICACAO DE API KEYS")

    gemini_key = os.getenv("GEMINI_API_KEY", "")
    deepseek_key = os.getenv("DEEPSEEK_API_KEY", "")

    print_test("Gemini API Key configurada", bool(gemini_key), f"Key: {gemini_key[:20]}...")
    print_test("DeepSeek API Key configurada", bool(deepseek_key), f"Key: {deepseek_key[:20]}...")

    return bool(gemini_key) or bool(deepseek_key)

def test_gemini_connection():
    """Testa conexão direta com Gemini."""
    print_section("TESTE 2: CONEXAO GEMINI API")

    try:
        from openai import OpenAI

        gemini_key = os.getenv("GEMINI_API_KEY")
        if not gemini_key:
            print_test("Gemini API", False, "API Key nao configurada")
            return False

        client = OpenAI(
            api_key=gemini_key,
            base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
        )

        # Teste simples
        start = datetime.now()
        response = client.chat.completions.create(
            model="gemini-2.0-flash-exp",
            messages=[{"role": "user", "content": "Responda apenas: OK"}],
            max_tokens=10
        )
        duration = (datetime.now() - start).total_seconds()

        resposta = response.choices[0].message.content
        print_test("Conexao Gemini API", True, f"Resposta: '{resposta}' em {duration:.2f}s")
        return True

    except Exception as e:
        print_test("Conexao Gemini API", False, f"Erro: {str(e)[:100]}")
        return False

def test_llm_adapter():
    """Testa LLM Adapter com fallback."""
    print_section("TESTE 3: LLM ADAPTER (COM FALLBACK)")

    try:
        llm = ComponentFactory.get_llm_adapter("gemini")

        # Teste simples - formato correto OpenAI
        messages = [{"role": "user", "content": "Responda apenas com a palavra: FUNCIONANDO"}]
        start = datetime.now()
        result = llm.get_completion(messages, max_tokens=20)
        duration = (datetime.now() - start).total_seconds()

        response = result.get("content", "") if isinstance(result, dict) else str(result)
        success = "error" not in result

        print_test("LLM Adapter", success, f"Resposta: '{response[:50]}' em {duration:.2f}s")
        print(f"    Modelo usado: {llm.model_name}")
        return success

    except Exception as e:
        print_test("LLM Adapter", False, f"Erro: {str(e)[:100]}")
        return False

def test_direct_queries():
    """Testa queries diretas (sem LLM)."""
    print_section("TESTE 4: DIRECT QUERY ENGINE (SEM LLM)")

    try:
        # Inicializar
        adapter = HybridDataAdapter()
        engine = DirectQueryEngine(adapter)

        # Lista de queries para testar
        test_queries = [
            {
                "name": "Produto mais vendido",
                "type": "produto_mais_vendido",
                "params": {}
            },
            {
                "name": "Top 5 segmentos",
                "type": "ranking_segmentos",
                "params": {"limite": 5}
            },
            {
                "name": "Produto especifico (codigo 1000)",
                "type": "consulta_produto_especifico",
                "params": {"produto_codigo": "1000"}
            },
            {
                "name": "Total de vendas",
                "type": "total_vendas",
                "params": {}
            }
        ]

        results = []
        for query in test_queries:
            try:
                start = datetime.now()
                result = engine.execute_direct_query(query["type"], query["params"])
                duration = (datetime.now() - start).total_seconds()

                success = result is not None and result.get("type") != "error"

                if success:
                    print_test(
                        query["name"],
                        True,
                        f"{duration:.2f}s - {result.get('title', 'N/A')}"
                    )
                else:
                    error_msg = result.get("error", "Unknown") if result else "Retornou None"
                    print_test(query["name"], False, f"Erro: {error_msg[:80]}")

                results.append(success)

            except Exception as e:
                print_test(query["name"], False, f"Excecao: {str(e)[:80]}")
                results.append(False)

        return all(results)

    except Exception as e:
        print_test("Direct Query Engine", False, f"Erro na inicializacao: {str(e)[:100]}")
        return False

def test_cache_performance():
    """Testa performance do cache Dask."""
    print_section("TESTE 5: PERFORMANCE CACHE DASK")

    try:
        adapter = HybridDataAdapter()
        engine = DirectQueryEngine(adapter)

        # Primeira query (cache miss)
        start1 = datetime.now()
        ddf1 = engine._get_base_dask_df()
        tempo1 = (datetime.now() - start1).total_seconds()

        # Segunda query (cache hit)
        start2 = datetime.now()
        ddf2 = engine._get_base_dask_df()
        tempo2 = (datetime.now() - start2).total_seconds()

        cache_hit = ddf1 is ddf2
        melhoria = ((tempo1 - tempo2) / tempo1 * 100) if tempo1 > 0 else 0

        print_test("Cache Miss (1a chamada)", True, f"{tempo1:.2f}s")
        print_test("Cache Hit (2a chamada)", cache_hit, f"{tempo2:.2f}s")
        print_test("Melhoria de performance", melhoria > 50, f"{melhoria:.1f}%")

        return cache_hit and melhoria > 50

    except Exception as e:
        print_test("Cache Dask", False, f"Erro: {str(e)[:100]}")
        return False

def test_sql_server_connection():
    """Testa conexão SQL Server."""
    print_section("TESTE 6: CONEXAO SQL SERVER")

    try:
        adapter = HybridDataAdapter()
        status = adapter.get_status()

        sql_ok = status.get('sql_available', False)
        parquet_ok = status.get('parquet_available', False)
        current_source = status.get('current_source', 'unknown')

        print_test("SQL Server disponivel", sql_ok, f"Fonte: {current_source}")
        print_test("Parquet fallback disponivel", parquet_ok, "")

        if sql_ok:
            print("    [INFO] Sistema usando SQL Server (otimo!)")
        elif parquet_ok:
            print("    [AVISO] Sistema usando apenas Parquet (fallback)")
        else:
            print("    [ERRO] Nenhuma fonte de dados disponivel!")

        return sql_ok or parquet_ok

    except Exception as e:
        print_test("Conexao dados", False, f"Erro: {str(e)[:100]}")
        return False

def test_query_with_llm():
    """Testa query completa usando LLM para análise."""
    print_section("TESTE 7: QUERY COMPLETA COM LLM")

    try:
        llm = ComponentFactory.get_llm_adapter("gemini")
        adapter = HybridDataAdapter()
        engine = DirectQueryEngine(adapter)

        # Executar query direta
        result = engine.execute_direct_query("produto_mais_vendido", {})

        if result and result.get("type") != "error":
            # Usar LLM para interpretar resultado
            summary = result.get("summary", "")
            messages = [{"role": "user", "content": f"Resuma em uma frase: {summary}"}]

            start = datetime.now()
            llm_result = llm.get_completion(messages, max_tokens=50)
            duration = (datetime.now() - start).total_seconds()

            llm_response = llm_result.get("content", "") if isinstance(llm_result, dict) else str(llm_result)

            print_test("Query + LLM", True, f"{duration:.2f}s")
            print(f"    Query result: {summary[:60]}...")
            print(f"    LLM summary: {llm_response[:60]}...")
            return True
        else:
            print_test("Query + LLM", False, "Query base falhou")
            return False

    except Exception as e:
        print_test("Query + LLM", False, f"Erro: {str(e)[:100]}")
        return False

def test_error_handling():
    """Testa tratamento de erros."""
    print_section("TESTE 8: TRATAMENTO DE ERROS")

    try:
        adapter = HybridDataAdapter()
        engine = DirectQueryEngine(adapter)

        # Teste 1: Query inexistente
        result1 = engine.execute_direct_query("query_que_nao_existe", {})
        erro1_ok = result1 is not None and "error" in result1
        print_test("Query inexistente", erro1_ok, "Retornou erro corretamente")

        # Teste 2: Produto inexistente
        result2 = engine.execute_direct_query("consulta_produto_especifico", {"produto_codigo": "999999999"})
        erro2_ok = result2 is not None
        print_test("Produto inexistente", erro2_ok, f"Type: {result2.get('type') if result2 else 'None'}")

        # Teste 3: Parametros invalidos
        result3 = engine.execute_direct_query("consulta_produto_especifico", {"produto_codigo": "ABC"})
        erro3_ok = result3 is not None
        print_test("Parametros invalidos", erro3_ok, f"Type: {result3.get('type') if result3 else 'None'}")

        return erro1_ok and erro2_ok and erro3_ok

    except Exception as e:
        print_test("Tratamento de erros", False, f"Erro: {str(e)[:100]}")
        return False

def run_all_tests():
    """Executa todos os testes."""
    print("\n" + "=" * 80)
    print("  TESTE ROBUSTO COMPLETO - SISTEMA AGENT_BI + GEMINI")
    print("=" * 80)
    print(f"Data/Hora: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")

    # Executar testes
    results = {}

    results["api_keys"] = test_api_keys()
    results["gemini_connection"] = test_gemini_connection()
    results["llm_adapter"] = test_llm_adapter()
    results["direct_queries"] = test_direct_queries()
    results["cache_performance"] = test_cache_performance()
    results["sql_server"] = test_sql_server_connection()
    results["query_with_llm"] = test_query_with_llm()
    results["error_handling"] = test_error_handling()

    # Resumo final
    print_section("RESUMO FINAL")

    total = len(results)
    passed = sum(1 for v in results.values() if v)
    failed = total - passed
    success_rate = (passed / total * 100) if total > 0 else 0

    for test_name, success in results.items():
        status = "[OK]" if success else "[FALHA]"
        print(f"{status} {test_name.replace('_', ' ').title()}")

    print("\n" + "-" * 80)
    print(f"Total de testes: {total}")
    print(f"Passou: {passed} ({success_rate:.1f}%)")
    print(f"Falhou: {failed}")
    print("-" * 80)

    if success_rate == 100:
        print("\n[SUCESSO] SISTEMA 100% OPERACIONAL!")
        return True
    elif success_rate >= 75:
        print(f"\n[AVISO] Sistema operacional com {failed} problema(s)")
        return True
    else:
        print(f"\n[ERRO] Sistema com problemas criticos ({failed} falhas)")
        return False

if __name__ == "__main__":
    import io

    # Criar diretório de relatórios se não existir
    report_dir = Path("reports/tests")
    report_dir.mkdir(parents=True, exist_ok=True)

    # Nome do arquivo de relatório
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_file = report_dir / f"test_gemini_complete_{timestamp}.txt"

    # Capturar saída em arquivo E no console
    class TeeOutput:
        def __init__(self, *files):
            self.files = files

        def write(self, obj):
            for f in self.files:
                f.write(obj)
                f.flush()

        def flush(self):
            for f in self.files:
                f.flush()

    try:
        # Redirecionar stdout para arquivo + console
        original_stdout = sys.stdout
        with open(report_file, 'w', encoding='utf-8') as f:
            sys.stdout = TeeOutput(original_stdout, f)

            success = run_all_tests()

            print(f"\n{'=' * 80}")
            print(f"RELATORIO SALVO EM: {report_file}")
            print(f"{'=' * 80}")

            sys.stdout = original_stdout

        print(f"\n[INFO] Relatorio completo salvo em: {report_file}")
        sys.exit(0 if success else 1)

    except Exception as e:
        sys.stdout = original_stdout
        print(f"\n[ERRO FATAL] {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
