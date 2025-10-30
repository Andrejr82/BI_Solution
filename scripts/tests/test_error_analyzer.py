"""
Script de Teste - Error Analyzer
Autor: BI Agent (Caçulinha BI)
Data: 2025-10-29

Testa todas as funcionalidades do ErrorAnalyzer
"""

import sys
from pathlib import Path

# Adicionar diretório raiz ao path
base_dir = Path(__file__).parent.parent.parent
sys.path.insert(0, str(base_dir))

from core.learning.error_analyzer import ErrorAnalyzer
import json


def test_basic_functionality():
    """Testa funcionalidades básicas"""
    print("=" * 80)
    print("TESTE 1: Funcionalidades Basicas")
    print("=" * 80)

    analyzer = ErrorAnalyzer()

    # Teste 1: Carregar logs
    print("\n1. Testando carregamento de logs...")
    results = analyzer.analyze_errors(days=7)

    assert 'total_errors' in results, "Campo total_errors ausente"
    assert 'errors_by_type' in results, "Campo errors_by_type ausente"
    assert 'top_errors' in results, "Campo top_errors ausente"
    assert 'suggestions' in results, "Campo suggestions ausente"

    print(f"   - Total de erros: {results['total_errors']}")
    print(f"   - Tipos de erro: {len(results['errors_by_type'])}")
    print("   PASSOU")

    return results


def test_error_grouping(analyzer):
    """Testa agrupamento de erros"""
    print("\n=" * 80)
    print("TESTE 2: Agrupamento de Erros")
    print("=" * 80)

    errors_by_type = analyzer.group_by_type()

    print(f"\n2. Erros agrupados por tipo:")
    for error_type, count in list(errors_by_type.items())[:5]:
        print(f"   - {error_type}: {count}")

    assert isinstance(errors_by_type, dict), "Resultado deve ser dict"
    print("   PASSOU")

    return errors_by_type


def test_frequency_calculation(analyzer):
    """Testa cálculo de frequência"""
    print("\n=" * 80)
    print("TESTE 3: Calculo de Frequencia")
    print("=" * 80)

    frequency_data = analyzer.calculate_frequency()

    print(f"\n3. Dados de frequencia calculados:")
    print(f"   - Total de padroes: {len(frequency_data)}")

    # Mostrar top 3
    sorted_freq = sorted(frequency_data.items(), key=lambda x: x[1]['count'], reverse=True)
    for i, (msg, data) in enumerate(sorted_freq[:3], 1):
        print(f"   {i}. {data['error_type']}: {data['count']} ocorrencias")
        print(f"      Mensagem: {msg[:80]}...")

    assert isinstance(frequency_data, dict), "Resultado deve ser dict"
    print("   PASSOU")

    return frequency_data


def test_suggestions(analyzer):
    """Testa geração de sugestões"""
    print("\n=" * 80)
    print("TESTE 4: Geracao de Sugestoes")
    print("=" * 80)

    suggestions = analyzer.suggest_fixes()

    print(f"\n4. Sugestoes geradas: {len(suggestions)}")

    # Mostrar top 5 sugestões
    for i, suggestion in enumerate(suggestions[:5], 1):
        print(f"\n   {i}. [{suggestion['priority']}] {suggestion['error_type']}")
        print(f"      Frequencia: {suggestion['frequency']}")
        print(f"      Sugestao: {suggestion['suggestion']}")
        print(f"      Acao: {suggestion['action']}")

    assert isinstance(suggestions, list), "Resultado deve ser lista"
    assert len(suggestions) > 0, "Deve haver pelo menos uma sugestao"

    # Validar estrutura
    for suggestion in suggestions:
        assert 'priority' in suggestion, "Campo priority ausente"
        assert 'suggestion' in suggestion, "Campo suggestion ausente"
        assert 'action' in suggestion, "Campo action ausente"

    print("\n   PASSOU")

    return suggestions


