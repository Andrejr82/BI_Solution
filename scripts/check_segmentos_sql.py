"""Verificar segmentos disponiveis no SQL Server"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from dotenv import load_dotenv
load_dotenv()

import pyodbc
import os

print("=" * 80)
print("  VERIFICANDO SEGMENTOS NO SQL SERVER")
print("=" * 80)

# Conectar ao SQL Server
connection_string = (
    f"DRIVER={{{os.getenv('DB_DRIVER')}}};"
    f"SERVER={os.getenv('DB_SERVER')};"
    f"DATABASE={os.getenv('DB_NAME')};"
    f"UID={os.getenv('DB_USER')};"
    f"PWD={os.getenv('DB_PASSWORD')}"
)

print("\n[1/4] Conectando ao SQL Server...")
conn = pyodbc.connect(connection_string)
cursor = conn.cursor()
print("[OK] Conectado!")

# Query 1: Buscar todos os segmentos
print("\n[2/4] Buscando segmentos disponiveis...")
query_segmentos = """
SELECT DISTINCT nomesegmento
FROM admatao
ORDER BY nomesegmento
"""
cursor.execute(query_segmentos)
segmentos = [row[0] for row in cursor.fetchall()]

print(f"\n[INFO] Total de segmentos: {len(segmentos)}")
print("\nSegmentos disponiveis:")
for i, seg in enumerate(segmentos, 1):
    # Destacar se tem TECIDO no nome
    if 'TECIDO' in str(seg).upper():
        print(f"  {i:2}. {seg} <--- TEM TECIDO!")
    else:
        print(f"  {i:2}. {seg}")

# Query 2: Verificar se existe segmento com TECIDO
print("\n[3/4] Buscando produtos com TECIDO no segmento...")
query_tecidos = """
SELECT TOP 10
    nome_produto,
    codigo,
    vendas_total,
    nomesegmento
FROM admatao
WHERE nomesegmento LIKE '%TECIDO%'
ORDER BY vendas_total DESC
"""
cursor.execute(query_tecidos)
produtos_tecidos = cursor.fetchall()

if produtos_tecidos:
    print(f"\n[OK] Encontrados {len(produtos_tecidos)} produtos com TECIDO")
    print("\nTop 10 produtos do segmento TECIDOS:")
    print("-" * 80)

    for i, (nome, codigo, vendas, segmento) in enumerate(produtos_tecidos, 1):
        print(f"\n{i}. {nome}")
        print(f"   Codigo: {codigo}")
        print(f"   Vendas: {vendas:,.0f} unidades")
        print(f"   Segmento: {segmento}")

    print("\n" + "=" * 80)
    print("  PRODUTO MAIS VENDIDO EM TECIDOS:")
    print("=" * 80)
    nome, codigo, vendas, segmento = produtos_tecidos[0]
    print(f"\nNome: {nome}")
    print(f"Codigo: {codigo}")
    print(f"Vendas: {vendas:,.0f} unidades")
    print(f"Segmento: {segmento}")
else:
    print("\n[AVISO] NENHUM produto encontrado com TECIDO no segmento")

# Query 3: Estatísticas gerais
print("\n[4/4] Estatisticas gerais do banco...")
query_stats = """
SELECT
    COUNT(DISTINCT codigo) as total_produtos,
    COUNT(DISTINCT une) as total_unes,
    SUM(vendas_total) as vendas_totais
FROM admatao
"""
cursor.execute(query_stats)
total_produtos, total_unes, vendas_totais = cursor.fetchone()

print(f"\nTotal de produtos: {total_produtos:,}")
print(f"Total de UNEs: {total_unes}")
print(f"Vendas totais: R$ {vendas_totais:,.2f}")

cursor.close()
conn.close()

print("\n" + "=" * 80)
print("  CONCLUSAO")
print("=" * 80)

tem_tecidos = any('TECIDO' in str(seg).upper() for seg in segmentos)
if tem_tecidos:
    print("\n[OK] Segmento TECIDOS existe no banco de dados")
    print("[OK] Query sobre TECIDOS DEVERIA funcionar")
else:
    print("\n[AVISO] Segmento TECIDOS NAO existe no banco")
    print("[INFO] Usuario pode ter perguntado sobre segmento inexistente")

print("\n" + "=" * 80)
