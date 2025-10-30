"""
Executor do Sistema de Análise de Erros
FASE 3.1 - Sistema Automático de Análise de Erros LLM

Autor: BI Agent (Caçulinha BI)
Data: 2025-10-29
"""

import sys
import json
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Any
from collections import defaultdict, Counter
import re


class ErrorAnalyzer:
    """Analisador automático de erros do sistema"""

    def __init__(self, learning_dir: str = None):
        """Inicializa o analisador de erros"""
        if learning_dir is None:
            base_dir = Path(__file__).parent.parent
            learning_dir = base_dir / "data" / "learning"

        self.learning_dir = Path(learning_dir)
        self.errors_data = []
        self.analysis_results = {}

    def analyze_errors(self, days: int = 7) -> Dict[str, Any]:
        """Analisa logs de erro dos últimos N dias"""
        print(f"Analisando erros dos ultimos {days} dias...")

        # Carregar logs de erro
        self.errors_data = self._load_error_logs(days)

        if not self.errors_data:
            print("Nenhum erro encontrado nos logs")
            return {
                "total_errors": 0,
                "period_days": days,
                "analysis_date": datetime.now().isoformat(),
                "errors_by_type": {},
                "top_errors": [],
                "suggestions": []
            }

        # Executar análises
        errors_by_type = self.group_by_type()
        frequency_data = self.calculate_frequency()
        severity_data = self._calculate_severity()
        suggestions = self.suggest_fixes()

        # Compilar resultados
        self.analysis_results = {
            "total_errors": len(self.errors_data),
            "period_days": days,
            "analysis_date": datetime.now().isoformat(),
            "errors_by_type": errors_by_type,
            "frequency_data": frequency_data,
            "severity_data": severity_data,
            "top_errors": self._get_top_errors(10),
            "suggestions": suggestions,
            "error_timeline": self._get_error_timeline()
        }

        print(f"Analise concluida: {len(self.errors_data)} erros analisados")
        return self.analysis_results

    def _load_error_logs(self, days: int) -> List[Dict]:
        """Carrega logs de erro dos últimos N dias"""
        errors = []
        cutoff_date = datetime.now() - timedelta(days=days)

        # Procurar arquivos de log de erro
        pattern = "error_log_*.jsonl"
        log_files = list(self.learning_dir.glob(pattern))

        print(f"Encontrados {len(log_files)} arquivos de log")

        for log_file in log_files:
            try:
                # Extrair data do nome do arquivo
                date_str = log_file.stem.replace("error_log_", "")
                file_date = datetime.strptime(date_str, "%Y%m%d")

                # Verificar se está no período
                if file_date < cutoff_date:
                    continue

                # Ler arquivo JSONL
                with open(log_file, 'r', encoding='utf-8') as f:
                    for line in f:
                        try:
                            error_entry = json.loads(line.strip())
                            error_entry['log_file'] = log_file.name
                            errors.append(error_entry)
                        except json.JSONDecodeError:
                            continue

            except Exception as e:
                print(f"Erro ao processar {log_file.name}: {e}")
                continue

        return errors

    def group_by_type(self) -> Dict[str, int]:
        """Agrupa erros por tipo"""
        type_counter = Counter()

        for error in self.errors_data:
            error_type = error.get('error_type', 'Unknown')
            type_counter[error_type] += 1

        return dict(type_counter.most_common())

    def calculate_frequency(self) -> Dict[str, Any]:
        """Calcula frequência de cada erro"""
        error_messages = defaultdict(list)

        for error in self.errors_data:
            raw_msg = error.get('error_message', '')
            normalized = self._normalize_error_message(raw_msg)

            error_messages[normalized].append({
                'timestamp': error.get('timestamp'),
                'error_type': error.get('error_type'),
                'query': error.get('query', ''),
                'raw_message': raw_msg
            })

        frequency_data = {}
        for normalized_msg, occurrences in error_messages.items():
            frequency_data[normalized_msg] = {
                'count': len(occurrences),
                'error_type': occurrences[0]['error_type'],
                'first_seen': min(o['timestamp'] for o in occurrences),
                'last_seen': max(o['timestamp'] for o in occurrences),
                'sample_query': occurrences[0]['query'][:100] if occurrences[0]['query'] else '',
                'occurrences': occurrences
            }

        return frequency_data

    def _normalize_error_message(self, message: str) -> str:
        """Normaliza mensagem de erro removendo dados específicos"""
        normalized = re.sub(r'\d+', 'N', message)
        normalized = re.sub(r'[A-Za-z]:\\[^\s]+', 'PATH', normalized)
        normalized = re.sub(r'/[^\s]+/', 'PATH/', normalized)
        normalized = re.sub(r"'[^']{20,}'", "'VALUE'", normalized)
        return normalized.strip()

    def _calculate_severity(self) -> Dict[str, List[Dict]]:
        """Calcula severidade dos erros"""
        severity_levels = {
            'CRITICAL': [],
            'HIGH': [],
            'MEDIUM': [],
            'LOW': []
        }

        frequency_data = self.calculate_frequency()

        for normalized_msg, data in frequency_data.items():
            count = data['count']
            error_type = data['error_type']

            if error_type in ['RuntimeError', 'SystemError'] or count > 20:
                level = 'CRITICAL'
            elif count > 10:
                level = 'HIGH'
            elif count >= 3:
                level = 'MEDIUM'
            else:
                level = 'LOW'

            severity_levels[level].append({
                'message': normalized_msg,
                'count': count,
                'error_type': error_type,
                'first_seen': data['first_seen'],
                'last_seen': data['last_seen']
            })

        for level in severity_levels:
            severity_levels[level].sort(key=lambda x: x['count'], reverse=True)

        return severity_levels

    def suggest_fixes(self) -> List[Dict[str, Any]]:
        """Gera sugestões automáticas de correção"""
        suggestions = []
        frequency_data = self.calculate_frequency()

        fix_patterns = [
            {
                'pattern': r'KeyError.*column',
                'suggestion': 'Validar existencia da coluna antes de acessar. Usar column_validator.py',
                'priority': 'HIGH',
                'action': 'Implementar validacao de colunas no inicio da query'
            },
            {
                'pattern': r'KeyError.*UNE_NOME',
                'suggestion': 'Corrigir mapeamento de coluna UNE_NOME. Verificar une_mapping.py',
                'priority': 'CRITICAL',
                'action': 'Atualizar mapeamento de colunas em config/une_mapping.py'
            },
            {
                'pattern': r'ValueError.*convert',
                'suggestion': 'Implementar conversao de tipos com tratamento de erro',
                'priority': 'MEDIUM',
                'action': 'Adicionar try-except para conversoes de tipo'
            },
            {
                'pattern': r'RuntimeError.*lazy',
                'suggestion': 'Corrigir uso de LazyFrame. Usar .collect() quando necessario',
                'priority': 'HIGH',
                'action': 'Revisar pipeline Polars e adicionar .collect() apropriadamente'
            },
            {
                'pattern': r'AttributeError.*NoneType',
                'suggestion': 'Adicionar verificacao de None antes de acessar atributos',
                'priority': 'MEDIUM',
                'action': 'Implementar guards com if obj is not None'
            }
        ]

        for normalized_msg, data in frequency_data.items():
            count = data['count']
            error_type = data['error_type']

            matched_fix = None
            for fix_pattern in fix_patterns:
                if re.search(fix_pattern['pattern'], normalized_msg, re.IGNORECASE):
                    matched_fix = fix_pattern
                    break

            if matched_fix:
                suggestions.append({
                    'error_message': normalized_msg[:200],
                    'error_type': error_type,
                    'frequency': count,
                    'priority': matched_fix['priority'],
                    'suggestion': matched_fix['suggestion'],
                    'action': matched_fix['action'],
                    'affected_queries': len(data['occurrences'])
                })
            else:
                suggestions.append({
                    'error_message': normalized_msg[:200],
                    'error_type': error_type,
                    'frequency': count,
                    'priority': 'MEDIUM' if count > 5 else 'LOW',
                    'suggestion': f'Investigar erro do tipo {error_type}',
                    'action': 'Adicionar tratamento especifico para este caso',
                    'affected_queries': len(data['occurrences'])
                })

        priority_order = {'CRITICAL': 0, 'HIGH': 1, 'MEDIUM': 2, 'LOW': 3}
        suggestions.sort(key=lambda x: (priority_order[x['priority']], -x['frequency']))

        return suggestions

    def _get_top_errors(self, n: int = 10) -> List[Dict[str, Any]]:
        """Retorna os top N erros mais frequentes"""
        frequency_data = self.calculate_frequency()

        top_errors = []
        for normalized_msg, data in frequency_data.items():
            top_errors.append({
                'rank': 0,
                'error_message': normalized_msg,
                'error_type': data['error_type'],
                'count': data['count'],
                'first_seen': data['first_seen'],
                'last_seen': data['last_seen'],
                'sample_query': data['sample_query'],
                'impact': self._calculate_impact(data)
            })

        top_errors.sort(key=lambda x: x['count'], reverse=True)

        for i, error in enumerate(top_errors[:n], 1):
            error['rank'] = i

        return top_errors[:n]

    def _calculate_impact(self, error_data: Dict) -> str:
        """Calcula o impacto do erro"""
        count = error_data['count']

        if count >= 20:
            return 'CRITICAL'
        elif count >= 10:
            return 'HIGH'
        elif count >= 5:
            return 'MEDIUM'
        else:
            return 'LOW'

    def _get_error_timeline(self) -> Dict[str, int]:
        """Retorna timeline de erros por dia"""
        timeline = defaultdict(int)

        for error in self.errors_data:
            timestamp = error.get('timestamp', '')
            try:
                date = datetime.fromisoformat(timestamp).date().isoformat()
                timeline[date] += 1
            except:
                continue

        return dict(sorted(timeline.items()))

    def export_analysis(self, output_file: str = None) -> str:
        """Exporta análise para arquivo JSON"""
        if output_file is None:
            output_file = self.learning_dir / "error_analysis.json"

        output_path = Path(output_file)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(self.analysis_results, f, indent=2, ensure_ascii=False)

        print(f"Analise exportada para: {output_path}")
        return str(output_path)

    def generate_report(self) -> str:
        """Gera relatório em formato Markdown"""
        if not self.analysis_results:
            return "Nenhuma analise disponivel. Execute analyze_errors() primeiro."

        report = []
        report.append("# Relatorio de Analise de Erros - FASE 3.1")
        report.append(f"\nData da Analise: {self.analysis_results['analysis_date']}")
        report.append(f"Periodo: ultimos {self.analysis_results['period_days']} dias")
        report.append(f"Total de Erros: {self.analysis_results['total_errors']}")

        # Sumário por tipo
        report.append("\n## Erros por Tipo\n")
        report.append("| Tipo | Quantidade | Percentual |")
        report.append("|------|------------|------------|")

        total = self.analysis_results['total_errors']
        for error_type, count in self.analysis_results['errors_by_type'].items():
            pct = (count / total * 100) if total > 0 else 0
            report.append(f"| {error_type} | {count} | {pct:.1f}% |")

        # Top 10 Erros
        report.append("\n## Top 10 Erros Mais Frequentes\n")
        for error in self.analysis_results['top_errors']:
            report.append(f"\n### {error['rank']}. {error['error_type']} (Impacto: {error['impact']})")
            report.append(f"- **Ocorrencias:** {error['count']}")
            report.append(f"- **Primeira ocorrencia:** {error['first_seen']}")
            report.append(f"- **Ultima ocorrencia:** {error['last_seen']}")
            report.append(f"- **Mensagem:** `{error['error_message'][:150]}...`")
            if error['sample_query']:
                report.append(f"- **Query exemplo:** `{error['sample_query']}`")

        # Sugestões de Correção
        report.append("\n## Sugestoes de Correcao (Top 10)\n")
        report.append("| Prioridade | Erro | Frequencia | Sugestao |")
        report.append("|------------|------|------------|----------|")

        for suggestion in self.analysis_results['suggestions'][:10]:
            error_msg = suggestion['error_message'][:40] + "..."
            sugg = suggestion['suggestion'][:50] + "..."

            report.append(
                f"| {suggestion['priority']} | "
                f"{suggestion['error_type']} | "
                f"{suggestion['frequency']} | "
                f"{sugg} |"
            )

        # Timeline
        report.append("\n## Timeline de Erros\n")
        report.append("| Data | Quantidade |")
        report.append("|------|------------|")

        for date, count in self.analysis_results['error_timeline'].items():
            report.append(f"| {date} | {count} |")

        # Comentário do Analista
        report.append("\n## Comentario do Analista\n")
        report.append(self._generate_analyst_comment())

        return "\n".join(report)

    def _generate_analyst_comment(self) -> str:
        """Gera comentário automático do analista"""
        comments = []

        total = self.analysis_results['total_errors']
        top_error = self.analysis_results['top_errors'][0] if self.analysis_results['top_errors'] else None
        critical_suggestions = [s for s in self.analysis_results['suggestions'] if s['priority'] == 'CRITICAL']

        comments.append(f"Total de {total} erros analisados no periodo.")

        if top_error:
            comments.append(
                f"\nO erro mais frequente e do tipo **{top_error['error_type']}** "
                f"com {top_error['count']} ocorrencias, representando "
                f"{(top_error['count'] / total * 100):.1f}% do total."
            )

        if critical_suggestions:
            comments.append(
                f"\n**ATENCAO:** Foram identificados {len(critical_suggestions)} erros criticos "
                f"que devem ser corrigidos imediatamente."
            )

        timeline = self.analysis_results['error_timeline']
        if len(timeline) >= 2:
            dates = sorted(timeline.keys())
            first_day_count = timeline[dates[0]]
            last_day_count = timeline[dates[-1]]

            if last_day_count > first_day_count * 1.5:
                comments.append(
                    f"\n**TENDENCIA:** Os erros estao AUMENTANDO. "
                    f"De {first_day_count} erros em {dates[0]} para {last_day_count} em {dates[-1]}."
                )
            elif last_day_count < first_day_count * 0.5:
                comments.append(
                    f"\n**TENDENCIA:** Os erros estao DIMINUINDO. "
                    f"De {first_day_count} erros em {dates[0]} para {last_day_count} em {dates[-1]}."
                )

        comments.append("\n**Recomendacoes:**")
        comments.append("1. Priorizar correcao dos erros marcados como CRITICAL")
        comments.append("2. Implementar validacoes preventivas para erros de tipo KeyError")
        comments.append("3. Adicionar testes unitarios para casos de erro mais frequentes")
        comments.append("4. Configurar alertas para erros que ultrapassem 10 ocorrencias/dia")

        return "\n".join(comments)


