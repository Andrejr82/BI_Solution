"""
Testes para validadores e handlers implementados.

Este módulo testa:
- SchemaValidator
- QueryValidator
- ErrorHandler

Autor: Code Agent
Data: 2025-10-17
"""

import pytest
import pandas as pd
import logging
from pathlib import Path
import tempfile
import json

# Configurar imports relativos ao projeto
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.validators.schema_validator import SchemaValidator, validate_parquet_schema
from core.utils.query_validator import (
    QueryValidator,
    validate_columns,
    handle_nulls,
    safe_filter,
    get_friendly_error
)
from core.utils.error_handler import (
    ErrorHandler,
    ErrorContext,
    handle_error,
    get_error_stats,
    error_handler_decorator,
    create_error_response
)

# Configurar logging para testes
logging.basicConfig(level=logging.INFO)


class TestSchemaValidator:
    """Testes para SchemaValidator."""

    def test_init_validator(self):
        """Teste de inicialização do validador."""
        validator = SchemaValidator()
        assert validator is not None
        assert validator.catalog is not None
        assert isinstance(validator.catalog, dict)

    def test_type_mapping(self):
        """Teste do mapeamento de tipos."""
        validator = SchemaValidator()

        # Tipos compatíveis
        assert validator._is_type_compatible('int64', 'int64')
        assert validator._is_type_compatible('int32', 'int64')
        assert validator._is_type_compatible('float64', 'float32')
        assert validator._is_type_compatible('string', 'utf8')

        # Tipos incompatíveis
        assert not validator._is_type_compatible('string', 'int64')
        assert not validator._is_type_compatible('bool', 'float64')

    def test_validate_columns(self):
        """Teste de validação de colunas."""
        validator = SchemaValidator()

        # Criar schema mock
        import pyarrow as pa
        schema = pa.schema([
            ('col1', pa.int64()),
            ('col2', pa.string()),
            ('col3', pa.float64())
        ])

        expected_schema = {
            'columns': {
                'col1': {'type': 'int64'},
                'col2': {'type': 'string'},
                'col3': {'type': 'float64'}
            }
        }

        errors = validator._validate_columns(schema, expected_schema, 'test_table')
        assert len(errors) == 0  # Nenhum erro

        # Testar com coluna faltante
        expected_schema['columns']['col4'] = {'type': 'string'}
        errors = validator._validate_columns(schema, expected_schema, 'test_table')
        assert len(errors) > 0  # Deve ter erro

    def test_list_required_columns(self):
        """Teste de listagem de colunas obrigatórias."""
        validator = SchemaValidator()

        # Mock: adicionar tabela de teste ao catálogo
        validator.catalog['test_table'] = {
            'columns': {
                'id': {'type': 'int64'},
                'name': {'type': 'string'}
            }
        }

        required = validator.list_required_columns('test_table')
        assert 'id' in required
        assert 'name' in required

    def test_validate_query_columns(self):
        """Teste de validação de colunas de query."""
        validator = SchemaValidator()

        # Mock
        validator.catalog['test_table'] = {
            'columns': {
                'col1': {'type': 'int64'},
                'col2': {'type': 'string'}
            }
        }

        # Query válida
        is_valid, invalid = validator.validate_query_columns(
            'test_table',
            ['col1', 'col2']
        )
        assert is_valid
        assert len(invalid) == 0

        # Query inválida
        is_valid, invalid = validator.validate_query_columns(
            'test_table',
            ['col1', 'col_inexistente']
        )
        assert not is_valid
        assert 'col_inexistente' in invalid


class TestQueryValidator:
    """Testes para QueryValidator."""

    def test_init_query_validator(self):
        """Teste de inicialização."""
        validator = QueryValidator(default_timeout=30)
        assert validator.default_timeout == 30

    def test_validate_columns_in_dataframe(self):
        """Teste de validação de colunas em DataFrame."""
        df = pd.DataFrame({
            'col1': [1, 2, 3],
            'col2': ['a', 'b', 'c']
        })

        is_valid, missing = validate_columns(df, ['col1', 'col2'])
        assert is_valid
        assert len(missing) == 0

        is_valid, missing = validate_columns(df, ['col1', 'col3'])
        assert not is_valid
        assert 'col3' in missing

    def test_handle_null_values(self):
        """Teste de tratamento de valores nulos."""
        df = pd.DataFrame({
            'col1': [1, None, 3],
            'col2': ['a', None, 'c']
        })

        # Estratégia: drop
        df_clean = handle_nulls(df, 'col1', strategy='drop')
        assert df_clean['col1'].isna().sum() == 0
        assert len(df_clean) == 2

        # Estratégia: fill
        df_clean = handle_nulls(df, 'col2', strategy='fill', fill_value='N/A')
        assert df_clean['col2'].isna().sum() == 0
        assert 'N/A' in df_clean['col2'].values

    def test_validate_and_convert_types(self):
        """Teste de conversão de tipos."""
        validator = QueryValidator()

        df = pd.DataFrame({
            'col_int': ['1', '2', '3'],
            'col_float': ['1.5', '2.5', 'invalid'],
            'col_str': [1, 2, 3]
        })

        df_converted = validator.validate_and_convert_types(df, {
            'col_int': 'int',
            'col_float': 'float',
            'col_str': 'str'
        })

        assert df_converted['col_int'].dtype == 'int64'
        assert df_converted['col_float'].dtype == 'float64'
        assert df_converted['col_str'].dtype == 'object'

    def test_safe_filter(self):
        """Teste de filtro seguro."""
        df = pd.DataFrame({
            'col1': [1, 2, 3, 4, 5]
        })

        # Filtro válido
        df_filtered = safe_filter(
            df,
            filter_func=lambda df: df[df['col1'] > 2]
        )
        assert len(df_filtered) == 3

        # Filtro inválido (coluna inexistente) - deve retornar DataFrame original
        df_filtered = safe_filter(
            df,
            filter_func=lambda df: df[df['col_inexistente'] > 2]
        )
        assert len(df_filtered) == len(df)  # DataFrame original

    def test_get_user_friendly_error(self):
        """Teste de mensagens amigáveis."""
        error = FileNotFoundError("arquivo.parquet")
        message = get_friendly_error(error)

        assert 'não encontrado' in message.lower()
        assert isinstance(message, str)


