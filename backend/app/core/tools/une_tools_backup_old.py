# backend/app/core/tools/une_tools.py

from typing import Dict, Any, List, Optional
from functools import lru_cache

# Assuming HybridAdapter exists in infrastructure/data as per TASK_LIST
# We will create a placeholder for it later if it doesn't exist
# from ....infrastructure.data.hybrid_adapter import HybridAdapter
# Placeholder for now
class HybridAdapter:
    def __init__(self, parquet_dir: str = "data/parquet", sql_server_conn_str: Optional[str] = None):
        print(f"HybridAdapter initialized with parquet_dir={parquet_dir} and sql_server_conn_str={'<hidden>' if sql_server_conn_str else 'None'}")
        # Placeholder for actual data loading/connection
        self.data = {} # Simulating loaded data
        self.schema = {
            "une_id": "int", "produto_id": "int", "segmento": "str",
            "media_considerada_lv": "float", "estoque_origem": "int",
            "estoque_destino": "int", "linha_verde": "int",
            "vendas_diarias": "float", "transferencias_pendentes": "int",
            "criticidade": "str" # URGENTE/ALTA/NORMAL
        }

    def fetch_data(self, filters: Dict[str, Any], columns: Optional[List[str]] = None) -> List[Dict]:
        print(f"Fetching data with filters: {filters}, columns: {columns}")
        # Simulate data fetching
        # In a real scenario, this would query Parquet or SQL Server
        # For now, return some dummy data that matches schema
        dummy_data = [
            {"une_id": 1, "produto_id": 101, "segmento": "A", "media_considerada_lv": 10.0, "estoque_origem": 50, "estoque_destino": 20, "linha_verde": 30, "vendas_diarias": 5.0, "transferencias_pendentes": 0, "criticidade": "NORMAL"},
            {"une_id": 1, "produto_id": 102, "segmento": "A", "media_considerada_lv": 20.0, "estoque_origem": 10, "estoque_destino": 5, "linha_verde": 40, "vendas_diarias": 10.0, "transferencias_pendentes": 0, "criticidade": "URGENTE"},
            {"une_id": 2, "produto_id": 101, "segmento": "B", "media_considerada_lv": 15.0, "estoque_origem": 100, "estoque_destino": 80, "linha_verde": 20, "vendas_diarias": 7.0, "transferencias_pendentes": 0, "criticidade": "NORMAL"},
            {"une_id": 3, "produto_id": 103, "segmento": "C", "media_considerada_lv": 5.0, "estoque_origem": 5, "estoque_destino": 2, "linha_verde": 10, "vendas_diarias": 1.0, "transferencias_pendentes": 0, "criticidade": "ALTA"},
        ]
        
        # Apply simple filtering for demonstration
        filtered_data = []
        for item in dummy_data:
            match = True
            for key, value in filters.items():
                if key in item and item[key] != value:
                    match = False
                    break
            if match:
                filtered_data.append(item)
        
        if columns:
            return [{col: item[col] for col in columns if col in item} for item in filtered_data]
        return filtered_data
    
    def get_known_columns(self) -> Dict[str, str]:
        return self.schema

# Placeholder for @tool decorator
def tool(func):
    def wrapper(*args, **kwargs):
        print(f"Tool '{func.__name__}' called with args: {args}, kwargs: {kwargs}")
        return func(*args, **kwargs)
    return wrapper

# --- Helper Functions (T3.2.2, T3.2.3, T3.2.4) ---

@lru_cache(maxsize=1)
def _get_data_adapter() -> HybridAdapter:
    """
    Returns a cached instance of HybridAdapter.
    In a real scenario, configuration for parquet_dir and sql_server_conn_str
    would come from settings.
    """
    # Placeholder: assuming data/parquet is standard, and SQL Server conn_str might be None for now
    # We will expand this once settings.py is updated.
    return HybridAdapter(parquet_dir="data/parquet")

def _normalize_dataframe(df_data: List[Dict]) -> List[Dict]:
    """
    Normalizes column names from SQL to Parquet conventions if necessary,
    and ensures consistent data types.
    Placeholder for actual normalization logic.
    """
    # Example: if SQL had 'UNE_ID', convert to 'une_id'
    normalized_data = []
    for row in df_data:
        new_row = {k.lower(): v for k, v in row.items()} # Simple lowercase normalization
        normalized_data.append(new_row)
    return normalized_data

