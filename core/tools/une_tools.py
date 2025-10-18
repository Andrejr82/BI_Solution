"""
Ferramentas LangChain para operações UNE.
Implementa regras de abastecimento, MC e política de preços.

Este módulo fornece ferramentas para:
- Cálculo de necessidades de abastecimento por UNE
- Consulta de MC (Média Comum) de produtos
- Cálculo de preços finais aplicando política de preços UNE
"""

from langchain_core.tools import tool
import pandas as pd
import os
import logging
from typing import Dict, Any, List, Optional
from functools import lru_cache

# Validadores integrados (v3.0)
from core.validators.schema_validator import SchemaValidator
from core.utils.query_validator import validate_columns, handle_nulls, safe_filter
from core.utils.error_handler import error_handler_decorator

logger = logging.getLogger(__name__)

# Flag para usar HybridAdapter (SQL/Parquet automático)
USE_HYBRID_ADAPTER = os.getenv("UNE_USE_HYBRID_ADAPTER", "true").lower() == "true"

# Mapeamento de colunas SQL Server → formato padrão
COLUMN_MAPPING_SQL = {
    'PRODUTO': 'codigo',
    'NOME': 'nome_produto',
    'UNE': 'une',
    'ESTOQUE_UNE': 'estoque_atual',
    'ESTOQUE_LV': 'linha_verde',
    'MEDIA_CONSIDERADA_LV': 'mc',
    'VENDA_30DD': 'venda_30_d',
    'NOMESEGMENTO': 'nomesegmento'
}

# Mapeamento de colunas Parquet padrão → formato padrão
COLUMN_MAPPING_PARQUET = {
    'estoque_lv': 'linha_verde',
    'media_considerada_lv': 'mc'
}

@lru_cache(maxsize=1)
def _get_data_adapter():
    """Retorna adapter de dados (HybridAdapter ou Parquet direto) com cache"""
    global USE_HYBRID_ADAPTER

    if USE_HYBRID_ADAPTER:
        try:
            from core.connectivity.hybrid_adapter import HybridDataAdapter
            adapter = HybridDataAdapter()
            logger.info(f"Usando HybridAdapter - fonte: {adapter.current_source}")
            return adapter
        except Exception as e:
            logger.warning(f"Erro ao inicializar HybridAdapter: {e}, usando Parquet direto")
            USE_HYBRID_ADAPTER = False

    # Fallback: usar Parquet direto
    PARQUET_PATH_EXTENDED = os.path.join(os.getcwd(), "data", "parquet", "admmat_extended.parquet")
    PARQUET_PATH_DEFAULT = os.path.join(os.getcwd(), "data", "parquet", "admmat.parquet")

    if os.path.exists(PARQUET_PATH_EXTENDED):
        return {'type': 'parquet', 'path': PARQUET_PATH_EXTENDED, 'extended': True}
    else:
        return {'type': 'parquet', 'path': PARQUET_PATH_DEFAULT, 'extended': False}

def _normalize_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """Normaliza DataFrame para ter colunas consistentes independente da fonte"""
    # Verificar se precisa mapear colunas SQL
    if 'PRODUTO' in df.columns:
        # Dados vieram do SQL Server
        for sql_col, std_col in COLUMN_MAPPING_SQL.items():
            if sql_col in df.columns and std_col not in df.columns:
                df[std_col] = df[sql_col]

    # Verificar se precisa mapear colunas Parquet padrão
    for parquet_col, std_col in COLUMN_MAPPING_PARQUET.items():
        if parquet_col in df.columns and std_col not in df.columns:
            df[std_col] = df[parquet_col]

    return df

def _load_data(filters: Dict[str, Any] = None, columns: List[str] = None) -> pd.DataFrame:
    """
    Carrega dados usando adapter apropriado (SQL ou Parquet) com validação

    Args:
        filters: Filtros a aplicar (ex: {'une': 2586, 'codigo': 369947})
        columns: Colunas específicas a carregar (otimização)

    Returns:
        DataFrame normalizado e validado
    """
    adapter = _get_data_adapter()

    # Validar schema se for Parquet direto
    if isinstance(adapter, dict):
        validator = SchemaValidator()
        is_valid, errors = validator.validate_parquet_file(adapter['path'])
        if not is_valid:
            logger.error(f"Schema inválido: {errors}")
            raise ValueError(f"Schema do arquivo Parquet inválido: {errors}")

    if isinstance(adapter, dict):
        # Parquet direto
        if columns:
            if not adapter['extended']:
                # Mapear colunas solicitadas para colunas do Parquet padrão
                parquet_cols = []
                for col in columns:
                    if col == 'linha_verde':
                        parquet_cols.append('estoque_lv')
                    elif col == 'mc':
                        parquet_cols.append('media_considerada_lv')
                    else:
                        parquet_cols.append(col)
                columns = parquet_cols

            df = pd.read_parquet(adapter['path'], columns=columns)
        else:
            df = pd.read_parquet(adapter['path'])

        # Aplicar filtros manualmente
        if filters:
            for col, val in filters.items():
                if col in df.columns:
                    df = df[df[col] == val]
    else:
        # HybridAdapter (SQL ou Parquet automático)
        # Se não há filtros e está usando Parquet, carregar arquivo direto
        if not filters and adapter.current_source == "parquet":
            logger.info("Carregando Parquet completo (sem filtros)")
            parquet_path = adapter.file_path

            if columns:
                # Mapear colunas padrão para colunas do Parquet
                parquet_cols = []
                for col in columns:
                    if col == 'linha_verde':
                        parquet_cols.append('estoque_lv')
                    elif col == 'mc':
                        parquet_cols.append('media_considerada_lv')
                    else:
                        parquet_cols.append(col)

                df = pd.read_parquet(parquet_path, columns=parquet_cols)
            else:
                df = pd.read_parquet(parquet_path)
        else:
            result = adapter.execute_query(filters or {})
            df = pd.DataFrame(result)

    # Normalizar colunas
    df = _normalize_dataframe(df)

    # Tratar nulls com validador (mais robusto)
    for col in ['estoque_atual', 'linha_verde', 'mc', 'venda_30_d']:
        if col in df.columns:
            df = handle_nulls(df, col, strategy="fill", fill_value=0)

    # Converter tipos com segurança (usando pandas)
    for col in ['estoque_atual', 'linha_verde', 'mc', 'venda_30_d']:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)

    return df


