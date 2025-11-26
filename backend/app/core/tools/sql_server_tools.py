"""
Ferramentas para executar consultas SQL Server através do agente.
Integração direta com o banco de dados para respostas em tempo real.
"""

import logging
from typing import Dict, Any
from langchain_core.tools import tool
from app.core.database.database import get_db_manager
from sqlalchemy import text

logger = logging.getLogger(__name__)


@tool
def query_database(sql_query: str) -> Dict[str, Any]:
    """
    Executa uma consulta SQL diretamente no banco de dados.

    Args:
        sql_query: Consulta SQL para executar

    Returns:
        Dicionário com os resultados ou erro
    """
    logger.info(f"Executando query: {sql_query}")

    try:
        db_manager = get_db_manager()

        with db_manager.get_connection() as conn:
            result = conn.execute(text(sql_query))
            rows = result.fetchall()
            columns = result.keys() if rows else []

            if not rows:
                return {
                    "status": "success",
                    "message": "Nenhum resultado encontrado",
                    "data": [],
                }

            # Converter ResultProxy para lista de dicts
            data = [dict(zip(columns, row)) for row in rows]

            return {
                "status": "success",
                "message": f"{len(data)} registros encontrados",
                "columns": list(columns),
                "data": data,
                "count": len(data),
            }

    except Exception as e:
        logger.error(f"Erro ao executar query: {e}", exc_info=True)
        return {
            "status": "error",
            "message": f"Erro ao executar consulta: {str(e)}",
            "data": [],
        }


@tool
def get_product_by_code(product_code: str) -> Dict[str, Any]:
    """
    Busca um produto pelo código na tabela ADMAT_OPCOM.

    Args:
        product_code: Código do produto

    Returns:
        Informações do produto
    """
    logger.info(f"Buscando produto com código: {product_code}")

    try:
        db_manager = get_db_manager()
        query = """
        SELECT TOP 1
            CAST([CÓDIGO] AS VARCHAR(50)) as codigo,
            [NOME] as nome,
            [PREÇO 38%] as preco,
            [FABRICANTE] as fabricante,
            [EMBALAGEM] as embalagem,
            [CATEGORIA] as categoria,
            [GRUPO] as grupo,
            [SUBGRUPO] as subgrupo,
            [EST# UNE] as estoque,
            [ULTIMA_VENDA] as ultima_venda
        FROM dbo.Admat_OPCOM
        WHERE CAST([CÓDIGO] AS VARCHAR(50)) = :codigo
           OR [CÓDIGO] = :codigo_int
        """

        with db_manager.get_connection() as conn:
            result = conn.execute(
                text(query),
                {
                    "codigo": product_code,
                    "codigo_int": int(product_code) if product_code.isdigit() else 0,
                },
            )
            row = result.fetchone()

            if not row:
                return {
                    "status": "not_found",
                    "message": f"Produto {product_code} não encontrado",
                }

            columns = result.keys()
            data = dict(zip(columns, row))

            return {"status": "success", "message": "Produto encontrado", "data": data}

    except Exception as e:
        logger.error(f"Erro ao buscar produto: {e}", exc_info=True)
        return {"status": "error", "message": f"Erro ao buscar produto: {str(e)}"}


@tool
def search_products_by_name(product_name: str, limit: int = 10) -> Dict[str, Any]:
    """
    Busca produtos pelo nome (parcial) na tabela ADMAT_OPCOM.

    Args:
        product_name: Nome ou parte do nome do produto
        limit: Número máximo de resultados

    Returns:
        Lista de produtos encontrados
    """
    logger.info(f"Buscando produtos com nome contendo: {product_name}")

    try:
        db_manager = get_db_manager()
        query = f"""
        SELECT TOP {limit}
            CAST([CÓDIGO] AS VARCHAR(50)) as codigo,
            [NOME] as nome,
            [PREÇO 38%] as preco,
            [CATEGORIA] as categoria,
            [EST# UNE] as estoque
        FROM dbo.Admat_OPCOM
        WHERE [NOME] LIKE :search_term
        ORDER BY [NOME]
        """

        with db_manager.get_connection() as conn:
            result = conn.execute(text(query), {"search_term": f"%{product_name}%"})
            rows = result.fetchall()
            columns = result.keys() if rows else []

            if not rows:
                return {
                    "status": "not_found",
                    "message": f"Nenhum produto encontrado com '{product_name}'",
                    "data": [],
                }

            data = [dict(zip(columns, row)) for row in rows]

            return {
                "status": "success",
                "message": f"{len(data)} produtos encontrados",
                "data": data,
                "count": len(data),
            }

    except Exception as e:
        logger.error(f"Erro ao buscar produtos: {e}", exc_info=True)
        return {
            "status": "error",
            "message": f"Erro ao buscar produtos: {str(e)}",
            "data": [],
        }