def _load_data(filters: Dict[str, Any], columns: Optional[List[str]] = None) -> List[Dict]:
    """
    Loads data using the HybridAdapter with given filters and columns.
    Includes basic schema validation and error handling (placeholder).
    """
    adapter = _get_data_adapter()
    raw_data = adapter.fetch_data(filters, columns)
    
    # Placeholder for schema validation and recovery
    valid_data = []
    expected_schema = adapter.get_known_columns()
    for row in raw_data:
        # Simple validation: ensure all expected columns (if specified) are present
        # and basic type checks
        is_valid = True
        if columns:
            for col in columns:
                if col not in row:
                    print(f"Warning: Column '{col}' missing in row: {row}")
                    is_valid = False
                    break
        if is_valid:
            valid_data.append(row)
            
    return _normalize_dataframe(valid_data)

# --- UNE Business Rules (T3.2.5) ---

@tool
def calcular_abastecimento_une(une_id: int, segmento: Optional[str] = None, limite: int = 10) -> List[Dict]:
    """
    Calcula a necessidade de abastecimento para uma UNE específica, opcionalmente por segmento.
    Retorna os produtos com maior criticidade de abastecimento.
    """
    print(f"Calculating supply for UNE: {une_id}, Segmento: {segmento}, Limite: {limite}")
    
    # Placeholder for fetching relevant data
    filters = {"une_id": une_id}
    if segmento:
        filters["segmento"] = segmento
        
    data = _load_data(filters)
    
    results = []
    for row in data:
        # Implementar cálculo de criticidade de abastecimento (placeholder)
        # Exemplo: (linha_verde - estoque_origem) / vendas_diarias
        estoque = row.get("estoque_origem", 0)
        linha_verde = row.get("linha_verde", 0)
        vendas_diarias = row.get("vendas_diarias", 1) # Avoid division by zero
        
        necessidade = linha_verde - estoque
        dias_para_ruptura = necessidade / vendas_diarias if vendas_diarias > 0 else float('inf')

        criticidade_abastecimento = "NORMAL"
        if dias_para_ruptura < 5 and necessidade > 0: # Example rule
            criticidade_abastecimento = "URGENTE"
        elif dias_para_ruptura < 10 and necessidade > 0:
            criticidade_abastecimento = "ALTA"

        row["necessidade_abastecimento"] = necessidade
        row["dias_para_ruptura"] = round(dias_para_ruptura, 2)
        row["criticidade_abastecimento"] = criticidade_abastecimento
        results.append(row)

    # Sort by criticidade_abastecimento (URGENTE > ALTA > NORMAL) and then necessidade
    priority_order = {"URGENTE": 3, "ALTA": 2, "NORMAL": 1}
    results.sort(key=lambda x: (priority_order.get(x.get("criticidade_abastecimento"), 0), x.get("necessidade_abastecimento", 0)), reverse=True)
    
    return results[:limite]


@tool
def calcular_mc_produto(produto_id: int, une_id: int) -> Dict[str, Any]:
    """
    Calcula a Margem de Contribuição (MC) para um produto específico em uma UNE.
    A MC é baseada na 'media_considerada_lv' ou na média de vendas, conforme regras de negócio.
    """
    print(f"Calculating MC for Produto: {produto_id}, UNE: {une_id}")
    
    data = _load_data({"produto_id": produto_id, "une_id": une_id}, columns=["media_considerada_lv", "vendas_diarias"])
    
    if not data:
        return {"produto_id": produto_id, "une_id": une_id, "mc_calculada": None, "mensagem": "Dados não encontrados para o produto/UNE."}
        
    product_data = data[0]
    media_considerada_lv = product_data.get("media_considerada_lv")
    vendas_diarias = product_data.get("vendas_diarias")

    mc_calculada = None
    mensagem = "Cálculo de MC não aplicável com os dados fornecidos."
    
    # Placeholder for actual MC calculation logic (T3.2.5)
    # Exemplo: se media_considerada_lv existe, usa ela. Senão, usa vendas_diarias como base.
    if media_considerada_lv is not None:
        mc_calculada = media_considerada_lv * 0.25 # Exemplo: 25% de MC sobre a LV
        mensagem = "MC calculada com base na média considerada LV."
    elif vendas_diarias is not None:
        mc_calculada = vendas_diarias * 0.20 # Exemplo: 20% de MC sobre vendas diárias
        mensagem = "MC calculada com base na média de vendas diárias."

    return {
        "produto_id": produto_id,
        "une_id": une_id,
        "mc_calculada": round(mc_calculada, 2) if mc_calculada is not None else None,
        "mensagem": mensagem
    }