@tool
@error_handler_decorator(
    context_func=lambda une_id, segmento=None: {"une_id": une_id, "segmento": segmento, "funcao": "calcular_abastecimento_une"},
    return_on_error={"error": "Erro ao calcular abastecimento", "total_produtos": 0, "produtos": []}
)
def calcular_abastecimento_une(une_id: int, segmento: str = None) -> Dict[str, Any]:
    """
    Calcula produtos que precisam de abastecimento em uma UNE.

    Regra aplicada: ESTOQUE_UNE <= 50% LINHA_VERDE

    Args:
        une_id: ID da UNE (1-10)
        segmento: Filtro opcional por segmento (ex: "TECIDOS", "PAPELARIA")

    Returns:
        dict com:
        - total_produtos: int (total de produtos que precisam abastecimento)
        - produtos: list[dict] (top 20 produtos ordenados por qtd_a_abastecer DESC)
        - regra_aplicada: str (descrição da regra de abastecimento)
        - une_id: int
        - segmento: str (se aplicado)

    Example:
        >>> result = calcular_abastecimento_une(une_id=1, segmento="TECIDOS")
        >>> print(f"Total produtos: {result['total_produtos']}")
    """
    # Validação de inputs
    if not isinstance(une_id, int) or une_id <= 0:
        return {"error": "une_id deve ser um inteiro positivo"}

    # Carregar dados com validação integrada
    logger.info(f"Carregando dados de abastecimento para UNE {une_id}")
    df = _load_data(filters={'une': une_id})

    # Validar colunas necessárias
    required_cols = ['une', 'codigo', 'nome_produto', 'estoque_atual', 'linha_verde']
    is_valid, missing = validate_columns(df, required_cols)
    if not is_valid:
        return {"error": f"Colunas ausentes: {missing}"}

    # Filtrar por UNE com segurança
    df_une = safe_filter(df, 'une', une_id)

    if df_une.empty:
        return {
            "error": f"Nenhum produto encontrado para UNE {une_id}",
            "une_id": une_id
        }

    # Filtrar por segmento (se fornecido)
    if segmento:
        if 'nomesegmento' in df_une.columns:
            df_une = df_une[
                df_une['nomesegmento'].str.contains(segmento, case=False, na=False)
            ]
            if df_une.empty:
                return {
                    "error": f"Nenhum produto encontrado para segmento '{segmento}' na UNE {une_id}",
                    "une_id": une_id,
                    "segmento": segmento
                }
        else:
            logger.warning("Coluna 'nomesegmento' não encontrada no dataset")

    # Filtrar produtos que precisam abastecimento
    if 'precisa_abastecimento' not in df_une.columns:
        return {"error": "Coluna 'precisa_abastecimento' não encontrada no dataset"}

    df_abastecer = df_une[df_une['precisa_abastecimento'] == True].copy()

    total_produtos = len(df_abastecer)

    if total_produtos == 0:
        return {
            "total_produtos": 0,
            "produtos": [],
            "regra_aplicada": "ESTOQUE_UNE <= 50% LINHA_VERDE",
            "une_id": une_id,
            "segmento": segmento if segmento else "Todos",
            "mensagem": "Nenhum produto precisa de abastecimento no momento"
        }

    # Ordenar por qtd_a_abastecer DESC e pegar top 20
    df_abastecer = df_abastecer.sort_values('qtd_a_abastecer', ascending=False)
    top_20 = df_abastecer.head(20)

    # Preparar lista de produtos
    produtos = []
    for _, row in top_20.iterrows():
        produto = {
            "codigo": int(row['codigo']) if pd.notna(row['codigo']) else None,
            "nome_produto": str(row['nome_produto']) if pd.notna(row['nome_produto']) else "N/A",
            "segmento": str(row['nomesegmento']) if 'nomesegmento' in row and pd.notna(row['nomesegmento']) else "N/A",
            "estoque_atual": float(row['estoque_atual']) if pd.notna(row['estoque_atual']) else 0.0,
            "linha_verde": float(row['linha_verde']) if pd.notna(row['linha_verde']) else 0.0,
            "qtd_a_abastecer": float(row['qtd_a_abastecer']) if pd.notna(row['qtd_a_abastecer']) else 0.0,
            "percentual_estoque": round((float(row['estoque_atual']) / float(row['linha_verde']) * 100), 2) if pd.notna(row['linha_verde']) and row['linha_verde'] > 0 else 0.0
        }
        produtos.append(produto)

    logger.info(f"Encontrados {total_produtos} produtos para abastecimento na UNE {une_id}")

    return {
        "total_produtos": total_produtos,
        "produtos": produtos,
        "regra_aplicada": "ESTOQUE_UNE <= 50% LINHA_VERDE",
        "une_id": une_id,
        "segmento": segmento if segmento else "Todos"
    }


