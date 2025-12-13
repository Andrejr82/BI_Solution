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

from pathlib import Path

# Validadores integrados (v3.0) - Ajustado para FastAPI
from app.core.validators.schema_validator import SchemaValidator
from app.core.utils.query_validator import validate_columns, handle_nulls, safe_filter
from app.core.utils.error_handler import error_handler_decorator

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
    'NOMESEGMENTO': 'nomesegmento',
    'ESTOQUE_CD': 'estoque_cd', # Adicionado mapeamento para estoque_cd
    'UNE_NOME': 'une_nome', # Added this for consistency
    'NOMEFABRICANTE': 'nomefabricante', # Added this for consistency
}

# Mapeamento de colunas Parquet padrão → formato padrão
COLUMN_MAPPING_PARQUET = {
    'estoque_lv': 'linha_verde',
    'media_considerada_lv': 'mc',
}

@lru_cache(maxsize=1)
def _get_data_adapter():
    """Retorna adapter de dados (HybridAdapter ou Parquet direto) com cache"""
    global USE_HYBRID_ADAPTER

    if USE_HYBRID_ADAPTER:
        try:
            from app.infrastructure.data.hybrid_adapter import HybridDataAdapter
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

    # Mapear colunas do Parquet para nomes padronizados
    # (mapeamento reverso do que é feito em _load_data)
    if 'media_considerada_lv' in df.columns and 'mc' not in df.columns:
        df['mc'] = df['media_considerada_lv']

    if 'estoque_lv' in df.columns and 'linha_verde' not in df.columns:
        df['linha_verde'] = df['estoque_lv']

    if 'estoque_gondola_lv' in df.columns and 'estoque_gondola' not in df.columns:
        df['estoque_gondola'] = df['estoque_gondola_lv']

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
        # Pass the specific parquet file name to the validator
        parquet_file_stem = Path(adapter['path']).stem
        is_valid, errors = validator.validate_parquet_file(adapter['path'], table_name=parquet_file_stem)
        if not is_valid:
            logger.error(f"Schema inválido: {errors}")
            raise ValueError(f"Schema do arquivo Parquet inválido: {errors}")

    # Create reverse mappings (moved outside if columns block)
    reverse_mapping_sql = {v: k for k, v in COLUMN_MAPPING_SQL.items()}
    reverse_mapping_parquet = {v: k for v, k in COLUMN_MAPPING_PARQUET.items()} # Should be k:v for reverse

    if isinstance(adapter, dict):
        # Parquet direto
        if columns:
            # Map requested standard columns back to Parquet original names for loading
            parquet_cols_to_load = []
            
            for col in columns:
                if col in reverse_mapping_sql:
                    parquet_cols_to_load.append(reverse_mapping_sql[col])
                elif col in reverse_mapping_parquet:
                    parquet_cols_to_load.append(reverse_mapping_parquet[col])
                else:
                    # Default: assume the column name is the same in Parquet
                    parquet_cols_to_load.append(col) 
            
            # Ensure unique columns
            parquet_cols_to_load = list(set(parquet_cols_to_load))
            logger.debug(f"Loading parquet from {adapter['path']} with columns: {parquet_cols_to_load}")

            df = pd.read_parquet(adapter['path'], columns=parquet_cols_to_load)
        else:
            df = pd.read_parquet(adapter['path'])

        # Aplicar filtros manualmente
        if filters:
            for col, val in filters.items():
                # Map filter key back to original parquet column name if necessary
                mapped_col = col
                if col in reverse_mapping_sql:
                    mapped_col = reverse_mapping_sql[col]
                elif col in reverse_mapping_parquet:
                    mapped_col = reverse_mapping_parquet[col]
                else:
                    # Default: assume the column name is the same in Parquet
                    mapped_col = col

                if mapped_col in df.columns:
                    df = df[df[mapped_col] == val]
    else:
        # 🚀 OTIMIZAÇÃO URGENTE: PRIORIZAR PARQUET (SQL Server muito lento - 5min/query)
        # HybridAdapter (SQL ou Parquet automático)
        try:
            # Sempre tentar Parquet primeiro para performance máxima
            import glob

            parquet_path = adapter.file_path if hasattr(adapter, 'file_path') else os.path.join(os.getcwd(), 'data', 'parquet', 'admmat.parquet')

            # Expandir wildcard se necessário
            if '*' in parquet_path:
                matched_files = glob.glob(parquet_path)
                if matched_files:
                    # Priorizar admmat.parquet se existir, senão pegar primeiro
                    parquet_path = next((f for f in matched_files if 'admmat.parquet' in f), matched_files[0])

            logger.info(f"🚀 OTIMIZAÇÃO: Usando Parquet direto (SQL muito lento) - {parquet_path}")

            # Mapear colunas padrão para colunas do Parquet
            if columns:
                parquet_cols = []
                for col in columns:
                    if col == 'linha_verde':
                        parquet_cols.append('estoque_lv')
                    elif col == 'mc':
                        parquet_cols.append('media_considerada_lv')
                    elif col == 'estoque_gondola_lv':
                        # Já é o nome correto do Parquet
                        parquet_cols.append(col)
                    elif col in ['ESTOQUE_GONDOLA', 'estoque_gondola']:
                        # Mapear variações antigas para coluna correta
                        parquet_cols.append('estoque_gondola_lv')
                    else:
                        parquet_cols.append(col)

                df = pd.read_parquet(parquet_path, columns=parquet_cols)
            else:
                df = pd.read_parquet(parquet_path)

            # Aplicar filtros manualmente (SUPER RÁPIDO com Polars/Pandas)
            if filters:
                for col, val in filters.items():
                    # Normalizar nome da coluna
                    if col == 'linha_verde' and 'estoque_lv' in df.columns:
                        col = 'estoque_lv'
                    elif col == 'mc' and 'media_considerada_lv' in df.columns:
                        col = 'media_considerada_lv'

                    if col in df.columns:
                        df = df[df[col] == val]

            logger.info(f"✅ Parquet carregado com sucesso: {len(df)} registros")

        except Exception as e:
            # Fallback: usar HybridAdapter (Polars/SQL)
            logger.info(f"⚠️ Fallback para HybridAdapter: {e}")
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

    # Verificar se dataframe não está vazio
    if df.empty:
        logger.warning(f"Query retornou 0 linhas para UNE {une_id}")
        return {
            "error": f"Nenhum dado encontrado para UNE {une_id}",
            "une_id": une_id,
            "total_produtos": 0,
            "produtos": []
        }

    # Normalizar DataFrame (garantir mapeamento de colunas SQL -> padrão)
    df = _normalize_dataframe(df)

    # Validar colunas necessárias
    required_cols = ['une', 'codigo', 'nome_produto', 'estoque_atual', 'linha_verde']
    is_valid, missing = validate_columns(df, required_cols)
    if not is_valid:
        logger.error(f"Colunas disponíveis: {list(df.columns)}")
        logger.error(f"Colunas faltantes: {missing}")
        return {
            "error": f"Colunas ausentes após normalização: {missing}",
            "colunas_disponiveis": list(df.columns),
            "une_id": une_id
        }

    # Calcular colunas derivadas se não existirem
    if 'precisa_abastecimento' not in df.columns:
        logger.info("Calculando coluna 'precisa_abastecimento' (não encontrada nos dados)")
        # Regra: ESTOQUE_UNE <= 50% LINHA_VERDE
        df['precisa_abastecimento'] = (df['estoque_atual'] <= (df['linha_verde'] * 0.5))

    if 'qtd_a_abastecer' not in df.columns:
        logger.info("Calculando coluna 'qtd_a_abastecer' (não encontrada nos dados)")
        # Quantidade a abastecer = LINHA_VERDE - ESTOQUE_ATUAL (se positivo)
        df['qtd_a_abastecer'] = (df['linha_verde'] - df['estoque_atual']).clip(lower=0)

    # Filtrar por UNE com segurança
    df_une = df[df['une'] == une_id]

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
    # (coluna já foi calculada anteriormente se não existia)
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

        # Carregar dados usando _load_data() com filtros (padrão refatorado)
        logger.info(f"Buscando MC do produto {produto_id} na UNE {une_id}")
        # CORREÇÃO: Remover colunas ESTOQUE_GONDOLA/estoque_gondola que não existem no Parquet
        # Usar estoque_gondola_lv que existe no Parquet
        produto_df = _load_data(
            filters={'codigo': produto_id, 'une': une_id},
            columns=['codigo', 'nome_produto', 'une', 'mc', 'estoque_atual',
                    'linha_verde', 'nomesegmento', 'estoque_gondola_lv']
        )

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

        # Estoque gôndola (usar estoque_gondola_lv que existe no Parquet)
        estoque_gondola = None
        if 'estoque_gondola_lv' in row:
            estoque_gondola = float(row['estoque_gondola_lv']) if pd.notna(row['estoque_gondola_lv']) else 0.0
        elif 'ESTOQUE_GONDOLA' in row:
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
    - Incorpora a regra de ruptura crítica (sem estoque no CD).

    Args:
        produto_id: Código do produto a transferir
        une_origem: ID da UNE que vai enviar o produto
        une_destino: ID da UNE que vai receber o produto
        quantidade: Quantidade a transferir

    Returns:
        dict com:
        - valido: bool (se a transferência é válida)
        - prioridade: str ("URGENTE", "ALTA", "NORMAL", "BAIXA", "NAO_RECOMENDADA")
        - score_prioridade: float (0-100, quanto maior mais prioritária)
        - motivo: str (justificativa da validação)
        - recomendacoes: list[str] (ações sugeridas)
        ... e outros detalhes.
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

        logger.info(f"Validando transferência: Produto {produto_id}, UNE {une_origem} -> {une_destino}, Qtd: {quantidade}")

        try:
            # Carregar dados necessários, incluindo estoque_cd
            colunas_necessarias = [
                'codigo', 'nome_produto', 'une', 'estoque_atual', 'linha_verde',
                'mc', 'venda_30_d', 'nomesegmento', 'estoque_cd'
            ]
            df = _load_data(filters={'codigo': produto_id}, columns=colunas_necessarias)
            df = df[df['une'].isin([une_origem, une_destino])]
        except Exception as e:
            logger.error(f"Erro ao carregar dados: {e}")
            return {"error": f"Erro ao acessar dados: {str(e)}", "valido": False}

        # Dados da Origem
        origem_df = df[df['une'] == une_origem]
        if origem_df.empty:
            return {"valido": False, "motivo": f"Produto {produto_id} não encontrado na UNE origem {une_origem}"}

        # Dados do Destino
        destino_df = df[df['une'] == une_destino]
        if destino_df.empty:
            return {"valido": False, "motivo": f"Produto {produto_id} não encontrado na UNE destino {une_destino}"}

        origem = origem_df.iloc[0]
        destino = destino_df.iloc[0]

        # Extrair dados numéricos com segurança
        estoque_origem = float(origem.get('estoque_atual', 0))
        linha_verde_origem = float(origem.get('linha_verde', 0))
        estoque_destino = float(destino.get('estoque_atual', 0))
        linha_verde_destino = float(destino.get('linha_verde', 0))
        venda_30d_destino = float(destino.get('venda_30_d', 0))
        mc_destino = float(destino.get('mc', 0))
        estoque_cd = float(origem.get('estoque_cd', 0)) # Estoque do CD é o mesmo para o produto

        # --- Validações de Bloqueio ---
        if estoque_origem < quantidade:
            return {"valido": False, "motivo": f"Estoque insuficiente na origem. Disponível: {estoque_origem:.0f}, Solicitado: {quantidade}"}

        estoque_origem_apos = estoque_origem - quantidade
        perc_origem_apos = (estoque_origem_apos / linha_verde_origem * 100) if linha_verde_origem > 0 else 0.0
        if perc_origem_apos < 50:
            return {"valido": False, "motivo": f"Transferência deixaria origem com estoque crítico ({perc_origem_apos:.1f}% da linha verde)"}

        # --- Cálculo de Score de Prioridade ---
        score_prioridade = 0.0
        recomendacoes = []
        
        perc_origem = (estoque_origem / linha_verde_origem * 100) if linha_verde_origem > 0 else 0.0
        perc_destino = (estoque_destino / linha_verde_destino * 100) if linha_verde_destino > 0 else 0.0

        # Fator 1: Necessidade do destino (0-40 pontos)
        if perc_destino < 25: score_prioridade += 40
        elif perc_destino < 50: score_prioridade += 30
        elif perc_destino < 75: score_prioridade += 20
        else: score_prioridade += 5

        # Fator 2: Excesso na origem (0-30 pontos)
        if perc_origem > 150: score_prioridade += 30
        elif perc_origem > 125: score_prioridade += 20
        elif perc_origem > 100: score_prioridade += 10

        # Fator 3: Demanda do destino (0-30 pontos)
        if venda_30d_destino > 0:
            dias_estoque_destino = estoque_destino / (venda_30d_destino / 30)
            if dias_estoque_destino < 7: score_prioridade += 30
            elif dias_estoque_destino < 15: score_prioridade += 20
            elif dias_estoque_destino < 30: score_prioridade += 10
        
        # Fator 4: Ruptura Crítica Sistêmica (Bônus de 50 pontos)
        if estoque_cd <= 0 and perc_destino < 75:
            score_prioridade += 50
            recomendacoes.append("ALERTA CRÍTICO: Produto sem estoque no CD. Transferência de alta prioridade para evitar ruptura.")

        # --- Recomendações Adicionais ---
        pode_transferir = max(0, int(estoque_origem - linha_verde_origem)) if perc_origem > 100 else int(estoque_origem * 0.25)
        pode_receber = max(0, int(linha_verde_destino - estoque_destino))
        quantidade_recomendada = min(pode_transferir, pode_receber)
        
        if quantidade != quantidade_recomendada and quantidade_recomendada > 0:
            recomendacoes.append(f"Sugerimos transferir {quantidade_recomendada} unidades.")
        if perc_destino < 25:
            recomendacoes.append("CRÍTICO: Destino com estoque muito baixo.")
        if mc_destino > estoque_destino:
            recomendacoes.append("MC do destino > estoque atual, indicando alta demanda.")
        if not recomendacoes:
            recomendacoes.append("Transferência dentro dos padrões normais.")

        # --- Determinar Prioridade Final ---
        if score_prioridade >= 90: prioridade = "URGENTE"
        elif score_prioridade >= 70: prioridade = "ALTA"
        elif score_prioridade >= 40: prioridade = "NORMAL"
        else: prioridade = "BAIXA"

        # --- Montar Resposta ---
        resultado = {
            "valido": True,
            "produto_id": int(produto_id),
            "nome_produto": str(origem.get('nome_produto', "N/A")),
            "prioridade": prioridade,
            "score_prioridade": round(score_prioridade, 2),
            "quantidade_recomendada": int(quantidade_recomendada),
            "motivo": f"Transferência válida com prioridade {prioridade}",
            "recomendacoes": recomendacoes,
            # ... (outros detalhes podem ser adicionados aqui)
        }
        return resultado

    except Exception as e:
        logger.error(f"Erro em validar_transferencia_produto: {e}", exc_info=True)
        return {"error": f"Erro ao validar transferência: {str(e)}", "valido": False}