@tool
def get_products_by_category(category: str, limit: int = 20) -> Dict[str, Any]:
    """
    Busca produtos por categoria.

    Args:
        category: Nome da categoria
        limit: Número máximo de resultados

    Returns:
        Lista de produtos da categoria
    """
    logger.info(f"Buscando produtos da categoria: {category}")

    try:
        db_manager = get_db_manager()
        query = f"""
        SELECT TOP {limit}
            CAST([CÓDIGO] AS VARCHAR(50)) as codigo,
            [NOME] as nome,
            [PREÇO 38%] as preco,
            [CATEGORIA] as categoria,
            [GRUPO] as grupo,
            [EST# UNE] as estoque
        FROM dbo.Admat_OPCOM
        WHERE [CATEGORIA] = :category
        ORDER BY [NOME]
        """

        with db_manager.get_connection() as conn:
            result = conn.execute(text(query), {"category": category})
            rows = result.fetchall()
            columns = result.keys() if rows else []

            if not rows:
                return {
                    "status": "not_found",
                    "message": f"Nenhum produto encontrado na categoria '{category}'",
                    "data": [],
                }

            data = [dict(zip(columns, row)) for row in rows]

            return {
                "status": "success",
                "message": f"{len(data)} produtos encontrados",
                "data": data,
                "count": len(data),
            }

    except Exception as e:
        logger.error(f"Erro ao buscar por categoria: {e}", exc_info=True)
        return {
            "status": "error",
            "message": f"Erro ao buscar por categoria: {str(e)}",
            "data": [],
        }


@tool
def get_top_selling_products(limit: int = 10) -> Dict[str, Any]:
    """
    Retorna os produtos mais vendidos nos últimos 30 dias.

    Args:
        limit: Número máximo de resultados

    Returns:
        Lista dos produtos mais vendidos
    """
    logger.info(f"Buscando top {limit} produtos mais vendidos")

    try:
        db_manager = get_db_manager()
        query = f"""
        SELECT TOP {limit}
            CAST([CÓDIGO] AS VARCHAR(50)) as codigo,
            [NOME] as nome,
            [VENDA 30D] as vendas_30d,
            [PREÇO 38%] as preco,
            [CATEGORIA] as categoria
        FROM dbo.Admat_OPCOM
        WHERE [VENDA 30D] > 0
        ORDER BY [VENDA 30D] DESC
        """

        with db_manager.get_connection() as conn:
            result = conn.execute(text(query))
            rows = result.fetchall()
            columns = result.keys() if rows else []

            if not rows:
                return {
                    "status": "not_found",
                    "message": "Nenhum produto com vendas encontrado",
                    "data": [],
                }

            data = [dict(zip(columns, row)) for row in rows]

            return {
                "status": "success",
                "message": f"{len(data)} produtos com vendas encontrados",
                "data": data,
                "count": len(data),
            }

    except Exception as e:
        logger.error(f"Erro ao buscar produtos mais vendidos: {e}", exc_info=True)
        return {
            "status": "error",
            "message": f"Erro ao buscar produtos: {str(e)}",
            "data": [],
        }


@tool
def get_product_stock(product_code: str) -> Dict[str, Any]:
    """
    Retorna o estoque de um produto específico.

    Args:
        product_code: Código do produto

    Returns:
        Informações de estoque
    """
    logger.info(f"Buscando estoque do produto: {product_code}")

    try:
        db_manager = get_db_manager()
        query = """
        SELECT TOP 1
            CAST([CÓDIGO] AS VARCHAR(50)) as codigo,
            [NOME] as nome,
            [EST# UNE] as estoque_unidades,
            [CATEGORIA] as categoria,
            [PREÇO 38%] as preco
        FROM dbo.Admat_OPCOM
        WHERE CAST([CÓDIGO] AS VARCHAR(50)) = :codigo
           OR [CÓDIGO] = :codigo_int
        """

        with db_manager.get_connection() as conn:
            result = conn.execute(
                text(query),
                {
                    "codigo": product_code,
                    "codigo_int": int(product_code) if product_code.isdigit() else 0,
                },
            )
            row = result.fetchone()

            if not row:
                return {
                    "status": "not_found",
                    "message": f"Produto {product_code} não encontrado",
                }

            columns = result.keys()
            data = dict(zip(columns, row))

            return {"status": "success", "message": "Estoque encontrado", "data": data}

    except Exception as e:
        logger.error(f"Erro ao buscar estoque: {e}", exc_info=True)
        return {"status": "error", "message": f"Erro ao buscar estoque: {str(e)}"}


# Lista de ferramentas SQL Server
sql_server_tools = [
    query_database,
    get_product_by_code,
    search_products_by_name,
    get_products_by_category,
    get_top_selling_products,
    get_product_stock,
]
