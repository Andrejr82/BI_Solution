"""Teste simples: Buscar produtos do segmento TECIDOS"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from dotenv import load_dotenv
load_dotenv()

from core.connectivity.hybrid_adapter import HybridDataAdapter

print("=" * 80)
print("  BUSCANDO DADOS REAIS - SEGMENTO TECIDOS")
print("=" * 80)

print("\n[1/3] Conectando ao banco...")
adapter = HybridDataAdapter()
from core.business_intelligence.direct_query_engine import DirectQueryEngine
engine = DirectQueryEngine(adapter)
ddf = engine._get_base_dask_df()

print("[2/3] Buscando segmentos disponiveis...")
segmentos = ddf['nomesegmento'].unique().compute()
print(f"\n[INFO] Total de segmentos: {len(segmentos)}")
print("\nSegmentos disponiveis:")
for i, seg in enumerate(sorted(segmentos), 1):
    print(f"  {i:2}. {seg}")

print("\n[3/3] Buscando produtos com 'TECIDO' no nome do segmento...")
ddf_tecidos = ddf[ddf['nomesegmento'].str.upper().str.contains('TECIDO', na=False)]
total = len(ddf_tecidos)
print(f"\n[RESULTADO] Linhas com TECIDOS: {total:,}")

if total > 0:
    print("\n[INFO] Top 5 produtos do segmento TECIDOS:")
    print("-" * 80)

    top5 = ddf_tecidos.nlargest(5, 'vendas_total')[
        ['nome_produto', 'vendas_total', 'nomesegmento', 'codigo']
    ].compute()

    for idx, row in top5.iterrows():
        print(f"\n{idx+1}. {row['nome_produto']}")
        print(f"   Codigo: {row['codigo']}")
        print(f"   Vendas: {row['vendas_total']:,.0f} unidades")
        print(f"   Segmento: {row['nomesegmento']}")

    print("\n" + "=" * 80)
    print("  PRODUTO MAIS VENDIDO EM TECIDOS:")
    print("=" * 80)
    campeao = top5.iloc[0]
    print(f"\nNome: {campeao['nome_produto']}")
    print(f"Codigo: {campeao['codigo']}")
    print(f"Vendas: {campeao['vendas_total']:,.0f} unidades")
else:
    print("\n[AVISO] Nenhum produto encontrado com 'TECIDO' no segmento")
    print("\n[INFO] Verificando se existe segmento exato 'TECIDOS'...")

    tem_tecidos = any('TECIDO' in str(seg).upper() for seg in segmentos)
    if tem_tecidos:
        print("[INFO] Existe segmento com TECIDO no nome")
        tecido_segs = [s for s in segmentos if 'TECIDO' in str(s).upper()]
        for seg in tecido_segs:
            print(f"  - {seg}")
    else:
        print("[AVISO] NAO existe segmento TECIDOS no banco de dados")

print("\n" + "=" * 80)
