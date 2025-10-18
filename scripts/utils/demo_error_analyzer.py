"""
Demonstração e validação do ErrorAnalyzer.

Este script:
1. Cria dados de exemplo no formato JSONL
2. Demonstra todas as funcionalidades do ErrorAnalyzer
3. Valida conformidade com especificação
"""

import json
from pathlib import Path
from datetime import datetime, timedelta
import tempfile
import shutil


def create_sample_feedback_data(feedback_dir: Path):
    """Cria dados de exemplo para demonstração"""

    print("Criando dados de feedback de exemplo...")

    # Cria feedback dos últimos 7 dias
    for days_ago in range(7):
        date = (datetime.now() - timedelta(days=days_ago))
        date_str = date.strftime("%Y%m%d")
        feedback_file = feedback_dir / f"feedback_{date_str}.jsonl"

        with open(feedback_file, 'w', encoding='utf-8') as f:
            # Simula diferentes tipos de erro com frequências variadas

            # missing_limit: erro mais comum (HIGH priority)
            for i in range(3):
                entry = {
                    "query": f"SELECT * FROM vendas WHERE data >= '{date.strftime('%Y-%m-%d')}'",
                    "issue_type": "missing_limit",
                    "timestamp": date.isoformat(),
                    "error_message": "Query retornou muitos resultados"
                }
                f.write(json.dumps(entry) + '\n')

            # wrong_column: erro médio (MEDIUM priority)
            if days_ago % 2 == 0:  # Dias alternados
                entry = {
                    "query": "SELECT produto_nome, valor_total FROM vendas",
                    "issue_type": "wrong_column",
                    "timestamp": date.isoformat(),
                    "error_message": "Column 'valor_total' not found"
                }
                f.write(json.dumps(entry) + '\n')

            # wrong_segmento: erro ocasional (LOW priority)
            if days_ago == 0 or days_ago == 3:
                entry = {
                    "query": "SELECT * FROM vendas WHERE segmento = 'varejo'",
                    "issue_type": "wrong_segmento",
                    "timestamp": date.isoformat(),
                    "error_message": "Invalid segmento value"
                }
                f.write(json.dumps(entry) + '\n')

            # syntax_error: erro raro
            if days_ago == 1:
                entry = {
                    "query": "SELECT * FROM vendas WHERE",
                    "issue_type": "syntax_error",
                    "timestamp": date.isoformat(),
                    "error_message": "Syntax error near 'WHERE'"
                }
                f.write(json.dumps(entry) + '\n')

    print(f"✓ Criados 7 arquivos de feedback")


