import logging

from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.utils.function_calling import convert_to_openai_tool

from ..factory.component_factory import ComponentFactory
from ..tools.sql_server_tools import db_schema_info, sql_server_tools

# Configuração de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class GraphAgent:
    """
    Agente principal do grafo, responsável por orquestrar o LLM e as ferramentas.
    """

    def __init__(self, llm=None, tools=None):
        """
        Inicializa o agente.

        Args:
            llm (LLMAdapter, optional): O adaptador LLM a ser usado (Gemini/DeepSeek).
            tools (list, optional): A lista de ferramentas disponíveis.
        """
        self.llm = llm or ComponentFactory.get_llm_adapter("gemini")
        self.tools = tools or sql_server_tools
        self.agent_runnable = self._create_agent_runnable()

    def _get_system_prompt_template(self):
        """Retorna o template do prompt do sistema."""
        schema = db_schema_info or "Schema não disponível. Use get_database_schema."
        tool_names = ", ".join([t.name for t in self.tools])

        return (
            "Você é Caçulinha, um assistente de BI especialista em SQL Server.\n"
            "Seu papel é responder perguntas executando consultas SELECT seguras.\n"
            f"Schema do Banco: {schema}\n"
            f"Ferramentas: {tool_names}\n"
            "**Regras:**\n"
            "1. Responda em português.\n"
            "2. Se não souber o schema, use `get_database_schema` PRIMEIRO.\n"
            "3. Depois, use `execute_sql_query` com um SELECT válido.\n"
            "4. NUNCA use DELETE, UPDATE, INSERT. Apenas permissão de leitura.\n"
            "5. Se a consulta falhar, informe o usuário e peça para reformular.\n"
        )

    def _create_agent_runnable(self):
        """Cria o 'Agent Runnable' com as ferramentas vinculadas."""
        system_prompt = self._get_system_prompt_template()
        prompt = ChatPromptTemplate.from_messages(
            [
                ("system", system_prompt),
                MessagesPlaceholder(variable_name="messages"),
            ]
        )
        # Nota: Este método precisa ser adaptado para usar os adaptadores LLM customizados
        # Em vez de bind_tools, usaremos uma abordagem mais simples com get_completion
        self.prompt = prompt
        return self._process_with_custom_llm

    def _process_with_custom_llm(self, data):
        """Processa usando o adaptador LLM customizado."""
        messages = data.get("messages", [])
        # Converte mensagens para formato simples
        formatted_messages = []
        for msg in messages:
            if hasattr(msg, 'content'):
                formatted_messages.append({"role": "user", "content": msg.content})

        # Adiciona prompt do sistema
        system_prompt = self._get_system_prompt_template()
        all_messages = [{"role": "system", "content": system_prompt}] + formatted_messages

        # Chama o LLM
        response = self.llm.get_completion(all_messages)
        return response

    def process(self, messages):
        """
        Processa uma lista de mensagens através do agente.

        Args:
            messages (list): A lista de mensagens da conversa.

        Returns:
            A resposta do agente.
        """
        logger.info("Processando mensagem com o GraphAgent...")
        return self.agent_runnable({"messages": messages})


if __name__ == "__main__":
    # Exemplo de como usar o agente
    print("Inicializando o GraphAgent para teste...")
    agent = GraphAgent()
    print("Agente inicializado.")
    # Para testar, você precisaria de uma lista de mensagens, por exemplo:
    # from langchain_core.messages import HumanMessage
    # messages = [HumanMessage(content="Qual o produto mais vendido?")]
    # response = agent.process(messages)
    # print("Resposta do agente:", response)
    print("Script concluído.")
