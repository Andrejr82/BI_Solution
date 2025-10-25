#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Verificação de pré-requisitos para instalação RAG.

Autor: Code Agent
Data: 2025-10-24
Versão: 1.0.0

Verifica:
- Versão do Python
- Pip disponível
- Espaço em disco
- Conectividade de rede
- Ambiente virtual
"""

import sys
import subprocess
import shutil
import urllib.request
from pathlib import Path


def check_python_version():
    """Verifica se a versão do Python é compatível."""
    print("\n" + "="*60)
    print("🐍 VERIFICANDO VERSÃO DO PYTHON")
    print("="*60)

    version = sys.version_info
    version_str = f"{version.major}.{version.minor}.{version.micro}"

    print(f"Python: {version_str}")

    if version.major < 3 or (version.major == 3 and version.minor < 7):
        print(f"❌ Python {version_str} não suportado")
        print(f"   Requerido: Python >= 3.7")
        return False

    if version.major == 3 and version.minor < 8:
        print(f"⚠️  Python {version_str} funciona mas recomenda-se >= 3.8")

    print(f"✅ Versão compatível")
    return True


def check_pip():
    """Verifica se pip está disponível."""
    print("\n" + "="*60)
    print("📦 VERIFICANDO PIP")
    print("="*60)

    try:
        result = subprocess.run(
            [sys.executable, '-m', 'pip', '--version'],
            capture_output=True,
            text=True,
            timeout=10
        )

        if result.returncode == 0:
            print(f"✅ {result.stdout.strip()}")
            return True
        else:
            print(f"❌ Pip não encontrado")
            return False

    except Exception as e:
        print(f"❌ Erro ao verificar pip: {str(e)}")
        return False


def check_disk_space():
    """Verifica espaço disponível em disco."""
    print("\n" + "="*60)
    print("💾 VERIFICANDO ESPAÇO EM DISCO")
    print("="*60)

    try:
        # Obter espaço no disco atual
        total, used, free = shutil.disk_usage(Path.cwd())

        total_gb = total / (1024**3)
        free_gb = free / (1024**3)

        print(f"Total: {total_gb:.2f} GB")
        print(f"Livre: {free_gb:.2f} GB")

        required_gb = 1.0  # 1GB para modelos e dependências

        if free_gb < required_gb:
            print(f"⚠️  Pouco espaço disponível")
            print(f"   Recomendado: {required_gb} GB livre")
            print(f"   Disponível: {free_gb:.2f} GB")
            return False

        print(f"✅ Espaço suficiente ({free_gb:.2f} GB > {required_gb} GB)")
        return True

    except Exception as e:
        print(f"⚠️  Não foi possível verificar espaço: {str(e)}")
        return True  # Não bloquear instalação


def check_network():
    """Verifica conectividade de rede."""
    print("\n" + "="*60)
    print("🌐 VERIFICANDO CONECTIVIDADE")
    print("="*60)

    urls = [
        ('PyPI', 'https://pypi.org'),
        ('HuggingFace', 'https://huggingface.co'),
        ('GitHub', 'https://github.com')
    ]

    all_ok = True

    for name, url in urls:
        try:
            urllib.request.urlopen(url, timeout=5)
            print(f"✅ {name}: OK")
        except Exception as e:
            print(f"❌ {name}: FALHOU ({str(e)})")
            all_ok = False

    return all_ok


def check_venv():
    """Verifica se está em ambiente virtual."""
    print("\n" + "="*60)
    print("🔒 VERIFICANDO AMBIENTE VIRTUAL")
    print("="*60)

    in_venv = hasattr(sys, 'real_prefix') or (
        hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix
    )

    if in_venv:
        print(f"✅ Executando em ambiente virtual")
        print(f"   Prefix: {sys.prefix}")
        return True
    else:
        print(f"⚠️  NÃO está em ambiente virtual")
        print(f"   Recomenda-se usar venv para isolar dependências")
        print(f"   Para criar: python -m venv venv")
        print(f"   Para ativar: venv\\Scripts\\activate (Windows)")
        return False


def check_existing_packages():
    """Verifica pacotes já instalados."""
    print("\n" + "="*60)
    print("📋 VERIFICANDO PACOTES EXISTENTES")
    print("="*60)

    packages = [
        'sentence-transformers',
        'faiss-cpu',
        'spacy',
        'torch',
        'numpy'
    ]

    installed = []
    missing = []

    for pkg in packages:
        try:
            result = subprocess.run(
                [sys.executable, '-m', 'pip', 'show', pkg],
                capture_output=True,
                text=True,
                timeout=5
            )

            if result.returncode == 0:
                # Extrair versão
                for line in result.stdout.split('\n'):
                    if line.startswith('Version:'):
                        version = line.split(':')[1].strip()
                        print(f"✅ {pkg}: {version}")
                        installed.append(pkg)
                        break
            else:
                print(f"❌ {pkg}: Não instalado")
                missing.append(pkg)

        except Exception as e:
            print(f"⚠️  {pkg}: Erro ao verificar ({str(e)})")
            missing.append(pkg)

    return installed, missing


def main():
    """Executa todas as verificações."""
    print("\n" + "="*60)
    print("🔍 VERIFICAÇÃO DE PRÉ-REQUISITOS RAG")
    print("="*60)

    checks = {
        'Python Version': check_python_version(),
        'Pip Available': check_pip(),
        'Disk Space': check_disk_space(),
        'Network': check_network(),
        'Virtual Env': check_venv()
    }

    # Verificar pacotes existentes
    installed, missing = check_existing_packages()

    # Relatório final
    print("\n" + "="*60)
    print("📊 RELATÓRIO DE PRÉ-REQUISITOS")
    print("="*60)

    print("\n✅ Verificações Aprovadas:")
    for name, status in checks.items():
        if status:
            print(f"   ✅ {name}")

    print("\n⚠️  Verificações com Avisos:")
    for name, status in checks.items():
        if not status:
            print(f"   ⚠️  {name}")

    print(f"\n📦 Pacotes:")
    print(f"   Instalados: {len(installed)}")
    print(f"   Faltantes: {len(missing)}")

    if missing:
        print(f"\n   Serão instalados:")
        for pkg in missing:
            print(f"      - {pkg}")

    # Determinar se pode prosseguir
    critical_checks = ['Python Version', 'Pip Available']
    can_proceed = all(checks.get(check, False) for check in critical_checks)

    print("\n" + "="*60)

    if can_proceed:
        print("✅ SISTEMA PRONTO PARA INSTALAÇÃO RAG")
        print("\nPróximos passos:")
        print("   1. Execute: scripts\\INSTALAR_RAG.bat")
        print("   2. Ou: python scripts/install_rag_dependencies.py")
        return 0
    else:
        print("❌ SISTEMA NÃO ESTÁ PRONTO")
        print("\nCorreções necessárias:")

        if not checks.get('Python Version'):
            print("   - Atualizar Python para versão >= 3.7")

        if not checks.get('Pip Available'):
            print("   - Instalar/reparar pip")

        return 1


if __name__ == '__main__':
    sys.exit(main())
