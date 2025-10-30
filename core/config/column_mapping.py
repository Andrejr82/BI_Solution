"""
Mapeamento Oficial de Colunas do Parquet
Sistema: Agent_Solution_BI
Data: 2025-10-25

Este módulo contém o mapeamento entre nomes legados (código antigo) e nomes reais
das colunas do Parquet. Usado para normalizar queries e evitar erros de KeyError.

FONTE: Extraído diretamente do Parquet real (97 colunas)
"""

# ==================== MAPEAMENTO PRINCIPAL ====================
# Mapeamento: Nome Legado → Nome Real no Parquet
COLUMN_MAP = {
    # Colunas básicas do produto
    "PRODUTO": "codigo",
    "CODIGO": "codigo",
    "NOME": "nome_produto",
    "NOME_PRODUTO": "nome_produto",

    # UNE
    "UNE": "une",
    "UNE_NOME": "une_nome",
    "NOMEUNE": "une_nome",

    # Classificações
    "NOMESEGMENTO": "nomesegmento",
    "SEGMENTO": "nomesegmento",
    "NOMEGRUPO": "nomegrupo",
    "GRUPO": "nomegrupo",
    "NOMECATEGORIA": "NOMECATEGORIA",  # Já está MAIÚSCULO no Parquet
    "CATEGORIA": "NOMECATEGORIA",
    "NOMESUBGRUPO": "NOMESUBGRUPO",  # Já está MAIÚSCULO no Parquet
    "SUBGRUPO": "NOMESUBGRUPO",
    "NOMEFABRICANTE": "NOMEFABRICANTE",  # Já está MAIÚSCULO no Parquet
    "FABRICANTE": "NOMEFABRICANTE",

    # Vendas
    "VENDA_30DD": "venda_30_d",
    "VENDA_30D": "venda_30_d",
    "VENDA_30_DIAS": "venda_30_d",
    "VENDAS_30D": "venda_30_d",

    # Estoque (5 variações)
    "ESTOQUE": "estoque_atual",  # Padrão
    "ESTOQUE_UNE": "estoque_atual",
    "ESTOQUE_ATUAL": "estoque_atual",
    "ESTOQUE_LV": "estoque_lv",
    "ESTOQUE_LINHA_VERDE": "estoque_lv",
    "ESTOQUE_CD": "estoque_cd",
    "ESTOQUE_GONDOLA": "estoque_gondola_lv",
    "ESTOQUE_ILHA": "estoque_ilha_lv",

    # Preços
    "LIQUIDO_38": "preco_38_percent",
    "PRECO_38": "preco_38_percent",
    "PRECO_LIQUIDO_38": "preco_38_percent",
    "PRECO": "preco_38_percent",

    # Médias
    "MC": "media_considerada_lv",
    "MEDIA": "media_considerada_lv",
    "MEDIA_CONSIDERADA": "media_considerada_lv",
    "MEDIA_CONSIDERADA_LV": "media_considerada_lv",
    "MEDIA_TRAVADA": "media_travada",

    # ABC (Classificação)
    "ABC_UNE_30DD": "abc_une_30_dd",
    "ABC_30D": "abc_une_30_dd",
    "ABC_CACULA_90DD": "abc_cacula_90_dd",
    "ABC_90D": "abc_cacula_90_dd",

    # Outros
    "EAN": "ean",
    "EMBALAGEM": "embalagem",
    "TIPO": "tipo",
    "PROMOCIONAL": "promocional",
    "FORALINHA": "foralinha",
}