@tool
def sugerir_transferencias_automaticas(limite: int = 20, une_origem_filtro: int = None, une_destino_id: int = None) -> Dict[str, Any]:
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
        logger.info(f"Produtos com excesso (perc_linha_verde > 100): {len(df_excesso)}")

        # Identificar UNEs com falta (<75% linha verde)
        df_falta = df[df['perc_linha_verde'] < 75].copy()
        logger.info(f"Produtos com falta (perc_linha_verde < 75): {len(df_falta)}")

        if df_excesso.empty or df_falta.empty:
            logger.info("df_excesso ou df_falta estão vazios, retornando 0 sugestões.")
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
                logger.info(f"Limite de sugestões atingido ({len(sugestoes)}), parando a geração.")
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

                    if une_destino_id is not None and une_destino != une_destino_id:
                        continue

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
        logger.info(f"Total de sugestões geradas antes da ordenação e limite: {len(sugestoes)}")

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


@tool
@error_handler_decorator(
    context_func=lambda une_id: {"une_id": une_id, "funcao": "calcular_produtos_sem_vendas"},
    return_on_error={"error": "Erro ao calcular produtos sem vendas", "total_produtos": 0, "produtos": []}
)
def calcular_produtos_sem_vendas(une_id: int, limite: int = 50, fabricante: str = None) -> Dict[str, Any]:
    """
    Identifica produtos sem vendas (VENDA_30DD = 0) em uma UNE, com filtro opcional por fabricante.

    Esta ferramenta é útil para:
    - Identificar produtos sem giro
    - Detectar itens parados em estoque
    - Analisar a ruptura de um fabricante específico

    Args:
        une_id: ID da UNE (ex: 2586 para SCR, 261 para MAD)
        limite: Número máximo de produtos a retornar (default: 50)
        fabricante: Nome do fabricante para filtrar os resultados (opcional)

    Returns:
        dict com:
        - total_produtos: int (total de produtos sem vendas)
        - produtos: list[dict] (produtos sem vendas com estoque > 0)
        - une_id: int
        - criterio: str (descrição do filtro aplicado)

    Example:
        >>> result = calcular_produtos_sem_vendas(une_id=2586, limite=20, fabricante="KIT")
        >>> print(f"Total: {result['total_produtos']} produtos sem vendas do fabricante KIT")
    """
    # Validação de inputs
    if not isinstance(une_id, int) or une_id <= 0:
        return {"error": "une_id deve ser um inteiro positivo"}

    if not isinstance(limite, int) or limite <= 0:
        limite = 50

    logger.info(f"Buscando produtos sem vendas na UNE {une_id} para o fabricante {fabricante or 'Todos'}")

    # Construir filtros
    filters = {'une': une_id}
    if fabricante:
        # Usar o nome real da coluna no Parquet
        filters['NOMEFABRICANTE'] = fabricante.upper()

    # Carregar dados da UNE
    df = _load_data(
        filters=filters,
        columns=['codigo', 'nome_produto', 'une', 'estoque_atual', 'venda_30_d',
                'linha_verde', 'nomesegmento', 'mc', 'NOMEFABRICANTE']
    )

    if df.empty:
        logger.warning(f"Nenhum dado encontrado para UNE {une_id} e fabricante {fabricante}")
        return {
            "error": f"Nenhum dado encontrado para UNE {une_id} com o filtro de fabricante '{fabricante}'",
            "une_id": une_id,
            "total_produtos": 0,
            "produtos": []
        }

    # Normalizar DataFrame
    df = _normalize_dataframe(df)

    # Filtrar produtos SEM vendas (venda_30_d = 0) mas COM estoque
    df_sem_vendas = df[
        (df['venda_30_d'] == 0) &
        (df['estoque_atual'] > 0)
    ].copy()

    total_produtos = len(df_sem_vendas)

    if total_produtos == 0:
        return {
            "total_produtos": 0,
            "produtos": [],
            "une_id": une_id,
            "criterio": "VENDA_30DD = 0 E ESTOQUE > 0" + (f" E NOMEFABRICANTE = '{fabricante.upper()}'" if fabricante else ""),
            "mensagem": "Nenhum produto sem vendas encontrado com os filtros aplicados."
        }

    # Ordenar por estoque (produtos com mais estoque parado = mais críticos)
    df_sem_vendas = df_sem_vendas.sort_values('estoque_atual', ascending=False)

    # Limitar ao número solicitado
    top_produtos = df_sem_vendas.head(limite)

    # Preparar lista de produtos
    produtos = []
    for _, row in top_produtos.iterrows():
        produto = {
            "codigo": int(row['codigo']) if pd.notna(row['codigo']) else None,
            "nome_produto": str(row['nome_produto']) if pd.notna(row['nome_produto']) else "N/A",
            "segmento": str(row['nomesegmento']) if 'nomesegmento' in row and pd.notna(row['nomesegmento']) else "N/A",
            "estoque_atual": float(row['estoque_atual']) if pd.notna(row['estoque_atual']) else 0.0,
            "linha_verde": float(row['linha_verde']) if pd.notna(row['linha_verde']) else 0.0,
            "venda_30d": 0.0,  # Sempre zero (critério da busca)
            "dias_sem_venda": "> 30 dias"
        }
        produtos.append(produto)

    logger.info(f"Encontrados {total_produtos} produtos sem vendas na UNE {une_id} para o fabricante {fabricante or 'Todos'}")

    return {
        "total_produtos": total_produtos,
        "produtos": produtos,
        "une_id": une_id,
        "criterio": "VENDA_30DD = 0 E ESTOQUE > 0" + (f" E NOMEFABRICANTE = '{fabricante.upper()}'" if fabricante else ""),
        "limite_exibido": len(produtos),
        "recomendacao": "Considere ações promocionais ou transferência para UNEs com demanda" if total_produtos > 0 else None
    }


