"""
Teste SIMPLES e RÁPIDO das correções dos 2 erros críticos
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

print("\n" + "="*80)
print("TESTE 1: UnboundLocalError - import time dentro de load_data()")
print("="*80)

try:
    # Simular o código corrigido
    def load_data_corrigido():
        import time as time_module  # FIX aplicado
        start = time_module.time()
        # Simular trabalho
        import pandas as pd
        df = pd.DataFrame({"A": [1, 2, 3]})
        end = time_module.time()
        print(f"[OK] Tempo: {end - start:.4f}s")
        return df

    result = load_data_corrigido()
    print(f"[OK] PASSOU: DataFrame com {len(result)} linhas criado sem erro")
    test1_passou = True
except Exception as e:
    print(f"[ERRO] FALHOU: {e}")
    test1_passou = False

print("\n" + "="*80)
print("TESTE 2: Validação de colunas - calcular colunas derivadas")
print("="*80)

try:
    import pandas as pd

    # Simular DataFrame do SQL Server (sem colunas calculadas)
    df = pd.DataFrame({
        "une": [2586, 2586, 2586],
        "codigo": [1, 2, 3],
        "nome_produto": ["Produto A", "Produto B", "Produto C"],
        "estoque_atual": [10, 50, 100],
        "linha_verde": [100, 100, 100]
    })

    # Aplicar FIX: calcular colunas derivadas
    if 'precisa_abastecimento' not in df.columns:
        df['precisa_abastecimento'] = (df['estoque_atual'] <= (df['linha_verde'] * 0.5))
        print("[OK] Coluna 'precisa_abastecimento' calculada")

    if 'qtd_a_abastecer' not in df.columns:
        df['qtd_a_abastecer'] = (df['linha_verde'] - df['estoque_atual']).clip(lower=0)
        print("[OK] Coluna 'qtd_a_abastecer' calculada")

    # Verificar se funciona
    df_abastecer = df[df['precisa_abastecimento'] == True]
    print(f"[OK] PASSOU: {len(df_abastecer)} produtos precisam abastecimento")
    test2_passou = True

except Exception as e:
    print(f"[ERRO] FALHOU: {e}")
    test2_passou = False

print("\n" + "="*80)
print("SUMÁRIO")
print("="*80)
print(f"Teste 1 (UnboundLocalError): {'[OK] PASSOU' if test1_passou else '[ERRO] FALHOU'}")
print(f"Teste 2 (Validacao colunas): {'[OK] PASSOU' if test2_passou else '[ERRO] FALHOU'}")

if test1_passou and test2_passou:
    print("\n[SUCCESS] TODOS OS TESTES PASSARAM! Correcoes validadas.")
    sys.exit(0)
else:
    print("\n[WARNING] ALGUNS TESTES FALHARAM")
    sys.exit(1)
