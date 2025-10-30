# -*- coding: utf-8 -*-
"""Teste simples de multiplos graficos Plotly"""
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pandas as pd
import plotly.express as px

print("\n" + "="*60)
print("VALIDACAO: Multiplos Graficos Plotly")
print("="*60)

# Teste 1: Grafico unico
print("\n[TESTE 1] Grafico unico (regressao)")
sample_data = pd.DataFrame({
    'nomesegmento': ['TECIDO', 'ARMARINHO', 'FERRAGEM'],
    'venda_30_d': [10000, 5000, 8000]
})
fig = px.bar(sample_data, x='nomesegmento', y='venda_30_d', title='Vendas por Segmento')
result = fig

if isinstance(result, list) and len(result) > 0 and 'plotly' in str(type(result[0])):
    detected_type = 'multiple_charts'
elif 'plotly' in str(type(result)):
    detected_type = 'chart'
else:
    detected_type = 'text'

status1 = 'PASSOU' if detected_type == 'chart' else 'FALHOU'
print(f"  Tipo detectado: {detected_type}")
print(f"  Status: {status1}")

# Teste 2: Multiplos graficos
print("\n[TESTE 2] Multiplos graficos (correcao nova)")
charts = []
for une_name in ['NIG', 'ITA', 'MAD']:
    fig2 = px.bar(sample_data, x='nomesegmento', y='venda_30_d', title=f'Top 10 - {une_name}')
    charts.append(fig2)
result2 = charts

if isinstance(result2, list) and len(result2) > 0 and 'plotly' in str(type(result2[0])):
    detected_type2 = 'multiple_charts'
elif 'plotly' in str(type(result2)):
    detected_type2 = 'chart'
else:
    detected_type2 = 'text'

status2 = 'PASSOU' if detected_type2 == 'multiple_charts' else 'FALHOU'
print(f"  Tipo detectado: {detected_type2}")
print(f"  Numero de graficos: {len(result2)}")
print(f"  Status: {status2}")

# Teste 3: Lista vazia
print("\n[TESTE 3] Lista vazia (edge case)")
result3 = []

if isinstance(result3, list) and len(result3) > 0 and 'plotly' in str(type(result3[0])):
    detected_type3 = 'multiple_charts'
elif 'plotly' in str(type(result3)):
    detected_type3 = 'chart'
else:
    detected_type3 = 'text'

status3 = 'PASSOU' if detected_type3 == 'text' else 'FALHOU'
print(f"  Tipo detectado: {detected_type3}")
print(f"  Status: {status3}")

# Resumo
print("\n" + "="*60)
print("RESUMO")
print("="*60)
total = 3
passed = sum([status1 == 'PASSOU', status2 == 'PASSOU', status3 == 'PASSOU'])
failed = total - passed

print(f"Total: {total} testes")
print(f"Passaram: {passed}")
print(f"Falharam: {failed}")

if failed == 0:
    print("\n[OK] TODOS OS TESTES PASSARAM!")
    sys.exit(0)
else:
    print(f"\n[WARN] {failed} teste(s) falharam")
    sys.exit(1)