@tool
@error_handler_decorator(
    context_func=lambda: {"funcao": "encontrar_rupturas_criticas"},
    return_on_error={"error": "Erro ao encontrar rupturas críticas", "total_criticos": 0, "produtos_criticos": []}
)
def encontrar_rupturas_criticas(limite: Optional[int] = 100) -> Dict[str, Any]:
    """
    Identifica produtos em situação de ruptura crítica sistêmica, ordenados por gravidade.

    A regra de negócio para ruptura crítica é:
    1. O estoque no Centro de Distribuição (CD) é zero ou negativo (estoque_cd <= 0).
    2. O estoque na UNE (loja) está abaixo da linha verde (estoque_atual < linha_verde).

    A lista é ordenada para mostrar primeiro os produtos com "Estoque Negativo Crítico"
    e depois por 'percentual_cobertura' (do menor para o maior), que representa
    o quão cheio o estoque está em relação à linha verde.

    Args:
        limite: Número máximo de produtos críticos a retornar. Se None, retorna todos.

    Returns:
        dict com:
        - total_criticos: int (total de produtos em situação crítica)
        - produtos_criticos: list[dict] (lista dos produtos, incluindo 'motivo_ruptura', 'alerta_de_estoque' e 'percentual_cobertura')
        - criterio: str (descrição da regra aplicada)

    Example:
        >>> result = encontrar_rupturas_criticas(limite=10)
        >>> print(f"Total de produtos críticos: {result['total_criticos']}")
    """
    try:
        logger.info(f"Buscando produtos em ruptura crítica (limite: {limite})")

        # Carregar dados necessários de forma otimizada, incluindo venda_30_d
        colunas_necessarias = [
            'codigo', 'nome_produto', 'une', 'une_nome', 'estoque_atual',
            'linha_verde', 'estoque_cd', 'nomesegmento', 'venda_30_d'
        ]
        
        # Usar _load_data para abstrair a fonte de dados
        df = _load_data(columns=colunas_necessarias)

        if df.empty:
            return {
                "total_criticos": 0,
                "produtos_criticos": [],
                "mensagem": "Nenhum dado de produto encontrado."
            }

        # Garantir que as colunas numéricas são do tipo correto
        for col in ['estoque_cd', 'estoque_atual', 'linha_verde', 'venda_30_d']:
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)

        # Aplicar a regra de negócio
        # 1. Estoque no CD <= 0
        df_sem_estoque_cd = df[df['estoque_cd'] <= 0]

        if df_sem_estoque_cd.empty:
            return {
                "total_criticos": 0,
                "produtos_criticos": [],
                "mensagem": "Nenhum produto encontrado com estoque zerado no CD."
            }

        # 2. Estoque na UNE < Linha Verde
        df_criticos = df_sem_estoque_cd[df_sem_estoque_cd['estoque_atual'] < df_sem_estoque_cd['linha_verde']].copy()

        total_criticos = len(df_criticos)

        if total_criticos == 0:
            return {
                "total_criticos": 0,
                "produtos_criticos": [],
                "criterio": "estoque_cd <= 0 E estoque_atual < linha_verde",
                "mensagem": "Nenhuma ruptura crítica encontrada. Todas as UNEs com estoque abaixo da linha verde possuem cobertura no CD."
            }

        # Adicionar campos para alerta e ordenação
        df_criticos['alerta_de_estoque'] = df_criticos['estoque_atual'].apply(
            lambda x: "Estoque Negativo Crítico" if x < 0 else "Estoque Baixo"
        )
        df_criticos['percentual_cobertura'] = df_criticos.apply(
            lambda row: (row['estoque_atual'] / row['linha_verde'] * 100) if row['linha_verde'] > 0 else 0,
            axis=1
        )
        
        # Criar uma coluna temporária para ordenação que prioriza os negativos
        df_criticos['is_negativo'] = df_criticos['estoque_atual'].apply(lambda x: 1 if x < 0 else 0)

        # Ordenar por status de alerta (negativos primeiro) e depois por percentual de cobertura
        df_criticos = df_criticos.sort_values(
            by=['is_negativo', 'percentual_cobertura'], 
            ascending=[False, True]
        )

        # Limitar ao número solicitado, se um limite for fornecido
        top_criticos = df_criticos
        if limite is not None:
            top_criticos = df_criticos.head(limite)

        # Preparar lista de produtos
        produtos = []
        for _, row in top_criticos.iterrows():
            # Determinar o motivo da ruptura
            motivo_ruptura = "Risco de Reposição (Estoque CD Zerado)"
            if row['linha_verde'] < row['venda_30_d']:
                motivo_ruptura = "Planejamento Incorreto (Linha Verde < Vendas)"

            produto = {
                "codigo": int(row['codigo']) if pd.notna(row['codigo']) else None,
                "nome_produto": str(row['nome_produto']) if pd.notna(row['nome_produto']) else "N/A",
                "segmento": str(row['nomesegmento']) if 'nomesegmento' in row and pd.notna(row['nomesegmento']) else "N/A",
                "une_afetada_id": int(row['une']) if pd.notna(row['une']) else None,
                "une_afetada_nome": str(row['une_nome']) if 'une_nome' in row and pd.notna(row['une_nome']) else "N/A",
                "alerta_de_estoque": row['alerta_de_estoque'],
                "estoque_na_une": float(row['estoque_atual']),
                "linha_verde_na_une": float(row['linha_verde']),
                "percentual_cobertura": round(row['percentual_cobertura'], 2),
                "venda_30_dias": float(row['venda_30_d']),
                "necessidade_na_une": float(row['linha_verde'] - row['estoque_atual']),
                "estoque_no_cd": float(row['estoque_cd']),
                "motivo_ruptura": motivo_ruptura
            }
            produtos.append(produto)

        logger.info(f"Encontradas {total_criticos} situações de ruptura crítica.")

        return {
            "total_criticos": total_criticos,
            "produtos_criticos": produtos,
            "criterio": "estoque_cd <= 0 E estoque_atual < linha_verde",
            "limite_exibido": len(produtos)
        }

    except Exception as e:
        logger.error(f"Erro em encontrar_rupturas_criticas: {e}", exc_info=True)
        return {"error": f"Erro ao processar rupturas críticas: {str(e)}"}


