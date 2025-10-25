#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script de instalação e validação de dependências RAG.

Autor: Code Agent
Data: 2025-10-24
Versão: 1.0.0
"""

import subprocess
import sys
import json
from datetime import datetime
from pathlib import Path


def run_command(cmd, description):
    """
    Executa comando shell e retorna resultado.

    Args:
        cmd: Lista com comando e argumentos
        description: Descrição da operação

    Returns:
        tuple: (sucesso: bool, output: str)
    """
    print(f"\n{'='*60}")
    print(f"🔧 {description}")
    print(f"{'='*60}")

    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=300
        )

        output = result.stdout + result.stderr
        print(output)

        if result.returncode == 0:
            print(f"✅ {description} - SUCESSO")
            return True, output
        else:
            print(f"❌ {description} - FALHOU")
            return False, output

    except subprocess.TimeoutExpired:
        print(f"⏰ {description} - TIMEOUT (300s)")
        return False, "Timeout ao executar comando"
    except Exception as e:
        print(f"❌ {description} - ERRO: {str(e)}")
        return False, str(e)


def check_package_installed(package_name):
    """
    Verifica se um pacote está instalado.

    Args:
        package_name: Nome do pacote (pode incluir versão)

    Returns:
        bool: True se instalado, False caso contrário
    """
    pkg = package_name.split('==')[0]
    try:
        result = subprocess.run(
            [sys.executable, '-m', 'pip', 'show', pkg],
            capture_output=True,
            text=True
        )
        return result.returncode == 0
    except:
        return False


def install_package(package):
    """
    Instala um pacote via pip.

    Args:
        package: String com nome e versão do pacote

    Returns:
        tuple: (sucesso: bool, output: str)
    """
    return run_command(
        [sys.executable, '-m', 'pip', 'install', package],
        f"Instalando {package}"
    )


def test_imports():
    """
    Testa imports das bibliotecas instaladas.

    Returns:
        dict: Resultados dos testes
    """
    print(f"\n{'='*60}")
    print("🧪 TESTANDO IMPORTS")
    print(f"{'='*60}\n")

    results = {}

    # Test sentence-transformers
    try:
        from sentence_transformers import SentenceTransformer
        print("✅ sentence-transformers: OK")
        results['sentence_transformers'] = True
    except Exception as e:
        print(f"❌ sentence-transformers: FALHOU - {str(e)}")
        results['sentence_transformers'] = False

    # Test faiss
    try:
        import faiss
        print("✅ faiss-cpu: OK")
        results['faiss'] = True
    except Exception as e:
        print(f"❌ faiss-cpu: FALHOU - {str(e)}")
        results['faiss'] = False

    # Test spacy
    try:
        import spacy
        print("✅ spacy: OK")
        results['spacy'] = True
    except Exception as e:
        print(f"❌ spacy: FALHOU - {str(e)}")
        results['spacy'] = False

    # Test spacy model
    try:
        import spacy
        nlp = spacy.load('pt_core_news_sm')
        print("✅ spacy pt_core_news_sm: OK")
        results['spacy_model'] = True
    except Exception as e:
        print(f"❌ spacy pt_core_news_sm: FALHOU - {str(e)}")
        results['spacy_model'] = False

    return results


def update_requirements():
    """
    Atualiza requirements.txt com novas dependências.

    Returns:
        bool: Sucesso da operação
    """
    print(f"\n{'='*60}")
    print("📝 ATUALIZANDO requirements.txt")
    print(f"{'='*60}\n")

    req_file = Path("C:/Users/André/Documents/Agent_Solution_BI/requirements.txt")

    if not req_file.exists():
        print(f"❌ Arquivo {req_file} não encontrado")
        return False

    # Ler requirements atuais
    with open(req_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    # Dependências a adicionar
    new_deps = [
        'sentence-transformers==2.2.2',
        'faiss-cpu==1.7.4',
        'spacy==3.7.2'
    ]

    # Remover versões antigas se existirem
    filtered_lines = []
    for line in lines:
        line_clean = line.strip()
        if line_clean and not any(
            line_clean.startswith(dep.split('==')[0])
            for dep in new_deps
        ):
            filtered_lines.append(line)

    # Adicionar novas dependências
    for dep in new_deps:
        if not any(dep in line for line in filtered_lines):
            filtered_lines.append(f"{dep}\n")

    # Ordenar alfabeticamente (exceto comentários)
    comments = [l for l in filtered_lines if l.strip().startswith('#')]
    deps = sorted([l for l in filtered_lines if not l.strip().startswith('#') and l.strip()])

    final_lines = comments + deps

    # Escrever arquivo atualizado
    with open(req_file, 'w', encoding='utf-8') as f:
        f.writelines(final_lines)

    print(f"✅ requirements.txt atualizado com sucesso")
    print(f"   Adicionados: {', '.join(new_deps)}")

    return True


def main():
    """Função principal de instalação."""
    print("\n" + "="*60)
    print("🚀 INSTALAÇÃO DE DEPENDÊNCIAS RAG")
    print("="*60)
    print(f"Data: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Python: {sys.version}")
    print(f"Pip: {subprocess.run([sys.executable, '-m', 'pip', '--version'], capture_output=True, text=True).stdout.strip()}")

    # Dependências a instalar
    dependencies = {
        'sentence-transformers==2.2.2': 'Embeddings multilíngues',
        'faiss-cpu==1.7.4': 'Busca vetorial rápida',
        'spacy==3.7.2': 'Processamento de texto'
    }

    results = {
        'timestamp': datetime.now().isoformat(),
        'python_version': sys.version,
        'installations': {},
        'tests': {},
        'requirements_updated': False
    }

    # 1. Verificar e instalar dependências
    print(f"\n{'='*60}")
    print("📦 VERIFICANDO DEPENDÊNCIAS")
    print(f"{'='*60}\n")

    for package, description in dependencies.items():
        pkg_name = package.split('==')[0]

        if check_package_installed(package):
            print(f"✅ {package} já instalado - {description}")
            results['installations'][pkg_name] = {'status': 'already_installed', 'success': True}
        else:
            print(f"📥 {package} não encontrado - instalando...")
            success, output = install_package(package)
            results['installations'][pkg_name] = {
                'status': 'installed' if success else 'failed',
                'success': success,
                'output': output[:500]  # Limitar output
            }

    # 2. Baixar modelo spacy português
    if check_package_installed('spacy'):
        print(f"\n{'='*60}")
        print("🌐 BAIXANDO MODELO SPACY PORTUGUÊS")
        print(f"{'='*60}\n")

        success, output = run_command(
            [sys.executable, '-m', 'spacy', 'download', 'pt_core_news_sm'],
            "Download modelo pt_core_news_sm"
        )
        results['installations']['pt_core_news_sm'] = {
            'status': 'downloaded' if success else 'failed',
            'success': success,
            'output': output[:500]
        }

    # 3. Atualizar requirements.txt
    results['requirements_updated'] = update_requirements()

    # 4. Testar imports
    results['tests'] = test_imports()

    # 5. Gerar relatório final
    print(f"\n{'='*60}")
    print("📊 RELATÓRIO FINAL")
    print(f"{'='*60}\n")

    all_success = all(
        v.get('success', False) for v in results['installations'].values()
    ) and all(results['tests'].values())

    if all_success:
        print("✅ TODAS AS DEPENDÊNCIAS INSTALADAS E VALIDADAS COM SUCESSO!")
    else:
        print("⚠️  ALGUMAS OPERAÇÕES FALHARAM - VERIFIQUE O LOG ACIMA")

    print(f"\n📈 Resumo:")
    print(f"   - Instalações: {sum(1 for v in results['installations'].values() if v.get('success', False))}/{len(results['installations'])}")
    print(f"   - Testes: {sum(results['tests'].values())}/{len(results['tests'])}")
    print(f"   - requirements.txt: {'✅' if results['requirements_updated'] else '❌'}")

    # Salvar relatório JSON
    report_file = Path("C:/Users/André/Documents/Agent_Solution_BI/reports/rag_installation_report.json")
    report_file.parent.mkdir(parents=True, exist_ok=True)

    with open(report_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)

    print(f"\n💾 Relatório salvo em: {report_file}")

    return 0 if all_success else 1


if __name__ == '__main__':
    sys.exit(main())
