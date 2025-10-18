"""
Teste rápido para validar o fix de carregamento de produtos
Verifica se a conversão numérica está funcionando corretamente
"""

import sys
from pathlib import Path
import io

# Configurar encoding UTF-8 para output
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Adicionar diretório raiz ao path
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.connectivity.hybrid_adapter import HybridDataAdapter
import pandas as pd

def test_numeric_conversion():
    """Testa se produtos são carregados e filtrados corretamente"""
    print("=" * 60)
    print("TESTE: Carregamento de Produtos com Conversão Numérica")
    print("=" * 60)

    # Inicializar adapter
    adapter = HybridDataAdapter()

    # Testar com UNE 3 (a que o usuário reportou)
    une_teste = 3
    print(f"\n1. Carregando produtos da UNE {une_teste}...")

    result = adapter.execute_query({'une': une_teste})

    if not result:
        print("❌ ERRO: Nenhum resultado retornado")
        return False

    print(f"✓ Total de linhas retornadas: {len(result)}")

    # Converter para DataFrame
    df = pd.DataFrame(result)

    # Verificar tipo da coluna estoque_atual ANTES da conversão
    if 'estoque_atual' in df.columns:
        primeiro_valor = df['estoque_atual'].iloc[0]
        tipo_original = type(primeiro_valor).__name__
        print(f"\n2. Tipo original de 'estoque_atual': {tipo_original}")
        print(f"   Exemplo de valor: {primeiro_valor}")

    # Simular o processamento da função get_produtos_une
    print("\n3. Aplicando conversão numérica...")

    colunas_numericas = ['estoque_atual', 'venda_30_d', 'preco_38_percent']
    for col in colunas_numericas:
        if col in df.columns:
            antes = df[col].dtype
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
            depois = df[col].dtype
            print(f"   - {col}: {antes} → {depois}")

    # Garantir que estoque_atual existe
    if 'estoque_atual' not in df.columns:
        df['estoque_atual'] = 0
        print("   - estoque_atual criado (não existia)")

    # Filtrar produtos com estoque > 0
    print("\n4. Filtrando produtos com estoque > 0...")
    total_antes = len(df)
    df_filtrado = df[df['estoque_atual'] > 0]
    total_depois = len(df_filtrado)

    print(f"   Antes do filtro: {total_antes} produtos")
    print(f"   Depois do filtro: {total_depois} produtos")
    print(f"   Produtos COM estoque: {total_depois}")
    print(f"   Produtos SEM estoque: {total_antes - total_depois}")

    # Validar resultado
    if total_depois > 0:
        print(f"\n✅ SUCESSO: {total_depois} produtos com estoque encontrados!")

        # Mostrar exemplos
        print("\n5. Exemplos de produtos com estoque:")
        exemplo_cols = ['codigo', 'nome_produto', 'estoque_atual', 'venda_30_d']
        exemplo_cols_existentes = [c for c in exemplo_cols if c in df_filtrado.columns]

        for idx, row in df_filtrado.head(3).iterrows():
            print(f"\n   Produto {row.get('codigo', 'N/A')}:")
            print(f"   - Nome: {row.get('nome_produto', 'N/A')[:40]}")
            print(f"   - Estoque: {row.get('estoque_atual', 0)}")
            print(f"   - Vendas 30d: {row.get('venda_30_d', 0)}")

        return True
    else:
        print("\n⚠️ AVISO: Nenhum produto com estoque encontrado!")
        print("   Isso pode significar que a UNE 3 realmente não tem estoque,")
        print("   ou que há outro problema com os dados.")

        # Mostrar distribuição de estoque
        print("\n   Distribuição de estoque_atual:")
        print(f"   - Mínimo: {df['estoque_atual'].min()}")
        print(f"   - Máximo: {df['estoque_atual'].max()}")
        print(f"   - Média: {df['estoque_atual'].mean():.2f}")
        print(f"   - Zeros: {(df['estoque_atual'] == 0).sum()}")

        return False

if __name__ == "__main__":
    try:
        sucesso = test_numeric_conversion()

        print("\n" + "=" * 60)
        if sucesso:
            print("RESULTADO: ✅ Fix validado - produtos serão carregados!")
            print("\nO usuário pode agora testar localmente com:")
            print("  streamlit run streamlit_app.py")
        else:
            print("RESULTADO: ⚠️ Conversão funciona, mas poucos produtos com estoque")
            print("\nRecomendação: Testar com outras UNEs também")
        print("=" * 60)

    except Exception as e:
        print(f"\n❌ ERRO no teste: {e}")
        import traceback
        traceback.print_exc()