@tool
@error_handler_decorator(
    context_func=lambda une_id=None, produto_id=None, segmento=None, termo_busca=None: {
        "une_id": une_id, "produto_id": produto_id, "segmento": segmento, "termo_busca": termo_busca, "funcao": "consultar_dados_gerais"
    },
    return_on_error={"error": "Erro ao consultar dados gerais", "total_resultados": 0, "resultados": []}
)
def consultar_dados_gerais(
    une_id: Optional[int] = None,
    produto_id: Optional[int] = None,
    segmento: Optional[str] = None,
    termo_busca: Optional[str] = None,
    limite: int = 20
) -> Dict[str, Any]:
    """
    Consulta dados gerais de produtos, estoque e vendas com filtros flexíveis.
    Use esta ferramenta para responder perguntas gerais como:
    - "Qual o estoque do produto X na UNE Y?"
    - "Quais produtos do segmento Z temos na UNE Y?"
    - "Dados do produto 12345"

    Args:
        une_id: ID da UNE (opcional)
        produto_id: Código do produto (opcional)
        segmento: Nome do segmento (opcional, ex: "TECIDOS")
        termo_busca: Parte do nome do produto para busca (opcional)
        limite: Máximo de resultados (default: 20)

    Returns:
        dict com 'total_resultados' e lista de 'resultados'.
    """
    logger.info(f"Consultando dados gerais: une={une_id}, prod={produto_id}, seg={segmento}, busca={termo_busca}")

    filters = {}
    if une_id:
        filters['une'] = une_id
    if produto_id:
        filters['codigo'] = produto_id
    
    # Se tiver filtro de segmento, precisamos carregar e filtrar depois ou usar _load_data se suportar
    # _load_data suporta filtro exato. Para contains (termo_busca), faremos via pandas.

    try:
        # Colunas relevantes para consulta geral
        cols = [
            'codigo', 'nome_produto', 'une', 'une_nome', 'estoque_atual', 'linha_verde', 
            'venda_30_d', 'mc', 'nomesegmento', 'estoque_cd', 'NOMEFABRICANTE'
        ]
        
        # Otimização: se tiver ID ou UNE, filtrar na carga
        df = _load_data(filters=filters if filters else None, columns=cols)
        
        if df.empty:
            return {"total_resultados": 0, "resultados": [], "mensagem": "Nenhum dado encontrado com os filtros iniciais."}

        # Normalizar
        df = _normalize_dataframe(df)
        
        # Filtros adicionais (pandas)
        if segmento and 'nomesegmento' in df.columns:
            df = df[df['nomesegmento'].str.contains(segmento, case=False, na=False)]
        
        if termo_busca and 'nome_produto' in df.columns:
            df = df[df['nome_produto'].str.contains(termo_busca, case=False, na=False)]

        total = len(df)
        if total == 0:
             return {"total_resultados": 0, "resultados": [], "mensagem": "Nenhum dado encontrado após filtros de texto."}

        # Limitar e formatar
        df_res = df.head(limite)
        resultados = []
        for _, row in df_res.iterrows():
            item = {
                "codigo": int(row['codigo']) if pd.notna(row.get('codigo')) else None,
                "nome": str(row['nome_produto']) if pd.notna(row.get('nome_produto')) else "N/A",
                "une": int(row['une']) if pd.notna(row.get('une')) else None,
                "estoque": float(row['estoque_atual']) if pd.notna(row.get('estoque_atual')) else 0.0,
                "venda_30d": float(row['venda_30_d']) if pd.notna(row.get('venda_30_d')) else 0.0,
                "linha_verde": float(row['linha_verde']) if pd.notna(row.get('linha_verde')) else 0.0,
                "segmento": str(row['nomesegmento']) if pd.notna(row.get('nomesegmento')) else "N/A"
            }
            # Adicionar campos extras se disponíveis
            if 'estoque_cd' in row and pd.notna(row['estoque_cd']):
                item['estoque_cd'] = float(row['estoque_cd'])
            
            resultados.append(item)

        return {
            "total_resultados": total,
            "resultados": resultados,
            "limite_aplicado": limite
        }

    except Exception as e:
        logger.error(f"Erro em consultar_dados_gerais: {e}", exc_info=True)
        return {"error": f"Erro na consulta: {str(e)}"}

