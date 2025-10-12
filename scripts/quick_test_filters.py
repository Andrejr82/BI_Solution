"""
Teste rápido para validar que os filtros estão sendo aplicados corretamente.
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from core.connectivity.parquet_adapter import ParquetAdapter

def test_filters():
    """Testa se filtros reduzem dados carregados."""

    print("="*70)
    print("TESTE RAPIDO - VALIDACAO DE FILTROS")
    print("="*70)

    parquet_path = "data/parquet/admmat.parquet"
    if not os.path.exists(parquet_path):
        print(f"[ERRO] Arquivo nao encontrado")
        return

    adapter = ParquetAdapter(parquet_path)

    tests = [
        {
            "name": "SEM filtro (dataset completo)",
            "filters": {},
            "expected_rows": 1000000  # Esperado: > 1M linhas
        },
        {
            "name": "COM filtro UNE (TIJ)",
            "filters": {"une_nome": "TIJ"},
            "expected_rows": 50000  # Esperado: < 50K linhas
        },
        {
            "name": "COM filtro Segmento (TECIDOS)",
            "filters": {"nomesegmento": "TECIDOS"},
            "expected_rows": 200000  # Esperado: < 200K linhas
        }
    ]

    print("\n[INFO] Executando testes...\n")

    for test in tests:
        print(f"[TEST] {test['name']}")
        print(f"       Filtros: {test['filters']}")

        try:
            data = adapter.execute_query(test['filters'])

            if data and 'error' not in data[0]:
                row_count = len(data)
                print(f"  [OK] Linhas carregadas: {row_count:,}")

                if test['filters']:  # Se tem filtro, deve carregar menos
                    if row_count < test['expected_rows']:
                        print(f"  [OK] Filtro EFETIVO! Carregou {row_count:,} linhas (< {test['expected_rows']:,})")
                    else:
                        print(f"  [AVISO] Filtro NAO efetivo! Carregou {row_count:,} linhas (>= {test['expected_rows']:,})")
                else:  # Sem filtro, deve carregar tudo
                    if row_count > test['expected_rows']:
                        print(f"  [OK] Dataset completo carregado")
                    else:
                        print(f"  [AVISO] Dataset incompleto?")
            else:
                print(f"  [ERRO] {data[0].get('error', 'Unknown error')}")

        except Exception as e:
            print(f"  [ERRO] Excecao: {str(e)}")

        print()

    print("="*70)
    print("[INFO] Teste concluido!")
    print("="*70)

if __name__ == "__main__":
    test_filters()
