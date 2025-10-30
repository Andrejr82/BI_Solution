"""
Script para consultar UNEs do banco de dados SQL Server
e gerar mapeamento atualizado.
"""
import pyodbc
import os
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()

def get_unes_from_database():
    """Consulta todas as UNEs do banco de dados"""

    # Configurações do banco
    server = os.getenv('DB_HOST', 'FAMILIA\\SQLJR')
    database = os.getenv('DB_NAME', 'Projeto_Caculinha')
    username = os.getenv('DB_USER', 'AgenteVirtual')
    password = os.getenv('DB_PASSWORD')
    driver = os.getenv('DB_DRIVER', 'ODBC Driver 17 for SQL Server')

    # String de conexão
    conn_str = (
        f"DRIVER={{{driver}}};"
        f"SERVER={server};"
        f"DATABASE={database};"
        f"UID={username};"
        f"PWD={password};"
        f"TrustServerCertificate=yes;"
    )

    try:
        print("Conectando ao SQL Server...")
        conn = pyodbc.connect(conn_str, timeout=10)
        cursor = conn.cursor()

        # Consultar UNEs distintas da tabela principal
        query = """
        SELECT DISTINCT
            UNE as codigo,
            NOMEUNE as nome
        FROM admmat
        WHERE UNE IS NOT NULL
            AND NOMEUNE IS NOT NULL
        ORDER BY UNE
        """

        print("Consultando UNEs...")
        cursor.execute(query)

        unes = []
        for row in cursor.fetchall():
            codigo = str(row.codigo).strip()
            nome = str(row.nome).strip()
            unes.append((codigo, nome))
            print(f"  {codigo}: {nome}")

        cursor.close()
        conn.close()

        print(f"\nTotal de UNEs encontradas: {len(unes)}")
        return unes

    except Exception as e:
        print(f"ERRO ao consultar banco: {e}")
        return None

def generate_mapping_code(unes):
    """Gera código Python para o mapeamento"""

    if not unes:
        print("ERRO: Nenhuma UNE para gerar mapeamento")
        return None

    # Dicionário UNE_MAP (siglas e variações)
    une_map_lines = []
    une_names_lines = []

    for codigo, nome in unes:
        # Extrair sigla do nome (ex: "MAD - MADRID" -> "MAD")
        parts = nome.split('-')
        if len(parts) >= 2:
            sigla = parts[0].strip()
            nome_completo = parts[1].strip() if len(parts) > 1 else nome
        else:
            sigla = nome[:3].upper()  # Primeiras 3 letras
            nome_completo = nome

        # Adicionar ao UNE_MAP
        une_map_lines.append(f'    "{sigla.lower()}": "{codigo}",')
        une_map_lines.append(f'    "{nome_completo.lower()}": "{codigo}",')
        une_map_lines.append(f'    "une {sigla.lower()}": "{codigo}",')

        # Adicionar ao UNE_NAMES
        une_names_lines.append(f'    "{codigo}": "{sigla} - {nome_completo}",')

    print("\n" + "="*60)
    print("MAPEAMENTO GERADO")
    print("="*60)

    print("\n# UNE_MAP:")
    print("UNE_MAP = {")
    for line in une_map_lines:
        print(line)
    print("}")

    print("\n# UNE_NAMES:")
    print("UNE_NAMES = {")
    for line in une_names_lines:
        print(line)
    print("}")

    return une_map_lines, une_names_lines

if __name__ == "__main__":
    import sys
    import io
    # Configurar encoding UTF-8
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

    print("="*60)
    print("CONSULTA DE UNEs DO BANCO DE DADOS")
    print("="*60)
    print()

    unes = get_unes_from_database()

    if unes:
        generate_mapping_code(unes)

        # Salvar em arquivo
        output_file = "data/reports/unes_from_db.txt"
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write("UNEs do Banco de Dados\n")
            f.write("="*60 + "\n\n")
            for codigo, nome in unes:
                f.write(f"{codigo}: {nome}\n")

        print(f"\nLista salva em: {output_file}")
    else:
        print("\nFalha ao obter UNEs do banco")