# Lista de ferramentas disponíveis para exportação
__all__ = [
    'calcular_abastecimento_une',
    'calcular_mc_produto',
    'calcular_preco_final_une',
    'validar_transferencia_produto',
    'sugerir_transferencias_automaticas',
    'calcular_produtos_sem_vendas',
    'encontrar_rupturas_criticas',
    'consultar_dados_gerais'
]


# -----------------------------------------------------------------------------
# Compatibility wrapper functions (shims) expected by older tests/scripts
# These provide a stable, high-level API (get_*) that returns the
# standardized dict: {"success": bool, "data": ..., "message": str}
# They call the existing implementations where possible or provide
# safe fallbacks so test-collection/imports do not fail.
# -----------------------------------------------------------------------------


def _standard_response(data=None, message: str = "", success: bool = True):
    return {"success": success, "data": data if data is not None else [], "message": message}


def get_produtos_une(une_id: int):
    """Compat wrapper: retorna produtos para uma UNE.

    Usa `_load_data` e devolve lista de registros normalizados.
    """
    try:
        if not isinstance(une_id, int) or une_id <= 0:
            return _standard_response([], "une_id inválido", False)

        df = _load_data(filters={"une": une_id})
        records = df.to_dict(orient="records") if not df.empty else []

        return _standard_response(records, "OK", True)
    except Exception as e:
        logger.error(f"Erro em get_produtos_une: {e}", exc_info=True)
        return _standard_response([], f"Erro: {e}", False)


