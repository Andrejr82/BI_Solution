# core/agents/tool_agent.py
import logging
import os
from typing import Any, Dict, List # Import List for chat_history type hint

<<<<<<< HEAD
from langchain.agents import AgentExecutor, create_openai_tools_agent  # OpenAI-compatible tools format
=======
from langchain.agents import AgentExecutor, create_openai_tools_agent
>>>>>>> 946e2ce9d874562f3c9e0f0d54e9c41c50cb3399
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import BaseMessage # Import BaseMessage for type hinting chat_history
from langchain_core.runnables import RunnableConfig

from core.llm_base import BaseLLMAdapter
<<<<<<< HEAD
from core.factory.component_factory import ComponentFactory
# from core.llm_langchain_adapter import CustomLangChainLLM  # Arquivo não existe
=======
from core.llm_adapter import OpenAILLMAdapter
from core.llm_langchain_adapter import CustomLangChainLLM
>>>>>>> 946e2ce9d874562f3c9e0f0d54e9c41c50cb3399

from core.tools.mcp_sql_server_tools import sql_tools


class ToolAgent:
    def __init__(self, llm_adapter: BaseLLMAdapter):
        self.logger = logging.getLogger(__name__)
        self.llm_adapter = llm_adapter
        
        self.langchain_llm = CustomLangChainLLM(llm_adapter=self.llm_adapter)
        
        self.agent_executor = self._create_agent_executor()
<<<<<<< HEAD
        self.logger.info("ToolAgent inicializado com LangChain Tools Agent.")

    def _create_agent_executor(self) -> AgentExecutor:
        """Cria e retorna um AgentExecutor com agente de ferramentas (formato OpenAI-compatible)."""
=======
        self.logger.info("ToolAgent com OpenAI Tools Agent inicializado.")

    def _create_agent_executor(self) -> AgentExecutor:
        """Cria e retorna um AgentExecutor com o agente de ferramentas OpenAI."""
>>>>>>> 946e2ce9d874562f3c9e0f0d54e9c41c50cb3399
        prompt = ChatPromptTemplate.from_messages(
            [
                ("system", "Você é um assistente de BI útil e eficiente. Use as ferramentas disponíveis para responder às perguntas do usuário de forma direta."),
                MessagesPlaceholder(variable_name="chat_history"), # Add chat history placeholder
                ("human", "{input}"),
                MessagesPlaceholder(variable_name="agent_scratchpad"),
            ]
        )

        agent = create_openai_tools_agent(
            llm=self.langchain_llm, tools=sql_tools, prompt=prompt
        )

        return AgentExecutor(
            agent=agent,
            tools=sql_tools,
            verbose=True,
        )

    def process_query(self, query: str, chat_history: List[BaseMessage] = None) -> Dict[str, Any]:
        """Processa a query do usuário usando o agente LangChain."""
<<<<<<< HEAD
        self.logger.info(f"Processando query com LangChain Tools Agent: {query}")
=======
        self.logger.info(f"Processando query com o Agente OpenAI Tools: {query}")
>>>>>>> 946e2ce9d874562f3c9e0f0d54e9c41c50cb3399
        try:
            # Ensure chat_history is not None for invoke
            if chat_history is None:
                chat_history = []

            config = RunnableConfig(recursion_limit=10)

            self.logger.debug(f"Invocando agente com query: {query} e chat_history: {chat_history}")
            response = self.agent_executor.invoke(
                {"input": query, "chat_history": chat_history}, # Pass chat_history
                config=config
            )
            self.logger.debug(f"Resposta bruta do agente: {response}")
            return {"type": "text", "output": response.get("output", "Não foi possível gerar uma resposta.")}
        except Exception as e:
            self.logger.error(f"Erro ao invocar o agente LangChain: {e}", exc_info=True)
            return {
                "type": "error", "output": "Desculpe, não consegui processar sua solicitação no momento. Por favor, tente novamente ou reformule sua pergunta."
            }


def initialize_agent_for_session():
    """Função de fábrica para inicializar o agente."""
<<<<<<< HEAD
            llm_adapter = ComponentFactory.get_llm_adapter("gemini")
            return ToolAgent(llm_adapter=llm_adapter)
=======
    return ToolAgent(llm_adapter=OpenAILLMAdapter())
>>>>>>> 946e2ce9d874562f3c9e0f0d54e9c41c50cb3399
