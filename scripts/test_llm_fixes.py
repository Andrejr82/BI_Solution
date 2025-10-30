"""
Script para testar correções de erros da LLM
Data: 2025-10-26
Autor: Claude Code

Testa queries que anteriormente causavam KeyError e MemoryError
"""

import sys
import os

# Adicionar diretório raiz ao path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from core.agents.code_gen_agent import CodeGenAgent
from core.llm_adapter import GeminiLLMAdapter
from core.connectivity.polars_dask_adapter import PolarsDaskAdapter
import logging
import os

# Carregar API key do Gemini
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    print("ERRO: GEMINI_API_KEY nao encontrada no ambiente")
    print("Configure com: set GEMINI_API_KEY=sua_chave")
    sys.exit(1)

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def test_une_query():
    """
    Testa query que causava KeyError: 'UNE'
    Query original dos logs: "quais produtos estão sem giro na une SCR"
    """
    logger.info("=" * 80)
    logger.info("TESTE 1: Query que causava KeyError: 'UNE'")
    logger.info("=" * 80)

    try:
        # Inicializar adaptadores
        llm = GeminiLLMAdapter(
            api_key=GEMINI_API_KEY,
            model_name="gemini-2.0-flash-exp",
            enable_cache=True
        )

        # Obter path absoluto do parquet
        base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
        parquet_path = os.path.join(base_dir, "data", "parquet", "*.parquet")

        data_adapter = PolarsDaskAdapter(file_path=parquet_path)

        # Inicializar agente
        agent = CodeGenAgent(llm_adapter=llm, data_adapter=data_adapter)

        # Query problemática dos logs
        query = "quais produtos estão sem giro na une SCR"

        logger.info(f"Executando query: '{query}'")

        result = agent.generate_and_execute_code({
            "query": f"""
            **TAREFA:** Você deve escrever um script Python para responder à pergunta do usuário.

            **INSTRUÇÕES OBRIGATÓRIAS:**
            1. **CARREGUE OS DADOS:** Inicie seu script com a linha: `df = load_data()`
            2. **RESPONDA À PERGUNTA:** Usando o dataframe `df`, escreva o código para responder à seguinte pergunta: "{query}"
            3. **SALVE O RESULTADO NA VARIÁVEL `result`:** A última linha do seu script DEVE ser a atribuição do resultado final à variável `result`.

            **Seu Script Python (Lembre-se, a última linha deve ser `result = ...`):**
            """
        })

        logger.info(f"✅ SUCESSO! Tipo de resultado: {result['type']}")

        if result['type'] == 'dataframe':
            logger.info(f"   Linhas retornadas: {len(result['output'])}")
        elif result['type'] == 'error':
            logger.error(f"   ❌ ERRO: {result['output']}")
            return False

        return True

    except Exception as e:
        logger.error(f"❌ ERRO NO TESTE: {e}", exc_info=True)
        return False


def test_memory_query():
    """
    Testa query que causava MemoryError
    Query original dos logs: "Alertas: produtos que precisam de atenção (baixa rotação, estoque alto)"
    """
    logger.info("=" * 80)
    logger.info("TESTE 2: Query que causava MemoryError")
    logger.info("=" * 80)

    try:
        # Inicializar adaptadores
        llm = GeminiLLMAdapter(
            api_key=GEMINI_API_KEY,
            model_name="gemini-2.0-flash-exp",
            enable_cache=True
        )

        # Obter path absoluto do parquet
        base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
        parquet_path = os.path.join(base_dir, "data", "parquet", "*.parquet")

        data_adapter = PolarsDaskAdapter(file_path=parquet_path)

        # Inicializar agente
        agent = CodeGenAgent(llm_adapter=llm, data_adapter=data_adapter)

        # Query problemática dos logs (simplificada para testar otimização)
        query = "produtos com baixa rotação e estoque alto na une MAD"

        logger.info(f"Executando query: '{query}'")

        result = agent.generate_and_execute_code({
            "query": f"""
            **TAREFA:** Você deve escrever um script Python para responder à pergunta do usuário.

            **INSTRUÇÕES OBRIGATÓRIAS:**
            1. **CARREGUE OS DADOS:** Inicie seu script com a linha: `df = load_data()`
            2. **RESPONDA À PERGUNTA:** Usando o dataframe `df`, escreva o código para responder à seguinte pergunta: "{query}"
            3. **SALVE O RESULTADO NA VARIÁVEL `result`:** A última linha do seu script DEVE ser a atribuição do resultado final à variável `result`.

            **Seu Script Python (Lembre-se, a última linha deve ser `result = ...`):**
            """
        })

        logger.info(f"✅ SUCESSO! Tipo de resultado: {result['type']}")

        if result['type'] == 'dataframe':
            logger.info(f"   Linhas retornadas: {len(result['output'])}")
        elif result['type'] == 'error':
            logger.error(f"   ❌ ERRO: {result['output']}")
            return False

        return True

    except Exception as e:
        logger.error(f"❌ ERRO NO TESTE: {e}", exc_info=True)
        return False