def get_transferencias(une: int = None, data_inicio: str = None, data_fim: str = None, status: str = None):
    """Compat wrapper: retorna transferencias (usa sugerir_transferencias_automaticas como fallback)."""
    try:
        limite = 50
        result = sugerir_transferencias_automaticas(limite=limite, une_origem_filtro=une)
        sugestoes = result.get("sugestoes") if isinstance(result, dict) else []
        return _standard_response(sugestoes, "OK", True)
    except Exception as e:
        logger.error(f"Erro em get_transferencias: {e}", exc_info=True)
        return _standard_response([], f"Erro: {e}", False)


def get_estoque_une(une_id: int):
    try:
        df = _load_data(filters={"une": une_id})
        if df.empty:
            return _standard_response([], "Nenhum dado", True)

        total_estoque = int(df['estoque_atual'].fillna(0).sum()) if 'estoque_atual' in df.columns else 0
        return _standard_response({"une": une_id, "total_estoque": total_estoque}, "OK", True)
    except Exception as e:
        logger.error(f"Erro em get_estoque_une: {e}", exc_info=True)
        return _standard_response([], f"Erro: {e}", False)


def get_vendas_une(une_id: int):
    try:
        df = _load_data(filters={"une": une_id})
        total_vendas = float(df['venda_30_d'].fillna(0).sum()) if 'venda_30_d' in df.columns else 0.0
        return _standard_response({"une": une_id, "total_vendas_30d": total_vendas}, "OK", True)
    except Exception as e:
        logger.error(f"Erro em get_vendas_une: {e}", exc_info=True)
        return _standard_response([], f"Erro: {e}", False)


