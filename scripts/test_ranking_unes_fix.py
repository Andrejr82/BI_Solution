"""
Script de Teste: Validação da Correção do Ranking de UNEs
===========================================================

Testa se a LLM agora gera código correto para ranking de vendas das UNEs
usando a coluna 'une_nome' (que existe no Parquet).

Autor: Claude Code + Context7
Data: 2025-10-27
"""

import sys
import os
import logging

# Adicionar raiz do projeto ao path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.llm_base import BaseLLMAdapter
from core.agents.code_gen_agent import CodeGenAgent
from core.connectivity.polars_dask_adapter import PolarsDaskAdapter

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def test_ranking_unes():
    """Testa query de ranking de vendas das UNEs."""

    print("="*80)
    print("TESTE DE CORREÇÃO: Ranking de Vendas das UNEs")
    print("="*80)

    # Inicializar componentes
    try:
        # LLM Adapter
        llm_adapter = BaseLLMAdapter()
        logger.info("✅ LLM Adapter inicializado")

        # Data Adapter (Polars/Dask)
        parquet_path = os.path.join("data", "parquet", "admmat*.parquet")
        data_adapter = PolarsDaskAdapter(file_path=parquet_path)
        logger.info(f"✅ Data Adapter inicializado: {parquet_path}")

        # Code Gen Agent
        code_agent = CodeGenAgent(llm_adapter, data_adapter)
        logger.info("✅ CodeGenAgent inicializado")

    except Exception as e:
        logger.error(f"❌ Erro ao inicializar componentes: {e}")
        return False

    # Queries de teste
    test_queries = [
        "ranking de vendas todas as unes",
        "gere gráfico ranking de vendas das unes",
        "top 10 unes por vendas",
        "ranking unes por venda_30_d"
    ]

    results = []

    for i, query in enumerate(test_queries, 1):
        print(f"\n{'─'*80}")
        print(f"TESTE {i}/{len(test_queries)}: {query}")
        print(f"{'─'*80}")

        try:
            # Executar query
            input_data = {"query": query, "raw_data": None}
            result = code_agent.generate_and_execute_code(input_data)

            # Validar resultado
            result_type = result.get("type")

            if result_type == "error":
                error_msg = result.get("output", "Erro desconhecido")

                # Verificar se é o erro antigo (une_nome não encontrado)
                if "une_nome" in error_msg.lower() and "não encontrada" in error_msg.lower():
                    print(f"❌ FALHA: Ainda ocorre erro de coluna 'une_nome' não encontrada")
                    print(f"   Erro: {error_msg}")
                    results.append({"query": query, "status": "FAILED_OLD_ERROR", "error": error_msg})
                else:
                    print(f"⚠️ ERRO DIFERENTE: {error_msg}")
                    results.append({"query": query, "status": "FAILED_OTHER_ERROR", "error": error_msg})

            elif result_type in ["dataframe", "chart", "multiple_charts"]:
                print(f"✅ SUCESSO: Tipo de resultado = {result_type}")

                if result_type == "dataframe":
                    output = result.get("output")
                    print(f"   DataFrame retornado: {len(output)} linhas")
                    if len(output) > 0:
                        print(f"   Colunas: {list(output.columns)}")
                        print(f"   Primeiras 3 linhas:\n{output.head(3)}")
                elif result_type == "chart":
                    print(f"   Gráfico Plotly gerado com sucesso")
                elif result_type == "multiple_charts":
                    charts = result.get("output", [])
                    print(f"   {len(charts)} gráficos Plotly gerados")

                results.append({"query": query, "status": "SUCCESS", "type": result_type})

            else:
                print(f"⚠️ RESULTADO INESPERADO: tipo = {result_type}")
                results.append({"query": query, "status": "UNEXPECTED", "type": result_type})

        except Exception as e:
            print(f"❌ EXCEÇÃO: {type(e).__name__}: {e}")
            results.append({"query": query, "status": "EXCEPTION", "error": str(e)})

    # Resumo
    print(f"\n{'='*80}")
    print("RESUMO DOS TESTES")
    print(f"{'='*80}")

    success_count = sum(1 for r in results if r["status"] == "SUCCESS")
    failed_old_count = sum(1 for r in results if r["status"] == "FAILED_OLD_ERROR")
    failed_other_count = sum(1 for r in results if r["status"] == "FAILED_OTHER_ERROR")
    exception_count = sum(1 for r in results if r["status"] == "EXCEPTION")
    unexpected_count = sum(1 for r in results if r["status"] == "UNEXPECTED")

    print(f"✅ Sucesso: {success_count}/{len(test_queries)}")
    print(f"❌ Falha (erro antigo une_nome): {failed_old_count}/{len(test_queries)}")
    print(f"⚠️ Falha (outros erros): {failed_other_count}/{len(test_queries)}")
    print(f"🔥 Exceções: {exception_count}/{len(test_queries)}")
    print(f"❓ Resultados inesperados: {unexpected_count}/{len(test_queries)}")

    # Veredito final
    print(f"\n{'='*80}")
    if failed_old_count == 0 and success_count == len(test_queries):
        print("🎉 CORREÇÃO 100% VALIDADA - PROBLEMA RESOLVIDO!")
        print("="*80)
        return True
    elif failed_old_count == 0 and success_count > 0:
        print("✅ CORREÇÃO PARCIAL - Erro antigo resolvido, mas alguns testes falharam por outros motivos")
        print("="*80)
        return True
    else:
        print("❌ CORREÇÃO NÃO VALIDADA - Erro antigo ainda persiste")
        print("="*80)
        return False

if __name__ == "__main__":
    success = test_ranking_unes()
    sys.exit(0 if success else 1)