class TestErrorHandler:
    """Testes para ErrorHandler."""

    def test_error_context_creation(self):
        """Teste de criação de contexto de erro."""
        error = ValueError("Teste de erro")
        context = {'function': 'test_func', 'param': 'value'}

        error_ctx = ErrorContext(error, context)

        assert error_ctx.error_type == 'ValueError'
        assert error_ctx.error_message == "Teste de erro"
        assert error_ctx.context == context
        assert error_ctx.user_message is not None

    def test_error_context_to_dict(self):
        """Teste de conversão para dict."""
        error = KeyError("campo")
        context = {'operation': 'query'}

        error_ctx = ErrorContext(error, context)
        error_dict = error_ctx.to_dict()

        assert 'timestamp' in error_dict
        assert 'error_type' in error_dict
        assert 'user_message' in error_dict
        assert error_dict['error_type'] == 'KeyError'

    def test_handle_error(self):
        """Teste de tratamento de erro."""
        try:
            raise ValueError("Erro de teste")
        except Exception as e:
            error_ctx = handle_error(
                e,
                context={'test': True},
                user_message="Erro personalizado"
            )

            assert error_ctx.user_message == "Erro personalizado"
            assert error_ctx.context['test'] is True

    def test_error_stats(self):
        """Teste de estatísticas de erros."""
        handler = ErrorHandler()
        handler.clear_stats()

        # Gerar alguns erros
        errors = [
            ValueError("erro 1"),
            ValueError("erro 2"),
            KeyError("erro 3")
        ]

        for error in errors:
            handler.handle_error(error, {}, save_to_file=False)

        stats = handler.get_error_stats()

        assert stats['total_errors'] == 3
        assert stats['error_counts']['ValueError'] == 2
        assert stats['error_counts']['KeyError'] == 1
        assert stats['most_common_error'] == 'ValueError'

    def test_error_handler_decorator(self):
        """Teste de decorador de error handling."""

        @error_handler_decorator(
            context_func=lambda x: {'param': x},
            return_on_error={'success': False, 'error': None}
        )
        def function_that_fails(param):
            if param == 'fail':
                raise ValueError("Falha intencional")
            return {'success': True, 'data': param}

        # Caso de sucesso
        result = function_that_fails('ok')
        assert result['success'] is True
        assert result['data'] == 'ok'

        # Caso de falha
        result = function_that_fails('fail')
        assert result['success'] is False
        assert 'error' in result

    def test_create_error_response(self):
        """Teste de criação de resposta de erro."""
        error = FileNotFoundError("arquivo.txt")
        context = {'operation': 'read_file', 'file': 'arquivo.txt'}

        response = create_error_response(error, context, include_details=True)

        assert response['success'] is False
        assert response['count'] == 0
        assert len(response['data']) == 0
        assert 'message' in response
        assert 'error_type' in response
        assert response['error_type'] == 'FileNotFoundError'
        assert 'error_details' in response


class TestIntegration:
    """Testes de integração."""

    def test_full_validation_flow(self):
        """Teste de fluxo completo de validação."""

        # 1. Criar DataFrame de teste
        df = pd.DataFrame({
            'produto_id': ['P001', 'P002', 'P003'],
            'preco': [10.5, None, 30.0],
            'estoque': ['5', '10', 'invalid']
        })

        # 2. Validar colunas
        is_valid, missing = validate_columns(
            df,
            ['produto_id', 'preco', 'estoque']
        )
        assert is_valid

        # 3. Tratar nulos
        df = handle_nulls(df, 'preco', strategy='fill', fill_value=0.0)
        assert df['preco'].isna().sum() == 0

        # 4. Converter tipos
        validator = QueryValidator()
        df = validator.validate_and_convert_types(df, {
            'preco': 'float',
            'estoque': 'int'
        })

        assert df['preco'].dtype == 'float64'
        assert df['estoque'].dtype == 'int64'

        # 5. Aplicar filtro
        df_filtered = safe_filter(
            df,
            filter_func=lambda df: df[df['preco'] > 0]
        )

        assert len(df_filtered) > 0


def run_all_tests():
    """Executa todos os testes."""
    print("\n" + "="*60)
    print("EXECUTANDO TESTES DE VALIDADORES E HANDLERS")
    print("="*60 + "\n")

    # Executar pytest programaticamente
    pytest.main([__file__, '-v', '--tb=short'])


if __name__ == "__main__":
    run_all_tests()
