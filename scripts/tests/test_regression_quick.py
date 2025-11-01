"""
Teste de Regressão Rápido - Validação das Correções LLM
Data: 30/10/2025
Versão simplificada com apenas queries essenciais para validação rápida
"""

import sys
from pathlib import Path

# Adicionar diretório raiz ao path
ROOT_DIR = Path(__file__).parent.parent.parent
sys.path.insert(0, str(ROOT_DIR))

import os
import json
import time
from datetime import datetime
import logging

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


# Queries de teste reduzidas (3 de cada categoria prioritária)
TEST_QUERIES = {
    "graficos_temporais": [
        "gere um gráfico de evolução dos segmentos na une tij",
    ],
    "rankings": [
        "ranking de vendas do segmento tecidos",
    ],
    "top_n": [
        "top 10 produtos mais vendidos",
    ],
}


def test_single_query(code_gen_agent, query: str):
    """Testa uma query individual"""
    logger.info(f"\n[TEST] {query}")

    try:
        start_time = time.time()

        result = code_gen_agent.generate_and_execute_code({
            "query": query,
            "context": {}
        })

        execution_time = time.time() - start_time

        if result and result.get("type") in ["dataframe", "chart", "text"]:
            logger.info(f"[OK] Sucesso em {execution_time:.2f}s - Tipo: {result.get('type')}")
            return True
        else:
            error_msg = result.get("output", "Unknown error") if result else "No response"
            logger.error(f"[FAIL] Erro: {error_msg}")
            return False

    except Exception as e:
        logger.error(f"[FAIL] Exceção: {e}")
        return False


def main():
    """Função principal"""
    try:
        logger.info("="*80)
        logger.info("[START] TESTE RAPIDO DE REGRESSAO")
        logger.info("="*80)

        # Inicializar componentes
        logger.info("\n[INIT] Inicializando componentes...")

        from dotenv import load_dotenv
        from core.agents.code_gen_agent import CodeGenAgent
        from core.llm_adapter import GeminiLLMAdapter
        from core.connectivity.parquet_adapter import ParquetAdapter

        # Carregar .env
        load_dotenv()

        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            logger.error("[FAIL] GEMINI_API_KEY não encontrada no .env")
            return 1

        llm_adapter = GeminiLLMAdapter(
            api_key=api_key,
            model_name="gemini-2.0-flash-exp",
            enable_cache=True
        )
        logger.info("[OK] LLM Adapter")

        data_adapter = ParquetAdapter()
        logger.info("[OK] Data Adapter")

        code_gen_agent = CodeGenAgent(
            llm_adapter=llm_adapter,
            data_adapter=data_adapter
        )
        logger.info("[OK] CodeGenAgent\n")

        # Executar testes
        total = 0
        passed = 0

        for category, queries in TEST_QUERIES.items():
            logger.info(f"\n[CATEGORY] {category.upper()}")
            logger.info("-"*80)

            for query in queries:
                total += 1
                if test_single_query(code_gen_agent, query):
                    passed += 1

        # Resumo
        logger.info("\n" + "="*80)
        logger.info(f"[SUMMARY] Resultados: {passed}/{total} ({passed/total*100:.1f}%)")
        logger.info("="*80)

        return 0 if passed == total else 1

    except Exception as e:
        logger.error(f"[ERROR] Erro crítico: {e}", exc_info=True)
        return 2


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
