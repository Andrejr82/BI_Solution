# core/query_processor.py
import logging
from app.core.agents.supervisor_agent import SupervisorAgent
from app.core.factory.component_factory import ComponentFactory
from app.core.llm_factory import LLMFactory
from app.core.cache import Cache


class QueryProcessor:
    """
    Ponto de entrada principal para o processamento de consultas.
    Delega a tarefa para o SupervisorAgent para orquestração.
    """

    def __init__(self):
        """
        Inicializa o processador de consultas e o agente supervisor.
        """
        self.logger = logging.getLogger(__name__)
        # Usar factory para obter adapter com fallback automático
        try:
            self.llm_adapter = LLMFactory.get_adapter()
            self.supervisor = SupervisorAgent(gemini_adapter=self.llm_adapter)
            self.cache = Cache()
            self.logger.info(
                "QueryProcessor inicializado e pronto para delegar ao SupervisorAgent."
            )
        except ValueError as e:
            self.logger.error(f"Erro ao inicializar QueryProcessor: {e}")
            self.llm_adapter = None
            self.supervisor = None
            self.cache = Cache()
            raise RuntimeError(
                "GEMINI_API_KEY não configurada. Configure a chave da API do Google Gemini nos secrets do Streamlit Cloud."
            ) from e

    def process_query(self, query: str) -> dict:
        """
        Processa a consulta do usuário, delegando-a diretamente ao SupervisorAgent.

        Args:
            query (str): A consulta do usuário.

        Returns:
            dict: O resultado do processamento pelo agente especialista apropriado.
        """
        # Verificar se o supervisor foi inicializado
        if self.supervisor is None:
            return {
                "type": "text",
                "output": "⚠️ **GEMINI_API_KEY não configurada!**\n\nPara usar o agente, você precisa:\n\n1. Acessar **Settings** no Streamlit Cloud\n2. Adicionar nos **Secrets**:\n```\nGEMINI_API_KEY = \"sua_chave_aqui\"\n```\n\n3. Obter a chave em: https://aistudio.google.com/app/apikey\n\n4. Salvar e aguardar o app reiniciar"
            }

        # Interceptar perguntas sobre o nome do agente
        if query.lower() in ["qual seu nome", "quem é você", "qual o seu nome"]:
            return {
                "type": "text",
                "output": "Eu sou um Agente de Negócios, pronto para ajudar com suas análises de dados."
            }

        cached_result = self.cache.get(query)
        if cached_result:
            self.logger.info(
                f'Resultado recuperado do cache para a consulta: "{query}"'
            )
            return cached_result

        self.logger.info(f'Delegando a consulta para o Supervisor: "{query}"')
        result = self.supervisor.route_query(query)
        self.cache.set(query, result)
        return result
