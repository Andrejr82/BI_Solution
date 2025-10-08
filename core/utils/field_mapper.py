"""
Módulo de Mapeamento de Campos
================================

Este módulo fornece mapeamento centralizado entre termos em linguagem natural
e os nomes reais das colunas na tabela admatao.parquet.

Baseado em: data/catalog_focused.json
Tabela: admatao.parquet (1.113.822 registros, 95 colunas)
"""

import json
import logging
from typing import Dict, List, Optional, Any
from pathlib import Path

logger = logging.getLogger(__name__)


class FieldMapper:
    """
    Classe responsável por mapear termos de linguagem natural para nomes de campos reais.
    """
    
    # Mapeamento de termos comuns para campos reais
    FIELD_MAPPING = {
        # Identificação e Classificação
        "segmento": "NOMESEGMENTO",
        "categoria": "NomeCategoria",
        "grupo": "NOMEGRUPO",
        "subgrupo": "NomeSUBGRUPO",
        "codigo": "PRODUTO",
        "código": "PRODUTO",
        "produto": "PRODUTO",
        "nome": "NOME",
        "nome_produto": "NOME",
        "fabricante": "NomeFabricante",
        "embalagem": "EMBALAGEM",
        "ean": "EAN",
        "tipo": "TIPO",
        "une": "UNE",
        "unidade": "UNE",
        "une_nome": "UNE_NOME",
        
        # Preços e Valores
        "preco": "LIQUIDO_38",
        "preço": "LIQUIDO_38",
        "preco_38": "LIQUIDO_38",
        "liquido_38": "LIQUIDO_38",
        
        # Estoque (PRINCIPAL)
        "estoque": "ESTOQUE_UNE",
        "estoque_une": "ESTOQUE_UNE",
        "estoque_cd": "ESTOQUE_CD",
        "estoque_lv": "ESTOQUE_LV",
        "estoque_gondola": "ESTOQUE_GONDOLA_LV",
        "estoque_ilha": "ESTOQUE_ILHA_LV",
        
        # Vendas
        "vendas": "VENDA_30DD",
        "vendas_30d": "VENDA_30DD",
        "vendas_30_dias": "VENDA_30DD",
        "venda_30dd": "VENDA_30DD",
        
        # Vendas Mensais
        "mes_01": "MES_01",
        "mes_02": "MES_02",
        "mes_03": "MES_03",
        "mes_04": "MES_04",
        "mes_05": "MES_05",
        "mes_06": "MES_06",
        "mes_07": "MES_07",
        "mes_08": "MES_08",
        "mes_09": "MES_09",
        "mes_10": "MES_10",
        "mes_11": "MES_11",
        "mes_12": "MES_12",
        "mes_parcial": "MES_PARCIAL",
        
        # ABC
        "abc_une_30dd": "ABC_UNE_30DD",
        "abc_cacula_90dd": "ABC_CACULA_90DD",
        
        # Datas
        "ultima_venda": "ULTIMA_VENDA_DATA_UNE",
        "ultima_entrada_cd": "ULTIMA_ENTRADA_DATA_CD",
        "ultima_entrada_une": "ULTIMA_ENTRADA_DATA_UNE",
        "ultimo_inventario": "ULTIMO_INVENTARIO_UNE",
        
        # Status
        "promocional": "PROMOCIONAL",
        "fora_linha": "FORALINHA",
        "foralinha": "FORALINHA",
        
        # Linha Verde
        "media_lv": "MEDIA_CONSIDERADA_LV",
        "leadtime_lv": "LEADTIME_LV",
        "ponto_pedido_lv": "PONTO_PEDIDO_LV",
        "exposicao_minima": "EXPOSICAO_MINIMA",
        "exposicao_maxima": "EXPOSICAO_MAXIMA_UNE",
        
        # Solicitações
        "solicitacao_pendente": "SOLICITACAO_PENDENTE",
        "solicitacao_data": "SOLICITACAO_PENDENTE_DATA",
        "solicitacao_qtde": "SOLICITACAO_PENDENTE_QTDE",
        
        # Outros
        "picklist": "PICKLIST",
        "nota": "NOTA",
        "serie": "SERIE",
    }
    
    # Tipos de dados dos campos
    FIELD_TYPES = {
        "PRODUTO": "integer",
        "NOME": "string",
        "NOMESEGMENTO": "string",
        "NomeCategoria": "string",
        "NOMEGRUPO": "string",
        "NomeSUBGRUPO": "string",
        "NomeFabricante": "string",
        "EMBALAGEM": "string",
        "EAN": "string",
        "LIQUIDO_38": "float",
        "ESTOQUE_UNE": "float",
        "ESTOQUE_CD": "float",
        "ESTOQUE_LV": "float",
        "ESTOQUE_GONDOLA_LV": "float",
        "ESTOQUE_ILHA_LV": "float",
        "VENDA_30DD": "float",
        "UNE": "integer",
        "UNE_NOME": "string",
        "TIPO": "integer",
        "PROMOCIONAL": "string",
        "FORALINHA": "string",
    }
    
    # Campos de estoque disponíveis (ordenados por prioridade)
    STOCK_FIELDS = [
        "ESTOQUE_UNE",      # Principal - Estoque na unidade
        "ESTOQUE_CD",       # Estoque no centro de distribuição
        "ESTOQUE_LV",       # Estoque linha verde
        "ESTOQUE_GONDOLA_LV",  # Estoque na gôndola
        "ESTOQUE_ILHA_LV",  # Estoque na ilha
    ]
    
    def __init__(self, catalog_path: Optional[str] = None):
        """
        Inicializa o mapeador de campos.
        
        Args:
            catalog_path: Caminho para o arquivo catalog_focused.json
        """
        self.catalog_path = catalog_path
        self.catalog_data = None
        
        if catalog_path:
            self._load_catalog()
    
    def _load_catalog(self):
        """Carrega o catálogo de dados."""
        try:
            with open(self.catalog_path, 'r', encoding='utf-8') as f:
                self.catalog_data = json.load(f)
            logger.info(f"Catálogo carregado: {self.catalog_path}")
        except Exception as e:
            logger.error(f"Erro ao carregar catálogo: {e}")
    
    def map_field(self, user_term: str) -> Optional[str]:
        """
        Mapeia um termo do usuário para o nome real do campo.
        
        Args:
            user_term: Termo em linguagem natural
            
        Returns:
            Nome real do campo ou None se não encontrado
        """
        # Normaliza o termo (lowercase, remove espaços)
        normalized = user_term.lower().strip().replace(" ", "_")
        
        # Busca no mapeamento
        real_field = self.FIELD_MAPPING.get(normalized)
        
        if real_field:
            logger.debug(f"Campo mapeado: '{user_term}' → '{real_field}'")
            return real_field
        
        # Se não encontrou, verifica se já é um nome de campo válido
        if user_term in self.get_all_fields():
            return user_term
        
        logger.warning(f"Campo não mapeado: '{user_term}'")
        return None
    
    def get_field_type(self, field_name: str) -> str:
        """
        Retorna o tipo de dados de um campo.
        
        Args:
            field_name: Nome do campo
            
        Returns:
            Tipo do campo ('string', 'integer', 'float', etc.)
        """
        return self.FIELD_TYPES.get(field_name, "string")
    
    def is_string_field(self, field_name: str) -> bool:
        """Verifica se um campo é do tipo string."""
        return self.get_field_type(field_name) == "string"
    
    def is_numeric_field(self, field_name: str) -> bool:
        """Verifica se um campo é numérico."""
        return self.get_field_type(field_name) in ["integer", "float"]
    
    def get_stock_field(self, stock_type: Optional[str] = None) -> str:
        """
        Retorna o campo de estoque apropriado.
        
        Args:
            stock_type: Tipo de estoque ('une', 'cd', 'lv', etc.) ou None para padrão
            
        Returns:
            Nome do campo de estoque
        """
        if stock_type:
            mapped = self.map_field(f"estoque_{stock_type}")
            if mapped:
                return mapped
        
        # Retorna o campo padrão
        return "ESTOQUE_UNE"
    
    def build_filter_condition(self, field_name: str, value: Any, operator: str = "==") -> str:
        """
        Constrói uma condição de filtro SQL apropriada para o campo.
        
        Args:
            field_name: Nome do campo
            value: Valor para filtrar
            operator: Operador ('==', '>', '<', 'contains', etc.)
            
        Returns:
            Condição SQL como string
        """
        if self.is_string_field(field_name):
            if operator == "contains" or operator == "like":
                return f"UPPER({field_name}) LIKE '%{str(value).upper()}%'"
            else:
                return f"UPPER({field_name}) = '{str(value).upper()}'"
        else:
            if operator == "==":
                return f"{field_name} = {value}"
            else:
                return f"{field_name} {operator} {value}"
    
    def build_zero_stock_condition(self, stock_field: Optional[str] = None) -> str:
        """
        Constrói condição SQL para estoque zero (incluindo NULL).
        
        Args:
            stock_field: Campo de estoque específico ou None para usar padrão
            
        Returns:
            Condição SQL
        """
        field = stock_field or self.get_stock_field()
        return f"({field} = 0 OR {field} IS NULL)"
    
    def get_all_fields(self) -> List[str]:
        """Retorna lista de todos os campos disponíveis."""
        if self.catalog_data and len(self.catalog_data) > 0:
            schema = self.catalog_data[0].get("schema", {})
            return list(schema.keys())
        return list(self.FIELD_MAPPING.values())
    
    def get_field_description(self, field_name: str) -> str:
        """
        Retorna a descrição de um campo do catálogo.
        
        Args:
            field_name: Nome do campo
            
        Returns:
            Descrição do campo
        """
        if self.catalog_data and len(self.catalog_data) > 0:
            descriptions = self.catalog_data[0].get("column_descriptions", {})
            return descriptions.get(field_name, "Sem descrição")
        return "Sem descrição"
    
    def generate_query_template(self, query_type: str, **kwargs) -> str:
        """
        Gera template de query SQL baseado no tipo.
        
        Args:
            query_type: Tipo de query ('categorias_estoque_zero', 'produtos_por_segmento', etc.)
            **kwargs: Parâmetros da query
            
        Returns:
            Query SQL como string
        """
        templates = {
            "categorias_estoque_zero": """
                SELECT 
                    {categoria_field} AS CATEGORIA,
                    COUNT(DISTINCT {produto_field}) AS TOTAL_PRODUTOS
                FROM admatao
                WHERE UPPER({segmento_field}) LIKE '%{segmento}%'
                    AND {stock_condition}
                GROUP BY {categoria_field}
                ORDER BY TOTAL_PRODUTOS DESC
            """,
            "produtos_por_segmento": """
                SELECT 
                    {produto_field} AS CODIGO,
                    {nome_field} AS NOME,
                    {categoria_field} AS CATEGORIA,
                    {estoque_field} AS ESTOQUE,
                    {preco_field} AS PRECO
                FROM admatao
                WHERE UPPER({segmento_field}) LIKE '%{segmento}%'
                ORDER BY {nome_field}
            """,
            "estoque_por_categoria": """
                SELECT 
                    {categoria_field} AS CATEGORIA,
                    COUNT(DISTINCT {produto_field}) AS TOTAL_PRODUTOS,
                    SUM(CASE WHEN {stock_condition} THEN 1 ELSE 0 END) AS PRODUTOS_SEM_ESTOQUE,
                    ROUND(AVG({estoque_field}), 2) AS MEDIA_ESTOQUE,
                    SUM({estoque_field}) AS ESTOQUE_TOTAL
                FROM admatao
                WHERE UPPER({segmento_field}) LIKE '%{segmento}%'
                GROUP BY {categoria_field}
                ORDER BY PRODUTOS_SEM_ESTOQUE DESC
            """
        }
        
        template = templates.get(query_type, "")
        if not template:
            return ""
        
        # Preenche os campos padrão
        params = {
            "produto_field": self.map_field("produto"),
            "nome_field": self.map_field("nome"),
            "categoria_field": self.map_field("categoria"),
            "segmento_field": self.map_field("segmento"),
            "estoque_field": self.get_stock_field(),
            "preco_field": self.map_field("preco"),
            "stock_condition": self.build_zero_stock_condition(),
        }
        params.update(kwargs)
        
        return template.format(**params).strip()


# Instância global do mapeador
_field_mapper = None

def get_field_mapper(catalog_path: Optional[str] = None) -> FieldMapper:
    """
    Retorna a instância global do FieldMapper.
    
    Args:
        catalog_path: Caminho para o catálogo (usado apenas na primeira chamada)
        
    Returns:
        Instância do FieldMapper
    """
    global _field_mapper
    if _field_mapper is None:
        _field_mapper = FieldMapper(catalog_path)
    return _field_mapper