def get_unes_disponiveis():
    try:
        df = _load_data()
        if 'une' in df.columns:
            unes = sorted(list(df['une'].dropna().unique()))
        else:
            unes = []
        return _standard_response(unes, "OK", True)
    except Exception as e:
        logger.error(f"Erro em get_unes_disponiveis: {e}", exc_info=True)
        return _standard_response([], f"Erro: {e}", False)


def get_preco_produto(une_id: int, produto_codigo: str):
    try:
        df = _load_data(filters={"une": une_id, "codigo": produto_codigo})
        if df.empty:
            return _standard_response({}, "Produto não encontrado", False)
        row = df.iloc[0].to_dict()
        preco = row.get('preco_venda') or row.get('preco') or 0.0
        return _standard_response({"produto": produto_codigo, "preco_venda": float(preco)}, "OK", True)
    except Exception as e:
        logger.error(f"Erro em get_preco_produto: {e}", exc_info=True)
        return _standard_response({}, f"Erro: {e}", False)


def get_total_vendas_une(une_id: int):
    try:
        df = _load_data(filters={"une": une_id})
        total = float(df['venda_30_d'].fillna(0).sum()) if 'venda_30_d' in df.columns else 0.0
        return _standard_response(total, "OK", True)
    except Exception as e:
        logger.error(f"Erro em get_total_vendas_une: {e}", exc_info=True)
        return _standard_response(0, f"Erro: {e}", False)


def get_total_estoque_une(une_id: int):
    try:
        df = _load_data(filters={"une": une_id})
        total = int(df['estoque_atual'].fillna(0).sum()) if 'estoque_atual' in df.columns else 0
        return _standard_response(total, "OK", True)
    except Exception as e:
        logger.error(f"Erro em get_total_estoque_une: {e}", exc_info=True)
        return _standard_response(0, f"Erro: {e}", False)


def health_check():
    try:
        base = os.path.join(os.getcwd(), 'data', 'parquet')
        files = os.listdir(base) if os.path.exists(base) else []
        expected = ['produtos.parquet', 'transferencias.parquet']
        missing = [f for f in expected if f not in files]
        status = {"present_files": files, "missing_expected": missing}
        success = len(missing) == 0
        return _standard_response(status, "OK" if success else "Arquivos faltando", success)
    except Exception as e:
        logger.error(f"Erro em health_check: {e}", exc_info=True)
        return _standard_response({}, f"Erro: {e}", False)

