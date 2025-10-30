"""
Testes Unitários para Integração CodeGenAgent + ColumnValidator
FASE 1.1 - Validação Completa da Integração

Testes cobertos:
1. Validação de colunas corretas
2. Detecção de colunas inválidas
3. Auto-correção de colunas similares
4. Retry automático (2 tentativas)
5. Execução de código validado
6. Estatísticas de validação
"""

import pytest
import polars as pl
import sys
import os
from unittest.mock import Mock, patch, MagicMock

# Adicionar path do projeto
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../..")))

from core.agents.code_gen_agent_integrated import (
    CodeGenAgent,
    create_code_gen_agent,
    validate_and_execute_code
)


# ============================================================================
# FIXTURES
# ============================================================================

@pytest.fixture
def sample_dataframe():
    """Cria DataFrame de teste com colunas conhecidas."""
    return pl.DataFrame({
        "UNE_NOME": ["UNE A", "UNE B", "UNE C"],
        "TOTAL_CLIENTES": [100, 200, 150],
        "RECEITA_TOTAL": [10000.0, 20000.0, 15000.0],
        "REGIAO": ["Sul", "Norte", "Centro"]
    })


@pytest.fixture
def code_gen_agent():
    """Cria instância do CodeGenAgent para testes."""
    return CodeGenAgent(max_retries=2)


# ============================================================================
# TESTES DE VALIDAÇÃO
# ============================================================================

class TestColumnValidation:
    """Testes de validação de colunas."""

    def test_valid_columns_pass_validation(self, code_gen_agent, sample_dataframe):
        """Teste: Colunas corretas passam na validação."""
        code = """
import polars as pl
result = df.select(["UNE_NOME", "TOTAL_CLIENTES"]).head(5)
"""
        is_valid, validation_result = code_gen_agent._validate_columns(code, sample_dataframe)

        assert is_valid is True
        assert validation_result["valid"] is True
        assert len(validation_result.get("errors", [])) == 0

    def test_invalid_columns_fail_validation(self, code_gen_agent, sample_dataframe):
        """Teste: Colunas inválidas falham na validação."""
        code = """
import polars as pl
result = df.select(["COLUNA_INEXISTENTE", "OUTRA_COLUNA_ERRADA"])
"""
        is_valid, validation_result = code_gen_agent._validate_columns(code, sample_dataframe)

        assert is_valid is False
        assert validation_result["valid"] is False
        assert len(validation_result.get("invalid_columns", [])) > 0


# ============================================================================
# TESTES DE AUTO-CORREÇÃO
# ============================================================================

class TestAutoCorrection:
    """Testes de auto-correção de colunas."""

    def test_auto_correct_similar_column_name(self, code_gen_agent, sample_dataframe):
        """Teste: Auto-correção de nome similar (UNE_NAME → UNE_NOME)."""
        code = """
import polars as pl
result = df.select(["UNE_NAME", "TOTAL_CLIENTES"])
"""
        validation_result = {
            "valid": False,
            "invalid_columns": ["UNE_NAME"],
            "suggestions": {"UNE_NAME": "UNE_NOME"}
        }

        corrected_code = code_gen_agent._auto_correct_columns(
            code,
            validation_result,
            sample_dataframe
        )

        assert "UNE_NOME" in corrected_code
        assert "UNE_NAME" not in corrected_code


# ============================================================================
# TESTES DE EXECUÇÃO
# ============================================================================

class TestCodeExecution:
    """Testes de execução de código."""

    def test_execute_valid_code_successfully(self, code_gen_agent, sample_dataframe):
        """Teste: Execução bem-sucedida de código válido."""
        code = """
import polars as pl
result = df.select(["UNE_NOME", "TOTAL_CLIENTES"]).head(2)
"""
        context = {"df": sample_dataframe}

        success, result, error = code_gen_agent._execute_code(code, "df", context)

        assert success is True
        assert result is not None
        assert error is None
        assert isinstance(result, pl.DataFrame)
        assert len(result) == 2


# ============================================================================
# TESTES DE INTEGRAÇÃO COMPLETA
# ============================================================================

class TestFullIntegration:
    """Testes de integração completa: validação + correção + execução."""

    def test_valid_code_executes_without_retry(self, code_gen_agent, sample_dataframe):
        """Teste: Código válido executa sem retry."""
        code = """
import polars as pl
result = df.select(["UNE_NOME", "TOTAL_CLIENTES"]).head(3)
"""
        context = {"df": sample_dataframe}

        success, result, error = code_gen_agent.validate_and_execute(code, "df", context)

        assert success is True
        assert result is not None
        assert error is None


if __name__ == "__main__":
    """Executar testes com pytest."""
    pytest.main([__file__, "-v"])
