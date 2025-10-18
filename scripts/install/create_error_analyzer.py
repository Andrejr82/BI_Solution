"""
Script para criar o ErrorAnalyzer conforme especificação do PLANO_PILAR_4_EXECUCAO.md
"""

from pathlib import Path

# Conteúdo do error_analyzer.py
ERROR_ANALYZER_CONTENT = '''"""
Módulo para análise de erros e geração de sugestões de melhoria.

Este módulo implementa o ErrorAnalyzer que processa feedback de erros
armazenados em arquivos JSONL e gera insights sobre problemas comuns
e sugestões de correção.
"""

import json
import logging
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, Any, List
from collections import defaultdict

logger = logging.getLogger(__name__)


class ErrorAnalyzer:
    """
    Analisa erros de queries e gera sugestões de melhoria.

    Esta classe processa arquivos de feedback em formato JSONL,
    identifica padrões de erros comuns e sugere melhorias baseadas
    nos problemas mais frequentes.
    """

    def __init__(self, feedback_dir: str = "data/learning"):
        """
        Inicializa o ErrorAnalyzer.

        Args:
            feedback_dir: Diretório onde os arquivos de feedback são armazenados.
                         Padrão: "data/learning"
        """
        self.feedback_dir = Path(feedback_dir)

        # Cria diretório se não existir
        try:
            self.feedback_dir.mkdir(parents=True, exist_ok=True)
            logger.info(f"Diretório de feedback configurado: {self.feedback_dir}")
        except Exception as e:
            logger.error(f"Erro ao criar diretório {self.feedback_dir}: {e}")
            raise

    def analyze_errors(self, days: int = 7) -> Dict[str, Any]:
        """
        Analisa erros dos últimos N dias e gera relatório com sugestões.

        Carrega arquivos feedback_*.jsonl dos últimos N dias, agrupa os erros
        por tipo e gera sugestões de melhoria baseadas nos problemas mais comuns.

        Args:
            days: Número de dias para considerar na análise. Padrão: 7

        Returns:
            Dicionário contendo:
            - most_common_errors: Lista de erros mais frequentes com exemplos
            - suggested_improvements: Lista de sugestões priorizadas

        Example:
            {
              "most_common_errors": [
                {"type": "missing_limit", "count": 15, "example_query": "..."},
                {"type": "wrong_column", "count": 8, "example_query": "..."}
              ],
              "suggested_improvements": [
                {"issue": "...", "solution": "...", "priority": "HIGH"}
              ]
            }
        """
        logger.info(f"Iniciando análise de erros dos últimos {days} dias")

        # Calcula data de corte
        cutoff_date = datetime.now() - timedelta(days=days)

        # Agrupa erros por tipo
        error_groups = defaultdict(list)

        try:
            # Processa arquivos de feedback
            feedback_files = list(self.feedback_dir.glob("feedback_*.jsonl"))
            logger.debug(f"Encontrados {len(feedback_files)} arquivos de feedback")

            for feedback_file in feedback_files:
                try:
                    # Extrai data do nome do arquivo (formato: feedback_YYYYMMDD.jsonl)
                    date_str = feedback_file.stem.split('_')[1]
                    file_date = datetime.strptime(date_str, "%Y%m%d")

                    # Verifica se arquivo está dentro do período
                    if file_date < cutoff_date:
                        continue

                    # Processa cada linha do arquivo JSONL
                    with open(feedback_file, 'r', encoding='utf-8') as f:
                        for line_num, line in enumerate(f, 1):
                            try:
                                # Parse da linha JSON
                                feedback_entry = json.loads(line.strip())

                                # Extrai tipo de erro e agrupa
                                issue_type = feedback_entry.get('issue_type', 'unknown')
                                error_groups[issue_type].append(feedback_entry)

                            except json.JSONDecodeError as e:
                                logger.warning(
                                    f"Erro ao parsear linha {line_num} "
                                    f"em {feedback_file.name}: {e}"
                                )
                            except Exception as e:
                                logger.warning(
                                    f"Erro ao processar linha {line_num} "
                                    f"em {feedback_file.name}: {e}"
                                )

                except ValueError as e:
                    logger.warning(f"Nome de arquivo inválido {feedback_file.name}: {e}")
                except Exception as e:
                    logger.error(f"Erro ao processar arquivo {feedback_file.name}: {e}")

            # Monta lista de erros mais comuns
            most_common_errors = []
            for error_type, entries in error_groups.items():
                if entries:  # Apenas se houver ocorrências
                    most_common_errors.append({
                        "type": error_type,
                        "count": len(entries),
                        "example_query": entries[0].get('query', '')
                    })

            # Ordena por contagem (mais frequentes primeiro)
            most_common_errors.sort(key=lambda x: x['count'], reverse=True)

            # Gera sugestões baseadas nos erros
            suggested_improvements = self._generate_suggestions(error_groups)

            result = {
                "most_common_errors": most_common_errors,
                "suggested_improvements": suggested_improvements
            }

            logger.info(
                f"Análise concluída: {len(most_common_errors)} tipos de erro, "
                f"{len(suggested_improvements)} sugestões geradas"
            )

            return result

        except Exception as e:
            logger.error(f"Erro durante análise de erros: {e}")
            return {
                "most_common_errors": [],
                "suggested_improvements": []
            }

    def get_error_types(self) -> List[str]:
        """
        Retorna lista de tipos de erro conhecidos.

        Varre todos os arquivos de feedback e retorna uma lista única
        de todos os tipos de erro (issue_type) encontrados.

        Returns:
            Lista de strings com os tipos de erro conhecidos.

        Example:
            ["missing_limit", "wrong_column", "wrong_segmento", "syntax_error"]
        """
        logger.debug("Coletando tipos de erro conhecidos")

        error_types = set()

        try:
            # Processa todos os arquivos de feedback
            feedback_files = list(self.feedback_dir.glob("feedback_*.jsonl"))

            for feedback_file in feedback_files:
                try:
                    with open(feedback_file, 'r', encoding='utf-8') as f:
                        for line in f:
                            try:
                                feedback_entry = json.loads(line.strip())
                                issue_type = feedback_entry.get('issue_type')
                                if issue_type:
                                    error_types.add(issue_type)
                            except json.JSONDecodeError:
                                continue
                            except Exception:
                                continue

                except Exception as e:
                    logger.warning(f"Erro ao processar {feedback_file.name}: {e}")

            result = sorted(list(error_types))
            logger.info(f"Encontrados {len(result)} tipos de erro conhecidos")
            return result

        except Exception as e:
            logger.error(f"Erro ao coletar tipos de erro: {e}")
            return []

    def _generate_suggestions(self, error_groups: Dict) -> List[Dict]:
        """
        Gera sugestões de melhoria baseadas nos erros mais comuns.

        Analisa os grupos de erros e cria sugestões específicas para cada
        tipo de problema identificado, com priorização baseada na frequência.

        Args:
            error_groups: Dicionário com erros agrupados por tipo

        Returns:
            Lista de dicionários com sugestões priorizadas:
            [
              {"issue": "...", "solution": "...", "priority": "HIGH/MEDIUM/LOW"},
              ...
            ]
        """
        logger.debug("Gerando sugestões de melhoria")

        suggestions = []

        # Define threshold para prioridades
        high_threshold = 10
        medium_threshold = 5

        try:
            # Processa cada tipo de erro
            for error_type, entries in error_groups.items():
                count = len(entries)

                # Determina prioridade baseada na frequência
                if count >= high_threshold:
                    priority = "HIGH"
                elif count >= medium_threshold:
                    priority = "MEDIUM"
                else:
                    priority = "LOW"

                # Gera sugestão específica para cada tipo de erro
                suggestion = None

                if error_type == "missing_limit":
                    suggestion = {
                        "issue": f"Queries sem LIMIT ({count} ocorrências)",
                        "solution": (
                            "Adicionar .head(N) ao final das queries para limitar "
                            "resultados e melhorar performance. Exemplo: df.head(100)"
                        ),
                        "priority": priority
                    }

                elif error_type == "wrong_segmento":
                    suggestion = {
                        "issue": f"Valores incorretos de segmento ({count} ocorrências)",
                        "solution": (
                            "Usar valores exatos de segmento disponíveis no banco. "
                            "Consultar tabela dim_segmentos para valores válidos. "
                            "Exemplos: 'VAREJO', 'ATACADO', 'INDUSTRIA'"
                        ),
                        "priority": priority
                    }

                elif error_type == "wrong_column":
                    suggestion = {
                        "issue": f"Colunas inexistentes ou incorretas ({count} ocorrências)",
                        "solution": (
                            "Validar nomes de colunas usando schema do banco. "
                            "Verificar case-sensitivity e nomenclatura exata das colunas."
                        ),
                        "priority": priority
                    }

                elif error_type == "syntax_error":
                    suggestion = {
                        "issue": f"Erros de sintaxe SQL/Pandas ({count} ocorrências)",
                        "solution": (
                            "Revisar sintaxe das queries geradas. "
                            "Verificar vírgulas, parênteses e palavras-chave SQL."
                        ),
                        "priority": priority
                    }

                elif error_type == "timeout":
                    suggestion = {
                        "issue": f"Queries com timeout ({count} ocorrências)",
                        "solution": (
                            "Otimizar queries adicionando filtros e limites. "
                            "Considerar indexação de colunas frequentemente consultadas."
                        ),
                        "priority": priority
                    }

                else:
                    # Sugestão genérica para tipos desconhecidos
                    suggestion = {
                        "issue": f"Erros do tipo '{error_type}' ({count} ocorrências)",
                        "solution": (
                            "Investigar causa raiz deste tipo de erro e implementar "
                            "tratamento específico."
                        ),
                        "priority": priority
                    }

                if suggestion:
                    suggestions.append(suggestion)

            # Ordena sugestões por prioridade (HIGH > MEDIUM > LOW) e depois por contagem
            priority_order = {"HIGH": 0, "MEDIUM": 1, "LOW": 2}
            suggestions.sort(key=lambda x: priority_order.get(x["priority"], 3))

            logger.info(f"Geradas {len(suggestions)} sugestões de melhoria")
            return suggestions

        except Exception as e:
            logger.error(f"Erro ao gerar sugestões: {e}")
            return []
'''

