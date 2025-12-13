"""
Script para analisar a estrutura do admmat.parquet
e gerar documentação para o ChatBI
"""

import pandas as pd
import pyarrow.parquet as pq
from pathlib import Path
import json

def analyze_parquet_structure():
    """Analisa estrutura do arquivo Parquet"""
    
    parquet_path = Path("data/parquet/admmat.parquet")
    
    if not parquet_path.exists():
        print(f"❌ Arquivo não encontrado: {parquet_path}")
        return
    
    print("=" * 80)
    print("📊 ANÁLISE DO ARQUIVO admmat.parquet")
    print("=" * 80)
    
    # 1. Informações básicas do arquivo
    file_size_mb = parquet_path.stat().st_size / (1024 * 1024)
    print(f"\n📁 Tamanho do arquivo: {file_size_mb:.2f} MB")
    
    # 2. Ler schema com PyArrow
    print("\n📋 SCHEMA DO ARQUIVO:")
    print("-" * 80)
    parquet_file = pq.ParquetFile(parquet_path)
    schema = parquet_file.schema
    
    print(f"Total de colunas: {len(schema)}")
    print("\nColunas e tipos:")
    for i, field in enumerate(schema, 1):
        print(f"{i:3d}. {field.name:30s} | {field.type}")
    
    # 3. Ler amostra de dados
    print("\n" + "=" * 80)
    print("📊 AMOSTRA DE DADOS (primeiras 5 linhas)")
    print("=" * 80)
    
    df = pd.read_parquet(parquet_path)
    print(f"\nTotal de registros: {len(df):,}")
    print(f"Total de colunas: {len(df.columns)}")
    
    # Mostrar primeiras linhas
    print("\nPrimeiras 5 linhas:")
    print(df.head())
    
    # 4. Estatísticas por coluna
    print("\n" + "=" * 80)
    print("📈 ESTATÍSTICAS DAS COLUNAS")
    print("=" * 80)
    
    for col in df.columns:
        print(f"\n🔹 {col}")
        print(f"   Tipo: {df[col].dtype}")
        print(f"   Valores únicos: {df[col].nunique():,}")
        print(f"   Valores nulos: {df[col].isna().sum():,} ({df[col].isna().sum()/len(df)*100:.1f}%)")
        
        # Mostrar amostra de valores
        if df[col].dtype == 'object':
            unique_vals = df[col].dropna().unique()[:5]
            print(f"   Exemplos: {', '.join(map(str, unique_vals))}")
        elif df[col].dtype in ['int64', 'float64']:
            print(f"   Min: {df[col].min()}, Max: {df[col].max()}, Média: {df[col].mean():.2f}")
    
    # 5. Gerar documentação JSON
    print("\n" + "=" * 80)
    print("📝 GERANDO DOCUMENTAÇÃO")
    print("=" * 80)
    
    doc = {
        "arquivo": "admmat.parquet",
        "total_registros": len(df),
        "total_colunas": len(df.columns),
        "tamanho_mb": round(file_size_mb, 2),
        "colunas": []
    }
    
    for col in df.columns:
        col_info = {
            "nome": col,
            "tipo": str(df[col].dtype),
            "valores_unicos": int(df[col].nunique()),
            "valores_nulos": int(df[col].isna().sum()),
            "percentual_nulos": round(df[col].isna().sum()/len(df)*100, 2)
        }
        
        # Adicionar estatísticas específicas por tipo
        if df[col].dtype in ['int64', 'float64']:
            col_info["min"] = float(df[col].min()) if pd.notna(df[col].min()) else None
            col_info["max"] = float(df[col].max()) if pd.notna(df[col].max()) else None
            col_info["media"] = float(df[col].mean()) if pd.notna(df[col].mean()) else None
        elif df[col].dtype == 'object':
            unique_vals = df[col].dropna().unique()[:10]
            col_info["exemplos"] = [str(v) for v in unique_vals]
        
        doc["colunas"].append(col_info)
    
    # Salvar documentação
    output_path = Path("data/parquet/admmat_schema.json")
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(doc, f, indent=2, ensure_ascii=False)
    
    print(f"\n✅ Documentação salva em: {output_path}")
    
    return doc

if __name__ == "__main__":
    analyze_parquet_structure()