# ==================== MAPEAMENTO REVERSO ====================
# Nome Real → Informações da Coluna
COLUMN_INFO = {
    "codigo": {
        "nome_legado": ["PRODUTO", "CODIGO"],
        "descricao": "Código único do produto",
        "tipo": "int",
        "exemplo": "704559",
        "nullable": False,
    },
    "nome_produto": {
        "nome_legado": ["NOME", "NOME_PRODUTO"],
        "descricao": "Nome completo do produto",
        "tipo": "str",
        "exemplo": "ALCA BOLSA 7337 DIAM.105MM PS MESCLADO 810",
        "nullable": False,
    },
    "une": {
        "nome_legado": ["UNE"],
        "descricao": "Código da Unidade de Negócio",
        "tipo": "int",
        "exemplo": "2586",
        "nullable": False,
    },
    "une_nome": {
        "nome_legado": ["UNE_NOME", "NOMEUNE"],
        "descricao": "Nome da UNE (ex: NIG, MAD, SCR)",
        "tipo": "str",
        "exemplo": "NIG",
        "nullable": False,
    },
    "nomesegmento": {
        "nome_legado": ["NOMESEGMENTO", "SEGMENTO"],
        "descricao": "Segmento do produto",
        "tipo": "str",
        "exemplo": "ARMARINHO E CONFECÇÃO",
        "nullable": False,
    },
    "nomegrupo": {
        "nome_legado": ["NOMEGRUPO", "GRUPO"],
        "descricao": "Grupo do produto",
        "tipo": "str",
        "exemplo": "FERRAGEM",
        "nullable": True,
    },
    "NOMECATEGORIA": {
        "nome_legado": ["NOMECATEGORIA", "CATEGORIA"],
        "descricao": "Categoria do produto",
        "tipo": "str",
        "exemplo": "ACABAMENTOS CONFECÇÃO",
        "nullable": True,
    },
    "NOMESUBGRUPO": {
        "nome_legado": ["NOMESUBGRUPO", "SUBGRUPO"],
        "descricao": "Subgrupo do produto",
        "tipo": "str",
        "exemplo": "SIMPLES",
        "nullable": True,
    },
    "NOMEFABRICANTE": {
        "nome_legado": ["NOMEFABRICANTE", "FABRICANTE"],
        "descricao": "Nome do fabricante",
        "tipo": "str",
        "exemplo": "KR AVIAMENTOS",
        "nullable": True,
    },
    "venda_30_d": {
        "nome_legado": ["VENDA_30DD", "VENDA_30D", "VENDA_30_DIAS"],
        "descricao": "Vendas dos últimos 30 dias (em unidades)",
        "tipo": "float",
        "exemplo": "2.5",
        "nullable": True,
    },
    "estoque_atual": {
        "nome_legado": ["ESTOQUE", "ESTOQUE_UNE", "ESTOQUE_ATUAL"],
        "descricao": "Estoque atual total da UNE",
        "tipo": "float",
        "exemplo": "15.0",
        "nullable": True,
    },
    "estoque_lv": {
        "nome_legado": ["ESTOQUE_LV", "ESTOQUE_LINHA_VERDE"],
        "descricao": "Estoque na Linha Verde (área de venda)",
        "tipo": "float",
        "exemplo": "5.0",
        "nullable": True,
    },
    "estoque_cd": {
        "nome_legado": ["ESTOQUE_CD"],
        "descricao": "Estoque no Centro de Distribuição",
        "tipo": "float",
        "exemplo": "100.0",
        "nullable": True,
    },
    "preco_38_percent": {
        "nome_legado": ["LIQUIDO_38", "PRECO_38", "PRECO"],
        "descricao": "Preço líquido com 38% de margem",
        "tipo": "float",
        "exemplo": "12.99",
        "nullable": True,
    },
    "media_considerada_lv": {
        "nome_legado": ["MC", "MEDIA", "MEDIA_CONSIDERADA"],
        "descricao": "Média de vendas considerada para reposição",
        "tipo": "float",
        "exemplo": "2.3",
        "nullable": True,
    },
}

# ==================== COLUNAS ESSENCIAIS ====================
# Colunas mínimas necessárias para análises básicas
ESSENTIAL_COLUMNS = [
    'codigo',           # Identificação do produto
    'nome_produto',     # Nome do produto
    'une',              # UNE (código)
    'une_nome',         # UNE (nome) - ESSENCIAL para rankings
    'nomesegmento',     # Segmento
    'venda_30_d',       # Vendas
    'estoque_atual',    # Estoque
    'preco_38_percent', # Preço
    'nomegrupo'         # Grupo
]

# ==================== FUNÇÕES AUXILIARES ====================

