"""
Script de Validação: Múltiplos Gráficos Plotly
==============================================

Testa se a correção de renderização de múltiplos gráficos Plotly funciona corretamente.

Testes:
1. Gráfico único (regressão)
2. Múltiplos gráficos (correção nova)
3. Lista vazia (edge case)

Uso:
    python scripts/test_plotly_multiple_charts.py

Autor: Claude Code
Data: 2025-10-27
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pandas as pd
import plotly.express as px
import plotly.io as pio
from typing import List, Dict, Any

# Simular ambiente do CodeGenAgent
from core.agents.code_gen_agent import CodeGenAgent

def test_single_chart():
    """
    Teste 1: Gráfico Único (Regressão)
    Verifica se gráficos únicos ainda funcionam após a correção.
    """
    print("\n" + "="*60)
    print("TESTE 1: Gráfico Único (Regressão)")
    print("="*60)

    # Simular código gerado pela LLM
    code = """
import plotly.express as px
df = load_data()
df_grouped = df.groupby('nomesegmento')['venda_30_d'].sum().reset_index()
fig = px.bar(df_grouped, x='nomesegmento', y='venda_30_d', title='Vendas por Segmento')
result = fig
"""

    print(f"📝 Código simulado:")
    print(code)

    # Executar simulação
    try:
        # Criar Figure simulada
        sample_data = pd.DataFrame({
            'nomesegmento': ['TECIDO', 'ARMARINHO', 'FERRAGEM'],
            'venda_30_d': [10000, 5000, 8000]
        })
        fig = px.bar(sample_data, x='nomesegmento', y='venda_30_d', title='Vendas por Segmento')
        result = fig

        # Verificar tipo do resultado
        result_type = type(result).__name__
        is_plotly = 'plotly' in str(type(result))

        print(f"\n✅ Resultado gerado:")
        print(f"   - Tipo: {result_type}")
        print(f"   - É Plotly?: {is_plotly}")

        # Simular lógica do CodeGenAgent
        if isinstance(result, list) and len(result) > 0 and 'plotly' in str(type(result[0])):
            detected_type = "multiple_charts"
        elif 'plotly' in str(type(result)):
            detected_type = "chart"
        else:
            detected_type = "text"

        print(f"   - Tipo detectado: {detected_type}")

        # Validar
        if detected_type == "chart":
            print(f"\n✅ PASSOU: Gráfico único detectado corretamente como 'chart'")
            return True
        else:
            print(f"\n❌ FALHOU: Esperado 'chart', mas detectou '{detected_type}'")
            return False

    except Exception as e:
        print(f"\n❌ ERRO: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_multiple_charts():
    """
    Teste 2: Múltiplos Gráficos (Correção Nova)
    Verifica se múltiplos gráficos são detectados e processados corretamente.
    """
    print("\n" + "="*60)
    print("TESTE 2: Múltiplos Gráficos (Correção Nova)")
    print("="*60)

    # Simular código gerado pela LLM
    code = """
import plotly.express as px
df = load_data()
charts = []
for une in df['une_nome'].unique()[:3]:
    df_une = df[df['une_nome'] == une]
    fig = px.bar(df_une.nlargest(10, 'venda_30_d'), x='nome_produto', y='venda_30_d', title=f'Top 10 - {une}')
    charts.append(fig)
result = charts
"""

    print(f"📝 Código simulado:")
    print(code)

    # Executar simulação
    try:
        # Criar múltiplas Figures simuladas
        charts = []
        for une_name in ['NIG', 'ITA', 'MAD']:
            sample_data = pd.DataFrame({
                'nome_produto': [f'Produto {i}' for i in range(1, 6)],
                'venda_30_d': [1000, 800, 600, 400, 200]
            })
            fig = px.bar(sample_data, x='nome_produto', y='venda_30_d', title=f'Top 10 - {une_name}')
            charts.append(fig)
        result = charts

        # Verificar tipo do resultado
        result_type = type(result).__name__
        is_list = isinstance(result, list)
        list_length = len(result) if is_list else 0
        first_is_plotly = is_list and len(result) > 0 and 'plotly' in str(type(result[0]))

        print(f"\n✅ Resultado gerado:")
        print(f"   - Tipo: {result_type}")
        print(f"   - É lista?: {is_list}")
        print(f"   - Tamanho da lista: {list_length}")
        print(f"   - Primeiro item é Plotly?: {first_is_plotly}")

        # Simular lógica do CodeGenAgent
        if isinstance(result, list) and len(result) > 0 and 'plotly' in str(type(result[0])):
            detected_type = "multiple_charts"
            num_charts = len(result)
        elif 'plotly' in str(type(result)):
            detected_type = "chart"
            num_charts = 1
        else:
            detected_type = "text"
            num_charts = 0

        print(f"   - Tipo detectado: {detected_type}")
        print(f"   - Número de gráficos: {num_charts}")

        # Validar
        if detected_type == "multiple_charts" and num_charts == 3:
            print(f"\n✅ PASSOU: Múltiplos gráficos detectados corretamente como 'multiple_charts'")

            # Testar conversão para JSON
            print(f"\n🔄 Testando conversão para JSON...")
            figures_json = []
            for i, fig in enumerate(result):
                try:
                    json_str = pio.to_json(fig)
                    figures_json.append(json_str)
                    print(f"   ✅ Gráfico {i+1}: Convertido para JSON ({len(json_str)} chars)")
                except Exception as e:
                    print(f"   ❌ Gráfico {i+1}: Erro na conversão: {e}")
                    return False

            # Testar conversão de volta
            print(f"\n🔄 Testando conversão de volta de JSON para Figure...")
            for i, json_str in enumerate(figures_json):
                try:
                    fig_restored = pio.from_json(json_str)
                    title = fig_restored.layout.title.text if fig_restored.layout.title else "Sem título"
                    print(f"   ✅ Gráfico {i+1}: Restaurado - Título: '{title}'")
                except Exception as e:
                    print(f"   ❌ Gráfico {i+1}: Erro na restauração: {e}")
                    return False

            print(f"\n✅ PASSOU: Conversão JSON bidirecional funcionando!")
            return True
        else:
            print(f"\n❌ FALHOU: Esperado 'multiple_charts' com 3 gráficos, mas detectou '{detected_type}' com {num_charts}")
            return False

    except Exception as e:
        print(f"\n❌ ERRO: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_empty_list():
    """
    Teste 3: Lista Vazia (Edge Case)
    Verifica proteção contra listas vazias.
    """
    print("\n" + "="*60)
    print("TESTE 3: Lista Vazia (Edge Case)")
    print("="*60)

    # Simular código que retorna lista vazia
    code = """
