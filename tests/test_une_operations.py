"""
Testes Automatizados para Operações UNE
Valida as 3 ferramentas: abastecimento, MC e preços

Para executar:
    pytest tests/test_une_operations.py -v
    pytest tests/test_une_operations.py -v --tb=short
"""

import pytest
import sys
import os

# Adicionar diretório raiz ao path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.tools.une_tools import (
    calcular_abastecimento_une,
    calcular_mc_produto,
    calcular_preco_final_une
)


class TestCalcularAbastecimentoUNE:
    """Testes para a ferramenta calcular_abastecimento_une"""

    def test_abastecimento_une_valida_com_segmento(self):
        """Teste 1: Calcular abastecimento com UNE e segmento válidos"""
        result = calcular_abastecimento_une.invoke({
            'une_id': 2586,
            'segmento': 'TECIDOS'
        })

        assert 'error' not in result, f"Erro inesperado: {result.get('error')}"
        assert 'total_produtos' in result
        assert 'produtos' in result
        assert 'regra_aplicada' in result
        assert result['regra_aplicada'] == "ESTOQUE_UNE <= 50% LINHA_VERDE"
        assert result['une_id'] == 2586
        assert result['segmento'] == 'TECIDOS'
        assert isinstance(result['total_produtos'], int)
        assert isinstance(result['produtos'], list)

        # Validar que retorna produtos se houver
        if result['total_produtos'] > 0:
            assert len(result['produtos']) > 0
            assert len(result['produtos']) <= 20  # Máximo 20 produtos

            # Validar estrutura do primeiro produto
            primeiro_produto = result['produtos'][0]
            assert 'codigo' in primeiro_produto
            assert 'nome_produto' in primeiro_produto
            assert 'estoque_atual' in primeiro_produto
            assert 'linha_verde' in primeiro_produto
            assert 'qtd_a_abastecer' in primeiro_produto
            assert 'percentual_estoque' in primeiro_produto

    def test_abastecimento_une_valida_sem_segmento(self):
        """Teste 2: Calcular abastecimento sem filtro de segmento"""
        result = calcular_abastecimento_une.invoke({
            'une_id': 2599
        })

        assert 'error' not in result, f"Erro inesperado: {result.get('error')}"
        assert 'total_produtos' in result
        assert result['une_id'] == 2599
        assert result['segmento'] == 'Todos'

    def test_abastecimento_une_id_invalido(self):
        """Teste 3: Validar erro com UNE ID inválido"""
        result = calcular_abastecimento_une.invoke({
            'une_id': -1,
            'segmento': 'TECIDOS'
        })

        assert 'error' in result
        assert 'inteiro positivo' in result['error']

    def test_abastecimento_une_inexistente(self):
        """Teste 4: Validar comportamento com UNE inexistente"""
        result = calcular_abastecimento_une.invoke({
            'une_id': 99999
        })

        assert 'error' in result
        assert 'Nenhum produto encontrado' in result['error']


class TestCalcularMCProduto:
    """Testes para a ferramenta calcular_mc_produto"""

    def test_mc_produto_valido(self):
        """Teste 5: Calcular MC para produto e UNE válidos"""
        result = calcular_mc_produto.invoke({
            'produto_id': 704559,
            'une_id': 2586
        })

        assert 'error' not in result, f"Erro inesperado: {result.get('error')}"
        assert 'produto_id' in result
        assert 'une_id' in result
        assert 'nome' in result
        assert 'segmento' in result
        assert 'mc_calculada' in result
        assert 'estoque_atual' in result
        assert 'linha_verde' in result
        assert 'percentual_linha_verde' in result
        assert 'recomendacao' in result

        assert result['produto_id'] == 704559
        assert result['une_id'] == 2586
        assert isinstance(result['mc_calculada'], (int, float))
        assert isinstance(result['estoque_atual'], (int, float))
        assert isinstance(result['linha_verde'], (int, float))
        assert isinstance(result['percentual_linha_verde'], (int, float))

        # Validar que recomendação existe e não está vazia
        assert len(result['recomendacao']) > 0

    def test_mc_produto_recomendacoes(self):
        """Teste 6: Validar lógica de recomendações baseada em percentual"""
        # Testar produto que deve ter baixo estoque
        result = calcular_mc_produto.invoke({
            'produto_id': 704559,
            'une_id': 2586
        })

        assert 'recomendacao' in result
        recomendacao = result['recomendacao']
        percentual = result['percentual_linha_verde']

        # Validar que a recomendação segue a lógica esperada
        if percentual < 50:
            assert 'URGENTE' in recomendacao or 'Abastecer' in recomendacao
        elif percentual < 75:
            assert 'ATENÇÃO' in recomendacao or 'Planejar' in recomendacao
        elif percentual > 100:
            assert 'ALERTA' in recomendacao or 'acima' in recomendacao

    def test_mc_produto_id_invalido(self):
        """Teste 7: Validar erro com produto_id inválido"""
        result = calcular_mc_produto.invoke({
            'produto_id': -1,
            'une_id': 2586
        })

        assert 'error' in result
        assert 'inteiro positivo' in result['error']

    def test_mc_produto_inexistente(self):
        """Teste 8: Validar comportamento com produto inexistente"""
        result = calcular_mc_produto.invoke({
            'produto_id': 999999999,
            'une_id': 2586
        })

        assert 'error' in result
        assert 'não encontrado' in result['error']