def normalize_column_name(column_name: str) -> str:
    """
    Normaliza nome de coluna (legado → real).

    Args:
        column_name: Nome da coluna (pode ser legado ou real)

    Returns:
        Nome real da coluna ou o próprio nome se não encontrado

    Examples:
        >>> normalize_column_name("PRODUTO")
        "codigo"
        >>> normalize_column_name("VENDA_30DD")
        "venda_30_d"
        >>> normalize_column_name("codigo")
        "codigo"
    """
    # Se já é um nome real, retornar
    if column_name in COLUMN_INFO:
        return column_name

    # Tentar encontrar no mapeamento
    upper_name = column_name.upper()
    return COLUMN_MAP.get(upper_name, column_name)


def get_column_info(column_name: str) -> dict:
    """
    Retorna informações sobre uma coluna.

    Args:
        column_name: Nome da coluna (real ou legado)

    Returns:
        Dicionário com informações ou None

    Example:
        >>> get_column_info("PRODUTO")
        {"nome_legado": ["PRODUTO"], "descricao": "Código único...", ...}
    """
    real_name = normalize_column_name(column_name)
    return COLUMN_INFO.get(real_name)


def validate_columns(columns: list, df_columns: list) -> dict:
    """
    Valida se colunas existem no DataFrame.

    Args:
        columns: Lista de colunas a validar
        df_columns: Lista de colunas disponíveis no DataFrame

    Returns:
        {"valid": [...], "invalid": [...], "suggestions": {...}}

    Example:
        >>> validate_columns(["PRODUTO", "VENDA_30DD"], df.columns)
        {"valid": ["codigo", "venda_30_d"], "invalid": [], "suggestions": {}}
    """
    valid = []
    invalid = []
    suggestions = {}

    for col in columns:
        normalized = normalize_column_name(col)

        if normalized in df_columns:
            valid.append(normalized)
        else:
            invalid.append(col)
            # Sugerir colunas similares
            similar = [c for c in df_columns if col.lower() in c.lower() or c.lower() in col.lower()]
            if similar:
                suggestions[col] = similar[:3]  # Top 3 sugestões

    return {
        "valid": valid,
        "invalid": invalid,
        "suggestions": suggestions
    }


def get_essential_columns() -> list:
    """
    Retorna lista de colunas essenciais.

    Returns:
        Lista com nomes reais das colunas essenciais
    """
    return ESSENTIAL_COLUMNS.copy()


def list_all_columns() -> list:
    """
    Lista todas as colunas conhecidas com suas informações.

    Returns:
        Lista de tuplas (nome_real, descricao)
    """
    return [(name, info["descricao"]) for name, info in COLUMN_INFO.items()]


if __name__ == "__main__":
    # Testes
    import sys
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

    print("=== Teste de Mapeamento de Colunas ===\n")

    test_cases = [
        "PRODUTO",
        "VENDA_30DD",
        "ESTOQUE_UNE",
        "LIQUIDO_38",
        "NOMESEGMENTO",
        "codigo",  # Já normalizado
        "COLUNA_INEXISTENTE"
    ]

    for col in test_cases:
        normalized = normalize_column_name(col)
        info = get_column_info(col)

        if info:
            print(f"OK '{col}' -> '{normalized}'")
            print(f"   Descricao: {info['descricao']}")
            print(f"   Tipo: {info['tipo']}, Exemplo: {info['exemplo']}")
        else:
            print(f"AVISO '{col}' -> '{normalized}' (sem info adicional)")
        print()

    print(f"\nTotal de colunas mapeadas: {len(COLUMN_INFO)}")
    print(f"Colunas essenciais: {len(ESSENTIAL_COLUMNS)}")

    # Teste de validação
    print("\n=== Teste de Validacao ===")
    test_cols = ["PRODUTO", "VENDA_30DD", "COLUNA_FALSA"]
    mock_df_cols = ["codigo", "venda_30_d", "une", "nome_produto"]

    result = validate_columns(test_cols, mock_df_cols)
    print(f"Validas: {result['valid']}")
    print(f"Invalidas: {result['invalid']}")
    print(f"Sugestoes: {result['suggestions']}")