@tool
def calcular_preco_final_une(produto_id: int, une_id: int) -> Dict[str, Any]:
    """
    Calcula o preço final de venda para um produto em uma UNE específica,
    considerando políticas de precificação (placeholder).
    """
    print(f"Calculating final price for Produto: {produto_id}, UNE: {une_id}")
    
    data = _load_data({"produto_id": produto_id, "une_id": une_id}, columns=["media_considerada_lv"])
    
    if not data:
        return {"produto_id": produto_id, "une_id": une_id, "preco_final": None, "mensagem": "Dados não encontrados para o produto/UNE."}
        
    product_data = data[0]
    base_price = product_data.get("media_considerada_lv") # Using LV as a base price placeholder
    
    preco_final = None
    mensagem = "Não foi possível calcular o preço final."

    if base_price is not None:
        # Placeholder for complex pricing policies (T3.2.5)
        # Exemplo: Adicionar 10% de margem e 5% de imposto
        preco_final = base_price * 1.10 * 1.05
        mensagem = "Preço final calculado com base no preço base e políticas internas."

    return {
        "produto_id": produto_id,
        "une_id": une_id,
        "preco_final": round(preco_final, 2) if preco_final is not None else None,
        "mensagem": mensagem
    }

@tool
def validar_transferencia_produto(produto_id: int, une_origem: int, une_destino: int, quantidade: int) -> Dict[str, Any]:
    """
    Valida se uma transferência de produto entre UNEs é possível,
    considerando estoque na origem, linha verde do destino, etc.
    """
    print(f"Validating transfer: Produto {produto_id} from UNE {une_origem} to UNE {une_destino}, Quantidade {quantidade}")
    
    # Fetch data for origin and destination UNEs
    origin_data = _load_data({"produto_id": produto_id, "une_id": une_origem}, columns=["estoque_origem"])
    dest_data = _load_data({"produto_id": produto_id, "une_id": une_destino}, columns=["linha_verde", "estoque_origem", "transferencias_pendentes"])
    
    if not origin_data:
        return {"status": "falha", "mensagem": f"Dados da UNE de origem {une_origem} não encontrados para o produto {produto_id}."}
    if not dest_data:
        return {"status": "falha", "mensagem": f"Dados da UNE de destino {une_destino} não encontrados para o produto {produto_id}."}
        
    estoque_origem = origin_data[0].get("estoque_origem", 0)
    linha_verde_destino = dest_data[0].get("linha_verde", 0)
    estoque_destino_atual = dest_data[0].get("estoque_origem", 0) # Using estoque_origem for current stock at destination
    transferencias_pendentes = dest_data[0].get("transferencias_pendentes", 0)

    # Placeholder for validation rules (T3.2.5)
    if estoque_origem < quantidade:
        return {"status": "falha", "mensagem": f"Estoque insuficiente na UNE de origem ({estoque_origem}) para transferir {quantidade} unidades."}
    
    # Check if destination would exceed Linea Verde after transfer + pending transfers
    estoque_apos_transferencia = estoque_destino_atual + quantidade + transferencias_pendentes
    if estoque_apos_transferencia > linha_verde_destino * 1.2: # Example: allow up to 20% over LV
        return {"status": "alerta", "mensagem": f"A transferência pode fazer a UNE de destino exceder significativamente a Linha Verde (LV={linha_verde_destino}). Estoque total após transferência: {estoque_apos_transferencia}."}
        
    return {"status": "sucesso", "mensagem": "Transferência validada e possível."}