@tool
def calcular_mc_produto(produto_id: int, une_id: int) -> Dict[str, Any]:
    """
    Retorna informações de MC (Média Comum) de um produto em uma UNE específica.

    A MC representa a média de vendas do produto, usada para dimensionar
    o estoque adequado em gôndola.

    Args:
        produto_id: Código do produto
        une_id: ID da UNE (1-10)

    Returns:
        dict com:
        - produto_id: int
        - nome: str
        - segmento: str
        - mc_calculada: float (Média Comum)
        - estoque_atual: float
        - linha_verde: float (estoque máximo)
        - estoque_gondola: float (se existir na base)
        - percentual_linha_verde: float (% do estoque em relação à linha verde)
        - recomendacao: str (orientação de abastecimento)

    Example:
        >>> result = calcular_mc_produto(produto_id=12345, une_id=1)
        >>> print(f"MC: {result['mc_calculada']}, Recomendação: {result['recomendacao']}")
    """
    try:
        # Validação de inputs
        if not isinstance(produto_id, int) or produto_id <= 0:
            return {"error": "produto_id deve ser um inteiro positivo"}

        if not isinstance(une_id, int) or une_id <= 0:
            return {"error": "une_id deve ser um inteiro positivo"}

        if not os.path.exists(PARQUET_PATH):
            return {"error": f"Arquivo não encontrado: {PARQUET_PATH}"}

        # Carregar dados do Parquet
        logger.info(f"Buscando MC do produto {produto_id} na UNE {une_id}")
        df = pd.read_parquet(PARQUET_PATH)

        # Filtrar por produto e UNE
        produto_df = df[(df['codigo'] == produto_id) & (df['une'] == une_id)]

        if produto_df.empty:
            return {
                "error": f"Produto {produto_id} não encontrado na UNE {une_id}",
                "produto_id": produto_id,
                "une_id": une_id
            }

        # Pegar primeira linha (deve ser única)
        row = produto_df.iloc[0]

        # Extrair dados
        mc_calculada = float(row['mc']) if pd.notna(row['mc']) else 0.0
        estoque_atual = float(row['estoque_atual']) if pd.notna(row['estoque_atual']) else 0.0
        linha_verde = float(row['linha_verde']) if pd.notna(row['linha_verde']) else 0.0

        # Estoque gôndola (se existir)
        estoque_gondola = None
        if 'ESTOQUE_GONDOLA' in row:
            estoque_gondola = float(row['ESTOQUE_GONDOLA']) if pd.notna(row['ESTOQUE_GONDOLA']) else 0.0
        elif 'estoque_gondola' in row:
            estoque_gondola = float(row['estoque_gondola']) if pd.notna(row['estoque_gondola']) else 0.0

        # Calcular percentual da linha verde
        percentual_linha_verde = 0.0
        if linha_verde > 0:
            percentual_linha_verde = round((estoque_atual / linha_verde) * 100, 2)

        # Gerar recomendação
        recomendacao = "Manter estoque atual"

        if estoque_gondola is not None and mc_calculada > estoque_gondola:
            recomendacao = "Aumentar ESTOQUE em gôndola - MC superior ao estoque atual"
        elif percentual_linha_verde < 50:
            recomendacao = "URGENTE: Abastecer produto - Estoque abaixo de 50% da linha verde"
        elif percentual_linha_verde < 75:
            recomendacao = "ATENÇÃO: Planejar abastecimento - Estoque entre 50% e 75% da linha verde"
        elif percentual_linha_verde > 100:
            recomendacao = "ALERTA: Estoque acima da linha verde - Verificar dimensionamento"

        resultado = {
            "produto_id": int(produto_id),
            "une_id": int(une_id),
            "nome": str(row['nome_produto']) if pd.notna(row['nome_produto']) else "N/A",
            "segmento": str(row['nomesegmento']) if 'nomesegmento' in row and pd.notna(row['nomesegmento']) else "N/A",
            "mc_calculada": mc_calculada,
            "estoque_atual": estoque_atual,
            "linha_verde": linha_verde,
            "percentual_linha_verde": percentual_linha_verde,
            "recomendacao": recomendacao
        }

        # Adicionar estoque_gondola se existir
        if estoque_gondola is not None:
            resultado["estoque_gondola"] = estoque_gondola

        logger.info(f"MC calculada para produto {produto_id}: {mc_calculada}")

        return resultado

    except Exception as e:
        logger.error(f"Erro em calcular_mc_produto: {e}", exc_info=True)
        return {"error": f"Erro ao calcular MC do produto: {str(e)}"}