class TestCalcularPrecoFinalUNE:
    """Testes para a ferramenta calcular_preco_final_une"""

    def test_preco_atacado_ranking_0_vista(self):
        """Teste 9: Calcular preço atacado (>=750) ranking 0 a vista"""
        result = calcular_preco_final_une.invoke({
            'valor_compra': 800.0,
            'ranking': 0,
            'forma_pagamento': 'vista'
        })

        assert 'error' not in result, f"Erro inesperado: {result.get('error')}"
        assert result['valor_original'] == 800.0
        assert result['tipo'] == 'Atacado'
        assert result['ranking'] == 0
        assert result['forma_pagamento'] == 'vista'
        assert 'preco_final' in result
        assert 'economia' in result
        assert 'percentual_economia' in result

        # Validar que preço final é menor que original
        assert result['preco_final'] < result['valor_original']
        assert result['economia'] > 0

        # Ranking 0 atacado: 38% + vista 38%
        # Valor esperado aproximado (não exato devido à aplicação sequencial)
        assert result['preco_final'] < 400  # Deve ser bem abaixo de 800

    def test_preco_varejo_ranking_2_30d(self):
        """Teste 10: Calcular preço varejo (<750) ranking 2 em 30 dias"""
        result = calcular_preco_final_une.invoke({
            'valor_compra': 600.0,
            'ranking': 2,
            'forma_pagamento': '30d'
        })

        assert 'error' not in result
        assert result['valor_original'] == 600.0
        assert result['tipo'] == 'Varejo'
        assert result['ranking'] == 2
        assert result['forma_pagamento'] == '30d'
        assert result['preco_final'] < result['valor_original']

        # Ranking 2 varejo: 30% + 30d: 36%
        assert result['preco_final'] < 400

    def test_preco_ranking_3_sem_desconto(self):
        """Teste 11: Validar ranking 3 (sem desconto de ranking)"""
        result = calcular_preco_final_une.invoke({
            'valor_compra': 1000.0,
            'ranking': 3,
            'forma_pagamento': 'vista'
        })

        assert 'error' not in result
        assert result['ranking'] == 3
        assert result['desconto_ranking'] == 'Sem desconto'

        # Apenas desconto de forma de pagamento deve ser aplicado
        # Vista = 38%, então: 1000 * (1-0.38) = 620
        assert result['preco_final'] == 620.0

    def test_preco_ranking_1_unico(self):
        """Teste 12: Validar ranking 1 (preço único, sempre 38%)"""
        result = calcular_preco_final_une.invoke({
            'valor_compra': 500.0,
            'ranking': 1,
            'forma_pagamento': '90d'
        })

        assert 'error' not in result
        assert result['ranking'] == 1
        assert result['tipo'] == 'Único'
        assert '38' in result['desconto_ranking']

    def test_preco_todas_formas_pagamento(self):
        """Teste 13: Validar todas as formas de pagamento"""
        formas = ['vista', '30d', '90d', '120d']
        descontos_esperados = [38.0, 36.0, 34.0, 30.0]

        for forma, desconto_esperado in zip(formas, descontos_esperados):
            result = calcular_preco_final_une.invoke({
                'valor_compra': 1000.0,
                'ranking': 3,  # Sem desconto de ranking
                'forma_pagamento': forma
            })

            assert 'error' not in result
            assert result['forma_pagamento'] == forma

            # Calcular preço esperado: 1000 * (1 - desconto/100)
            preco_esperado = 1000.0 * (1 - desconto_esperado / 100)
            # Usar aproximação para evitar erro de precisão float
            assert abs(result['preco_final'] - preco_esperado) < 0.01

    def test_preco_valor_invalido(self):
        """Teste 14: Validar erro com valor_compra inválido"""
        result = calcular_preco_final_une.invoke({
            'valor_compra': -100.0,
            'ranking': 0,
            'forma_pagamento': 'vista'
        })

        assert 'error' in result
        assert 'número positivo' in result['error']

    def test_preco_ranking_invalido(self):
        """Teste 15: Validar erro com ranking fora do intervalo"""
        result = calcular_preco_final_une.invoke({
            'valor_compra': 800.0,
            'ranking': 10,
            'forma_pagamento': 'vista'
        })

        assert 'error' in result
        assert 'entre 0 e 4' in result['error']

    def test_preco_forma_pagamento_invalida(self):
        """Teste 16: Validar erro com forma de pagamento inválida"""
        result = calcular_preco_final_une.invoke({
            'valor_compra': 800.0,
            'ranking': 0,
            'forma_pagamento': 'invalido'
        })

        assert 'error' in result


class TestIntegracaoCompleta:
    """Testes de integração end-to-end"""

    def test_workflow_completo_abastecimento_mc_preco(self):
        """Teste 17: Workflow completo - verificar produto, MC, calcular preço"""

        # Passo 1: Verificar produtos que precisam abastecimento
        abastecimento = calcular_abastecimento_une.invoke({
            'une_id': 2586,
            'segmento': 'TECIDOS'
        })

        assert 'error' not in abastecimento
        assert abastecimento['total_produtos'] >= 0

        # Passo 2: Se houver produtos, verificar MC do primeiro
        if abastecimento['total_produtos'] > 0:
            primeiro_produto = abastecimento['produtos'][0]
            produto_id = primeiro_produto['codigo']

            mc_result = calcular_mc_produto.invoke({
                'produto_id': produto_id,
                'une_id': 2586
            })

            assert 'error' not in mc_result
            assert mc_result['produto_id'] == produto_id

        # Passo 3: Calcular preço para uma compra típica
        preco_result = calcular_preco_final_une.invoke({
            'valor_compra': 1000.0,
            'ranking': 0,
            'forma_pagamento': 'vista'
        })

        assert 'error' not in preco_result
        assert preco_result['preco_final'] < 1000.0


# Configuração de pytest
if __name__ == "__main__":
    pytest.main([__file__, '-v', '--tb=short'])