@tool
def sugerir_transferencias_automaticas(segmento: Optional[str] = None, une_origem_excluir: Optional[int] = None, limite: int = 5) -> List[Dict[str, Any]]:
    """
    Sugere transferências automáticas baseadas em produtos com alta criticidade de ruptura
    e disponibilidade em outras UNEs.
    """
    print(f"Suggesting automatic transfers for Segmento: {segmento}, Excluir UNE: {une_origem_excluir}, Limite: {limite}")
    
    # Placeholder for identifying products in rupture (high criticality)
    rupture_products = encontrar_rupturas_criticas(limite=limite*2) # Get more to filter
    
    suggestions = []
    for prod_rupture in rupture_products:
        product_id = prod_rupture["produto_id"]
        une_destino = prod_rupture["une_id"]
        
        # Find potential origin UNEs
        filters = {"produto_id": product_id}
        if segmento:
            filters["segmento"] = segmento
        if une_origem_excluir:
            filters["une_id"] = {"$ne": une_origem_excluir} # Placeholder for "not equal"
            
        all_unes_for_product = _load_data(filters, columns=["une_id", "estoque_origem", "linha_verde"])
        
        for potential_origin in all_unes_for_product:
            une_origem = potential_origin["une_id"]
            estoque_origem = potential_origin["estoque_origem"]
            
            # Simple logic: if origin has enough stock and it's not the destination
            if estoque_origem > prod_rupture.get("necessidade_abastecimento", 0) and une_origem != une_destino:
                # Validate the transfer (using the tool itself for consistency)
                validation_result = validar_transferencia_produto(product_id, une_origem, une_destino, prod_rupture.get("necessidade_abastecimento", 1))
                
                if validation_result["status"] == "sucesso":
                    suggestions.append({
                        "produto_id": product_id,
                        "une_origem": une_origem,
                        "une_destino": une_destino,
                        "quantidade_sugerida": prod_rupture.get("necessidade_abastecimento", 1),
                        "mensagem": validation_result["mensagem"]
                    })
                    if len(suggestions) >= limite:
                        break
        if len(suggestions) >= limite:
            break
            
    return suggestions[:limite]


@tool
def encontrar_rupturas_criticas(limite: int = 5) -> List[Dict[str, Any]]:
    """
    Identifica UNEs/produtos com maior probabilidade de ruptura crítica,
    baseado em estoque atual, linha verde e vendas diárias.
    """
    print(f"Finding critical ruptures, Limite: {limite}")
    
    data = _load_data({}) # Load all data for rupture analysis
    
    ruptures = []
    for row in data:
        estoque = row.get("estoque_origem", 0)
        linha_verde = row.get("linha_verde", 0)
        vendas_diarias = row.get("vendas_diarias", 1) # Avoid division by zero
        
        # Placeholder for critical rupture logic (T3.2.5)
        # Criticidade: URGENTE (estoque < 0.5 * LV e < 3 dias de venda)
        # ALTA (estoque < LV e < 7 dias de venda)
        
        dias_cobertura = estoque / vendas_diarias if vendas_diarias > 0 else float('inf')
        
        criticidade = "NORMAL"
        if estoque < (0.5 * linha_verde) and dias_cobertura < 3 and linha_verde > 0:
            criticidade = "URGENTE"
        elif estoque < linha_verde and dias_cobertura < 7 and linha_verde > 0:
            criticidade = "ALTA"
            
        if criticidade in ["URGENTE", "ALTA"]:
            row["dias_cobertura"] = round(dias_cobertura, 2)
            row["criticidade_ruptura"] = criticidade
            # Add a 'necessidade_abastecimento' for consistency with other tools
            row["necessidade_abastecimento"] = max(0, linha_verde - estoque)
            ruptures.append(row)
            
    # Sort by criticidade_ruptura (URGENTE > ALTA) and then by necessidade_abastecimento
    priority_order = {"URGENTE": 3, "ALTA": 2, "NORMAL": 1}
    ruptures.sort(key=lambda x: (priority_order.get(x.get("criticidade_ruptura"), 0), x.get("necessidade_abastecimento", 0)), reverse=True)
            
    return ruptures[:limite]