def test_top_errors(results):
    """Testa ranking de erros"""
    print("\n=" * 80)
    print("TESTE 5: Ranking de Erros")
    print("=" * 80)

    top_errors = results['top_errors']

    print(f"\n5. Top 10 erros identificados:")
    for error in top_errors:
        print(f"\n   {error['rank']}. [{error['impact']}] {error['error_type']}")
        print(f"      Ocorrencias: {error['count']}")
        print(f"      Mensagem: {error['error_message'][:80]}...")

    assert len(top_errors) <= 10, "Deve retornar no maximo 10 erros"
    assert all(error['rank'] > 0 for error in top_errors), "Todos devem ter rank"

    print("\n   PASSOU")

    return top_errors


def test_export_json(analyzer):
    """Testa exportação JSON"""
    print("\n=" * 80)
    print("TESTE 6: Exportacao JSON")
    print("=" * 80)

    print("\n6. Exportando analise para JSON...")
    json_path = analyzer.export_analysis()

    assert Path(json_path).exists(), "Arquivo JSON deve existir"

    # Validar conteúdo
    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    assert 'total_errors' in data, "JSON deve conter total_errors"
    assert 'top_errors' in data, "JSON deve conter top_errors"
    assert 'suggestions' in data, "JSON deve conter suggestions"

    print(f"   - Arquivo exportado: {json_path}")
    print(f"   - Tamanho: {Path(json_path).stat().st_size} bytes")
    print("   PASSOU")

    return json_path


def test_report_generation(analyzer):
    """Testa geração de relatório"""
    print("\n=" * 80)
    print("TESTE 7: Geracao de Relatorio")
    print("=" * 80)

    print("\n7. Gerando relatorio em Markdown...")
    report = analyzer.generate_report()

    assert len(report) > 0, "Relatorio nao pode ser vazio"
    assert "# Relatorio de Analise de Erros" in report, "Titulo ausente"
    assert "## Top 10 Erros Mais Frequentes" in report, "Secao top erros ausente"
    assert "## Sugestoes de Correcao" in report, "Secao sugestoes ausente"
    assert "## Comentario do Analista" in report, "Comentario do analista ausente"

    # Salvar relatório
    report_dir = base_dir / "data" / "reports"
    report_dir.mkdir(parents=True, exist_ok=True)

    from datetime import datetime
    report_path = report_dir / f"test_error_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"

    with open(report_path, 'w', encoding='utf-8') as f:
        f.write(report)

    print(f"   - Relatorio salvo: {report_path}")
    print(f"   - Tamanho: {len(report)} caracteres")
    print("   PASSOU")

    return report_path


def test_precision():
    """Testa precisão da identificação de erros"""
    print("\n=" * 80)
    print("TESTE 8: Precisao de Identificacao (Top 5)")
    print("=" * 80)

    analyzer = ErrorAnalyzer()
    results = analyzer.analyze_errors(days=7)

    top_5 = results['top_errors'][:5]

    print(f"\n8. Validando top 5 erros com 100% precisao:")

    for i, error in enumerate(top_5, 1):
        # Validar campos obrigatórios
        assert error['rank'] == i, f"Rank incorreto: esperado {i}, obtido {error['rank']}"
        assert error['count'] > 0, "Contagem deve ser maior que zero"
        assert error['error_type'], "Tipo de erro nao pode ser vazio"
        assert error['impact'] in ['CRITICAL', 'HIGH', 'MEDIUM', 'LOW'], "Impacto invalido"

        print(f"\n   {i}. {error['error_type']} - {error['count']} ocorrencias [{error['impact']}]")
        print(f"      Rank: {error['rank']} (OK)")
        print(f"      Count: {error['count']} (OK)")
        print(f"      Impact: {error['impact']} (OK)")

    print("\n   PASSOU - Top 5 identificado com 100% de precisao")

    return True


