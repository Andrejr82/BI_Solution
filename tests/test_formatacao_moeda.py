"""
Teste de formatação de moeda brasileira
"""
import pandas as pd
from core.utils.dataframe_formatter import format_dataframe_for_display, detect_currency_columns

# Simular dados da query
data = [
    {'NOME': 'Produto A', 'VENDA_30DD': 15234.56, 'ESTOQUE_UNE': 100},
    {'NOME': 'Produto B', 'VENDA_30DD': 8945.23, 'ESTOQUE_UNE': 50},
    {'NOME': 'Produto C', 'VENDA_30DD': 3456.78, 'ESTOQUE_UNE': 25},
]

print("=" * 60)
print("TESTE: Formatação de Moeda Brasileira")
print("=" * 60)

# Criar DataFrame
df = pd.DataFrame(data)

print("\n1. DataFrame ORIGINAL:")
print(df)
print(f"\nTipos: {df.dtypes.to_dict()}")

# Detectar colunas monetárias
currency_cols = detect_currency_columns(df)
print(f"\n2. Colunas monetárias detectadas: {currency_cols}")

# Aplicar formatação
df_formatted = format_dataframe_for_display(df, auto_detect=True)

print("\n3. DataFrame FORMATADO:")
print(df_formatted)
print(f"\nTipos após formatação: {df_formatted.dtypes.to_dict()}")

# Verificar valores específicos
print("\n4. Verificação de valores:")
for i, row in df_formatted.iterrows():
    print(f"  {row['NOME']}: {row['VENDA_30DD']}")

# Esperado
print("\n5. Formato ESPERADO:")
print("  Produto A: R$ 15.234,56")
print("  Produto B: R$ 8.945,23")
print("  Produto C: R$ 3.456,78")

print("\n" + "=" * 60)
print("STATUS: Teste concluído")
print("=" * 60)
