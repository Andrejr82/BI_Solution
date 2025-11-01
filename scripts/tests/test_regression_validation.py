"""
Script de Teste de Regressão - Validação de Correções LLM
Data: 30/10/2025
Objetivo: Validar correções implementadas nas fases 1-5 do roadmap
"""

import sys
from pathlib import Path

# Adicionar diretório raiz ao path
ROOT_DIR = Path(__file__).parent.parent.parent
sys.path.insert(0, str(ROOT_DIR))

import json
import time
from datetime import datetime
from typing import Dict, List, Any
import logging

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


# ========================================
# CASOS DE TESTE ORGANIZADOS POR CATEGORIA
# ========================================

TEST_QUERIES = {
    "graficos_temporais": [
        "gere um gráfico de evolução dos segmentos na une tij",
        "mostre a evolução temporal de vendas do segmento tecidos",
        "evolução de vendas nos últimos 6 meses",
        "gráfico de tendência de vendas por mês",
    ],
    "rankings": [
        "ranking de vendas do segmento tecidos",
        "ranking completo de vendas por produto",
        "ranking de vendas na une scr",
        "ranking de produtos mais vendidos",
    ],
    "top_n": [
        "top 10 produtos mais vendidos",
        "top 5 segmentos com maiores vendas",
        "top 20 produtos do segmento papelaria",
        "top 3 unes com maior faturamento",
    ],
    "agregacoes": [
        "total de vendas do segmento tecidos",
        "soma das vendas da une tij",
        "média de vendas por produto",
        "quanto vendeu o segmento tecidos em 30 dias",
    ],
    "comparacoes": [
        "comparar vendas entre une tij e une scr",
        "diferença de vendas entre tecidos e papelaria",
        "vendas tecidos versus papelaria",
    ],
    "validacao_colunas": [
        # Testa Column Validator (Fase 1)
        "vendas por nomesegmento",
        "ranking por venda_30_d",
        "produtos com estoque zero",
    ],
    "queries_amplas": [
        # Testa Fallback para Queries Amplas (Fase 1)
        "mostre todas as vendas",
        "quero ver todos os dados",
        "mostre tudo do sistema",
    ],
    "graficos_complexos": [
        # Testa melhores práticas Plotly (Fase 1.1)
        "gráfico de barras de vendas por segmento",
        "gráfico de pizza de distribuição de vendas",
        "gráfico de dispersão entre estoque e vendas",
    ]
}


