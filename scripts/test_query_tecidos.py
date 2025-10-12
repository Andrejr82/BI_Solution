"""
Teste: Query específica sobre segmento TECIDOS
Valida se o sistema está respondendo corretamente queries com filtro de segmento
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from dotenv import load_dotenv
load_dotenv()

from datetime import datetime
from core.connectivity.hybrid_adapter import HybridDataAdapter
from core.business_intelligence.direct_query_engine import DirectQueryEngine

def test_query_tecidos():
    """Testa query: Qual produto mais vendeu no segmento TECIDOS?"""
    print("=" * 80)
    print("  TESTE: PRODUTO MAIS VENDIDO - SEGMENTO TECIDOS")
    print("=" * 80)
    print(f"Data/Hora: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}\n")

    print("[INFO] Inicializando sistema...")
    adapter = HybridDataAdapter()
    engine = DirectQueryEngine(adapter)

    # Teste 1: Query específica para segmento
    print("\n" + "-" * 80)
    print("TESTE 1: Query com filtro de segmento")
    print("-" * 80)

    pergunta = "Qual produto mais vendeu no segmento TECIDOS?"
    print(f"\n[PERGUNTA] {pergunta}")

    # Testar com diferentes tipos de query
    queries_testar = [
        {
            "tipo": "produto_mais_vendido_segmento",
            "params": {"segmento": "TECIDOS"},
            "descricao": "Query direta com segmento"
        },
        {
            "tipo": "produto_mais_vendido",
            "params": {"segmento": "TECIDOS"},
            "descricao": "Query produto_mais_vendido + segmento"
        },
        {
            "tipo": "analise_geral",
            "params": {"user_query": pergunta},
            "descricao": "Query analise_geral (pode estar sendo usada)"
        }
    ]

    for i, teste in enumerate(queries_testar, 1):
        print(f"\n--- Tentativa {i}: {teste['descricao']} ---")
        try:
            start = datetime.now()
            resultado = engine.execute_direct_query(
                teste["tipo"],
                teste["params"]
            )
            tempo = (datetime.now() - start).total_seconds()

            if resultado and resultado.get("type") != "error":
                print(f"[OK] Tempo: {tempo:.2f}s")
                print(f"[TITULO] {resultado.get('title', 'N/A')}")

                summary = resultado.get('summary', '')
                # Verificar se resposta menciona TECIDOS
                if 'TECIDOS' in summary.upper() or 'tecidos' in summary:
                    print(f"[SUCESSO] Resposta menciona TECIDOS!")
                    print(f"[RESPOSTA] {summary[:300]}...")
                else:
                    print(f"[PROBLEMA] Resposta NAO menciona TECIDOS (resposta generica?)")
                    print(f"[RESPOSTA] {summary[:300]}...")

                return resultado
            else:
                print(f"[ERRO] {resultado.get('error', 'Erro desconhecido')}")
        except Exception as e:
            print(f"[EXCECAO] {str(e)[:200]}")

    # Teste 2: Consulta manual para ver dados reais de TECIDOS
    print("\n" + "-" * 80)
    print("TESTE 2: Consulta manual no dataset (dados reais)")
    print("-" * 80)

    print("\n[INFO] Buscando produtos do segmento TECIDOS...")
    ddf = engine._get_base_dask_df()

    # Filtrar segmento TECIDOS
    ddf_tecidos = ddf[ddf['nomesegmento'].str.upper().str.contains('TECIDO', na=False)]

    # Contar produtos
    total_tecidos = len(ddf_tecidos)
    print(f"[INFO] Total de linhas com TECIDOS: {total_tecidos:,}")

    if total_tecidos > 0:
        # Pegar top 5 produtos
        print("\n[INFO] Calculando top 5 produtos do segmento TECIDOS...")
        top_tecidos = ddf_tecidos.nlargest(5, 'vendas_total')[
            ['nome_produto', 'vendas_total', 'nomesegmento']
        ].compute()

        print("\n[RESULTADO] Top 5 Produtos - Segmento TECIDOS:")
        print("-" * 80)
        for idx, row in top_tecidos.iterrows():
            print(f"{idx+1}. {row['nome_produto'][:60]}")
            print(f"   Vendas: {row['vendas_total']:,.0f} unidades")
            print(f"   Segmento: {row['nomesegmento']}")
            print()

        # Produto campeão
        campeao = top_tecidos.iloc[0]
        print("=" * 80)
        print("  RESPOSTA CORRETA ESPERADA:")
        print("=" * 80)
        print(f"\nProduto mais vendido no segmento TECIDOS:")
        print(f"Nome: {campeao['nome_produto']}")
        print(f"Vendas: {campeao['vendas_total']:,.0f} unidades")
        print(f"Segmento: {campeao['nomesegmento']}")
    else:
        print("\n[AVISO] Nenhum produto encontrado no segmento TECIDOS")
        print("[INFO] Verificando segmentos disponiveis...")

        segmentos = ddf['nomesegmento'].unique().compute()
        print(f"\n[INFO] Segmentos disponiveis no dataset:")
        for seg in sorted(segmentos)[:20]:
            print(f"  - {seg}")

    # Teste 3: Verificar se correcao da media esta ativa
    print("\n" + "-" * 80)
    print("TESTE 3: Verificar se correcao da media esta ativa")
    print("-" * 80)

    print("\n[INFO] Executando query analise_geral...")
    resultado_geral = engine.execute_direct_query("analise_geral", {"user_query": "analise geral"})

    if resultado_geral and resultado_geral.get("type") != "error":
        media = resultado_geral['result'].get('media_vendas', 0)
        print(f"\n[RESULTADO] Media de vendas por produto: R$ {media:,.2f}")

        if media < 100:
            print("[PROBLEMA] Media ainda esta ERRADA (R$ 44.87)")
            print("[CAUSA] Codigo nao foi recarregado ou cache antigo")
            print("[SOLUCAO] Reiniciar aplicacao Streamlit")
        else:
            print("[OK] Media esta CORRETA (R$ 499.72)")
            print("[SUCESSO] Correcao foi aplicada")

    print("\n" + "=" * 80)

if __name__ == "__main__":
    try:
        test_query_tecidos()
        print("\n[INFO] Teste concluido")
    except Exception as e:
        print(f"\n[ERRO FATAL] {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
