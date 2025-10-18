"""
Testes unitários para validar integração DynamicPrompt no CodeGenAgent
TAREFA 5 - PLANO_PILAR_4_EXECUCAO.md
"""

import unittest
import sys
import os
from unittest.mock import Mock, patch, MagicMock

# Adicionar diretório raiz ao path
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE_DIR)


class TestCodeGenAgentIntegration(unittest.TestCase):
    """Testes de integração do DynamicPrompt no CodeGenAgent"""

    def setUp(self):
        """Configuração antes de cada teste"""
        self.mock_llm_client = Mock()
        self.mock_llm_client.generate = Mock(return_value={
            "content": "SELECT * FROM vendas",
            "model": "test-model"
        })

    @patch('core.agents.code_gen_agent.DynamicPrompt')
    @patch('core.agents.code_gen_agent.LLMClient')
    def test_dynamic_prompt_initialization(self, mock_llm, mock_dynamic_prompt):
        """Testa que DynamicPrompt é inicializado corretamente"""
        from core.agents.code_gen_agent import CodeGenAgent

        mock_llm.return_value = self.mock_llm_client
        mock_dynamic_prompt.return_value = Mock()

        agent = CodeGenAgent()

        # Verificar que DynamicPrompt foi instanciado
        mock_dynamic_prompt.assert_called_once()

        # Verificar que agent tem atributo dynamic_prompt
        self.assertTrue(hasattr(agent, 'dynamic_prompt'))

    @patch('core.agents.code_gen_agent.DynamicPrompt')
    @patch('core.agents.code_gen_agent.LLMClient')
    def test_enhanced_prompt_is_used(self, mock_llm, mock_dynamic_prompt):
        """Testa que enhanced_prompt é usado na geração de código"""
        from core.agents.code_gen_agent import CodeGenAgent

        # Configurar mocks
        mock_llm.return_value = self.mock_llm_client

        mock_dp_instance = Mock()
        mock_dp_instance.get_enhanced_prompt = Mock(return_value="ENHANCED_PROMPT")
        mock_dynamic_prompt.return_value = mock_dp_instance

        # Criar agent e gerar código
        agent = CodeGenAgent()
        result = agent.generate_and_execute_code(
            user_query="Mostre vendas",
            context={"schema": {"vendas": ["id", "valor"]}}
        )

        # Verificar que get_enhanced_prompt foi chamado
        mock_dp_instance.get_enhanced_prompt.assert_called_once()

        # Verificar argumentos da chamada
        call_args = mock_dp_instance.get_enhanced_prompt.call_args
        self.assertEqual(call_args[1]['user_query'], "Mostre vendas")
        self.assertIn('schema', call_args[1]['context'])

        # Verificar que LLM foi chamado com prompt aprimorado
        self.mock_llm_client.generate.assert_called_once()
        llm_call_args = self.mock_llm_client.generate.call_args
        self.assertEqual(llm_call_args[1]['prompt'], "ENHANCED_PROMPT")

    @patch('core.agents.code_gen_agent.DynamicPrompt')
    @patch('core.agents.code_gen_agent.LLMClient')
    def test_context_is_passed_correctly(self, mock_llm, mock_dynamic_prompt):
        """Testa que contexto é passado corretamente para DynamicPrompt"""
        from core.agents.code_gen_agent import CodeGenAgent

        mock_llm.return_value = self.mock_llm_client

        mock_dp_instance = Mock()
        mock_dp_instance.get_enhanced_prompt = Mock(return_value="PROMPT")
        mock_dynamic_prompt.return_value = mock_dp_instance

        agent = CodeGenAgent()

        # Teste com contexto
        context = {
            "schema": {"vendas": ["produto", "valor"]},
            "examples": [{"query": "...", "code": "..."}],
            "user_preferences": {"format": "compact"}
        }

        agent.generate_and_execute_code(
            user_query="Query teste",
            context=context
        )

        # Verificar que contexto foi passado corretamente
        call_args = mock_dp_instance.get_enhanced_prompt.call_args
        self.assertEqual(call_args[1]['context'], context)

    @patch('core.agents.code_gen_agent.DynamicPrompt')
    @patch('core.agents.code_gen_agent.LLMClient')
    def test_context_default_empty_dict(self, mock_llm, mock_dynamic_prompt):
        """Testa que contexto vazio é passado quando None"""
        from core.agents.code_gen_agent import CodeGenAgent

        mock_llm.return_value = self.mock_llm_client

        mock_dp_instance = Mock()
        mock_dp_instance.get_enhanced_prompt = Mock(return_value="PROMPT")
        mock_dynamic_prompt.return_value = mock_dp_instance

        agent = CodeGenAgent()

        # Chamar sem contexto
        agent.generate_and_execute_code(user_query="Query teste")

        # Verificar que contexto vazio foi passado
        call_args = mock_dp_instance.get_enhanced_prompt.call_args
        self.assertEqual(call_args[1]['context'], {})

    @patch('core.agents.code_gen_agent.DynamicPrompt')
    @patch('core.agents.code_gen_agent.LLMClient')
    def test_result_includes_prompt_preview(self, mock_llm, mock_dynamic_prompt):
        """Testa que resultado inclui preview do prompt usado"""
        from core.agents.code_gen_agent import CodeGenAgent

        mock_llm.return_value = self.mock_llm_client

        long_prompt = "A" * 500  # Prompt longo
        mock_dp_instance = Mock()
        mock_dp_instance.get_enhanced_prompt = Mock(return_value=long_prompt)
        mock_dynamic_prompt.return_value = mock_dp_instance

        agent = CodeGenAgent()
        result = agent.generate_and_execute_code(user_query="Query teste")

        # Verificar que resultado tem preview do prompt
        self.assertIn('prompt_used', result)
        self.assertTrue(result['prompt_used'].endswith('...'))
        self.assertLessEqual(len(result['prompt_used']), 203)  # 200 + "..."

    @patch('core.agents.code_gen_agent.DynamicPrompt')
    @patch('core.agents.code_gen_agent.LLMClient')
    def test_logging_on_initialization(self, mock_llm, mock_dynamic_prompt):
        """Testa que log é gerado na inicialização"""
        from core.agents.code_gen_agent import CodeGenAgent

        mock_llm.return_value = self.mock_llm_client
        mock_dynamic_prompt.return_value = Mock()

        with patch('core.agents.code_gen_agent.logger') as mock_logger:
            agent = CodeGenAgent()

            # Verificar que log de inicialização foi chamado
            mock_logger.info.assert_called()
            calls = [str(call) for call in mock_logger.info.call_args_list]
            self.assertTrue(any('DynamicPrompt' in str(call) for call in calls))

    @patch('core.agents.code_gen_agent.DynamicPrompt')
    @patch('core.agents.code_gen_agent.LLMClient')
    def test_logging_on_prompt_generation(self, mock_llm, mock_dynamic_prompt):
        """Testa que log é gerado ao gerar prompt"""
        from core.agents.code_gen_agent import CodeGenAgent

        mock_llm.return_value = self.mock_llm_client

        mock_dp_instance = Mock()
        mock_dp_instance.get_enhanced_prompt = Mock(return_value="PROMPT_TEST")
        mock_dynamic_prompt.return_value = mock_dp_instance

        agent = CodeGenAgent()

        with patch('core.agents.code_gen_agent.logger') as mock_logger:
            agent.generate_and_execute_code(user_query="Query teste")

            # Verificar que log debug foi chamado
            mock_logger.debug.assert_called()

    @patch('core.agents.code_gen_agent.DynamicPrompt')
    @patch('core.agents.code_gen_agent.LLMClient')
    def test_statistics_includes_dynamic_prompt_flag(self, mock_llm, mock_dynamic_prompt):
        """Testa que estatísticas incluem flag do DynamicPrompt"""
        from core.agents.code_gen_agent import CodeGenAgent

        mock_llm.return_value = self.mock_llm_client
        mock_dynamic_prompt.return_value = Mock()

        agent = CodeGenAgent()
        stats = agent.get_statistics()

        # Verificar que estatísticas incluem flag
        self.assertIn('dynamic_prompt_enabled', stats)
        self.assertTrue(stats['dynamic_prompt_enabled'])

    @patch('core.agents.code_gen_agent.DynamicPrompt')
    @patch('core.agents.code_gen_agent.LLMClient')
    def test_error_handling_preserves_functionality(self, mock_llm, mock_dynamic_prompt):
        """Testa que erros no DynamicPrompt são tratados corretamente"""
        from core.agents.code_gen_agent import CodeGenAgent

        mock_llm.return_value = self.mock_llm_client

        # Simular erro no get_enhanced_prompt
        mock_dp_instance = Mock()
        mock_dp_instance.get_enhanced_prompt = Mock(side_effect=Exception("Erro no prompt"))
        mock_dynamic_prompt.return_value = mock_dp_instance

        agent = CodeGenAgent()

        # Chamar método e verificar que erro é capturado
        result = agent.generate_and_execute_code(user_query="Query teste")

        # Verificar que resultado indica erro
        self.assertFalse(result['success'])
        self.assertIn('error', result)


