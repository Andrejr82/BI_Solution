"""
Script de Verificação de Dados (Data Integrity Check)
---------------------------------------------------
Este script carrega o arquivo admmat.parquet gerado e executa
uma série de consultas analíticas para validar os dados.
"""
import pandas as pd
from pathlib import Path
import sys

# Configurar encoding para Windows
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

PARQUET_FILE = Path(__file__).parent.parent / "data" / "parquet" / "admmat.parquet"

def verify_data():
    print("\n" + "="*70)
    print("  🔎 VERIFICANDO INTEGRIDADE DOS DADOS PARQUET")
    print("="*70 + "\n")

    if not PARQUET_FILE.exists():
        print(f"❌ Erro: Arquivo não encontrado em {PARQUET_FILE}")
        return

    try:
        # 1. Metadados (Leitura Leve)
        print("📂 Lendo metadados do Parquet...")
        pf = pd.read_parquet(PARQUET_FILE, engine='fastparquet') # Leitura inicial pode trazer tudo se não cuidar.
        # Melhor usar PyArrow direto ou engine fastparquet com columns
        
        # Vamos usar uma abordagem mais leve lendo apenas colunas necessárias para cada teste
        
        print(f"\n✅ Arquivo acessível!")
        
        # Obter info básica via fastparquet (se disponível) ou carregando minimo
        # Para simplificar e garantir memória, vamos ler só uma coluna para contagem
        df_count = pd.read_parquet(PARQUET_FILE, columns=['PRODUTO']) 
        total_rows = len(df_count)
        del df_count
        
        print(f"   • Total de Linhas: {total_rows:,}")
        
        # Ler colunas para verificar esquema
        # Leitura de 1 linha
        df_schema = pd.read_parquet(PARQUET_FILE, engine='fastparquet').head(0)
        print(f"   • Total de Colunas: {len(df_schema.columns)}")

        # 2. Verificação de Colunas Críticas
        # Atualizado com base no schema real: PRODUTO, NOME, VENDA_30DD, ESTOQUE_UNE
        cols_check = ['PRODUTO', 'NOME', 'VENDA_30DD', 'ESTOQUE_UNE']
        print("\n🧐 Verificando colunas críticas:")
        missing_cols = [c for c in cols_check if c not in df_schema.columns]
        if missing_cols:
            print(f"   ❌ Colunas faltando: {missing_cols}")
        else:
            print(f"   ✅ Todas as colunas críticas encontradas: {cols_check}")

        # 3. Consultas de Teste (Queries BI)
        print("\n📊 Executando Consultas de Teste (Otimizadas)...")
        
        # Query A: Top 5 Produtos por Venda (Ler apenas NOME e VENDA_30DD)
        if 'VENDA_30DD' in df_schema.columns and 'NOME' in df_schema.columns:
            print("\n   🔹 Top 5 Produtos por Venda (30 dias):")
            df_sales = pd.read_parquet(PARQUET_FILE, columns=['NOME', 'VENDA_30DD'])
            top_sales = df_sales.nlargest(5, 'VENDA_30DD')
            for idx, row in top_sales.iterrows():
                print(f"      - {row['NOME'].strip()}: {row['VENDA_30DD']}")
            
            total_sales = df_sales['VENDA_30DD'].sum()
            print(f"\n   🔹 Venda Total Acumulada (30 dias): {total_sales:,.2f}")
            del df_sales

        # Query B: Estoque Total
        if 'ESTOQUE_UNE' in df_schema.columns:
            df_stock = pd.read_parquet(PARQUET_FILE, columns=['ESTOQUE_UNE'])
            # ESTOQUE_UNE parece ser string based on schema error (string), converter se necessario
            # Mas vamos tentar ler e converter
            df_stock['ESTOQUE_UNE'] = pd.to_numeric(df_stock['ESTOQUE_UNE'], errors='coerce')
            total_stock = df_stock['ESTOQUE_UNE'].sum()
            print(f"   🔹 Estoque Total (UNE): {total_stock:,.0f}")
            del df_stock

        print("\n" + "="*70)
        print("  ✅ VERIFICAÇÃO CONCLUÍDA")
        print("="*70)

    except Exception as e:
        print(f"\n❌ Erro ao ler arquivo: {e}")

if __name__ == "__main__":
    verify_data()
