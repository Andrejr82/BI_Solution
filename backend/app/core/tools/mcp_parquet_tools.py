# core/tools/mcp_sql_server_tools.py
import os
import pandas as pd
from typing import Dict, Any
from langchain_core.tools import tool
import logging

# Caminho para o arquivo Parquet - Fonte única: Filial_Madureira
PARQUET_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "data", "parquet")
FILIAL_MADUREIRA_PATH = os.path.join(PARQUET_DIR, "Filial_Madureira.parquet")


@tool
def get_product_data(product_code: str) -> Dict[str, Any]:
    """Busca dados de um produto em Filial_Madureira.parquet."""
    logging.info(f"Buscando produto: {product_code}")

    try:
        if not os.path.exists(FILIAL_MADUREIRA_PATH):
            logging.error(f"Arquivo não encontrado: {FILIAL_MADUREIRA_PATH}")
            return {"error": "Fonte de dados não encontrada."}

        df = pd.read_parquet(FILIAL_MADUREIRA_PATH)

        # Converter para string se a coluna de código existir
        if "CODIGO" in df.columns:
            df["CODIGO"] = df["CODIGO"].astype(str)
            product_code = str(product_code)
            product_info = df[df["CODIGO"] == product_code]
        elif "codigo" in df.columns:
            df["codigo"] = df["codigo"].astype(str)
            product_code = str(product_code)
            product_info = df[df["codigo"] == product_code]
        else:
            return {"error": "Coluna de código não encontrada."}

        if product_info.empty:
            return {"data": f"Produto não encontrado: {product_code}"}

        return {"data": product_info.to_dict(orient="records")}

    except Exception as e:
        logging.error(f"Erro ao buscar produto: {e}", exc_info=True)
        return {"error": f"Erro ao buscar dados: {e}"}


@tool
def get_product_stock(product_id: int) -> Dict[str, Any]:
    """Retorna dados de um produto específico em Filial_Madureira."""
    logging.info(f"Buscando dados do produto: {product_id}")
    try:
        if not os.path.exists(FILIAL_MADUREIRA_PATH):
            logging.error(f"Arquivo não encontrado: {FILIAL_MADUREIRA_PATH}")
            return {"error": "Fonte de dados não encontrada."}

        df = pd.read_parquet(FILIAL_MADUREIRA_PATH)

        product_stock_info = df[df["PRODUTO"] == product_id_str]

        if product_stock_info.empty:
            return {"data": f"Nenhum produto encontrado com o ID {product_id}."}

        # Assumindo que a coluna de estoque se chama 'ESTOQUE'
        stock = product_stock_info["ESTOQUE"].iloc[
            0
        ]  # Pega o primeiro valor de estoque encontrado
        return {"data": {"product_id": product_id, "stock": stock}}

    except Exception as e:
        logging.error(f"Erro ao buscar estoque do produto: {e}", exc_info=True)
        return {
            "error": f"Ocorreu um erro inesperado ao buscar o estoque do produto: {e}"
        }


@tool
def list_product_categories() -> Dict[str, Any]:
    """
    Retorna uma lista de todas as categorias de produtos disponíveis no arquivo Parquet 'Filial_Madureira.parquet'.
    """
    logging.info(
        "Listando categorias de produtos do arquivo Parquet 'Filial_Madureira.parquet'."
    )
    try:
        if not os.path.exists(FILIAL_MADUREIRA_PATH):
            logging.error(f"Arquivo Parquet não encontrado em: {FILIAL_MADUREIRA_PATH}")
            return {
                "error": "Fonte de dados de produtos (Filial_Madureira.parquet) não encontrada."
            }

        df = pd.read_parquet(FILIAL_MADUREIRA_PATH)

        # Assumindo que a coluna de categoria se chama 'CATEGORIA'
        if "CATEGORIA" not in df.columns:
            return {
                "error": "Coluna 'CATEGORIA' não encontrada no arquivo Filial_Madureira.parquet."
            }

        categories = df["CATEGORIA"].unique().tolist()
        return {"data": {"categories": categories}}

    except Exception as e:
        logging.error(f"Erro ao listar categorias de produtos: {e}", exc_info=True)
        return {
            "error": f"Ocorreu um erro inesperado ao listar categorias de produtos: {e}"
        }


# A lista de ferramentas agora reflete a nova arquitetura.
sql_tools = [
    get_product_data,
    get_product_stock,
    list_product_categories,
]