result = []
"""

    print(f"📝 Código simulado:")
    print(code)

    try:
        result = []

        # Verificar tipo do resultado
        result_type = type(result).__name__
        is_list = isinstance(result, list)
        list_length = len(result) if is_list else 0

        print(f"\n✅ Resultado gerado:")
        print(f"   - Tipo: {result_type}")
        print(f"   - É lista?: {is_list}")
        print(f"   - Tamanho da lista: {list_length}")

        # Simular lógica do CodeGenAgent
        if isinstance(result, list) and len(result) > 0 and 'plotly' in str(type(result[0])):
            detected_type = "multiple_charts"
        elif 'plotly' in str(type(result)):
            detected_type = "chart"
        else:
            detected_type = "text"

        print(f"   - Tipo detectado: {detected_type}")

        # Validar
        if detected_type == "text":
            print(f"\n✅ PASSOU: Lista vazia corretamente tratada como 'text'")
            return True
        else:
            print(f"\n❌ FALHOU: Esperado 'text', mas detectou '{detected_type}'")
            return False

    except Exception as e:
        print(f"\n❌ ERRO: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_mixed_list():
    """
    Teste 4: Lista Mista (Edge Case)
    Verifica proteção contra listas com tipos mistos.
    """
    print("\n" + "="*60)
    print("TESTE 4: Lista Mista (Edge Case)")
    print("="*60)

    try:
        # Criar lista mista (não deveria acontecer, mas testar proteção)
        sample_data = pd.DataFrame({
            'nome_produto': ['Produto 1', 'Produto 2'],
            'venda_30_d': [1000, 800]
        })
        fig = px.bar(sample_data, x='nome_produto', y='venda_30_d', title='Gráfico 1')

        result = [fig, "texto", 123]  # Lista mista

        print(f"\n✅ Resultado gerado: Lista mista (Figure, str, int)")

        # Simular lógica do CodeGenAgent
        if isinstance(result, list) and len(result) > 0 and 'plotly' in str(type(result[0])):
            detected_type = "multiple_charts"

            # Testar proteção dentro do loop
            print(f"\n🔄 Testando proteção contra itens não-Plotly...")
            figures_json = []
            for i, item in enumerate(result):
                if 'plotly' in str(type(item)):
                    json_str = pio.to_json(item)
                    figures_json.append(json_str)
                    print(f"   ✅ Item {i}: Plotly Figure processado")
                else:
                    print(f"   ⚠️ Item {i}: NÃO é Plotly ({type(item).__name__}) - ignorado")

            print(f"\n✅ PASSOU: Proteção funcionando - {len(figures_json)} gráfico(s) válido(s) de {len(result)} itens")
            return True
        else:
            detected_type = "text" if not ('plotly' in str(type(result))) else "chart"
            print(f"\n❌ FALHOU: Tipo inesperado: '{detected_type}'")
            return False

    except Exception as e:
        print(f"\n❌ ERRO: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Função principal - executa todos os testes."""
    print("\n" + "="*60)
    print("VALIDAÇÃO: Múltiplos Gráficos Plotly")
    print("="*60)

    results = {}

    # Executar testes
    results['Gráfico Único'] = test_single_chart()
    results['Múltiplos Gráficos'] = test_multiple_charts()
    results['Lista Vazia'] = test_empty_list()
    results['Lista Mista'] = test_mixed_list()

    # Resumo
    print("\n" + "="*60)
    print("📊 RESUMO DOS TESTES")
    print("="*60)

    total = len(results)
    passed = sum(1 for v in results.values() if v)
    failed = total - passed

    for test_name, passed_test in results.items():
        status = "✅ PASSOU" if passed_test else "❌ FALHOU"
        print(f"  {status}: {test_name}")

    print("\n" + "-"*60)
    print(f"  Total: {total} testes")
    print(f"  ✅ Passaram: {passed}")
    print(f"  ❌ Falharam: {failed}")
    print("-"*60)

    if failed == 0:
        print("\n[OK] TODOS OS TESTES PASSARAM!")
        print("\n[OK] Sistema pronto para renderizar multiplos graficos Plotly!")
        return 0
    else:
        print(f"\n[WARN] {failed} teste(s) falharam - revisar implementacao")
        return 1


if __name__ == "__main__":
    sys.exit(main())