@tool
def calcular_preco_final_une(valor_compra: float, ranking: int, forma_pagamento: str) -> Dict[str, Any]:
    """
    Calcula preço final aplicando política de preços UNE.

    Regras de Tipo de Preço:
    - Valor >= R$ 750,00 → Preço Atacado
    - Valor < R$ 750,00 → Preço Varejo

    Política por Ranking:
    - Ranking 0: Atacado 38%, Varejo 30%
    - Ranking 1: Preço único 38% (independente do valor)
    - Ranking 2: Atacado 38%, Varejo 30%
    - Ranking 3: Sem desconto (preço tabela)
    - Ranking 4: Atacado 38%, Varejo 24%

    Desconto por Forma de Pagamento:
    - 'vista': 38%
    - '30d': 36%
    - '90d': 34%
    - '120d': 30%

    Args:
        valor_compra: Valor total da compra em reais
        ranking: Classificação do produto (0-4)
        forma_pagamento: Tipo de pagamento ('vista', '30d', '90d', '120d')

    Returns:
        dict com:
        - valor_original: float
        - tipo: str ("Atacado" ou "Varejo")
        - ranking: int
        - desconto_ranking: str (percentual aplicado pelo ranking)
        - forma_pagamento: str
        - desconto_pagamento: str (percentual por forma de pagamento)
        - preco_final: float
        - economia: float (valor economizado)
        - detalhamento: str (explicação do cálculo)

    Example:
        >>> result = calcular_preco_final_une(valor_compra=1000.0, ranking=0, forma_pagamento='vista')
        >>> print(f"Preço final: R$ {result['preco_final']:.2f}")
    """
    try:
        # Validação de inputs
        if not isinstance(valor_compra, (int, float)) or valor_compra <= 0:
            return {"error": "valor_compra deve ser um número positivo"}

        if not isinstance(ranking, int) or ranking < 0 or ranking > 4:
            return {"error": "ranking deve ser um inteiro entre 0 e 4"}

        formas_validas = ['vista', '30d', '90d', '120d']
        if forma_pagamento not in formas_validas:
            return {"error": f"forma_pagamento deve ser uma das opções: {', '.join(formas_validas)}"}

        valor_original = float(valor_compra)

        # Determinar tipo de preço (Atacado ou Varejo)
        tipo_preco = "Atacado" if valor_compra >= 750.0 else "Varejo"

        # Definir desconto por ranking
        desconto_ranking_percent = 0.0

        if ranking == 0:
            desconto_ranking_percent = 38.0 if tipo_preco == "Atacado" else 30.0
        elif ranking == 1:
            desconto_ranking_percent = 38.0  # Preço único
            tipo_preco = "Único"  # Override para ranking 1
        elif ranking == 2:
            desconto_ranking_percent = 38.0 if tipo_preco == "Atacado" else 30.0
        elif ranking == 3:
            desconto_ranking_percent = 0.0  # Sem desconto
        elif ranking == 4:
            desconto_ranking_percent = 38.0 if tipo_preco == "Atacado" else 24.0

        # Aplicar desconto do ranking
        valor_apos_ranking = valor_original * (1 - desconto_ranking_percent / 100)

        # Definir desconto por forma de pagamento
        descontos_pagamento = {
            'vista': 38.0,
            '30d': 36.0,
            '90d': 34.0,
            '120d': 30.0
        }

        desconto_pagamento_percent = descontos_pagamento[forma_pagamento]

        # Aplicar desconto de forma de pagamento sobre o valor após desconto de ranking
        valor_final = valor_apos_ranking * (1 - desconto_pagamento_percent / 100)

        # Calcular economia total
        economia = valor_original - valor_final

        # Gerar detalhamento do cálculo
        detalhamento_partes = [
            f"Valor original: R$ {valor_original:.2f}",
            f"Tipo de preço: {tipo_preco} (valor {'>=' if valor_compra >= 750 else '<'} R$ 750,00)"
        ]

        if desconto_ranking_percent > 0:
            detalhamento_partes.append(
                f"Desconto ranking {ranking}: {desconto_ranking_percent}% -> R$ {valor_apos_ranking:.2f}"
            )
        else:
            detalhamento_partes.append(
                f"Ranking {ranking}: Sem desconto (preço tabela)"
            )

        detalhamento_partes.append(
            f"Desconto pagamento ({forma_pagamento}): {desconto_pagamento_percent}% -> R$ {valor_final:.2f}"
        )
        detalhamento_partes.append(
            f"Economia total: R$ {economia:.2f} ({(economia/valor_original)*100:.2f}%)"
        )

        detalhamento = " | ".join(detalhamento_partes)

        logger.info(
            f"Preço calculado: R$ {valor_original:.2f} -> R$ {valor_final:.2f} "
            f"(Ranking {ranking}, {forma_pagamento})"
        )

        return {
            "valor_original": round(valor_original, 2),
            "tipo": tipo_preco,
            "ranking": ranking,
            "desconto_ranking": f"{desconto_ranking_percent}%" if desconto_ranking_percent > 0 else "Sem desconto",
            "forma_pagamento": forma_pagamento,
            "desconto_pagamento": f"{desconto_pagamento_percent}%",
            "preco_final": round(valor_final, 2),
            "economia": round(economia, 2),
            "percentual_economia": round((economia / valor_original) * 100, 2),
            "detalhamento": detalhamento
        }

    except Exception as e:
        logger.error(f"Erro em calcular_preco_final_une: {e}", exc_info=True)
        return {"error": f"Erro ao calcular preço final: {str(e)}"}


