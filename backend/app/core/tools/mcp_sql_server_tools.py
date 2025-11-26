# core/tools/mcp_sql_server_tools.py
import os
import pandas as pd
from typing import Dict, Any
from langchain_core.tools import tool
import logging

# Caminho único para Filial_Madureira
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

        # Procurar coluna de código (CODIGO ou codigo)
        codigo_col = None
        if "CODIGO" in df.columns:
            codigo_col = "CODIGO"
        elif "codigo" in df.columns:
            codigo_col = "codigo"

        if not codigo_col:
            return {"error": "Coluna de código não encontrada."}

        df[codigo_col] = df[codigo_col].astype(str)
        product_code = str(product_code)
        product_info = df[df[codigo_col] == product_code]

        if product_info.empty:
            return {"data": f"Produto não encontrado: {product_code}"}

        return {"data": product_info.to_dict(orient="records")}

    except Exception as e:
        logging.error(f"Erro ao buscar produto: {e}", exc_info=True)
        return {"error": f"Erro ao buscar dados: {e}"}


@tool
def get_product_stock(product_id: int) -> Dict[str, Any]:
    """Retorna dados de um produto em Filial_Madureira."""
    logging.info(f"Buscando produto: {product_id}")
    try:
        if not os.path.exists(FILIAL_MADUREIRA_PATH):
            logging.error(f"Arquivo não encontrado: {FILIAL_MADUREIRA_PATH}")
            return {"error": "Fonte de dados não encontrada."}

        df = pd.read_parquet(FILIAL_MADUREIRA_PATH)

        # Procurar coluna de código
        codigo_col = None
        if "CODIGO" in df.columns:
            codigo_col = "CODIGO"
        elif "codigo" in df.columns:
            codigo_col = "codigo"

        if not codigo_col:
            return {"error": "Coluna de código não encontrada."}

        df[codigo_col] = df[codigo_col].astype(str)
        product_id_str = str(product_id)
        product_info = df[df[codigo_col] == product_id_str]

        if product_info.empty:
            return {"data": f"Produto não encontrado: {product_id}"}

        return {"data": product_info.to_dict(orient="records")}

    except Exception as e:
        logging.error(f"Erro ao buscar produto: {e}", exc_info=True)
        return {"error": f"Erro ao buscar dados: {e}"}


@tool
def list_product_categories() -> Dict[str, Any]:
    """Lista categorias disponíveis em Filial_Madureira."""
    logging.info("Listando categorias...")
    try:
        if not os.path.exists(FILIAL_MADUREIRA_PATH):
            logging.error(f"Arquivo não encontrado: {FILIAL_MADUREIRA_PATH}")
            return {"error": "Fonte de dados não encontrada."}

        df = pd.read_parquet(FILIAL_MADUREIRA_PATH)

        # Procurar coluna de categoria
        cat_col = None
        for col in df.columns:
            if "categoria" in col.lower() or "category" in col.lower():
                cat_col = col
                break

        if not cat_col and "CATEGORIA" in df.columns:
            cat_col = "CATEGORIA"

        if not cat_col:
            return {"error": "Coluna de categoria não encontrada."}

        categories = df[cat_col].unique().tolist()
        return {"data": {"categories": categories}}

    except Exception as e:
        logging.error(f"Erro ao listar categorias: {e}", exc_info=True)
        return {"error": f"Erro: {e}"}


# Lista de ferramentas
sql_tools = [
    get_product_data,
    get_product_stock,
    list_product_categories,
]