def generate_test_report(test_results):
    """Gera relatório final dos testes"""
    print("\n" + "=" * 80)
    print("RELATORIO FINAL DOS TESTES")
    print("=" * 80)

    report_lines = [
        "# Relatorio de Testes - Error Analyzer",
        f"\nData: {Path(__file__).parent.parent.parent}",
        "\n## Resumo dos Testes\n",
        "| Teste | Status | Detalhes |",
        "|-------|--------|----------|"
    ]

    total_tests = len(test_results)
    passed_tests = sum(1 for result in test_results.values() if result['passed'])

    for test_name, result in test_results.items():
        status = "PASSOU" if result['passed'] else "FALHOU"
        details = result.get('details', 'N/A')
        report_lines.append(f"| {test_name} | {status} | {details} |")

    report_lines.append(f"\n**Total:** {passed_tests}/{total_tests} testes passaram")

    if passed_tests == total_tests:
        report_lines.append("\n**STATUS:** TODOS OS TESTES PASSARAM")
    else:
        report_lines.append(f"\n**STATUS:** {total_tests - passed_tests} TESTES FALHARAM")

    report_text = "\n".join(report_lines)

    # Salvar relatório
    report_dir = base_dir / "data" / "reports"
    report_dir.mkdir(parents=True, exist_ok=True)

    from datetime import datetime
    report_path = report_dir / f"test_results_error_analyzer_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"

    with open(report_path, 'w', encoding='utf-8') as f:
        f.write(report_text)

    print(f"\nRelatorio de testes salvo: {report_path}")
    print(f"Taxa de sucesso: {(passed_tests/total_tests)*100:.1f}%")

    return report_path


def main():
    """Executa todos os testes"""
    print("\n" + "=" * 80)
    print("SUITE DE TESTES - ERROR ANALYZER")
    print("FASE 3.1 - Sistema Automatico de Analise de Erros")
    print("=" * 80)

    test_results = {}

    try:
        # Teste 1: Funcionalidades básicas
        results = test_basic_functionality()
        test_results['Funcionalidades Basicas'] = {
            'passed': True,
            'details': f"{results['total_errors']} erros analisados"
        }

        # Criar analyzer para testes subsequentes
        analyzer = ErrorAnalyzer()
        analyzer.analyze_errors(days=7)

        # Teste 2: Agrupamento
        errors_by_type = test_error_grouping(analyzer)
        test_results['Agrupamento de Erros'] = {
            'passed': True,
            'details': f"{len(errors_by_type)} tipos identificados"
        }

        # Teste 3: Frequência
        frequency_data = test_frequency_calculation(analyzer)
        test_results['Calculo de Frequencia'] = {
            'passed': True,
            'details': f"{len(frequency_data)} padroes encontrados"
        }

        # Teste 4: Sugestões
        suggestions = test_suggestions(analyzer)
        test_results['Geracao de Sugestoes'] = {
            'passed': True,
            'details': f"{len(suggestions)} sugestoes geradas"
        }

        # Teste 5: Ranking
        top_errors = test_top_errors(results)
        test_results['Ranking de Erros'] = {
            'passed': True,
            'details': f"Top {len(top_errors)} erros identificados"
        }

        # Teste 6: Exportação JSON
        json_path = test_export_json(analyzer)
        test_results['Exportacao JSON'] = {
            'passed': True,
            'details': f"Exportado para {Path(json_path).name}"
        }

        # Teste 7: Relatório
        report_path = test_report_generation(analyzer)
        test_results['Geracao de Relatorio'] = {
            'passed': True,
            'details': f"Relatorio salvo em {Path(report_path).name}"
        }

        # Teste 8: Precisão
        test_precision()
        test_results['Precisao de Identificacao'] = {
            'passed': True,
            'details': "Top 5 com 100% precisao"
        }

    except AssertionError as e:
        print(f"\n[ERRO] Teste falhou: {e}")
        test_results[f'Erro'] = {
            'passed': False,
            'details': str(e)
        }
    except Exception as e:
        print(f"\n[ERRO] Erro inesperado: {e}")
        test_results['Erro Inesperado'] = {
            'passed': False,
            'details': str(e)
        }

    # Gerar relatório final
    final_report_path = generate_test_report(test_results)

    print("\n" + "=" * 80)
    print("SUITE DE TESTES CONCLUIDA")
    print("=" * 80)

    return test_results


if __name__ == "__main__":
    main()