@tool
def validar_transferencia_produto(
    produto_id: int,
    une_origem: int,
    une_destino: int,
    quantidade: int
) -> Dict[str, Any]:
    """
    Valida se uma transferência de produto entre UNEs é viável e recomendada.

    Aplica regras de negócio para verificar:
    - Se UNE origem tem estoque suficiente
    - Se UNE destino realmente precisa do produto
    - Se a quantidade está dentro dos limites adequados
    - Se a transferência é prioritária baseada em linha verde e MC

    Args:
        produto_id: Código do produto a transferir
        une_origem: ID da UNE que vai enviar o produto
        une_destino: ID da UNE que vai receber o produto
        quantidade: Quantidade a transferir

    Returns:
        dict com:
        - valido: bool (se a transferência é válida)
        - prioridade: str ("URGENTE", "ALTA", "NORMAL", "BAIXA", "NAO_RECOMENDADA")
        - pode_transferir: int (quantidade máxima que pode ser transferida)
        - pode_receber: int (quantidade máxima que destino pode receber)
        - quantidade_recomendada: int (quantidade ideal para transferir)
        - score_prioridade: float (0-100, quanto maior mais prioritária)
        - motivo: str (justificativa da validação)
        - detalhes_origem: dict (dados do produto na origem)
        - detalhes_destino: dict (dados do produto no destino)
        - recomendacoes: list[str] (ações sugeridas)

    Example:
        >>> result = validar_transferencia_produto(12345, une_origem=1, une_destino=2, quantidade=50)
        >>> if result['valido']:
        ...     print(f"Transferência válida com prioridade {result['prioridade']}")
    """
    try:
        # Validação de inputs
        if not isinstance(produto_id, int) or produto_id <= 0:
            return {"error": "produto_id deve ser um inteiro positivo", "valido": False}

        if not isinstance(une_origem, int) or une_origem <= 0:
            return {"error": "une_origem deve ser um inteiro positivo", "valido": False}

        if not isinstance(une_destino, int) or une_destino <= 0:
            return {"error": "une_destino deve ser um inteiro positivo", "valido": False}

        if une_origem == une_destino:
            return {"error": "UNE origem e destino não podem ser iguais", "valido": False}

        if not isinstance(quantidade, int) or quantidade <= 0:
            return {"error": "quantidade deve ser um inteiro positivo", "valido": False}

        # Carregar dados usando adapter apropriado
        logger.info(f"Validando transferência: Produto {produto_id}, UNE {une_origem} -> {une_destino}, Qtd: {quantidade}")

        try:
            # Carregar apenas dados necessários (otimizado)
            colunas_necessarias = [
                'codigo', 'nome_produto', 'une', 'estoque_atual', 'linha_verde',
                'mc', 'venda_30_d', 'nomesegmento'
            ]

            # Filtrar por produto e UNEs específicas para otimizar
            df = _load_data(
                filters={'codigo': produto_id},
                columns=colunas_necessarias
            )

            # Filtrar apenas origem e destino
            df = df[df['une'].isin([une_origem, une_destino])]

        except Exception as e:
            logger.error(f"Erro ao carregar dados: {e}")
            return {"error": f"Erro ao acessar dados: {str(e)}", "valido": False}

        # Buscar produto na UNE origem
        origem_df = df[(df['codigo'] == produto_id) & (df['une'] == une_origem)]
        if origem_df.empty:
            return {
                "valido": False,
                "motivo": f"Produto {produto_id} não encontrado na UNE origem {une_origem}",
                "produto_id": produto_id,
                "une_origem": une_origem,
                "une_destino": une_destino
            }

        # Buscar produto na UNE destino
        destino_df = df[(df['codigo'] == produto_id) & (df['une'] == une_destino)]
        if destino_df.empty:
            return {
                "valido": False,
                "motivo": f"Produto {produto_id} não encontrado na UNE destino {une_destino}",
                "produto_id": produto_id,
                "une_origem": une_origem,
                "une_destino": une_destino
            }

        # Extrair dados da origem
        origem = origem_df.iloc[0]
        estoque_origem = float(origem['estoque_atual']) if pd.notna(origem['estoque_atual']) else 0.0
        linha_verde_origem = float(origem['linha_verde']) if pd.notna(origem['linha_verde']) else 0.0
        mc_origem = float(origem['mc']) if pd.notna(origem['mc']) else 0.0

        # Extrair dados do destino
        destino = destino_df.iloc[0]
        estoque_destino = float(destino['estoque_atual']) if pd.notna(destino['estoque_atual']) else 0.0
        linha_verde_destino = float(destino['linha_verde']) if pd.notna(destino['linha_verde']) else 0.0
        mc_destino = float(destino['mc']) if pd.notna(destino['mc']) else 0.0
        venda_30d_destino = float(destino['venda_30_d']) if pd.notna(destino['venda_30_d']) else 0.0

        # Calcular percentuais de linha verde
        perc_origem = (estoque_origem / linha_verde_origem * 100) if linha_verde_origem > 0 else 0.0
        perc_destino = (estoque_destino / linha_verde_destino * 100) if linha_verde_destino > 0 else 0.0

        # Calcular quantidades possíveis
        # Origem pode transferir até o excesso acima da linha verde (se houver)
        pode_transferir = max(0, int(estoque_origem - linha_verde_origem)) if perc_origem > 100 else 0

        # Se não tem excesso, mas tem estoque razoável (>75%), pode transferir parte
        if pode_transferir == 0 and perc_origem > 75:
            pode_transferir = max(0, int(estoque_origem * 0.25))  # Até 25% do estoque

        # Destino pode receber até atingir linha verde
        pode_receber = max(0, int(linha_verde_destino - estoque_destino))

        # Quantidade recomendada (mínimo entre o que pode transferir e o que precisa receber)
        quantidade_recomendada = min(pode_transferir, pode_receber) if pode_transferir > 0 and pode_receber > 0 else 0

        # Validar se tem estoque suficiente na origem
        if estoque_origem < quantidade:
            return {
                "valido": False,
                "motivo": f"Estoque insuficiente na origem. Disponível: {estoque_origem:.0f}, Solicitado: {quantidade}",
                "produto_id": produto_id,
                "une_origem": une_origem,
                "une_destino": une_destino,
                "estoque_origem": estoque_origem,
                "quantidade_solicitada": quantidade
            }

        # Verificar se transferência vai deixar origem em situação crítica
        estoque_origem_apos = estoque_origem - quantidade
        perc_origem_apos = (estoque_origem_apos / linha_verde_origem * 100) if linha_verde_origem > 0 else 0.0

        if perc_origem_apos < 50:
            return {
                "valido": False,
                "motivo": f"Transferência deixaria origem com estoque crítico ({perc_origem_apos:.1f}% da linha verde)",
                "produto_id": produto_id,
                "une_origem": une_origem,
                "une_destino": une_destino,
                "estoque_origem_atual": estoque_origem,
                "estoque_origem_apos": estoque_origem_apos,
                "percentual_apos": perc_origem_apos
            }

        # Calcular score de prioridade (0-100)
        score_prioridade = 0.0

        # Fator 1: Necessidade do destino (0-40 pontos)
        if perc_destino < 25:
            score_prioridade += 40
        elif perc_destino < 50:
            score_prioridade += 30
        elif perc_destino < 75:
            score_prioridade += 20
        else:
            score_prioridade += 5

        # Fator 2: Excesso na origem (0-30 pontos)
        if perc_origem > 150:
            score_prioridade += 30
        elif perc_origem > 125:
            score_prioridade += 20
        elif perc_origem > 100:
            score_prioridade += 10

        # Fator 3: MC e vendas do destino (0-30 pontos)
        if venda_30d_destino > 0:
            dias_estoque_destino = estoque_destino / (venda_30d_destino / 30) if venda_30d_destino > 0 else 999
            if dias_estoque_destino < 7:
                score_prioridade += 30
            elif dias_estoque_destino < 15:
                score_prioridade += 20
            elif dias_estoque_destino < 30:
                score_prioridade += 10

        # Determinar prioridade baseada no score
        if score_prioridade >= 80:
            prioridade = "URGENTE"
        elif score_prioridade >= 60:
            prioridade = "ALTA"
        elif score_prioridade >= 40:
            prioridade = "NORMAL"
        elif score_prioridade >= 20:
            prioridade = "BAIXA"
        else:
            prioridade = "NAO_RECOMENDADA"

        # Gerar recomendações
        recomendacoes = []

        if quantidade != quantidade_recomendada and quantidade_recomendada > 0:
            recomendacoes.append(f"Sugerimos transferir {quantidade_recomendada} unidades ao invés de {quantidade}")

        if perc_destino < 25:
            recomendacoes.append("CRÍTICO: Destino com estoque muito baixo - transferência urgente")

        if perc_origem > 150:
            recomendacoes.append("Origem com excesso significativo - boa oportunidade para balanceamento")

        if mc_destino > estoque_destino:
            recomendacoes.append("MC do destino > estoque atual - produto de alta demanda")

        if not recomendacoes:
            recomendacoes.append("Transferência dentro dos padrões normais")

        # Preparar resultado
        resultado = {
            "valido": True,
            "produto_id": int(produto_id),
            "nome_produto": str(origem['nome_produto']) if pd.notna(origem['nome_produto']) else "N/A",
            "une_origem": int(une_origem),
            "une_destino": int(une_destino),
            "quantidade_solicitada": int(quantidade),
            "prioridade": prioridade,
            "score_prioridade": round(score_prioridade, 2),
            "pode_transferir": int(pode_transferir),
            "pode_receber": int(pode_receber),
            "quantidade_recomendada": int(quantidade_recomendada),
            "motivo": f"Transferência válida com prioridade {prioridade}",
            "detalhes_origem": {
                "estoque_atual": estoque_origem,
                "linha_verde": linha_verde_origem,
                "percentual_linha_verde": round(perc_origem, 2),
                "mc": mc_origem,
                "estoque_apos_transferencia": estoque_origem - quantidade,
                "percentual_apos": round(perc_origem_apos, 2)
            },
            "detalhes_destino": {
                "estoque_atual": estoque_destino,
                "linha_verde": linha_verde_destino,
                "percentual_linha_verde": round(perc_destino, 2),
                "mc": mc_destino,
                "venda_30d": venda_30d_destino,
                "estoque_apos_transferencia": estoque_destino + quantidade,
                "percentual_apos": round((estoque_destino + quantidade) / linha_verde_destino * 100, 2) if linha_verde_destino > 0 else 0
            },
            "recomendacoes": recomendacoes
        }

        logger.info(f"Validação concluída: {prioridade} - Score: {score_prioridade:.2f}")
        return resultado

    except Exception as e:
        logger.error(f"Erro em validar_transferencia_produto: {e}", exc_info=True)
        return {"error": f"Erro ao validar transferência: {str(e)}", "valido": False}


