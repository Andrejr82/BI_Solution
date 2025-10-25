"""
Script de Diagnóstico do Sistema
Verifica todas as dependências e configurações críticas
"""
import sys
import os

# Adicionar diretório raiz ao path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def check_dependencies():
    """Verifica todas as dependências do sistema"""
    print("=" * 60)
    print("DIAGNOSTICO DO SISTEMA - Agent_Solution_BI")
    print("=" * 60)

    deps = {
        'Polars': 'polars',
        'Dask': 'dask',
        'Pandas': 'pandas',
        'Streamlit': 'streamlit',
        'LangChain': 'langchain',
        'FAISS': 'faiss',
        'Sentence Transformers': 'sentence_transformers',
        'Plotly': 'plotly',
        'PyArrow': 'pyarrow',
    }

    print("\n1. DEPENDENCIAS PRINCIPAIS")
    print("-" * 60)

    for name, module in deps.items():
        try:
            mod = __import__(module)
            version = getattr(mod, '__version__', 'N/A')
            print(f"  OK - {name:25} v{version}")
        except ImportError as e:
            print(f"  ERRO - {name:23} NAO INSTALADO: {e}")
        except Exception as e:
            print(f"  AVISO - {name:22} Erro: {e}")

    print("\n2. ADAPTADORES DE DADOS")
    print("-" * 60)

    try:
        from core.connectivity.polars_dask_adapter import POLARS_AVAILABLE, pl, PolarsDaskAdapter
        if POLARS_AVAILABLE:
            print(f"  OK - Polars disponivel (v{pl.__version__})")
            print(f"  OK - PolarsDaskAdapter carregado")
        else:
            print("  AVISO - Polars nao disponivel, usando apenas Dask")
    except Exception as e:
        print(f"  ERRO - PolarsDaskAdapter: {e}")

    print("\n3. SISTEMA RAG")
    print("-" * 60)

    try:
        from core.rag.query_retriever import QueryRetriever
        from core.rag.example_collector import ExampleCollector
        print("  OK - QueryRetriever carregado")
        print("  OK - ExampleCollector carregado")

        # Verificar banco de exemplos
        import json
        examples_file = "data/query_examples.json"
        if os.path.exists(examples_file):
            with open(examples_file, 'r', encoding='utf-8') as f:
                examples = json.load(f)
            print(f"  OK - Banco RAG: {len(examples)} exemplos")
        else:
            print("  AVISO - Banco RAG nao encontrado")
    except Exception as e:
        print(f"  ERRO - Sistema RAG: {e}")

    print("\n4. AGENTES")
    print("-" * 60)

    try:
        from core.agents.code_gen_agent import CodeGenAgent
        print("  OK - CodeGenAgent carregado")
    except Exception as e:
        print(f"  ERRO - CodeGenAgent: {e}")

    print("\n5. DADOS PARQUET")
    print("-" * 60)

    parquet_files = [
        "data/final_data.parquet",
        "data/produtos_vendidos_clean.parquet",
    ]

    for file_path in parquet_files:
        if os.path.exists(file_path):
            size_mb = os.path.getsize(file_path) / (1024 * 1024)
            print(f"  OK - {os.path.basename(file_path):35} ({size_mb:.1f} MB)")
        else:
            print(f"  AVISO - {os.path.basename(file_path):33} NAO ENCONTRADO")

    print("\n6. VARIAVEIS DE AMBIENTE")
    print("-" * 60)

    env_vars = [
        'GEMINI_API_KEY',
        'DEEPSEEK_API_KEY',
        'POLARS_ENABLED',
        'POLARS_THRESHOLD_MB',
    ]

    for var in env_vars:
        value = os.getenv(var)
        if value:
            # Mascarar API keys
            if 'KEY' in var:
                masked = value[:8] + '...' + value[-4:] if len(value) > 12 else '***'
                print(f"  OK - {var:25} = {masked}")
            else:
                print(f"  OK - {var:25} = {value}")
        else:
            if 'KEY' in var:
                print(f"  INFO - {var:24} = (nao configurada)")
            else:
                print(f"  OK - {var:25} = (padrao)")

    print("\n7. AUTENTICACAO")
    print("-" * 60)

    try:
        from core.auth import login, CLOUD_USERS
        print(f"  OK - Sistema de autenticacao carregado")
        print(f"  OK - {len(CLOUD_USERS)} usuarios cloud configurados")
    except Exception as e:
        print(f"  ERRO - Autenticacao: {e}")

    print("\n" + "=" * 60)
    print("DIAGNOSTICO CONCLUIDO")
    print("=" * 60)


if __name__ == '__main__':
    check_dependencies()
