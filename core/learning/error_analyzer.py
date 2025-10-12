"""
Analisador de padrões de erro para identificar problemas recorrentes.
"""

import json
import os
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, List
from collections import defaultdict, Counter


class ErrorAnalyzer:
    """
    Analisa logs de erro e identifica padrões recorrentes
    para melhorar o sistema.
    """

    def __init__(self, logs_dir: str = None):
        """
        Inicializa o analisador de erros.

        Args:
            logs_dir: Diretório com logs de erro (opcional)
        """
        self.logger = logging.getLogger(__name__)

        if logs_dir is None:
            logs_dir = os.path.join(os.getcwd(), "data", "learning")

        self.logs_dir = logs_dir
        self.logger.info(f"✅ ErrorAnalyzer inicializado com logs em {self.logs_dir}")

    def analyze_errors(self, days: int = 7) -> Dict[str, Any]:
        """
        Analisa erros dos últimos N dias e identifica padrões.

        Args:
            days: Número de dias para analisar

        Returns:
            Relatório de análise com erros mais comuns e sugestões
        """
        try:
            error_entries = self._load_error_logs(days)

            if not error_entries:
                return {
                    'total_errors': 0,
                    'most_common_errors': [],
                    'suggested_improvements': [],
                    'queries_with_errors': []
                }

            # Agrupar por tipo de erro
            error_by_type = defaultdict(list)
            for entry in error_entries:
                error_type = entry.get('error_type', 'unknown')
                error_by_type[error_type].append(entry)

            # Encontrar erros mais comuns
            most_common_errors = [
                {
                    'type': error_type,
                    'count': len(cases),
                    'percentage': len(cases) / len(error_entries) * 100,
                    'example_query': cases[0].get('query', ''),
                    'example_error': cases[0].get('error_message', '')
                }
                for error_type, cases in sorted(
                    error_by_type.items(),
                    key=lambda x: len(x[1]),
                    reverse=True
                )
            ]

            # Gerar sugestões baseadas nos erros
            suggestions = self._generate_suggestions(error_by_type)

            # Queries problemáticas
            query_counter = Counter(
                entry.get('query', '') for entry in error_entries
            )
            problematic_queries = [
                {'query': query, 'error_count': count}
                for query, count in query_counter.most_common(10)
            ]

            report = {
                'total_errors': len(error_entries),
                'most_common_errors': most_common_errors[:10],
                'suggested_improvements': suggestions,
                'queries_with_errors': problematic_queries,
                'analysis_period_days': days,
                'timestamp': datetime.now().isoformat()
            }

            self.logger.info(
                f"📊 Análise concluída: {len(error_entries)} erros em {days} dias"
            )

            return report

        except Exception as e:
            self.logger.error(f"❌ Erro ao analisar erros: {e}")
            return {
                'total_errors': 0,
                'error': str(e)
            }

    def _load_error_logs(self, days: int) -> List[Dict]:
        """Carrega logs de erro dos últimos N dias."""
        error_entries = []
        today = datetime.now()

        for i in range(days):
            date = today - timedelta(days=i)
            date_str = date.strftime('%Y%m%d')
            error_file = os.path.join(self.logs_dir, f'error_log_{date_str}.jsonl')

            if os.path.exists(error_file):
                try:
                    with open(error_file, 'r', encoding='utf-8') as f:
                        for line in f:
                            try:
                                entry = json.loads(line.strip())
                                error_entries.append(entry)
                            except json.JSONDecodeError:
                                continue
                except Exception as e:
                    self.logger.warning(f"⚠️ Erro ao ler {error_file}: {e}")

        return error_entries

    def _generate_suggestions(self, error_by_type: Dict) -> List[Dict[str, str]]:
        """
        Gera sugestões de melhoria baseadas nos erros mais comuns.
        """
        suggestions = []

        for error_type, cases in sorted(
            error_by_type.items(),
            key=lambda x: len(x[1]),
            reverse=True
        )[:5]:  # Top 5 tipos de erro

            if error_type == 'KeyError':
                suggestions.append({
                    'issue': 'KeyError frequente - colunas inexistentes',
                    'solution': 'Validar nomes de colunas antes de acessar. Melhorar mapeamento de colunas.',
                    'priority': 'HIGH',
                    'occurrences': len(cases)
                })

            elif error_type == 'TypeError':
                suggestions.append({
                    'issue': 'TypeError - operações inválidas em tipos de dados',
                    'solution': 'Adicionar conversão de tipos explícita no código gerado.',
                    'priority': 'MEDIUM',
                    'occurrences': len(cases)
                })

            elif error_type == 'ValueError':
                suggestions.append({
                    'issue': 'ValueError - valores inválidos em operações',
                    'solution': 'Adicionar validação de valores antes de operações matemáticas.',
                    'priority': 'MEDIUM',
                    'occurrences': len(cases)
                })

            elif error_type == 'AttributeError':
                suggestions.append({
                    'issue': 'AttributeError - métodos inexistentes',
                    'solution': 'Verificar tipo de objeto antes de chamar métodos. Adicionar type hints.',
                    'priority': 'MEDIUM',
                    'occurrences': len(cases)
                })

            elif error_type == 'IndexError':
                suggestions.append({
                    'issue': 'IndexError - acesso fora dos limites',
                    'solution': 'Adicionar verificação de tamanho antes de acessar índices.',
                    'priority': 'LOW',
                    'occurrences': len(cases)
                })

            elif error_type == 'timeout':
                suggestions.append({
                    'issue': 'Timeout - consultas demoram muito',
                    'solution': 'Otimizar queries. Adicionar amostragem de dados grandes.',
                    'priority': 'HIGH',
                    'occurrences': len(cases)
                })

            elif 'missing_limit' in str(cases[0].get('error_message', '')).lower():
                suggestions.append({
                    'issue': 'Código não limita resultados quando deveria',
                    'solution': 'Melhorar detecção de "top N" e adicionar .head() automaticamente.',
                    'priority': 'HIGH',
                    'occurrences': len(cases)
                })

        return suggestions

    def get_error_trends(self, days: int = 30) -> Dict[str, List]:
        """
        Analisa tendências de erro ao longo do tempo.

        Args:
            days: Número de dias para analisar

        Returns:
            Tendências por tipo de erro ao longo do tempo
        """
        try:
            today = datetime.now()
            trends = defaultdict(lambda: defaultdict(int))

            for i in range(days):
                date = today - timedelta(days=i)
                date_str = date.strftime('%Y%m%d')
                counter_file = os.path.join(self.logs_dir, f'error_counts_{date_str}.json')

                if os.path.exists(counter_file):
                    try:
                        with open(counter_file, 'r', encoding='utf-8') as f:
                            counts = json.load(f)
                            for error_type, count in counts.items():
                                trends[error_type][date_str] = count
                    except Exception as e:
                        self.logger.warning(f"⚠️ Erro ao ler {counter_file}: {e}")

            # Converter para formato mais legível
            formatted_trends = {}
            for error_type, date_counts in trends.items():
                formatted_trends[error_type] = [
                    {'date': date, 'count': count}
                    for date, count in sorted(date_counts.items())
                ]

            return formatted_trends

        except Exception as e:
            self.logger.error(f"❌ Erro ao calcular tendências: {e}")
            return {}

    def generate_report(self, days: int = 7, output_file: str = None) -> str:
        """
        Gera relatório completo de análise de erros.

        Args:
            days: Número de dias para analisar
            output_file: Arquivo de saída (opcional)

        Returns:
            Caminho do arquivo gerado ou string com relatório
        """
        analysis = self.analyze_errors(days)

        report = f"""
# 📊 RELATÓRIO DE ANÁLISE DE ERROS
**Período:** Últimos {days} dias
**Data:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

---

## 📈 ESTATÍSTICAS GERAIS
- **Total de erros:** {analysis['total_errors']}

---

## 🔴 ERROS MAIS COMUNS

"""

        for i, error in enumerate(analysis['most_common_errors'][:10], 1):
            report += f"""
### {i}. {error['type']}
- **Ocorrências:** {error['count']} ({error['percentage']:.1f}%)
- **Exemplo de query:** "{error['example_query']}"
- **Mensagem:** {error['example_error'][:200]}...

"""

        report += """
---

## 💡 SUGESTÕES DE MELHORIA

"""

        for i, suggestion in enumerate(analysis['suggested_improvements'], 1):
            report += f"""
### {i}. {suggestion['issue']}
- **Solução:** {suggestion['solution']}
- **Prioridade:** {suggestion['priority']}
- **Ocorrências:** {suggestion['occurrences']}

"""

        report += """
---

## ⚠️ QUERIES PROBLEMÁTICAS

"""

        for i, query_info in enumerate(analysis['queries_with_errors'][:10], 1):
            report += f"{i}. \"{query_info['query']}\" - {query_info['error_count']} erros\n"

        # Salvar em arquivo se especificado
        if output_file:
            try:
                with open(output_file, 'w', encoding='utf-8') as f:
                    f.write(report)
                self.logger.info(f"✅ Relatório salvo em {output_file}")
                return output_file
            except Exception as e:
                self.logger.error(f"❌ Erro ao salvar relatório: {e}")

        return report