class TestCodeGenAgentBackwardCompatibility(unittest.TestCase):
    """Testes de compatibilidade com código existente"""

    @patch('core.agents.code_gen_agent.DynamicPrompt')
    @patch('core.agents.code_gen_agent.LLMClient')
    def test_agent_can_be_initialized_without_llm_client(self, mock_llm, mock_dynamic_prompt):
        """Testa que agent pode ser inicializado sem LLMClient"""
        from core.agents.code_gen_agent import CodeGenAgent

        mock_llm.return_value = Mock()
        mock_dynamic_prompt.return_value = Mock()

        # Deve funcionar sem passar llm_client
        agent = CodeGenAgent()

        self.assertIsNotNone(agent)
        self.assertTrue(hasattr(agent, 'llm_client'))
        self.assertTrue(hasattr(agent, 'dynamic_prompt'))

    @patch('core.agents.code_gen_agent.DynamicPrompt')
    @patch('core.agents.code_gen_agent.LLMClient')
    def test_agent_accepts_custom_llm_client(self, mock_llm, mock_dynamic_prompt):
        """Testa que agent aceita LLMClient customizado"""
        from core.agents.code_gen_agent import CodeGenAgent

        custom_llm = Mock()
        mock_dynamic_prompt.return_value = Mock()

        agent = CodeGenAgent(llm_client=custom_llm)

        # Verificar que LLM customizado foi usado
        self.assertEqual(agent.llm_client, custom_llm)


def run_tests():
    """Executa todos os testes"""
    # Criar test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    # Adicionar testes
    suite.addTests(loader.loadTestsFromTestCase(TestCodeGenAgentIntegration))
    suite.addTests(loader.loadTestsFromTestCase(TestCodeGenAgentBackwardCompatibility))

    # Executar testes
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    return result.wasSuccessful()


if __name__ == '__main__':
    print("=" * 80)
    print("TESTES DE INTEGRAÇÃO - DynamicPrompt no CodeGenAgent")
    print("=" * 80)
    print()

    success = run_tests()

    print()
    print("=" * 80)
    if success:
        print("✓ TODOS OS TESTES PASSARAM!")
    else:
        print("✗ ALGUNS TESTES FALHARAM")
    print("=" * 80)

    sys.exit(0 if success else 1)