def demonstrate_functionality():
    """Demonstra todas as funcionalidades do ErrorAnalyzer"""

    print("\n" + "=" * 70)
    print("DEMONSTRAÇÃO DO ErrorAnalyzer")
    print("=" * 70 + "\n")

    # Cria diretório temporário
    temp_dir = Path(tempfile.mkdtemp())

    try:
        # Cria dados de exemplo
        create_sample_feedback_data(temp_dir)

        # Importa ErrorAnalyzer
        print("\nImportando ErrorAnalyzer...")
        from core.learning.error_analyzer import ErrorAnalyzer

        # Inicializa analyzer
        print(f"Inicializando ErrorAnalyzer com diretório: {temp_dir}")
        analyzer = ErrorAnalyzer(feedback_dir=str(temp_dir))
        print("✓ ErrorAnalyzer inicializado\n")

        # TESTE 1: analyze_errors()
        print("-" * 70)
        print("TESTE 1: analyze_errors(days=7)")
        print("-" * 70)

        result = analyzer.analyze_errors(days=7)

        print(f"\nErros encontrados: {len(result['most_common_errors'])}")
        print(f"Sugestões geradas: {len(result['suggested_improvements'])}\n")

        print("Erros mais comuns:")
        for i, error in enumerate(result['most_common_errors'], 1):
            print(f"  {i}. {error['type']}: {error['count']} ocorrências")
            print(f"     Exemplo: {error['example_query'][:60]}...")

        print("\nSugestões de melhoria:")
        for i, suggestion in enumerate(result['suggested_improvements'], 1):
            print(f"\n  {i}. [{suggestion['priority']}] {suggestion['issue']}")
            print(f"     Solução: {suggestion['solution'][:80]}...")

        # TESTE 2: get_error_types()
        print("\n" + "-" * 70)
        print("TESTE 2: get_error_types()")
        print("-" * 70)

        error_types = analyzer.get_error_types()
        print(f"\nTipos de erro conhecidos ({len(error_types)}):")
        for error_type in error_types:
            print(f"  - {error_type}")

        # TESTE 3: Filtro de dias
        print("\n" + "-" * 70)
        print("TESTE 3: Filtro de dias (analyze_errors com days=3)")
        print("-" * 70)

        result_3days = analyzer.analyze_errors(days=3)
        print(f"\nErros dos últimos 3 dias: {len(result_3days['most_common_errors'])}")

        for error in result_3days['most_common_errors']:
            print(f"  - {error['type']}: {error['count']} ocorrências")

        # VALIDAÇÃO
        print("\n" + "=" * 70)
        print("VALIDAÇÃO DE CONFORMIDADE COM ESPECIFICAÇÃO")
        print("=" * 70 + "\n")

        validations = []

        # Verifica estrutura do retorno
        validations.append(("Retorna 'most_common_errors'",
                          'most_common_errors' in result))
        validations.append(("Retorna 'suggested_improvements'",
                          'suggested_improvements' in result))

        # Verifica estrutura dos erros
        if result['most_common_errors']:
            first_error = result['most_common_errors'][0]
            validations.append(("Erro contém 'type'", 'type' in first_error))
            validations.append(("Erro contém 'count'", 'count' in first_error))
            validations.append(("Erro contém 'example_query'",
                              'example_query' in first_error))

        # Verifica estrutura das sugestões
        if result['suggested_improvements']:
            first_suggestion = result['suggested_improvements'][0]
            validations.append(("Sugestão contém 'issue'",
                              'issue' in first_suggestion))
            validations.append(("Sugestão contém 'solution'",
                              'solution' in first_suggestion))
            validations.append(("Sugestão contém 'priority'",
                              'priority' in first_suggestion))

        # Verifica prioridades
        priorities = {s['priority'] for s in result['suggested_improvements']}
        validations.append(("Prioridades válidas (HIGH/MEDIUM/LOW)",
                          priorities.issubset({'HIGH', 'MEDIUM', 'LOW'})))

        # Verifica ordenação por count
        counts = [e['count'] for e in result['most_common_errors']]
        validations.append(("Erros ordenados por frequência",
                          counts == sorted(counts, reverse=True)))

        # Verifica que get_error_types retorna lista
        validations.append(("get_error_types() retorna lista",
                          isinstance(error_types, list)))

        # Verifica que lista está ordenada
        validations.append(("Tipos de erro ordenados alfabeticamente",
                          error_types == sorted(error_types)))

        # Exibe resultados
        passed = sum(1 for _, result in validations if result)
        total = len(validations)

        for check, result in validations:
            status = "✓" if result else "✗"
            print(f"  {status} {check}")

        print(f"\nRESULTADO: {passed}/{total} validações passaram")

        if passed == total:
            print("\n🎉 TODAS AS VALIDAÇÕES PASSARAM!")
            print("ErrorAnalyzer está 100% conforme especificação.")
        else:
            print(f"\n⚠️  {total - passed} validações falharam")

        # Estatísticas finais
        print("\n" + "=" * 70)
        print("ESTATÍSTICAS")
        print("=" * 70)
        print(f"  Total de arquivos processados: 7")
        print(f"  Total de erros registrados: {sum(e['count'] for e in result['most_common_errors'])}")
        print(f"  Tipos de erro únicos: {len(error_types)}")
        print(f"  Sugestões de alta prioridade: {sum(1 for s in result['suggested_improvements'] if s['priority'] == 'HIGH')}")
        print(f"  Sugestões de média prioridade: {sum(1 for s in result['suggested_improvements'] if s['priority'] == 'MEDIUM')}")
        print(f"  Sugestões de baixa prioridade: {sum(1 for s in result['suggested_improvements'] if s['priority'] == 'LOW')}")

    except ImportError as e:
        print(f"\n❌ ERRO: Não foi possível importar ErrorAnalyzer")
        print(f"Execute primeiro: python install_error_analyzer.py")
        print(f"Erro: {e}")

    except Exception as e:
        print(f"\n❌ ERRO durante demonstração: {e}")
        import traceback
        traceback.print_exc()

    finally:
        # Limpa diretório temporário
        if temp_dir.exists():
            shutil.rmtree(temp_dir)
            print(f"\n✓ Diretório temporário removido")


def main():
    """Função principal"""

    print("\n" + "=" * 70)
    print("DEMONSTRAÇÃO E VALIDAÇÃO DO ErrorAnalyzer")
    print("TAREFA 1 - PILAR 4: APRENDIZADO CONTÍNUO")
    print("=" * 70)

    # Primeiro, garante que o ErrorAnalyzer foi instalado
    error_analyzer_file = Path("core/learning/error_analyzer.py")

    if not error_analyzer_file.exists():
        print("\n⚠️  ErrorAnalyzer não encontrado!")
        print("Executando instalação automaticamente...\n")

        import subprocess
        result = subprocess.run(
            ["python", "install_error_analyzer.py"],
            capture_output=True,
            text=True
        )

        if result.returncode != 0:
            print("❌ Falha na instalação:")
            print(result.stderr)
            return 1

        print(result.stdout)

    # Executa demonstração
    demonstrate_functionality()

    print("\n" + "=" * 70)
    print("DEMONSTRAÇÃO CONCLUÍDA")
    print("=" * 70 + "\n")

    return 0


if __name__ == "__main__":
    import sys
    sys.exit(main())