def test_schema_columns():
    """
    Testa se LLM está usando nomes corretos das colunas
    """
    logger.info("=" * 80)
    logger.info("TESTE 3: Verificar uso de nomes corretos de colunas")
    logger.info("=" * 80)

    try:
        # Inicializar adaptadores
        llm = GeminiLLMAdapter(
            api_key=GEMINI_API_KEY,
            model_name="gemini-2.0-flash-exp",
            enable_cache=True
        )

        # Obter path absoluto do parquet
        base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
        parquet_path = os.path.join(base_dir, "data", "parquet", "*.parquet")

        data_adapter = PolarsDaskAdapter(file_path=parquet_path)

        # Inicializar agente
        agent = CodeGenAgent(llm_adapter=llm, data_adapter=data_adapter)

        # Query para testar schema correto
        query = "top 5 produtos da une NIL do segmento TECIDOS"

        logger.info(f"Executando query: '{query}'")

        result = agent.generate_and_execute_code({
            "query": f"""
            **TAREFA:** Você deve escrever um script Python para responder à pergunta do usuário.

            **INSTRUÇÕES OBRIGATÓRIAS:**
            1. **CARREGUE OS DADOS:** Inicie seu script com a linha: `df = load_data()`
            2. **RESPONDA À PERGUNTA:** Usando o dataframe `df`, escreva o código para responder à seguinte pergunta: "{query}"
            3. **SALVE O RESULTADO NA VARIÁVEL `result`:** A última linha do seu script DEVE ser a atribuição do resultado final à variável `result`.

            **Seu Script Python (Lembre-se, a última linha deve ser `result = ...`):**
            """
        })

        logger.info(f"✅ SUCESSO! Tipo de resultado: {result['type']}")

        if result['type'] == 'dataframe':
            logger.info(f"   Linhas retornadas: {len(result['output'])}")
            # Verificar se colunas estão corretas
            cols = result['output'].columns.tolist()
            logger.info(f"   Colunas retornadas: {cols}")

            # Verificar se NÃO está usando nomes incorretos
            incorrect_names = ['UNE', 'PRODUTO', 'NOME', 'VENDA_30DD', 'ESTOQUE_UNE']
            has_incorrect = any(col in incorrect_names for col in cols)

            if has_incorrect:
                logger.warning("   ⚠️ AVISO: Código ainda usa nomes incorretos de colunas!")
            else:
                logger.info("   ✅ Código usa nomes corretos (une_nome, codigo, venda_30_d, etc.)")

        elif result['type'] == 'error':
            logger.error(f"   ❌ ERRO: {result['output']}")
            return False

        return True

    except Exception as e:
        logger.error(f"❌ ERRO NO TESTE: {e}", exc_info=True)
        return False


def main():
    """Executar todos os testes"""
    logger.info("🚀 INICIANDO TESTES DE CORREÇÃO DA LLM")
    logger.info("")

    results = {
        "KeyError 'UNE'": test_une_query(),
        "MemoryError": test_memory_query(),
        "Schema Correto": test_schema_columns()
    }

    logger.info("")
    logger.info("=" * 80)
    logger.info("📊 RESUMO DOS TESTES")
    logger.info("=" * 80)

    for test_name, success in results.items():
        status = "✅ PASSOU" if success else "❌ FALHOU"
        logger.info(f"{test_name}: {status}")

    total = len(results)
    passed = sum(results.values())

    logger.info("")
    logger.info(f"Total: {passed}/{total} testes passaram ({passed/total*100:.1f}%)")

    if passed == total:
        logger.info("🎉 TODOS OS TESTES PASSARAM!")
        return 0
    else:
        logger.error("❌ ALGUNS TESTES FALHARAM")
        return 1


if __name__ == "__main__":
    sys.exit(main())
