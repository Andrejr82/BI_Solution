"""
Diagnostico completo do erro: Produto 369947 nao encontrado na UNE MAD (2720)
"""
import polars as pl
import sys
from pathlib import Path

# Configurar encoding UTF-8 para output
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Adicionar path do projeto
sys.path.insert(0, str(Path(__file__).parent))

def diagnostico_completo():
    """Analise profunda do problema"""

    print("=" * 80)
    print("DIAGNOSTICO: Produto 369947 - UNE MAD (2720)")
    print("=" * 80)

    # 1. Carregar Parquet
    parquet_path = Path("data/parquet/admmat.parquet")
    print(f"\n1. Carregando {parquet_path}...")

    try:
        df = pl.read_parquet(parquet_path)
        print(f"   [OK] Carregado: {len(df):,} linhas x {len(df.columns)} colunas")
    except Exception as e:
        print(f"   [ERRO] ao carregar: {e}")
        return

    # 2. Verificar colunas
    print("\n2. Estrutura de colunas:")
    print(f"   Total: {len(df.columns)}")

    # Colunas relacionadas a codigo/produto
    cod_cols = [c for c in df.columns if 'cod' in c.lower() or 'produto' in c.lower()]
    print(f"\n   Colunas de codigo/produto: {cod_cols}")

    # Colunas relacionadas a UNE
    une_cols = [c for c in df.columns if 'une' in c.lower()]
    print(f"   Colunas UNE: {une_cols}")

    # Colunas relacionadas a MC
    mc_cols = [c for c in df.columns if 'mc' in c.lower() or 'margem' in c.lower()]
    print(f"   Colunas MC/Margem: {mc_cols}")

    # 3. Amostra dos dados
    print("\n3. Amostra de dados (primeiras 3 linhas):")
    cols_relevantes = list(set(cod_cols + une_cols + mc_cols))
    if cols_relevantes:
        print(df.select(cols_relevantes).head(3))

    # 4. Buscar produto 369947
    print("\n4. Buscando produto 369947...")

    # Testar em cada coluna de código
    for col in cod_cols:
        try:
            # Converter para string para comparação segura
            resultado = df.filter(pl.col(col).cast(pl.Utf8) == "369947")

            if len(resultado) > 0:
                print(f"\n   [OK] ENCONTRADO em coluna '{col}': {len(resultado)} registro(s)")
                print(f"\n   Dados do produto:")
                print(resultado.select(cols_relevantes if cols_relevantes else df.columns[:10]))

                # Verificar UNEs associadas
                if une_cols:
                    print(f"\n   UNEs associadas:")
                    for une_col in une_cols:
                        valores_une = resultado[une_col].unique().to_list()
                        print(f"      {une_col}: {valores_une}")
            else:
                print(f"   [X] NAO encontrado em '{col}'")
        except Exception as e:
            print(f"   [X] Erro ao buscar em '{col}': {e}")

    # 5. Verificar se existe UNE 2720 (MAD)
    print("\n5. Verificando UNE 2720 (MAD)...")

    for une_col in une_cols:
        try:
            # Buscar registros com UNE 2720
            une_mad = df.filter(pl.col(une_col).cast(pl.Utf8) == "2720")

            if len(une_mad) > 0:
                print(f"\n   [OK] UNE 2720 existe em '{une_col}': {len(une_mad):,} registros")

                # Verificar se produto 369947 esta nesta UNE
                for cod_col in cod_cols:
                    try:
                        prod_na_une = une_mad.filter(pl.col(cod_col).cast(pl.Utf8) == "369947")
                        if len(prod_na_une) > 0:
                            print(f"\n   [OK][OK] PRODUTO 369947 ENCONTRADO NA UNE 2720!")
                            print(f"      Coluna codigo: {cod_col}")
                            print(f"      Coluna UNE: {une_col}")
                            print("\n   Dados completos:")
                            print(prod_na_une)

                            # Calcular MC se disponivel
                            if mc_cols:
                                print(f"\n   Margem de Contribuicao:")
                                for mc_col in mc_cols:
                                    if mc_col in prod_na_une.columns:
                                        mc_value = prod_na_une[mc_col][0]
                                        print(f"      {mc_col}: {mc_value}")
                        else:
                            print(f"   [X] Produto 369947 NAO esta na UNE 2720 (testado em '{cod_col}')")
                    except Exception as e:
                        print(f"   [X] Erro ao verificar produto em '{cod_col}': {e}")
            else:
                print(f"   [X] UNE 2720 NAO encontrada em '{une_col}'")
        except Exception as e:
            print(f"   [X] Erro ao buscar UNE em '{une_col}': {e}")

    # 6. Tipos de dados
    print("\n6. Tipos de dados das colunas principais:")
    for col in cols_relevantes[:10]:  # Limitar a 10 colunas
        if col in df.columns:
            print(f"   {col}: {df[col].dtype}")

    # 7. Estatisticas
    print("\n7. Estatisticas gerais:")
    print(f"   Total de produtos unicos:")
    for cod_col in cod_cols:
        try:
            n_unique = df[cod_col].n_unique()
            print(f"      {cod_col}: {n_unique:,}")
        except:
            pass

    print(f"\n   Total de UNEs unicas:")
    for une_col in une_cols:
        try:
            n_unique = df[une_col].n_unique()
            print(f"      {une_col}: {n_unique:,}")
        except:
            pass

    print("\n" + "=" * 80)
    print("FIM DO DIAGNOSTICO")
    print("=" * 80)

if __name__ == "__main__":
    diagnostico_completo()
