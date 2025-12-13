# backend/app/core/utils/fast_path_detector.py

import re
from typing import Optional

def detect_fast_path_query(query: str) -> Optional[str]:
    """
    Detects if a query can be handled by a fast-path, bypassing complex agent orchestration. 
    
    Fast-path queries are typically simple, direct requests that can be routed to a
    specific tool or information retrieval mechanism without LLM reasoning steps.

    Args:
        query: The user's natural language query.

    Returns:
        The name of the target node/tool for the fast-path, or None if no fast-path is detected.
    """
    query_lower = query.lower()

    # Fast-path for UNE Operations
    if "abastecimento" in query_lower or \
       "mc produto" in query_lower or \
       "preço final" in query_lower or \
       "validar transferência" in query_lower or \
       "sugerir transferências" in query_lower or \
       "rupturas críticas" in query_lower:
        # These queries can likely be routed directly to the specific UNE tools
        # The CaculinhaBIAgent already handles this with its tool routing logic.
        # This function could return a specific tool name to indicate a fast-path match.
        if "abastecimento" in query_lower:
            return "calcular_abastecimento_une"
        elif "mc produto" in query_lower:
            return "calcular_mc_produto"
        elif "preço final" in query_lower:
            return "calcular_preco_final_une"
        elif "validar transferência" in query_lower:
            return "validar_transferencia_produto"
        elif "sugerir transferências" in query_lower:
            return "sugerir_transferencias_automaticas"
        elif "rupturas críticas" in query_lower:
            return "encontrar_rupturas_criticas"

    # Fast-path for simple data retrieval/listing
    if re.search(r"mostre-me (as )?(dez )?(cinco )?(dez )?(ultimas |primeiras )?vendas", query_lower) or \
       re.search(r"listar (todos )?(os )?produtos", query_lower):
        # These might be handled by a direct database query tool or a simple data listing tool
        return "simple_data_listing_tool"

    # Fast-path for status/health checks
    if "status" in query_lower or "saúde" in query_lower:
        return "status_check_tool" # Example: an API endpoint for health

    return None

if __name__ == '__main__':
    print("--- Testing Fast-Path Detector ---")
    
    # UNE related queries
    print(f"Query: 'Qual o abastecimento da UNE 101?' -> Fast-path: {detect_fast_path_query('Qual o abastecimento da UNE 101?')}")
    print(f"Query: 'Calcular MC do produto X' -> Fast-path: {detect_fast_path_query('Calcular MC do produto X')}")
    print(f"Query: 'Validar transferência de 10 unidades' -> Fast-path: {detect_fast_path_query('Validar transferência de 10 unidades')}")
    print(f"Query: 'Encontrar rupturas críticas' -> Fast-path: {detect_fast_path_query('Encontrar rupturas críticas')}")

    # Simple data retrieval
    print(f"Query: 'Mostre-me as últimas vendas' -> Fast-path: {detect_fast_path_query('Mostre-me as últimas vendas')}")
    print(f"Query: 'Listar todos os produtos' -> Fast-path: {detect_fast_path_query('Listar todos os produtos')}")

    # Non-fast-path queries
    print(f"Query: 'Qual a correlação entre vendas e marketing?' -> Fast-path: {detect_fast_path_query('Qual a correlação entre vendas e marketing?')}")
    print(f"Query: 'Quero um gráfico complexo' -> Fast-path: {detect_fast_path_query('Quero um gráfico complexo')}")

    print("\nFast-path detection tests completed.")
