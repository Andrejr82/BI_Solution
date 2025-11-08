"""
Analise completa do produto 369947 na UNE 2720 (MAD)
Verificar todas as colunas disponiveis
"""
import polars as pl
import sys
from pathlib import Path

# Configurar encoding UTF-8
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

sys.path.insert(0, str(Path(__file__).parent))

def analise_produto():
    """Analise detalhada do produto 369947 na UNE 2720"""

    print("=" * 80)
    print("ANALISE DETALHADA: Produto 369947 na UNE MAD (2720)")
    print("=" * 80)

    # Carregar dados
    df = pl.read_parquet("data/parquet/admmat.parquet")

    # Buscar produto especifico na UNE
    produto = df.filter(
        (pl.col('codigo') == 369947) & (pl.col('une') == 2720)
    )

    if len(produto) == 0:
        print("\n[ERRO] Produto nao encontrado!")
        return

    print(f"\n[OK] Produto encontrado: {len(produto)} registro(s)")

    # Mostrar TODAS as colunas e valores
    print("\n" + "=" * 80)
    print("TODAS AS COLUNAS E VALORES DO PRODUTO 369947 NA UNE 2720:")
    print("=" * 80)

    # Converter para dict para visualizacao melhor
    produto_dict = produto.to_dicts()[0]

    # Categorizar colunas
    categorias = {
        'identificacao': [],
        'preco_custo': [],
        'preco_venda': [],
        'margem': [],
        'vendas': [],
        'estoque': [],
        'movimentacao': [],
        'classificacao': [],
        'outros': []
    }

    for col, valor in produto_dict.items():
        col_lower = col.lower()

        # Identificacao
        if any(x in col_lower for x in ['id', 'codigo', 'une', 'nome', 'tipo']):
            categorias['identificacao'].append((col, valor))

        # Preco e custo
        elif any(x in col_lower for x in ['preco', 'custo', 'valor', 'price', 'cost']):
            categorias['preco_custo'].append((col, valor))

        # Margem
        elif any(x in col_lower for x in ['mc', 'margem', 'markup', 'lucro', 'rentab']):
            categorias['margem'].append((col, valor))

        # Vendas
        elif any(x in col_lower for x in ['venda', 'vd', 'fat', 'receita']):
            categorias['vendas'].append((col, valor))

        # Estoque
        elif any(x in col_lower for x in ['estoque', 'saldo', 'qtde', 'quantidade']):
            categorias['estoque'].append((col, valor))

        # Movimentacao
        elif any(x in col_lower for x in ['entrada', 'saida', 'movimento', 'invent']):
            categorias['movimentacao'].append((col, valor))

        # Classificacao
        elif any(x in col_lower for x in ['abc', 'class', 'categoria']):
            categorias['classificacao'].append((col, valor))

        else:
            categorias['outros'].append((col, valor))

    # Imprimir por categoria
    for categoria, colunas in categorias.items():
        if colunas:
            print(f"\n{categoria.upper()}:")
            print("-" * 80)
            for col, valor in sorted(colunas):
                # Formatacao especial para valores null
                if valor is None:
                    valor_str = "[NULL]"
                elif isinstance(valor, float):
                    valor_str = f"{valor:,.2f}"
                else:
                    valor_str = str(valor)

                print(f"  {col:40s} : {valor_str}")

    # Resumo dos valores importantes
    print("\n" + "=" * 80)
    print("RESUMO - VALORES CRITICOS PARA CALCULO DE MC:")
    print("=" * 80)

    valores_criticos = {}

    # Tentar identificar colunas-chave
    for col in df.columns:
        col_lower = col.lower()
        if any(x in col_lower for x in ['preco', 'custo', 'margem', 'mc', 'valor']):
            valor = produto_dict.get(col)
            if valor is not None and valor != 0:
                valores_criticos[col] = valor

    if valores_criticos:
        print("\nColunas com valores nao-nulos/zeros:")
        for col, valor in sorted(valores_criticos.items()):
            if isinstance(valor, float):
                print(f"  {col:40s} : {valor:,.2f}")
            else:
                print(f"  {col:40s} : {valor}")
    else:
        print("\n[ALERTA] Nenhuma coluna de preco/custo/margem com valor!")

    # Estatisticas gerais da UNE 2720
    print("\n" + "=" * 80)
    print("ESTATISTICAS DA UNE 2720 (MAD):")
    print("=" * 80)

    une_2720 = df.filter(pl.col('une') == 2720)
    print(f"\nTotal de produtos na UNE: {len(une_2720):,}")

    # Ver quais colunas tem dados na UNE
    print("\nColunas com dados nao-nulos na UNE 2720:")
    for col in df.columns:
        n_nulos = une_2720[col].null_count()
        n_nao_nulos = len(une_2720) - n_nulos
        if n_nao_nulos > 0:
            perc = (n_nao_nulos / len(une_2720)) * 100
            if any(x in col.lower() for x in ['preco', 'custo', 'margem', 'mc', 'valor', 'venda']):
                print(f"  {col:40s} : {n_nao_nulos:6,} registros ({perc:5.1f}%)")

    print("\n" + "=" * 80)

if __name__ == "__main__":
    analise_produto()
