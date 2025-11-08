"""
Script de teste para validar o formato de apresentação da MC
"""
import sys
import os

# Adicionar caminho do projeto ao PYTHONPATH
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Importar a função de formatação
from core.agents.bi_agent_nodes import format_mc_response

# Dados de exemplo (simulando retorno de calcular_mc_produto)
exemplo_mc = {
    "produto_id": 704559,
    "une_id": 135,
    "nome": "PAPEL CHAMEX A4 75GRS 500FLS",
    "segmento": "PAPELARIA",
    "mc_calculada": 1614,
    "estoque_atual": 1320,
    "linha_verde": 414,
    "percentual_linha_verde": 318.8,
    "recomendacao": "ALERTA: Estoque acima da linha verde - Verificar dimensionamento"
}

print("=" * 80)
print("TESTE DE FORMATAÇÃO - MC (Média Comum)")
print("=" * 80)
print()

# Testar a função de formatação
resultado_formatado = format_mc_response(exemplo_mc)

print(resultado_formatado)
print()
print("=" * 80)
print("TESTE CONCLUÍDO COM SUCESSO!")
print("=" * 80)
