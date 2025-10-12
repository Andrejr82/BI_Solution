"""
Script para implementar Predicate Pushdown (FASE 2) em métodos _query_*.
Adiciona filtros específicos para evitar carregar o dataset completo.
"""

import re

# Mapeamento de métodos para seus filtros
METHOD_FILTERS = {
    # Métodos que filtram por UNE
    '_query_preco_produto_une_especifica': {
        'filters': ['produto_codigo', 'une_nome'],
        'mapping': {'produto_codigo': 'codigo', 'une_nome': 'une_nome'}
    },
    '_query_top_produtos_une_especifica': {
        'filters': ['une_nome'],
        'mapping': {'une_nome': 'une_nome'}
    },
    '_query_vendas_une_mes_especifico': {
        'filters': ['une_nome'],
        'mapping': {'une_nome': 'une_nome'}
    },
    '_query_consulta_une_especifica': {
        'filters': ['une_nome'],
        'mapping': {'une_nome': 'une_nome'}
    },
    '_query_vendas_produto_une': {
        'filters': ['produto_codigo', 'une_nome'],
        'mapping': {'produto_codigo': 'codigo', 'une_nome': 'une_nome'}
    },
    '_query_produto_vendas_une_barras': {
        'filters': ['produto_codigo'],
        'mapping': {'produto_codigo': 'codigo'}
    },

    # Métodos que filtram por segmento
    '_query_top_produtos_por_segmento': {
        'filters': ['segmento'],
        'mapping': {'segmento': 'nomesegmento'}
    },
    '_query_top_produtos_segmento_une': {
        'filters': ['segmento', 'une_nome'],
        'mapping': {'segmento': 'nomesegmento', 'une_nome': 'une_nome'}
    },
    '_query_distribuicao_categoria': {
        'filters': ['segmento'],
        'mapping': {'segmento': 'nomesegmento'}
    },
    '_query_crescimento_segmento': {
        'filters': ['segmento'],
        'mapping': {'segmento': 'nomesegmento'}
    },
    '_query_ranking_unes_por_segmento': {
        'filters': ['segmento'],
        'mapping': {'segmento': 'nomesegmento'}
    },

    # Métodos que filtram por categoria
    '_query_top_produtos_categoria_une': {
        'filters': ['categoria', 'une_nome'],
        'mapping': {'categoria': 'NOMECATEGORIA', 'une_nome': 'une_nome'}
    },
    '_query_performance_categoria': {
        'filters': ['categoria'],
        'mapping': {'categoria': 'NOMECATEGORIA'}
    },

    # Métodos que filtram por produto específico
    '_query_consulta_produto_especifico': {
        'filters': ['produto_codigo'],
        'mapping': {'produto_codigo': 'codigo'}
    },
    '_query_evolucao_vendas_produto': {
        'filters': ['produto_codigo'],
        'mapping': {'produto_codigo': 'codigo'}
    },
    '_query_produto_vendas_todas_unes': {
        'filters': ['produto_codigo'],
        'mapping': {'produto_codigo': 'codigo'}
    },

    # Métodos que filtram por fabricante
    '_query_ranking_fabricantes': {
        'filters': ['fabricante'],
        'mapping': {'fabricante': 'NOMEFABRICANTE'}
    },
}

def generate_filter_code(method_name, config):
    """Gera código de filtro para um método específico."""
    filters = config['filters']
    mapping = config['mapping']

    lines = []
    lines.append("        # Construir filtros para Predicate Pushdown")
    lines.append("        filters = {}")

    for param_key in filters:
        column_name = mapping[param_key]
        lines.append(f"        if params.get('{param_key}'):")

        # Tratamento especial para códigos de produto
        if 'codigo' in param_key:
            lines.append(f"            try:")
            lines.append(f"                filters['{column_name}'] = int(params['{param_key}'])")
            lines.append(f"            except (ValueError, TypeError):")
            lines.append(f"                filters['{column_name}'] = str(params['{param_key}'])")
        else:
            lines.append(f"            filters['{column_name}'] = params['{param_key}']")

    lines.append("")
    lines.append("        # Aplicar Predicate Pushdown")
    lines.append("        data = adapter.execute_query(filters)")

    return '\n'.join(lines)

def implement_filters(file_path):
    """Implementa filtros em métodos específicos."""

    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Backup
    backup_path = file_path.replace('.py', '_before_phase2.py')
    with open(backup_path, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"[OK] Backup criado: {backup_path}")

    modified_count = 0

    for method_name, config in METHOD_FILTERS.items():
        # Procurar o método e substituir o código de carregamento
        pattern = f'(def {method_name}\\(self, adapter: ParquetAdapter, params: Dict\\[str, Any\\]\\) -> Dict\\[str, Any\\]:[^]*?"""[^"]*"""\\n)(\\s+)data = adapter\\.execute_query\\({{}}\\)'

        def replace_loading(match):
            nonlocal modified_count
            method_def = match.group(1)
            indent = match.group(2)

            # Gerar código de filtro
            filter_code = generate_filter_code(method_name, config)

            modified_count += 1
            print(f"[FIX] {method_name} - Filtros: {config['filters']}")

            return method_def + filter_code

        content = re.sub(pattern, replace_loading, content, flags=re.DOTALL)

    # Salvar
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)

    print(f"\n[OK] Arquivo atualizado: {file_path}")
    print(f"[STATS] Metodos com Predicate Pushdown: {modified_count}/{len(METHOD_FILTERS)}")

    return modified_count

if __name__ == "__main__":
    file_path = r"C:\Users\André\Documents\Agent_Solution_BI\core\business_intelligence\direct_query_engine.py"
    count = implement_filters(file_path)
    print(f"\n[OK] FASE 2 - {count} metodos otimizados com Predicate Pushdown!")