def main():
    """Função principal"""
    print("=" * 80)
    print("Sistema Automatico de Analise de Erros - FASE 3.1")
    print("=" * 80)

    analyzer = ErrorAnalyzer()
    results = analyzer.analyze_errors(days=7)

    # Exportar JSON
    json_path = analyzer.export_analysis()
    print(f"\nJSON exportado: {json_path}")

    # Gerar relatório
    report = analyzer.generate_report()

    base_dir = Path(__file__).parent.parent
    report_dir = base_dir / "data" / "reports"
    report_dir.mkdir(parents=True, exist_ok=True)

    report_path = report_dir / f"error_analysis_fase31_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write(report)

    print(f"Relatorio exportado: {report_path}")

    # Exibir resumo
    print("\n" + "=" * 80)
    print("RESUMO DA ANALISE")
    print("=" * 80)
    print(f"Total de erros: {results['total_errors']}")
    print(f"Tipos diferentes: {len(results['errors_by_type'])}")
    print(f"Sugestoes geradas: {len(results['suggestions'])}")

    print("\nTop 5 Erros:")
    for i, error in enumerate(results['top_errors'][:5], 1):
        print(f"{i}. [{error['impact']}] {error['error_type']} - {error['count']} ocorrencias")

    print("\nTop 5 Sugestoes (CRITICAL/HIGH):")
    critical_high = [s for s in results['suggestions'] if s['priority'] in ['CRITICAL', 'HIGH']]
    for i, suggestion in enumerate(critical_high[:5], 1):
        print(f"{i}. [{suggestion['priority']}] {suggestion['error_type']}")
        print(f"   Frequencia: {suggestion['frequency']}")
        print(f"   Sugestao: {suggestion['suggestion']}")
        print(f"   Acao: {suggestion['action']}\n")

    return results


if __name__ == "__main__":
    main()
