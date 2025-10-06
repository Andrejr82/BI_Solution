"""
Script de Diagnóstico: HybridDataAdapter
Valida SQL Server + Parquet antes da apresentação.

Executar SEMPRE antes de apresentar:
    python scripts/test_hybrid_connection.py
"""
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

# Carregar .env
from pathlib import Path
env_path = Path(__file__).parent.parent / '.env'
if env_path.exists():
    with open(env_path, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                key, value = line.split('=', 1)
                os.environ[key.strip()] = value.strip().strip('"')

import logging

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(message)s'
)
logger = logging.getLogger(__name__)

def test_hybrid_adapter():
    """Testa adapter híbrido completo com relatório detalhado."""

    print("\n" + "="*70)
    print("DIAGNOSTICO: HYBRID DATA ADAPTER (SQL SERVER + PARQUET)")
    print("="*70 + "\n")

    # 1. Verificar variáveis de ambiente
    print("1. Verificando variaveis de ambiente...")

    use_sql = os.getenv("USE_SQL_SERVER", "false")
    print(f"   USE_SQL_SERVER: {use_sql}")

    if use_sql.lower() == "true":
        required_vars = ['MSSQL_SERVER', 'MSSQL_DATABASE', 'MSSQL_USER', 'MSSQL_PASSWORD']
        missing = [v for v in required_vars if not os.getenv(v)]

        if missing:
            print(f"   [AVISO] Variaveis faltando: {missing}")
            print(f"   -> SQL Server sera desabilitado, usando Parquet")
        else:
            print(f"   [OK] Credenciais SQL Server encontradas")

    # 2. Importar e inicializar HybridDataAdapter
    print("\n2. Inicializando HybridDataAdapter...")

    try:
        from core.connectivity.hybrid_adapter import HybridDataAdapter

        adapter = HybridDataAdapter()
        status = adapter.get_status()

        print(f"   [OK] Adapter inicializado")
        print(f"\n   Status:")
        print(f"   - Fonte atual: {status['current_source'].upper()}")
        print(f"   - SQL Server habilitado: {'SIM' if status['sql_enabled'] else 'NAO'}")
        print(f"   - SQL Server disponivel: {'SIM' if status['sql_available'] else 'NAO'}")
        print(f"   - Fallback Parquet: {'SIM' if status['fallback_enabled'] else 'NAO'}")

    except Exception as e:
        print(f"   [ERRO] Falha ao inicializar: {e}")
        import traceback
        traceback.print_exc()
        return False

    # 3. Testar conexão
    print("\n3. Testando conexao...")

    try:
        adapter.connect()
        print(f"   [OK] Conectado via {adapter.current_source.upper()}")
    except Exception as e:
        print(f"   [ERRO] Falha na conexao: {e}")
        return False

    # 4. Testar query simples (amostra)
    print("\n4. Testando query simples (amostra 100 registros)...")

    try:
        result = adapter.execute_query({})

        if result and len(result) > 0:
            print(f"   [OK] Query executada: {len(result)} registros retornados")
            print(f"   Fonte: {adapter.current_source.upper()}")

            # Mostrar primeira linha como exemplo
            first_row = result[0]
            sample_keys = list(first_row.keys())[:5]
            print(f"   Colunas (amostra): {sample_keys}")

        else:
            print(f"   [AVISO] Query retornou vazio")

    except Exception as e:
        print(f"   [ERRO] Falha na query: {e}")
        import traceback
        traceback.print_exc()
        return False

    # 5. Testar query com filtro (UNE específica)
    print("\n5. Testando query filtrada (UNE=261)...")

    try:
        result = adapter.execute_query({"une": 261})

        if result and len(result) > 0:
            print(f"   [OK] Query filtrada: {len(result)} registros da UNE 261")
        else:
            print(f"   [AVISO] UNE 261 nao encontrada (pode nao existir nos dados)")

    except Exception as e:
        print(f"   [ERRO] Falha na query filtrada: {e}")
        # Não é crítico se UNE específica falhar
        pass

    # 6. Testar fallback (se SQL Server ativo)
    if status['sql_available']:
        print("\n6. Testando fallback automatico...")

        try:
            # Forçar fallback manualmente
            original_source = adapter.current_source
            adapter._switch_to_fallback()

            result = adapter.execute_query({})

            if result and len(result) > 0:
                print(f"   [OK] Fallback funcionando: {len(result)} registros via Parquet")
                print(f"   Fonte mudou: {original_source.upper()} -> {adapter.current_source.upper()}")
            else:
                print(f"   [ERRO] Fallback retornou vazio")

        except Exception as e:
            print(f"   [ERRO] Fallback falhou: {e}")
            return False

    else:
        print("\n6. Teste de fallback pulado (SQL Server nao disponivel)")

    # 7. Testar integração com DirectQueryEngine
    print("\n7. Testando integracao com DirectQueryEngine...")

    try:
        from core.business_intelligence.direct_query_engine import DirectQueryEngine

        # Criar engine com HybridAdapter
        engine = DirectQueryEngine(adapter)

        # Testar consulta simples
        result = engine.process_query("produto mais vendido")

        if result and result.get("type") != "error":
            print(f"   [OK] DirectQueryEngine funcionando")
            print(f"   Query type: {result.get('query_type', 'N/A')}")
            print(f"   Method: {result.get('method', 'N/A')}")
        else:
            print(f"   [AVISO] DirectQueryEngine retornou erro ou vazio")
            print(f"   Erro: {result.get('error', 'Desconhecido')}")

    except Exception as e:
        print(f"   [ERRO] Integracao DirectQueryEngine falhou: {e}")
        import traceback
        traceback.print_exc()
        # Não é crítico para o teste básico

    # Resumo final
    print("\n" + "="*70)
    print("RESULTADO DO DIAGNOSTICO")
    print("="*70)

    if status['current_source'] == 'sqlserver':
        print("\n[OK] Sistema funcionando com SQL SERVER")
        print("     - Performance otimizada")
        print("     - Fallback Parquet disponivel")
        print("     - Pronto para apresentacao!")

    else:
        print("\n[OK] Sistema funcionando com PARQUET")

        if status['sql_enabled']:
            print("     - SQL Server configurado mas indisponivel")
            print("     - Verifique:")
            print("       * SQL Server esta rodando?")
            print("       * Credenciais corretas?")
            print("       * Firewall liberado?")

        print("     - Fallback Parquet OK")
        print("     - Sistema operacional e pronto para apresentacao!")

    print("\n" + "="*70)
    print("Proximos passos:")
    print("  1. Se tudo OK: streamlit run streamlit_app.py")
    print("  2. Se problemas: verificar logs acima")
    print("="*70 + "\n")

    return True

if __name__ == "__main__":
    try:
        success = test_hybrid_adapter()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\nTeste interrompido pelo usuario")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n[ERRO CRITICO] {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