@tool
def sugerir_transferencias_automaticas(limite: int = 20, une_origem_filtro: int = None) -> Dict[str, Any]:
    """
    Sugere transferências automáticas entre UNEs baseadas em regras de negócio.

    Identifica oportunidades de balanceamento de estoque considerando:
    - UNEs com excesso de estoque (>100% linha verde)
    - UNEs com falta de estoque (<50% linha verde)
    - MC (Média Comum) e histórico de vendas
    - Priorização por criticidade

    Args:
        limite: Número máximo de sugestões a retornar (default: 20)
        une_origem_filtro: Filtrar sugestões apenas desta UNE origem (opcional)

    Returns:
        dict com:
        - total_sugestoes: int
        - sugestoes: list[dict] (sugestões ordenadas por prioridade)
        - estatisticas: dict (resumo das sugestões)

    Cada sugestão contém:
        - produto_id: int
        - nome_produto: str
        - une_origem: int
        - une_destino: int
        - quantidade_sugerida: int
        - prioridade: str
        - score: float
        - motivo: str
        - beneficio_estimado: str

    Example:
        >>> result = sugerir_transferencias_automaticas(limite=10, une_origem_filtro=3116)
        >>> for sug in result['sugestoes']:
        ...     print(f"{sug['nome_produto']}: UNE {sug['une_origem']} -> {sug['une_destino']}")
    """
    try:
        if not isinstance(limite, int) or limite <= 0:
            return {"error": "limite deve ser um inteiro positivo"}

        if une_origem_filtro is not None and (not isinstance(une_origem_filtro, int) or une_origem_filtro <= 0):
            return {"error": "une_origem_filtro deve ser um inteiro positivo ou None"}

        logger.info(f"Gerando sugestões automáticas de transferências (limite: {limite})")

        try:
            # OTIMIZAÇÃO: Usar PyArrow diretamente para carregar dataset completo de forma eficiente
            import pyarrow.parquet as pq
            from pathlib import Path

            parquet_path = Path(os.getcwd()) / 'data' / 'parquet' / 'admmat_extended.parquet'

            if not parquet_path.exists():
                parquet_path = Path(os.getcwd()) / 'data' / 'parquet' / 'admmat.parquet'

            # Carregar apenas colunas necessárias (reduz I/O significativamente)
            colunas_parquet = ['codigo', 'nome_produto', 'une', 'estoque_atual', 'estoque_lv',
                              'media_considerada_lv', 'venda_30_d', 'nomesegmento']

            logger.info(f"Carregando dados do Parquet com PyArrow: {parquet_path}")
            table = pq.read_table(parquet_path, columns=colunas_parquet)
            df = table.to_pandas()

            # Normalizar nomes de colunas
            df = df.rename(columns={
                'estoque_lv': 'linha_verde',
                'media_considerada_lv': 'mc'
            })

            # Converter colunas numéricas (CRÍTICO para evitar erros de comparação)
            for col in ['estoque_atual', 'linha_verde', 'mc', 'venda_30_d']:
                if col in df.columns:
                    df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)

            logger.info(f"Dados carregados: {len(df)} registros, {len(df['codigo'].unique())} produtos únicos")

        except Exception as e:
            logger.error(f"Erro ao carregar dados: {e}")
            return {"error": f"Erro ao acessar dados: {str(e)}"}

        # Calcular percentual de linha verde para todos os produtos (VETORIZADO para performance)
        df['perc_linha_verde'] = 0.0  # Inicializar com zero
        mask = (df['linha_verde'] > 0)  # Apenas onde linha_verde > 0
        df.loc[mask, 'perc_linha_verde'] = (df.loc[mask, 'estoque_atual'] / df.loc[mask, 'linha_verde'] * 100)

        # Identificar UNEs com excesso (>100% linha verde)
        df_excesso = df[df['perc_linha_verde'] > 100].copy()

        # Identificar UNEs com falta (<75% linha verde)
        df_falta = df[df['perc_linha_verde'] < 75].copy()

        if df_excesso.empty or df_falta.empty:
            return {
                "total_sugestoes": 0,
                "sugestoes": [],
                "mensagem": "Não há oportunidades de transferência no momento",
                "estatisticas": {
                    "produtos_com_excesso": len(df_excesso),
                    "produtos_com_falta": len(df_falta)
                }
            }

        sugestoes = []

        # OTIMIZAÇÃO: Limitar busca apenas aos produtos mais críticos para evitar timeout
        # Ordenar por criticidade (menor percentual = mais crítico)
        produtos_criticos = df_falta.nsmallest(500, 'perc_linha_verde')['codigo'].unique()

        logger.info(f"Analisando {len(produtos_criticos)} produtos críticos (top 500 por necessidade)")

        # Agrupar por produto para encontrar oportunidades
        for produto_id in produtos_criticos:
            # Early stopping: se já temos sugestões suficientes, parar
            if len(sugestoes) >= limite * 2:  # Coletar 2x o limite para ter opções após ordenação
                break

            # Pegar todas as UNEs com excesso deste produto
            produto_excesso = df_excesso[df_excesso['codigo'] == produto_id]

            # Pegar todas as UNEs com falta deste produto
            produto_falta = df_falta[df_falta['codigo'] == produto_id]

            if produto_falta.empty:
                continue

            # Para cada UNE com excesso, encontrar melhor destino (limitar a 5 origens por produto)
            for _, origem in produto_excesso.head(5).iterrows():
                estoque_origem = float(origem['estoque_atual'])
                linha_verde_origem = float(origem['linha_verde'])
                une_origem = int(origem['une'])

                # FILTRO: Se une_origem_filtro foi especificado, pular UNEs diferentes
                if une_origem_filtro is not None and une_origem != une_origem_filtro:
                    continue

                # Quantidade disponível para transferir (excesso)
                qtd_disponivel = int(estoque_origem - linha_verde_origem)

                if qtd_disponivel <= 0:
                    continue

                # Ordenar destinos por prioridade (menor percentual primeiro) e limitar a 3 destinos
                for _, destino in produto_falta.sort_values('perc_linha_verde').head(3).iterrows():
                    une_destino = int(destino['une'])

                    if une_origem == une_destino:
                        continue

                    estoque_destino = float(destino['estoque_atual'])
                    linha_verde_destino = float(destino['linha_verde'])
                    perc_destino = float(destino['perc_linha_verde'])
                    mc_destino = float(destino['mc']) if pd.notna(destino['mc']) else 0.0
                    venda_30d = float(destino['venda_30_d']) if pd.notna(destino['venda_30_d']) else 0.0

                    # Quantidade necessária no destino
                    qtd_necessaria = int(linha_verde_destino - estoque_destino)

                    if qtd_necessaria <= 0:
                        continue

                    # Quantidade sugerida (mínimo entre disponível e necessário)
                    qtd_sugerida = min(qtd_disponivel, qtd_necessaria)

                    # Calcular score de prioridade
                    score = 0.0

                    # Fator 1: Criticidade do destino (0-50 pontos)
                    if perc_destino < 25:
                        score += 50
                        prioridade = "URGENTE"
                    elif perc_destino < 50:
                        score += 35
                        prioridade = "ALTA"
                    elif perc_destino < 75:
                        score += 20
                        prioridade = "NORMAL"
                    else:
                        score += 10
                        prioridade = "BAIXA"

                    # Fator 2: Excesso na origem (0-25 pontos)
                    perc_origem = float(origem['perc_linha_verde'])
                    if perc_origem > 150:
                        score += 25
                    elif perc_origem > 125:
                        score += 15
                    elif perc_origem > 100:
                        score += 10

                    # Fator 3: Demanda do produto no destino (0-25 pontos)
                    if venda_30d > 0:
                        dias_estoque = estoque_destino / (venda_30d / 30)
                        if dias_estoque < 7:
                            score += 25
                        elif dias_estoque < 15:
                            score += 15
                        elif dias_estoque < 30:
                            score += 10

                    # Gerar motivo
                    motivo_partes = []
                    if perc_destino < 50:
                        motivo_partes.append(f"Destino crítico ({perc_destino:.1f}% LV)")
                    if perc_origem > 125:
                        motivo_partes.append(f"Origem com excesso ({perc_origem:.1f}% LV)")
                    if venda_30d > 0 and dias_estoque < 15:
                        motivo_partes.append(f"Alta demanda ({dias_estoque:.0f} dias estoque)")

                    motivo = " | ".join(motivo_partes) if motivo_partes else "Balanceamento de estoque"

                    # Calcular benefício estimado
                    melhoria_destino = (estoque_destino + qtd_sugerida) / linha_verde_destino * 100 if linha_verde_destino > 0 else 0
                    beneficio = f"Destino: {perc_destino:.1f}% -> {melhoria_destino:.1f}% da linha verde"

                    sugestao = {
                        "produto_id": int(produto_id),
                        "nome_produto": str(origem['nome_produto']) if pd.notna(origem['nome_produto']) else "N/A",
                        "segmento": str(origem['nomesegmento']) if 'nomesegmento' in origem and pd.notna(origem['nomesegmento']) else "N/A",
                        "une_origem": une_origem,
                        "une_destino": une_destino,
                        "quantidade_sugerida": qtd_sugerida,
                        "prioridade": prioridade,
                        "score": round(score, 2),
                        "motivo": motivo,
                        "beneficio_estimado": beneficio,
                        "detalhes": {
                            "origem": {
                                "estoque": estoque_origem,
                                "linha_verde": linha_verde_origem,
                                "percentual": round(perc_origem, 2)
                            },
                            "destino": {
                                "estoque": estoque_destino,
                                "linha_verde": linha_verde_destino,
                                "percentual": round(perc_destino, 2),
                                "mc": mc_destino,
                                "venda_30d": venda_30d
                            }
                        }
                    }

                    sugestoes.append(sugestao)

                    # Atualizar quantidade disponível
                    qtd_disponivel -= qtd_sugerida
                    if qtd_disponivel <= 0:
                        break

        # Ordenar sugestões por score (maior primeiro)
        sugestoes_ordenadas = sorted(sugestoes, key=lambda x: x['score'], reverse=True)

        # Limitar ao número solicitado
        sugestoes_final = sugestoes_ordenadas[:limite]

        # Calcular estatísticas
        total_sugestoes = len(sugestoes_final)
        urgentes = len([s for s in sugestoes_final if s['prioridade'] == 'URGENTE'])
        altas = len([s for s in sugestoes_final if s['prioridade'] == 'ALTA'])
        normais = len([s for s in sugestoes_final if s['prioridade'] == 'NORMAL'])
        baixas = len([s for s in sugestoes_final if s['prioridade'] == 'BAIXA'])
        total_unidades = sum([s['quantidade_sugerida'] for s in sugestoes_final])

        logger.info(f"Geradas {total_sugestoes} sugestões de transferência")

        return {
            "total_sugestoes": total_sugestoes,
            "sugestoes": sugestoes_final,
            "estatisticas": {
                "total": total_sugestoes,
                "urgentes": urgentes,
                "altas": altas,
                "normais": normais,
                "baixas": baixas,
                "total_unidades": total_unidades,
                "produtos_unicos": len(set([s['produto_id'] for s in sugestoes_final])),
                "unes_origem": len(set([s['une_origem'] for s in sugestoes_final])),
                "unes_destino": len(set([s['une_destino'] for s in sugestoes_final]))
            }
        }

    except Exception as e:
        logger.error(f"Erro em sugerir_transferencias_automaticas: {e}", exc_info=True)
        return {"error": f"Erro ao gerar sugestões: {str(e)}"}


# Lista de ferramentas disponíveis para exportação
__all__ = [
    'calcular_abastecimento_une',
    'calcular_mc_produto',
    'calcular_preco_final_une',
    'validar_transferencia_produto',
    'sugerir_transferencias_automaticas'
]