class RegressionTester:
    """Executor de testes de regressão"""

    def __init__(self):
        self.results = {
            "total_queries": 0,
            "successful": 0,
            "failed": 0,
            "errors": [],
            "by_category": {},
            "start_time": datetime.now().isoformat(),
        }

        # Importar apenas quando necessário
        self._code_gen_agent = None

    def _get_code_gen_agent(self):
        """Lazy loading do CodeGenAgent"""
        if self._code_gen_agent is None:
            try:
                import os
                from dotenv import load_dotenv
                from core.agents.code_gen_agent import CodeGenAgent
                from core.llm_adapter import GeminiLLMAdapter
                from core.connectivity.parquet_adapter import ParquetAdapter

                # Carregar variáveis de ambiente do .env
                load_dotenv()

                # Inicializar LLM Adapter
                api_key = os.getenv("GEMINI_API_KEY")
                if not api_key:
                    raise ValueError("GEMINI_API_KEY não encontrada no arquivo .env")

                llm_adapter = GeminiLLMAdapter(
                    api_key=api_key,
                    model_name="gemini-2.0-flash-exp",
                    enable_cache=True
                )
                logger.info("[OK] GeminiLLMAdapter inicializado")

                # Inicializar Data Adapter
                parquet_file_path = ROOT_DIR / "data" / "parquet" / "admmat_extended.parquet"
                data_adapter = ParquetAdapter(file_path=str(parquet_file_path))
                logger.info("[OK] ParquetAdapter inicializado")

                # Inicializar CodeGenAgent
                self._code_gen_agent = CodeGenAgent(
                    llm_adapter=llm_adapter,
                    data_adapter=data_adapter
                )
                logger.info("[OK] CodeGenAgent carregado com sucesso")
            except Exception as e:
                logger.error(f"[FAIL] Erro ao carregar CodeGenAgent: {e}")
                raise
        return self._code_gen_agent

    def test_query(self, query: str, category: str) -> Dict[str, Any]:
        """
        Testa uma query individual

        Returns:
            {
                "query": str,
                "category": str,
                "success": bool,
                "execution_time": float,
                "error": str (se houver),
                "result_type": str,
                "rows_returned": int (se aplicável)
            }
        """
        logger.info(f"\n[TEST] Testando [{category}]: {query}")

        result = {
            "query": query,
            "category": category,
            "success": False,
            "execution_time": 0.0,
            "error": None,
            "result_type": None,
            "rows_returned": 0
        }

        start_time = time.time()

        try:
            agent = self._get_code_gen_agent()

            # Executar query
            response = agent.generate_and_execute_code({
                "query": query,
                "context": {}
            })

            result["execution_time"] = time.time() - start_time

            # Analisar resposta
            if response and isinstance(response, dict):
                result["result_type"] = response.get("type", "unknown")

                if result["result_type"] == "error":
                    result["success"] = False
                    result["error"] = response.get("output", "Unknown error")
                    logger.error(f"[FAIL] FALHOU: {result['error']}")

                elif result["result_type"] in ["dataframe", "chart", "text"]:
                    result["success"] = True

                    # Tentar obter número de linhas
                    if result["result_type"] == "dataframe":
                        output = response.get("output")
                        if hasattr(output, "shape"):
                            result["rows_returned"] = output.shape[0]

                    logger.info(f"[OK] SUCESSO ({result['execution_time']:.2f}s) - Tipo: {result['result_type']}")

                else:
                    result["success"] = False
                    result["error"] = f"Tipo de resultado inesperado: {result['result_type']}"
                    logger.warning(f"[WARN] AVISO: {result['error']}")

            else:
                result["success"] = False
                result["error"] = "Resposta invalida do agente"
                logger.error(f"[FAIL] FALHOU: Resposta invalida")

        except Exception as e:
            result["execution_time"] = time.time() - start_time
            result["success"] = False
            result["error"] = str(e)
            logger.error(f"[FAIL] EXCECAO: {e}")

        return result

    def run_all_tests(self) -> Dict[str, Any]:
        """Executa todos os testes"""
        logger.info("="*80)
        logger.info("[START] INICIANDO TESTES DE REGRESSAO")
        logger.info("="*80)

        for category, queries in TEST_QUERIES.items():
            logger.info(f"\n[CATEGORY] {category.upper()}")
            logger.info("-"*80)

            category_results = {
                "total": len(queries),
                "successful": 0,
                "failed": 0,
                "queries": []
            }

            for query in queries:
                result = self.test_query(query, category)

                self.results["total_queries"] += 1

                if result["success"]:
                    self.results["successful"] += 1
                    category_results["successful"] += 1
                else:
                    self.results["failed"] += 1
                    category_results["failed"] += 1
                    self.results["errors"].append({
                        "query": query,
                        "category": category,
                        "error": result["error"]
                    })

                category_results["queries"].append(result)

            self.results["by_category"][category] = category_results

            # Resumo da categoria
            success_rate = (category_results["successful"] / category_results["total"] * 100) if category_results["total"] > 0 else 0
            logger.info(f"\n[SUMMARY] Resumo [{category}]: {category_results['successful']}/{category_results['total']} ({success_rate:.1f}%)")

        self.results["end_time"] = datetime.now().isoformat()

        return self.results

    def generate_report(self) -> str:
        """Gera relatório formatado dos testes"""

        success_rate = (self.results["successful"] / self.results["total_queries"] * 100) if self.results["total_queries"] > 0 else 0
        error_rate = 100 - success_rate

        report = f"""
================================================================================
                   RELATORIO DE TESTES DE REGRESSAO
                           {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}
================================================================================

RESUMO GERAL
--------------------------------------------------------------------------------
  Total de Queries Testadas: {self.results['total_queries']}
  [OK] Sucessos: {self.results['successful']} ({success_rate:.1f}%)
  [FAIL] Falhas: {self.results['failed']} ({error_rate:.1f}%)

  Meta do Roadmap: 95% de taxa de sucesso
  {'[OK] META ATINGIDA!' if success_rate >= 95 else f'[AVISO] Faltam {95 - success_rate:.1f}% para atingir meta'}

RESULTADOS POR CATEGORIA
--------------------------------------------------------------------------------
"""

        for category, data in self.results["by_category"].items():
            cat_success_rate = (data["successful"] / data["total"] * 100) if data["total"] > 0 else 0
            status_icon = "[OK]" if cat_success_rate >= 90 else "[WARN]" if cat_success_rate >= 70 else "[FAIL]"

            report += f"\n  {status_icon} {category.upper()}\n"
            report += f"     Sucesso: {data['successful']}/{data['total']} ({cat_success_rate:.1f}%)\n"

        if self.results["errors"]:
            report += f"""

ERROS ENCONTRADOS ({len(self.results['errors'])})
--------------------------------------------------------------------------------
"""
            for i, error in enumerate(self.results["errors"][:10], 1):
                report += f"\n  {i}. [{error['category']}] {error['query']}\n"
                report += f"     Erro: {error['error'][:100]}...\n"

            if len(self.results["errors"]) > 10:
                report += f"\n  ... e mais {len(self.results['errors']) - 10} erros\n"

        report += f"""

VALIDACAO DAS CORRECOES IMPLEMENTADAS
--------------------------------------------------------------------------------
"""

        # Validar cada fase
        validations = [
            ("Fase 1.1: Column Validator", "validacao_colunas"),
            ("Fase 1.2: Fallback Queries Amplas", "queries_amplas"),
            ("Fase 1.3: Gráficos Temporais", "graficos_temporais"),
            ("Fase 2: Few-Shot Learning (Rankings)", "rankings"),
            ("Fase 2: Few-Shot Learning (Top N)", "top_n"),
        ]

        for phase_name, category in validations:
            if category in self.results["by_category"]:
                data = self.results["by_category"][category]
                success_rate = (data["successful"] / data["total"] * 100) if data["total"] > 0 else 0
                status = "[OK] PASSOU" if success_rate >= 80 else "[WARN] ATENCAO" if success_rate >= 50 else "[FAIL] FALHOU"
                report += f"  {status} {phase_name}: {success_rate:.1f}%\n"

        report += f"""

DADOS SALVOS EM
--------------------------------------------------------------------------------
  Arquivo JSON: data/reports/test_regression_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json
  Logs Completos: logs/tests/regression_{datetime.now().strftime('%Y%m%d')}.log

================================================================================
                            FIM DO RELATORIO
================================================================================
"""

        return report

    def save_results(self):
        """Salva resultados em arquivo JSON"""
        reports_dir = ROOT_DIR / "data" / "reports"
        reports_dir.mkdir(parents=True, exist_ok=True)

        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filepath = reports_dir / f"test_regression_results_{timestamp}.json"

        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(self.results, f, indent=2, ensure_ascii=False)

        logger.info(f"[SAVE] Resultados salvos em: {filepath}")

        return filepath


def main():
    """Função principal"""
    try:
        tester = RegressionTester()

        # Executar testes
        results = tester.run_all_tests()

        # Gerar relatório
        report = tester.generate_report()
        print(report)

        # Salvar resultados
        filepath = tester.save_results()

        # Salvar relatório em markdown
        report_md_path = filepath.parent / f"test_regression_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
        with open(report_md_path, 'w', encoding='utf-8') as f:
            f.write(report)

        logger.info(f"[SAVE] Relatorio markdown salvo em: {report_md_path}")

        # Retornar código de saída baseado em taxa de sucesso
        success_rate = (results["successful"] / results["total_queries"] * 100) if results["total_queries"] > 0 else 0

        if success_rate >= 95:
            logger.info("[SUCCESS] TESTES CONCLUIDOS COM SUCESSO! Meta atingida.")
            return 0
        elif success_rate >= 80:
            logger.warning("[WARN] Testes concluidos com avisos. Taxa de sucesso abaixo da meta.")
            return 1
        else:
            logger.error("[FAIL] Testes falharam. Taxa de sucesso muito baixa.")
            return 2

    except Exception as e:
        logger.error(f"[ERROR] Erro critico durante testes: {e}", exc_info=True)
        return 3


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
