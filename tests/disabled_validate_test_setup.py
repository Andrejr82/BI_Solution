"""
Script de Validação Pré-Teste
Verifica se tudo está configurado corretamente antes de executar o teste de 80 perguntas
"""

import sys
from pathlib import Path

# Adicionar o diretório raiz ao path
root_dir = Path(__file__).parent.parent
sys.path.insert(0, str(root_dir))

def validate_environment():
    """Valida o ambiente e dependências"""
    print("=" * 80)
    print("VALIDAÇÃO DO AMBIENTE - TESTE 80 PERGUNTAS")
    print("=" * 80)

    issues = []
    warnings = []

    # 1. Verificar Python version
    print("\n[1/6] Verificando versão do Python...")
    python_version = sys.version_info
    if python_version.major >= 3 and python_version.minor >= 8:
        print(f"[OK] Python {python_version.major}.{python_version.minor}.{python_version.micro}")
    else:
        msg = f"Python {python_version.major}.{python_version.minor} - Recomendado: 3.8+"
        print(f"[WARN] {msg}")
        warnings.append(msg)

    # 2. Verificar dependências
    print("\n[2/6] Verificando dependências Python...")
    required_packages = {
        'pandas': 'Processamento de dados',
        'dask': 'Processamento paralelo',
        'pyarrow': 'Leitura de Parquet'
    }

    for package, descricao in required_packages.items():
        try:
            module = __import__(package)
            version = getattr(module, '__version__', 'unknown')
            print(f"[OK] {package:12} v{version:10} - {descricao}")
        except ImportError:
            msg = f"{package} não encontrado - {descricao}"
            print(f"[ERRO] {msg}")
            issues.append(msg)

    # 3. Verificar estrutura de diretórios
    print("\n[3/6] Verificando estrutura de diretórios...")
    required_dirs = [
        ('data', 'Diretório de dados'),
        ('data/parquet', 'Arquivos Parquet'),
        ('tests', 'Testes'),
        ('core', 'Código core'),
        ('core/business_intelligence', 'DirectQueryEngine'),
        ('core/connectivity', 'ParquetAdapter')
    ]

    for dir_path, descricao in required_dirs:
        full_path = root_dir / dir_path
        if full_path.exists():
            print(f"[OK] {dir_path:30} - {descricao}")
        else:
            msg = f"{dir_path} não encontrado - {descricao}"
            print(f"[ERRO] {msg}")
            issues.append(msg)

    # 4. Verificar arquivos Parquet
    print("\n[4/6] Verificando arquivos Parquet...")
    parquet_dir = root_dir / 'data' / 'parquet'

    if parquet_dir.exists():
        parquet_files = list(parquet_dir.glob('*.parquet'))
        if parquet_files:
            for pf in parquet_files:
                size_mb = pf.stat().st_size / (1024 * 1024)
                print(f"[OK] {pf.name:30} - {size_mb:.2f} MB")

            # Verificar se tem o arquivo preferencial
            admmat_extended = parquet_dir / 'admmat_extended.parquet'
            admmat = parquet_dir / 'admmat.parquet'

            if admmat_extended.exists():
                print(f"[INFO] Será usado: admmat_extended.parquet")
            elif admmat.exists():
                print(f"[INFO] Será usado: admmat.parquet")
            else:
                msg = "Nenhum arquivo admmat*.parquet encontrado"
                print(f"[WARN] {msg}")
                warnings.append(msg)
        else:
            msg = "Nenhum arquivo .parquet encontrado"
            print(f"[ERRO] {msg}")
            issues.append(msg)
    else:
        msg = "Diretório data/parquet não existe"
        print(f"[ERRO] {msg}")
        issues.append(msg)

    # 5. Verificar módulos do projeto
    print("\n[5/6] Verificando módulos do projeto...")
    modules_to_check = [
        ('core.business_intelligence.direct_query_engine', 'DirectQueryEngine'),
        ('core.connectivity.parquet_adapter', 'ParquetAdapter'),
        ('core.visualization.advanced_charts', 'AdvancedChartGenerator')
    ]

    for module_path, class_name in modules_to_check:
        try:
            module = __import__(module_path, fromlist=[class_name])
            if hasattr(module, class_name):
                print(f"[OK] {module_path:50} - {class_name}")
            else:
                msg = f"{module_path} não tem classe {class_name}"
                print(f"[WARN] {msg}")
                warnings.append(msg)
        except ImportError as e:
            msg = f"{module_path} não pode ser importado: {str(e)[:50]}"
            print(f"[ERRO] {msg}")
            issues.append(msg)

    # 6. Teste rápido de inicialização
    print("\n[6/6] Teste rápido de inicialização...")
    try:
        from core.connectivity.parquet_adapter import ParquetAdapter
        from core.business_intelligence.direct_query_engine import DirectQueryEngine

        # Encontrar arquivo parquet
        parquet_dir = root_dir / 'data' / 'parquet'
        admmat_extended = parquet_dir / 'admmat_extended.parquet'
        admmat = parquet_dir / 'admmat.parquet'

        if admmat_extended.exists():
            test_file = admmat_extended
        elif admmat.exists():
            test_file = admmat
        else:
            raise FileNotFoundError("Nenhum arquivo parquet encontrado")

        print(f"[INFO] Testando com: {test_file.name}")

        # Tentar inicializar
        adapter = ParquetAdapter(str(test_file))
        engine = DirectQueryEngine(adapter)

        print("[OK] DirectQueryEngine inicializado com sucesso!")

        # Teste simples
        print("[INFO] Executando teste simples...")
        result = engine.process_query("Mostre produtos da UNE SCR")

        if result:
            result_type = result.get('type', 'unknown')
            print(f"[OK] Teste simples executado - tipo: {result_type}")
        else:
            msg = "Teste simples retornou resultado vazio"
            print(f"[WARN] {msg}")
            warnings.append(msg)

    except Exception as e:
        msg = f"Falha no teste de inicialização: {str(e)[:100]}"
        print(f"[ERRO] {msg}")
        issues.append(msg)
        import traceback
        print(traceback.format_exc())

    # Resumo final
    print("\n" + "=" * 80)
    print("RESUMO DA VALIDAÇÃO")
    print("=" * 80)

    if not issues and not warnings:
        print("[✓] TUDO OK! Você pode executar o teste.")
        print("\nPara executar o teste, rode:")
        print("  python tests/run_test_80_perguntas.py")
        return 0
    else:
        if issues:
            print(f"\n[!] {len(issues)} PROBLEMAS CRÍTICOS encontrados:")
            for i, issue in enumerate(issues, 1):
                print(f"  {i}. {issue}")

        if warnings:
            print(f"\n[!] {len(warnings)} AVISOS:")
            for i, warning in enumerate(warnings, 1):
                print(f"  {i}. {warning}")

        if issues:
            print("\n[X] CORRIJA OS PROBLEMAS ANTES DE EXECUTAR O TESTE")
            return 1
        else:
            print("\n[✓] Avisos detectados, mas você pode prosseguir com cautela")
            return 0

if __name__ == "__main__":
    exit_code = validate_environment()
    sys.exit(exit_code)
