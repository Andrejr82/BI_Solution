"""
Gerador de Relatório Executivo
Agent_Solution_BI - BI Agent (Caçulinha BI)

Gera relatório executivo resumido com métricas principais.
"""

import json
from pathlib import Path
from datetime import datetime


def gerar_relatorio_executivo():
    """Gera relatório executivo baseado no último relatório de validação"""

    reports_dir = Path(r"C:\Users\André\Documents\Agent_Solution_BI\reports")

    # Encontrar último relatório JSON
    json_reports = sorted(reports_dir.glob("data_integrity_report_*.json"))

    if not json_reports:
        print("Nenhum relatório de validação encontrado.")
        print("Execute primeiro: python scripts/validacao_integridade_dados.py")
        return None

    latest_report_file = json_reports[-1]
    print(f"Usando relatório: {latest_report_file.name}\n")

    # Carregar dados
    with open(latest_report_file, 'r', encoding='utf-8') as f:
        data = json.load(f)

    # Extrair métricas principais
    health_score = data.get("health_score", 0)
    kpis = data.get("kpis", {})
    issues = data.get("issues", [])
    recommendations = data.get("recommendations", [])

    # Classificar status
    if health_score >= 90:
        status = "EXCELENTE"
        status_icon = "✅"
    elif health_score >= 75:
        status = "BOM"
        status_icon = "✔️"
    elif health_score >= 60:
        status = "REGULAR"
        status_icon = "⚠️"
    else:
        status = "CRITICO"
        status_icon = "❌"

    # Construir relatório executivo
    report = f"""
╔══════════════════════════════════════════════════════════════════════╗
║                    RELATÓRIO EXECUTIVO - BI AGENT                    ║
║                    Agent_Solution_BI (Caçulinha BI)                  ║
╚══════════════════════════════════════════════════════════════════════╝

Data/Hora: {datetime.now().strftime("%d/%m/%Y %H:%M:%S")}

┌─────────────────────────────────────────────────────────────────────┐
│ HEALTH SCORE: {health_score}/100 {status_icon}
│ STATUS: {status}
└─────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────┐
│ METRICAS PRINCIPAIS                                                  │
├─────────────────────────────────────────────────────────────────────┤
│ Taxa de Sucesso        : {kpis.get('success_rate_percent', 0):>6.2f}%                        │
│ Taxa de Erro           : {kpis.get('error_rate_percent', 0):>6.2f}%                        │
│ Qualidade dos Dados    : {kpis.get('data_quality_score', 0):>6.2f}%                        │
│ Total de Queries       : {kpis.get('total_queries', 0):>8,}                          │
│ Total de Linhas        : {kpis.get('total_data_rows', 0):>8,}                          │
│ Tamanho Parquet        : {kpis.get('total_parquet_size_mb', 0):>8.2f} MB                      │
│ Entradas de Cache      : {kpis.get('cache_entries', 0):>8,}                          │
│ Tamanho de Cache       : {kpis.get('cache_size_mb', 0):>8.2f} MB                      │
└─────────────────────────────────────────────────────────────────────┘
"""

    # Adicionar problemas críticos se houver
    critical_issues = [i for i in issues if i.get("severity") == "CRITICAL"]
    if critical_issues:
        report += f"""
┌─────────────────────────────────────────────────────────────────────┐
│ PROBLEMAS CRITICOS ({len(critical_issues)})                                              │
├─────────────────────────────────────────────────────────────────────┤
"""
        for issue in critical_issues[:3]:  # Mostrar no máximo 3
            category = issue.get("category", "Geral")
            message = issue.get("message", "")[:55]
            report += f"│ [{category}] {message:<55} │\n"

        if len(critical_issues) > 3:
            report += f"│ ... e mais {len(critical_issues) - 3} problemas                                        │\n"

        report += "└─────────────────────────────────────────────────────────────────────┘\n"

    # Adicionar warnings se houver
    warning_issues = [i for i in issues if i.get("severity") == "WARNING"]
    if warning_issues:
        report += f"""
┌─────────────────────────────────────────────────────────────────────┐
│ AVISOS ({len(warning_issues)})                                                      │
├─────────────────────────────────────────────────────────────────────┤
"""
        for issue in warning_issues[:3]:  # Mostrar no máximo 3
            category = issue.get("category", "Geral")
            message = issue.get("message", "")[:55]
            report += f"│ [{category}] {message:<55} │\n"

        if len(warning_issues) > 3:
            report += f"│ ... e mais {len(warning_issues) - 3} avisos                                         │\n"

        report += "└─────────────────────────────────────────────────────────────────────┘\n"

    # Adicionar recomendações de alta prioridade
    high_priority = [r for r in recommendations if r.get("priority") == "HIGH"]
    if high_priority:
        report += f"""
┌─────────────────────────────────────────────────────────────────────┐
│ ACOES URGENTES ({len(high_priority)})                                                │
├─────────────────────────────────────────────────────────────────────┤
"""
        for i, rec in enumerate(high_priority[:3], 1):
            action = rec.get("action", "")[:60]
            report += f"│ {i}. {action:<65} │\n"

        if len(high_priority) > 3:
            report += f"│ ... e mais {len(high_priority) - 3} ações                                           │\n"

        report += "└─────────────────────────────────────────────────────────────────────┘\n"

    # Rodapé
    report += f"""
┌─────────────────────────────────────────────────────────────────────┐
│ Para relatório completo, consulte:                                  │
│ {latest_report_file.name:<68} │
└─────────────────────────────────────────────────────────────────────┘

"""

    # Imprimir
    print(report)

    # Salvar
    exec_report_file = reports_dir / f"executive_summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
    with open(exec_report_file, 'w', encoding='utf-8') as f:
        f.write(report)

    print(f"Relatório executivo salvo em: {exec_report_file}")

    return report


def main():
    """Função principal"""
    gerar_relatorio_executivo()


if __name__ == "__main__":
    main()
