"""
Field Mapper - Mapeamento de Campos para admmat.parquet
========================================================

Este módulo fornece mapeamento centralizado entre termos naturais
e os nomes reais das colunas no arquivo admmat.parquet.

Atualizado para: admmat.parquet (extraído recentemente do banco de dados)
Data: 07 de outubro de 2025
"""

import logging
import json
from pathlib import Path
from typing import Dict, List, Optional, Any

logger = logging.getLogger(__name__)


class FieldMapper:
    """
    Mapeador de campos para admmat.parquet
    
    Converte termos naturais (como "segmento", "categoria", "estoque")
    para os nomes reais das colunas no arquivo Parquet.
    """
    
    def __init__(self, catalog_path: Optional[str] = None):
        """
        Inicializa o mapeador de campos.
        
        Args:
            catalog_path: Caminho para o catálogo JSON (opcional)
        """
        self.catalog_path = catalog_path
        self.catalog = self._load_catalog() if catalog_path else {}
        
        # Mapeamento baseado no admmat.parquet
        self.field_mapping = {
            # Campos de identificação
            "id": "id",
            "une": "une",
            "une_nome": "une_nome",
            "loja": "une_nome",
            "unidade": "une",
            
            # Produto
            "produto": "codigo",
            "codigo": "codigo",
            "cod": "codigo",
            "nome_produto": "nome_produto",
            "nome": "nome_produto",
            "descricao": "nome_produto",
            "ean": "ean",
            "embalagem": "embalagem",
            
            # Hierarquia de classificação (ATENÇÃO: capitalização mista!)
            "segmento": "nomesegmento",          # minúsculo
            "categoria": "NOMECATEGORIA",        # MAIÚSCULO
            "grupo": "nomegrupo",                # minúsculo
            "subgrupo": "NOMESUBGRUPO",          # MAIÚSCULO
            "fabricante": "NOMEFABRICANTE",      # MAIÚSCULO
            
            # Estoque (ATENÇÃO: campo principal é estoque_atual!)
            "estoque": "estoque_atual",          # Campo principal
            "estoque_une": "estoque_atual",      # Alias
            "estoque_atual": "estoque_atual",
            "estoque_cd": "estoque_cd",
            "estoque_lv": "estoque_lv",
            "estoque_gondola": "estoque_gondola_lv",
            "estoque_ilha": "estoque_ilha_lv",
            
            # Vendas
            "vendas": "venda_30_d",
            "vendas_30d": "venda_30_d",
            "venda_30_d": "venda_30_d",
            "venda_30_dd": "venda_30_d",
            "mes_01": "mes_01",
            "mes_02": "mes_02",
            "mes_03": "mes_03",
            "mes_04": "mes_04",
            "mes_05": "mes_05",
            "mes_06": "mes_06",
            "mes_07": "mes_07",
            "mes_08": "mes_08",
            "mes_09": "mes_09",
            "mes_10": "mes_10",
            "mes_11": "mes_11",
            "mes_12": "mes_12",
            
            # Preço
            "preco": "preco_38_percent",
            "valor": "preco_38_percent",
            "preco_38": "preco_38_percent",
            
            # ABC
            "abc": "abc_une_30_dd",
            "abc_une": "abc_une_30_dd",
            "abc_cacula": "abc_cacula_90_dd",
            "curva_abc": "abc_une_30_dd",
            
            # Flags
            "promocional": "promocional",
            "fora_linha": "foralinha",
            "tipo": "tipo",
            
            # Datas
            "ultima_venda": "ultima_venda_data_une",
            "ultima_entrada": "ultima_entrada_data_une",
            "ultimo_inventario": "ultimo_inventario_une",
        }
        
        # Tipos de dados dos campos
        self.field_types = {
            "id": "integer",
            "une": "integer",
            "codigo": "integer",
            "nomesegmento": "string",
            "NOMECATEGORIA": "string",
            "nomegrupo": "string",
            "NOMESUBGRUPO": "string",
            "NOMEFABRICANTE": "string",
            "estoque_atual": "numeric",
            "estoque_cd": "numeric",
            "estoque_lv": "numeric",
            "venda_30_d": "float",
            "preco_38_percent": "numeric",
            "promocional": "string",
            "foralinha": "string",
        }
        
        logger.info(f"FieldMapper inicializado com {len(self.field_mapping)} mapeamentos")
    
    def _load_catalog(self) -> Dict:
        """Carrega o catálogo JSON se disponível."""
        if not self.catalog_path or not Path(self.catalog_path).exists():
            return {}
        
        try:
            with open(self.catalog_path, 'r', encoding='utf-8') as f:
                catalog = json.load(f)
                logger.info(f"Catálogo carregado: {self.catalog_path}")
                return catalog
        except Exception as e:
            logger.warning(f"Erro ao carregar catálogo: {e}")
            return {}
    
    def map_field(self, user_term: str) -> str:
        """
        Mapeia um termo do usuário para o nome real da coluna.
        
        Args:
            user_term: Termo usado pelo usuário (ex: "segmento", "estoque")
        
        Returns:
            Nome real da coluna no Parquet
        
        Examples:
            >>> mapper.map_field("segmento")
            'nomesegmento'
            >>> mapper.map_field("categoria")
            'NOMECATEGORIA'
            >>> mapper.map_field("estoque")
            'estoque_atual'
        """
        normalized = user_term.lower().strip()
        return self.field_mapping.get(normalized, user_term)
    
    def get_field_type(self, field_name: str) -> str:
        """
        Retorna o tipo de dados de um campo.
        
        Args:
            field_name: Nome do campo
        
        Returns:
            Tipo do campo ('string', 'integer', 'float', 'numeric', 'date')
        """
        return self.field_types.get(field_name, "string")
    
    def build_filter_condition(
        self, 
        field_name: str, 
        value: Any, 
        operator: str = "=="
    ) -> str:
        """
        Constrói uma condição de filtro SQL apropriada.
        
        Args:
            field_name: Nome do campo
            value: Valor para comparação
            operator: Operador (==, !=, >, <, contains, etc.)
        
        Returns:
            Condição SQL formatada
        
        Examples:
            >>> mapper.build_filter_condition("nomesegmento", "TECIDO", "contains")
            "UPPER(nomesegmento) LIKE '%TECIDO%'"
            
            >>> mapper.build_filter_condition("estoque_atual", 0, "==")
            "estoque_atual = 0"
        """
        field_type = self.get_field_type(field_name)
        
        if operator == "contains":
            # Busca case-insensitive em campos de texto
            return f"UPPER({field_name}) LIKE '%{str(value).upper()}%'"
        
        elif operator == "startswith":
            return f"UPPER({field_name}) LIKE '{str(value).upper()}%'"
        
        elif operator == "endswith":
            return f"UPPER({field_name}) LIKE '%{str(value).upper()}'"
        
        elif operator in ["==", "="]:
            if field_type == "string":
                return f"{field_name} = '{value}'"
            else:
                return f"{field_name} = {value}"
        
        elif operator == "!=":
            if field_type == "string":
                return f"{field_name} != '{value}'"
            else:
                return f"{field_name} != {value}"
        
        elif operator in [">", "<", ">=", "<="]:
            return f"{field_name} {operator} {value}"
        
        else:
            return f"{field_name} {operator} {value}"
    
    def build_zero_stock_condition(self, stock_field: str = "estoque_atual") -> str:
        """
        Constrói condição para filtrar produtos com estoque zero.
        
        IMPORTANTE: Inclui produtos com estoque NULL!
        
        Args:
            stock_field: Nome do campo de estoque (padrão: estoque_atual)
        
        Returns:
            Condição SQL que captura estoque = 0 OU NULL
        
        Example:
            >>> mapper.build_zero_stock_condition()
            '(estoque_atual = 0 OR estoque_atual IS NULL)'
        """
        return f"({stock_field} = 0 OR {stock_field} IS NULL)"
    
    def generate_query_template(
        self, 
        query_type: str, 
        **kwargs
    ) -> str:
        """
        Gera template de query SQL baseado no tipo.
        
        Args:
            query_type: Tipo da query (ex: 'categorias_estoque_zero')
            **kwargs: Parâmetros adicionais
        
        Returns:
            Query SQL formatada
        """
        if query_type == "categorias_estoque_zero":
            segmento = kwargs.get("segmento", "")
            return f"""
                SELECT 
                    NOMECATEGORIA AS CATEGORIA,
                    COUNT(DISTINCT codigo) AS TOTAL_PRODUTOS
                FROM admmat
                WHERE UPPER(nomesegmento) LIKE '%{segmento.upper()}%'
                    AND (estoque_atual = 0 OR estoque_atual IS NULL)
                GROUP BY NOMECATEGORIA
                ORDER BY TOTAL_PRODUTOS DESC
            """
        
        elif query_type == "produtos_por_segmento":
            segmento = kwargs.get("segmento", "")
            return f"""
                SELECT 
                    codigo AS CODIGO,
                    nome_produto AS PRODUTO,
                    NOMECATEGORIA AS CATEGORIA,
                    estoque_atual AS ESTOQUE,
                    venda_30_d AS VENDAS_30D
                FROM admmat
                WHERE UPPER(nomesegmento) LIKE '%{segmento.upper()}%'
                ORDER BY venda_30_d DESC
                LIMIT 100
            """
        
        elif query_type == "top_vendas":
            limite = kwargs.get("limite", 10)
            return f"""
                SELECT 
                    codigo AS CODIGO,
                    nome_produto AS PRODUTO,
                    nomesegmento AS SEGMENTO,
                    NOMECATEGORIA AS CATEGORIA,
                    venda_30_d AS VENDAS_30D,
                    estoque_atual AS ESTOQUE
                FROM admmat
                WHERE venda_30_d > 0
                ORDER BY venda_30_d DESC
                LIMIT {limite}
            """
        
        else:
            return "SELECT * FROM admmat LIMIT 100"
    
    def get_all_mappings(self) -> Dict[str, str]:
        """Retorna todos os mapeamentos disponíveis."""
        return self.field_mapping.copy()
    
    def validate_field(self, field_name: str) -> bool:
        """
        Valida se um campo existe no mapeamento.
        
        Args:
            field_name: Nome do campo para validar
        
        Returns:
            True se o campo existe, False caso contrário
        """
        return field_name in self.field_mapping.values()


