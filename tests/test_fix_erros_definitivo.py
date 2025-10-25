"""
Teste definitivo das correções dos erros críticos
- UnboundLocalError em code_gen_agent.py
- Validação de colunas em une_tools.py
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import logging
from core.agents.code_gen_agent import CodeGenAgent
from core.llm_adapter import GeminiLLMAdapter
from core.tools.une_tools import calcular_abastecimento_une
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def test_query_grafico_temporal():
    """Teste 1: Query que causava UnboundLocalError"""
    logger.info("\n" + "="*80)
    logger.info("TESTE 1: Query de gráfico temporal (UnboundLocalError)")
    logger.info("="*80)

    try:
        api_key = os.getenv("GEMINI_API_KEY")
        llm_adapter = GeminiLLMAdapter(api_key=api_key, model_name="gemini-2.5-flash-lite")
        code_gen = CodeGenAgent(llm_adapter=llm_adapter)

        query = "gráfico de evolução segmento unes SCR"
        logger.info(f"Query: {query}")

        result = code_gen.generate_and_execute_code({"query": query})

        if result["type"] == "error":
            logger.error(f"❌ FALHOU: {result['output']}")
            return False
        else:
            logger.info(f"✅ SUCESSO: Tipo de resultado = {result['type']}")
            return True

    except Exception as e:
        logger.error(f"❌ EXCEÇÃO: {e}", exc_info=True)
        return False

def test_calcular_abastecimento_une():
    """Teste 2: Função UNE que causava erro de validação de colunas"""
    logger.info("\n" + "="*80)
    logger.info("TESTE 2: calcular_abastecimento_une (validação de colunas)")
    logger.info("="*80)

    try:
        # Testar com UNE 2586 (MAD - existe nos dados)
        une_id = 2586
        logger.info(f"Testando calcular_abastecimento_une(une_id={une_id})")

        # Invocar diretamente a função (não é LangChain tool neste contexto)
        from core.tools.une_tools import calcular_abastecimento_une as calc_func
        result = calc_func.invoke({"une_id": une_id})

        if "error" in result:
            logger.error(f"❌ FALHOU: {result['error']}")
            if "colunas_disponiveis" in result:
                logger.info(f"Colunas disponíveis: {result['colunas_disponiveis']}")
            return False
        else:
            logger.info(f"✅ SUCESSO: {result['total_produtos']} produtos encontrados")
            if result['total_produtos'] > 0:
                logger.info(f"Exemplo produto: {result['produtos'][0]['nome_produto']}")
            return True

    except Exception as e:
        logger.error(f"❌ EXCEÇÃO: {e}", exc_info=True)
        return False

def test_query_ranking_vendas():
    """Teste 3: Query simples de ranking para validar load_data()"""
    logger.info("\n" + "="*80)
    logger.info("TESTE 3: Query simples de ranking (validação load_data)")
    logger.info("="*80)

    try:
        api_key = os.getenv("GEMINI_API_KEY")
        llm_adapter = GeminiLLMAdapter(api_key=api_key, model_name="gemini-2.5-flash-lite")
        code_gen = CodeGenAgent(llm_adapter=llm_adapter)

        query = "top 5 produtos mais vendidos últimos 30 dias"
        logger.info(f"Query: {query}")

        result = code_gen.generate_and_execute_code({"query": query})

        if result["type"] == "error":
            logger.error(f"❌ FALHOU: {result['output']}")
            return False
        else:
            logger.info(f"✅ SUCESSO: Tipo de resultado = {result['type']}")
            if result["type"] == "dataframe":
                logger.info(f"Número de linhas: {len(result['output'])}")
            return True

    except Exception as e:
        logger.error(f"❌ EXCEÇÃO: {e}", exc_info=True)
        return False

def main():
    """Executar todos os testes"""
    logger.info("\n" + "="*80)
    logger.info("🔬 INICIANDO TESTES DE CORREÇÃO DEFINITIVA")
    logger.info("="*80)

    resultados = {
        "test_query_grafico_temporal": test_query_grafico_temporal(),
        "test_calcular_abastecimento_une": test_calcular_abastecimento_une(),
        "test_query_ranking_vendas": test_query_ranking_vendas()
    }

    # Sumário
    logger.info("\n" + "="*80)
    logger.info("📊 SUMÁRIO DOS TESTES")
    logger.info("="*80)

    total = len(resultados)
    passou = sum(resultados.values())
    falhou = total - passou

    for nome, passou_teste in resultados.items():
        status = "✅ PASSOU" if passou_teste else "❌ FALHOU"
        logger.info(f"{status}: {nome}")

    logger.info(f"\nTotal: {passou}/{total} testes passaram")

    if falhou == 0:
        logger.info("\n🎉 TODOS OS TESTES PASSARAM! Correções validadas com sucesso.")
        return True
    else:
        logger.error(f"\n⚠️ {falhou} teste(s) falharam. Revisar correções necessárias.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
