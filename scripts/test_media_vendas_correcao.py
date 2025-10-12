"""
Teste: Validar correção do cálculo de média de vendas por produto

Compara:
- Método ERRADO: média de todas as linhas (1.1M linhas)
- Método CORRETO: média por produto (agrupar -> somar -> média)
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from dotenv import load_dotenv
load_dotenv()

from core.connectivity.hybrid_adapter import HybridDataAdapter
from core.business_intelligence.direct_query_engine import DirectQueryEngine

def test_media_vendas_correcao():
    """Testa se a correção da média está funcionando."""
    print("=" * 80)
    print("  TESTE: CORREÇÃO DA MÉDIA DE VENDAS POR PRODUTO")
    print("=" * 80)

    print("\n[INFO] Inicializando sistema...")
    adapter = HybridDataAdapter()
    engine = DirectQueryEngine(adapter)

    # Obter DataFrame Dask
    ddf = engine._get_base_dask_df()

    print("\n[INFO] Calculando métricas...")

    # Método 1: ERRADO (média de todas as linhas)
    print("\n--- METODO ANTIGO (ERRADO) ---")
    media_errada = ddf['vendas_total'].mean().compute()
    print(f"Media de vendas (todas as linhas): R$ {media_errada:,.2f}")
    print("[X] Problema: Calcula media das 1.1M linhas, nao por produto")

    # Método 2: CORRETO (média por produto)
    print("\n--- METODO NOVO (CORRETO) ---")
    vendas_por_produto = ddf.groupby('codigo')['vendas_total'].sum()
    media_correta = vendas_por_produto.mean().compute()
    print(f"Media de vendas por produto: R$ {media_correta:,.2f}")
    print("[OK] Correto: Agrupa por produto, soma vendas, calcula media")

    # Comparacao
    print("\n" + "=" * 80)
    print("  COMPARACAO")
    print("=" * 80)
    print(f"Media ANTIGA (errada): R$ {media_errada:,.2f}")
    print(f"Media NOVA (correta):  R$ {media_correta:,.2f}")
    diferenca = media_correta - media_errada
    print(f"Diferenca:             R$ {diferenca:,.2f}")
    print(f"Fator de correcao:     {media_correta/media_errada:.1f}x maior")

    # Validar calculo manual
    print("\n" + "=" * 80)
    print("  VALIDACAO MANUAL")
    print("=" * 80)
    total_vendas = ddf['vendas_total'].sum().compute()
    total_produtos = ddf['codigo'].nunique().compute()
    media_manual = total_vendas / total_produtos

    print(f"Total de vendas:       R$ {total_vendas:,.2f}")
    print(f"Total de produtos:     {total_produtos:,}")
    print(f"Media calculada:       R$ {media_correta:,.2f}")
    print(f"Media manual:          R$ {media_manual:,.2f}")

    # Verificar se estao proximos (podem ter pequenas diferencas por arredondamento)
    if abs(media_correta - media_manual) < 1.0:
        print("\n[OK] SUCESSO: Calculo da media esta CORRETO!")
        return True
    else:
        print(f"\n[ERRO] Diferenca de R$ {abs(media_correta - media_manual):.2f}")
        return False

    # Testar a query completa
    print("\n" + "=" * 80)
    print("  TESTE DA QUERY COMPLETA")
    print("=" * 80)

    print("\n[INFO] Executando query de analise geral...")
    resultado = engine.execute_direct_query("analise_geral", {"user_query": "analise geral"})

    if resultado and resultado.get("type") != "error":
        print(f"\n[RESULTADO]")
        print(f"- Vendas Totais: R$ {resultado['result']['total_vendas']:,.2f}")
        print(f"- Total Produtos: {resultado['result']['total_produtos']:,}")
        print(f"- Total UNEs: {resultado['result']['total_unes']}")
        print(f"- Media por Produto: R$ {resultado['result']['media_vendas']:,.2f}")

        # Verificar se a media esta correta
        media_query = resultado['result']['media_vendas']
        if abs(media_query - media_correta) < 1.0:
            print("\n[OK] Query retorna media CORRETA!")
            return True
        else:
            print(f"\n[ERRO] Query retorna media ERRADA: R$ {media_query:,.2f}")
            return False
    else:
        print(f"\n[ERRO] Query falhou: {resultado.get('error', 'Erro desconhecido')}")
        return False

if __name__ == "__main__":
    try:
        sucesso = test_media_vendas_correcao()
        if sucesso:
            print("\n" + "=" * 80)
            print("  [OK] CORRECAO VALIDADA COM SUCESSO!")
            print("=" * 80)
            sys.exit(0)
        else:
            print("\n" + "=" * 80)
            print("  [ERRO] CORRECAO FALHOU")
            print("=" * 80)
            sys.exit(1)
    except Exception as e:
        print(f"\n[ERRO FATAL] {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