# Singleton global
_field_mapper_instance: Optional[FieldMapper] = None


def get_field_mapper(catalog_path: Optional[str] = None) -> FieldMapper:
    """
    Retorna a instância singleton do FieldMapper.
    
    Args:
        catalog_path: Caminho para o catálogo JSON (opcional)
    
    Returns:
        Instância do FieldMapper
    """
    global _field_mapper_instance
    
    if _field_mapper_instance is None:
        _field_mapper_instance = FieldMapper(catalog_path)
    
    return _field_mapper_instance


# ============================================================================
# TESTES
# ============================================================================

if __name__ == "__main__":
    print("=" * 80)
    print("TESTE DO FIELD MAPPER - admmat.parquet")
    print("=" * 80)
    print()
    
    mapper = FieldMapper()
    
    print("📋 Testes de Mapeamento:")
    print()
    
    tests = [
        ("segmento", "nomesegmento"),
        ("categoria", "NOMECATEGORIA"),
        ("produto", "codigo"),
        ("estoque", "estoque_atual"),
        ("vendas", "venda_30_d"),
        ("preco", "preco_38_percent"),
        ("fabricante", "NOMEFABRICANTE"),
    ]
    
    for user_term, expected in tests:
        result = mapper.map_field(user_term)
        status = "✅" if result == expected else "❌"
        print(f"   {status} '{user_term}' → '{result}' (esperado: '{expected}')")
    
    print()
    print("🔍 Teste de Condições de Filtro:")
    print()
    
    cond1 = mapper.build_filter_condition("nomesegmento", "TECIDO", "contains")
    print(f"   Segmento contém 'TECIDO':")
    print(f"   {cond1}")
    print()
    
    cond2 = mapper.build_zero_stock_condition()
    print(f"   Estoque zero (incluindo NULL):")
    print(f"   {cond2}")
    print()
    
    print("📊 Teste de Query Template:")
    print()
    
    query = mapper.generate_query_template("categorias_estoque_zero", segmento="TECIDO")
    print(f"   Query: Categorias do segmento TECIDOS com estoque 0")
    print(f"   {query.strip()}")
    print()
    
    print("=" * 80)
    print("TODOS OS TESTES CONCLUÍDOS!")
    print("=" * 80)
