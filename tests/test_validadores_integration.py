"""
Testes de Integração dos Validadores com une_tools.py
Valida que todas as funções estão usando os validadores corretamente
"""

import pytest
import pandas as pd
from pathlib import Path
import sys

# Adicionar path do projeto
sys.path.insert(0, str(Path(__file__).parent.parent))

# Import das funções a serem testadas
from core.tools.une_tools import (
    get_produtos_une,
    get_transferencias,
    get_estoque_une,
    get_vendas_une,
    get_unes_disponiveis,
    get_preco_produto,
    get_total_vendas_une,
    get_total_estoque_une,
    health_check
)


class TestValidadoresIntegration:
    """Suite de testes para validação da integração"""

    def test_imports_validadores(self):
        """Testa se imports dos validadores estão corretos"""
        try:
            from core.validators.schema_validator import SchemaValidator
            from core.utils.query_validator import validate_columns, handle_nulls, safe_filter
            from core.utils.error_handler import error_handler_decorator
            assert True
        except ImportError as e:
            pytest.fail(f"Erro ao importar validadores: {e}")

    def test_get_produtos_une_estrutura_retorno(self):
        """Testa estrutura de retorno padronizada de get_produtos_une"""
        result = get_produtos_une(1)

        # Validar estrutura
        assert isinstance(result, dict), "Retorno deve ser dict"
        assert "success" in result, "Deve ter campo 'success'"
        assert "data" in result, "Deve ter campo 'data'"
        assert "message" in result, "Deve ter campo 'message'"

        # Validar tipos
        assert isinstance(result["success"], bool), "success deve ser bool"
        assert isinstance(result["data"], list), "data deve ser list"
        assert isinstance(result["message"], str), "message deve ser str"

    def test_get_transferencias_estrutura_retorno(self):
        """Testa estrutura de retorno padronizada de get_transferencias"""
        result = get_transferencias(1)

        assert isinstance(result, dict)
        assert "success" in result
        assert "data" in result
        assert "message" in result

    def test_get_estoque_une_estrutura_retorno(self):
        """Testa estrutura de retorno padronizada de get_estoque_une"""
        result = get_estoque_une(1)

        assert isinstance(result, dict)
        assert "success" in result
        assert "data" in result
        assert "message" in result

    def test_get_vendas_une_estrutura_retorno(self):
        """Testa estrutura de retorno padronizada de get_vendas_une"""
        result = get_vendas_une(1)

        assert isinstance(result, dict)
        assert "success" in result
        assert "data" in result
        assert "message" in result

    def test_get_unes_disponiveis_estrutura_retorno(self):
        """Testa estrutura de retorno padronizada de get_unes_disponiveis"""
        result = get_unes_disponiveis()

        assert isinstance(result, dict)
        assert "success" in result
        assert "data" in result
        assert "message" in result

    def test_get_preco_produto_estrutura_retorno(self):
        """Testa estrutura de retorno padronizada de get_preco_produto"""
        result = get_preco_produto(1, "PROD001")

        assert isinstance(result, dict)
        assert "success" in result
        assert "data" in result
        assert "message" in result

    def test_health_check_estrutura_retorno(self):
        """Testa estrutura de retorno de health_check"""
        result = health_check()

        assert isinstance(result, dict)
        assert "success" in result
        assert "data" in result
        assert "message" in result

        # Validar estrutura de dados
        assert isinstance(result["data"], dict), "data deve ser dict com status de arquivos"

    def test_error_handling_une_invalida(self):
        """Testa se error handler captura UNE inválida"""
        # Testar com UNE None (deve ser capturado pelo decorator)
        try:
            result = get_produtos_une(None)
            # Se não crashou, validar resposta de erro
            assert result["success"] == False or result["data"] == []
        except Exception:
            pytest.fail("Erro não foi capturado pelo decorator")

    def test_error_handling_arquivo_inexistente(self):
        """Testa comportamento quando arquivo Parquet não existe"""
        # Simular chamada que tentaria acessar arquivo inexistente
        # (depende da implementação, mas não deve crashar)
        result = get_produtos_une(99999)

        # Não deve crashar, deve retornar resposta padronizada
        assert isinstance(result, dict)
        assert "success" in result

    def test_validacao_schema_executada(self):
        """Testa se validação de schema está sendo executada"""
        # Se arquivo existe e tem schema válido, deve retornar success=True
        # Se arquivo não existe ou schema inválido, deve retornar success=False com mensagem

        result = get_produtos_une(1)

        if result["success"] == False:
            # Validar que mensagem menciona schema ou arquivo
            assert any(palavra in result["message"].lower() for palavra in ["schema", "arquivo", "erro"])

    def test_tratamento_nulls_aplicado(self):
        """Testa se tratamento de nulls está sendo aplicado"""
        # Se houver registros retornados, verificar que não há nulls críticos
        result = get_produtos_une(1)

        if result["success"] and len(result["data"]) > 0:
            primeiro_produto = result["data"][0]

            # Campos críticos não devem ser None (devido a handle_nulls)
            if "preco_venda" in primeiro_produto:
                assert primeiro_produto["preco_venda"] is not None

    def test_conversao_tipos_aplicada(self):
        """Testa se conversão segura de tipos está sendo aplicada"""
        result = get_produtos_une(1)

        if result["success"] and len(result["data"]) > 0:
            primeiro_produto = result["data"][0]

            # Validar tipos esperados
            if "preco_venda" in primeiro_produto:
                assert isinstance(primeiro_produto["preco_venda"], (int, float))

            if "estoque_atual" in primeiro_produto:
                assert isinstance(primeiro_produto["estoque_atual"], int)

    def test_filtro_seguro_aplicado(self):
        """Testa se filtros seguros estão sendo aplicados"""
        # Buscar UNE específica
        result = get_produtos_une(1)

        if result["success"] and len(result["data"]) > 0:
            # Todos os registros devem ter UNE = 1
            for produto in result["data"]:
                if "UNE" in produto:
                    assert produto["UNE"] == 1, "Filtro não está funcionando corretamente"

    def test_transferencias_filtros_multiplos(self):
        """Testa se get_transferencias aceita múltiplos filtros"""
        # Testar com todos os parâmetros opcionais
        result = get_transferencias(
            une=1,
            data_inicio="2024-01-01",
            data_fim="2024-12-31",
            status="CONCLUIDA"
        )

        assert isinstance(result, dict)
        assert "success" in result

    def test_agregacoes_funcionam(self):
        """Testa se funções de agregação funcionam"""
        # get_total_vendas_une
        result_vendas = get_total_vendas_une(1)
        assert isinstance(result_vendas, dict)
        assert "success" in result_vendas

        if result_vendas["success"]:
            assert isinstance(result_vendas["data"], (int, float))

        # get_total_estoque_une
        result_estoque = get_total_estoque_une(1)
        assert isinstance(result_estoque, dict)
        assert "success" in result_estoque

        if result_estoque["success"]:
            assert isinstance(result_estoque["data"], (int, float))

    def test_health_check_valida_arquivos(self):
        """Testa se health_check valida todos os arquivos esperados"""
        result = health_check()

        assert result["success"] == True

        arquivos_esperados = [
            "produtos.parquet",
            "transferencias.parquet",
            "estoque.parquet",
            "vendas.parquet",
            "unes.parquet"
        ]

        # Todos os arquivos devem estar no status
        for arquivo in arquivos_esperados:
            assert arquivo in result["data"], f"Arquivo {arquivo} não verificado"

            # Validar estrutura de cada status
            status = result["data"][arquivo]
            assert "existe" in status
            assert "schema_valido" in status
            assert "erros" in status

    def test_mensagens_descritivas(self):
        """Testa se mensagens de retorno são descritivas"""
        result = get_produtos_une(1)

        # Mensagem não deve estar vazia
        assert len(result["message"]) > 0

        # Mensagem deve conter informação útil
        if result["success"]:
            assert any(palavra in result["message"].lower() for palavra in ["produto", "encontrado", "registros"])

    def test_compatibilidade_interface(self):
        """Testa se interface pública das funções não mudou"""
        # Testar chamadas básicas (não deve dar erro de assinatura)
        try:
            get_produtos_une(1)
            get_transferencias(1)
            get_estoque_une(1)
            get_vendas_une(1)
            get_unes_disponiveis()
            get_preco_produto(1, "PROD001")
            health_check()
            assert True
        except TypeError as e:
            pytest.fail(f"Interface pública mudou: {e}")


# =====================================================
# TESTES DE PERFORMANCE
# =====================================================

class TestPerformance:
    """Testes de performance das funções validadas"""

    def test_performance_get_produtos_une(self):
        """Testa se performance é aceitável (<2s)"""
        import time

        start = time.time()
        result = get_produtos_une(1)
        elapsed = time.time() - start

        assert elapsed < 2.0, f"Performance ruim: {elapsed:.2f}s (esperado <2s)"

    def test_performance_health_check(self):
        """Testa se health_check é rápido (<5s)"""
        import time

        start = time.time()
        result = health_check()
        elapsed = time.time() - start

        assert elapsed < 5.0, f"Performance ruim: {elapsed:.2f}s (esperado <5s)"


# =====================================================
# RUNNER
# =====================================================

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