# Conteúdo do __init__.py
INIT_CONTENT = '''"""
Módulo de aprendizado contínuo do Agent Solution BI.

Este módulo contém componentes para:
- Análise de erros (ErrorAnalyzer)
- Feedback de queries
- Aprendizado e melhoria contínua
"""

from .error_analyzer import ErrorAnalyzer

__all__ = ['ErrorAnalyzer']
'''


def main():
    """Cria os arquivos do ErrorAnalyzer"""

    # Diretório de destino
    learning_dir = Path("core/learning")
    learning_dir.mkdir(parents=True, exist_ok=True)

    # Cria error_analyzer.py
    error_analyzer_file = learning_dir / "error_analyzer.py"
    with open(error_analyzer_file, 'w', encoding='utf-8') as f:
        f.write(ERROR_ANALYZER_CONTENT)
    print(f"Criado: {error_analyzer_file.absolute()}")

    # Cria __init__.py
    init_file = learning_dir / "__init__.py"
    with open(init_file, 'w', encoding='utf-8') as f:
        f.write(INIT_CONTENT)
    print(f"Criado: {init_file.absolute()}")

    print("\nErrorAnalyzer implementado com sucesso!")
    print(f"Total de linhas em error_analyzer.py: {len(ERROR_ANALYZER_CONTENT.splitlines())}")


if __name__ == "__main__":
    main()
