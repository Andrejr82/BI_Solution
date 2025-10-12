"""
Health Check - Validação completa do sistema Agent_BI
"""

import os
import sys

# Adicionar diretório raiz ao PYTHONPATH
root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

from dotenv import load_dotenv
import pandas as pd

# Fix encoding for Windows
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

load_dotenv()

def check_api_keys():
    """Verifica se as chaves de API estão configuradas"""
    from openai import OpenAI

    results = {}

    # Gemini
    gemini_key = os.getenv("GEMINI_API_KEY", "").strip('"').strip("'")
    if gemini_key and gemini_key != "sua_chave_gemini_aqui":
        try:
            client = OpenAI(
                api_key=gemini_key,
                base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
            )
            client.chat.completions.create(
                model="gemini-2.5-flash",
                messages=[{"role": "user", "content": "test"}],
                max_tokens=5
            )
            results['gemini'] = "✅ OK"
        except Exception as e:
            results['gemini'] = f"❌ ERRO: {str(e)[:50]}"
    else:
        results['gemini'] = "⚠️  Não configurado"

    # DeepSeek
    deepseek_key = os.getenv("DEEPSEEK_API_KEY", "").strip('"').strip("'")
    if deepseek_key and deepseek_key != "sua_chave_deepseek_aqui":
        try:
            client = OpenAI(
                api_key=deepseek_key,
                base_url="https://api.deepseek.com/v1"
            )
            client.chat.completions.create(
                model="deepseek-chat",
                messages=[{"role": "user", "content": "test"}],
                max_tokens=5
            )
            results['deepseek'] = "✅ OK"
        except Exception as e:
            error_msg = str(e)
            if "402" in error_msg or "Insufficient Balance" in error_msg:
                results['deepseek'] = "⚠️  Sem créditos"
            else:
                results['deepseek'] = f"❌ ERRO: {str(e)[:50]}"
    else:
        results['deepseek'] = "⚠️  Não configurado"

    return results

def check_dataset():
    """Verifica se o dataset Parquet está acessível"""
    parquet_path = "data/parquet/admmat.parquet"

    if not os.path.exists(parquet_path):
        return {"status": "❌ Arquivo não encontrado", "path": parquet_path}

    try:
        df = pd.read_parquet(parquet_path)

        # Verificar colunas essenciais
        required_cols = ['une', 'nome_produto', 'estoque_atual', 'nomesegmento', 'NOMECATEGORIA']
        missing_cols = [col for col in required_cols if col not in df.columns]

        result = {
            "status": "✅ OK" if not missing_cols else "⚠️  Colunas faltando",
            "rows": len(df),
            "columns": len(df.columns),
            "unes": df['une_nome'].nunique() if 'une_nome' in df.columns else 0,
            "missing_columns": missing_cols if missing_cols else None
        }

        # Verificar produtos com estoque zero (teste do bug)
        if 'estoque_atual' in df.columns:
            estoque_zero = len(df[df['estoque_atual'] == 0])
            result['estoque_zero_count'] = estoque_zero
            if estoque_zero > 0:
                result['estoque_zero_status'] = "✅ OK"
            else:
                result['estoque_zero_status'] = "⚠️  Nenhum produto com estoque 0"

        return result
    except Exception as e:
        return {"status": f"❌ ERRO ao ler: {str(e)[:100]}"}

def check_core_modules():
    """Verifica se os módulos core podem ser importados"""
    results = {}

    modules = {
        "DirectQueryEngine": "core.business_intelligence.direct_query_engine",
        "ParquetAdapter": "core.connectivity.parquet_adapter",
        "HybridDataAdapter": "core.connectivity.hybrid_adapter",
        "GeminiLLMAdapter": "core.llm_adapter",
        "GraphBuilder": "core.graph.graph_builder"
    }

    for name, module_path in modules.items():
        try:
            __import__(module_path)
            results[name] = "✅ OK"
        except Exception as e:
            results[name] = f"❌ ERRO: {str(e)[:50]}"

    return results

def check_cache():
    """Verifica o sistema de cache"""
    cache_dir = "data/cache"

    if not os.path.exists(cache_dir):
        return {"status": "⚠️  Diretório não existe"}

    cache_files = [f for f in os.listdir(cache_dir) if f.endswith('.json')]

    return {
        "status": "✅ OK",
        "files_count": len(cache_files),
        "directory": cache_dir
    }

if __name__ == "__main__":
    print("=" * 70)
    print("HEALTH CHECK - AGENT_BI")
    print("=" * 70)

    print("\n[1/4] Verificando API Keys...")
    api_keys = check_api_keys()
    for key, status in api_keys.items():
        print(f"  {key.capitalize()}: {status}")

    print("\n[2/4] Verificando Dataset...")
    dataset = check_dataset()
    print(f"  Status: {dataset['status']}")
    if 'rows' in dataset:
        print(f"  Registros: {dataset['rows']:,}")
        print(f"  Colunas: {dataset['columns']}")
        print(f"  UNEs: {dataset.get('unes', 0)}")
        if 'estoque_zero_count' in dataset:
            print(f"  Produtos com estoque 0: {dataset['estoque_zero_count']:,} - {dataset['estoque_zero_status']}")

    print("\n[3/4] Verificando Módulos Core...")
    modules = check_core_modules()
    for module, status in modules.items():
        print(f"  {module}: {status}")

    print("\n[4/4] Verificando Sistema de Cache...")
    cache = check_cache()
    print(f"  Status: {cache['status']}")
    if 'files_count' in cache:
        print(f"  Arquivos em cache: {cache['files_count']}")

    print("\n" + "=" * 70)
    print("RESUMO")
    print("=" * 70)

    # Calcular status geral
    api_ok = any("✅" in v for v in api_keys.values())
    dataset_ok = "✅" in dataset['status'] or "⚠️" in dataset['status']
    modules_ok = all("✅" in v for v in modules.values())

    if api_ok and dataset_ok and modules_ok:
        print("\n✅ Sistema OPERACIONAL - Pronto para uso!")
    elif dataset_ok and modules_ok:
        print("\n⚠️  Sistema PARCIALMENTE operacional")
        print("   - Dataset e módulos OK")
        print("   - Verifique configuração de API keys")
    else:
        print("\n❌ Sistema com PROBLEMAS - Verifique erros acima")

    print("\n" + "=" * 70)
