# core/agents/tool_agent.py
import logging
import sys
import os
from typing import Any, Dict, List, Optional

# Suppress transformers warnings about torch
os.environ['TRANSFORMERS_OFFLINE'] = '1'
os.environ['HF_HUB_OFFLINE'] = '1'

LANGCHAIN_AVAILABLE = False
try:
    try:
        from langchain.agents import AgentExecutor, create_tool_calling_agent
    except ImportError:
        # Fallback for environments using langchain-classic
        from langchain_classic.agents import AgentExecutor, create_tool_calling_agent

    from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
    from langchain_core.messages import BaseMessage
    from langchain_core.runnables import RunnableConfig
    from langchain_core.agents import AgentAction, AgentFinish
    
    # Check for torch dependency explicitly to fail fast inside try block
    import transformers
    
    LANGCHAIN_AVAILABLE = True
except (ImportError, OSError) as e:
    logging.warning(f"LangChain/Transformers dependencies not available: {e}. ToolAgent will run in fallback mode.")
    # Define dummy classes for type hinting if needed, or just use Any
    BaseMessage = Any

from app.core.llm_base import BaseLLMAdapter
from app.core.llm_gemini_adapter import GeminiLLMAdapter
from app.core.llm_langchain_adapter import CustomLangChainLLM
from app.core.utils.response_parser import parse_agent_response
from app.core.utils.chart_saver import save_chart

from app.core.tools.unified_data_tools import unified_tools
from app.core.tools.date_time_tools import date_time_tools
from app.core.tools.chart_tools import chart_tools


class ToolAgent:
    def __init__(self, llm_adapter: BaseLLMAdapter):
        self.logger = logging.getLogger(__name__)
        self.llm_adapter = llm_adapter
        self.agent_executor = None

        if LANGCHAIN_AVAILABLE:
            try:
                self.langchain_llm = CustomLangChainLLM(llm_adapter=self.llm_adapter)
                self.tools = unified_tools + date_time_tools + chart_tools
                self.agent_executor = self._create_agent_executor()
                self.logger.info("ToolAgent inicializado com adaptador Gemini (LangChain ativo).")
            except Exception as e:
                self.logger.error(f"Erro ao inicializar LangChain Agent: {e}")
                self.agent_executor = None
        else:
            self.logger.warning("ToolAgent rodando em modo degradado (sem LangChain).")

    def _create_agent_executor(self):
        """Cria e retorna um AgentExecutor com agente de ferramentas."""
        if not LANGCHAIN_AVAILABLE:
            return None
            
        # ✅ FASE 3: PROMPT MINIMALISTA (30 linhas vs 168 linhas)
        prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    "Você é um assistente BI especializado. Use as ferramentas disponíveis para responder queries sobre dados.\n\n"
                    "REGRAS:\n"
                    "1. Responda de forma natural e direta\n"
                    "2. Use formatação Markdown para valores (**R$ X,XX**, **X unidades**)\n"
                    "3. NUNCA mencione nomes técnicos de colunas\n"
                    "4. SEMPRE use ferramentas para consultar dados\n\n"
                    "FERRAMENTAS PRINCIPAIS:\n"
                    "- consultar_dados(coluna, valor, coluna_retorno) - Consulta dados específicos\n"
                    "- listar_colunas_disponiveis() - Lista colunas disponíveis\n"
                    "- gerar_grafico_* - Gera gráficos\n\n"
                    "EXEMPLOS:\n"
                    "Query: 'preço do produto 123'\n"
                    "Ferramenta: consultar_dados('PRODUTO', '123', 'LIQUIDO_38')\n"
                    "Resposta: 'O preço do produto 123 é **R$ 45,90**'\n\n"
                    "COLUNAS COMUNS: PRODUTO, NOME, LIQUIDO_38 (preço), ESTOQUE_UNE (estoque), NOMEFABRICANTE\n"
                    "Use listar_colunas_disponiveis() para ver todas.\n\n"
                    "Seja direto e profissional."
                ),
                MessagesPlaceholder(variable_name="chat_history"),
                ("human", "{input}"),
                MessagesPlaceholder(variable_name="agent_scratchpad"),
            ]
        )

        agent = create_tool_calling_agent(
            llm=self.langchain_llm, tools=self.tools, prompt=prompt
        )

        return AgentExecutor(
            agent=agent,
            tools=self.tools,
            verbose=True,
            return_intermediate_steps=True,
        )

    def process_query(
        self, query: str, chat_history: List[Any] = None
    ) -> Dict[str, Any]:
        """Processa a query do usuário usando o agente LangChain."""
        
        if not self.agent_executor:
            return {
                "type": "text",
                "output": "⚠️ O sistema de Agentes Inteligentes está temporariamente indisponível (dependência ausente). Por favor, use o painel de Monitoramento ou contate o administrador."
            }

        self.logger.info(f"Processando query com o Agente de Ferramentas: {query}")
        try:
            # Ensure chat_history is not None for invoke
            if chat_history is None:
                chat_history = []

            config = RunnableConfig(recursion_limit=10)

            self.logger.debug(
                f"Invocando agente com query: {query} "
                f"e chat_history: {chat_history}"
            )
            response = self.agent_executor.invoke(
                {"input": query, "chat_history": chat_history}, config=config
            )
            self.logger.debug(f"Resposta bruta do agente: {response}")

            # Adicionando log detalhado para depuração
            self.logger.info(f"CONTEÚDO COMPLETO DA RESPOSTA DO AGENTE: {response}")

            final_output = response.get("output", "Não foi possível gerar uma resposta.")
            response_type = "text" # Padrão

            # Verificar se há passos intermediários e extrair a saída da ferramenta se aplicável
            if "intermediate_steps" in response and response["intermediate_steps"]:
                for step in reversed(response["intermediate_steps"]):
                    if isinstance(step, tuple) and len(step) == 2:
                        action, observation = step
                        
                        # Se a observação for um dicionário de uma ferramenta de gráfico bem-sucedida
                        if isinstance(observation, dict) and observation.get("status") == "success" and "chart_data" in observation:
                            self.logger.info(f"Extraindo dados do gráfico da ferramenta: {action.tool}")
                            final_output = observation["chart_data"]
                            response_type = "chart"
                            save_chart(final_output)  # Salvar o gráfico
                            break
                        
                        # Lógica existente para ferramentas que retornam string
                        elif isinstance(action, AgentAction) and isinstance(observation, str):
                            if action.tool == "consultar_dados":
                                final_output = observation
                                self.logger.info(f"Usando saída direta da ferramenta consultar_dados: {final_output}")
                                break

            # Se o tipo de resposta for gráfico, retorna diretamente
            if response_type == "chart":
                return {
                    "type": "chart",
                    "output": final_output,
                }

            # Processamento legado para texto
            response_type, processed = parse_agent_response(final_output)
            return {
                "type": "text", # Changed from response_type to "text" to ensure text output for general queries
                "output": processed.get("output", final_output),
            }

        except Exception as e:
            self.logger.error(f"Erro ao invocar o agente LangChain: {e}", exc_info=True)
            
            # Debug: Write error to file
            try:
                import traceback
                with open("error_log_agent.txt", "w", encoding="utf-8") as f:
                    f.write(f"Error: {str(e)}\n")
                    f.write(traceback.format_exc())
            except:
                pass
                
            return {
                "type": "error",
                "output": (
                    "Desculpe, não consegui processar sua solicitação "
                    "no momento. Por favor, tente novamente ou reformule "
                    "sua pergunta."
                ),
            }


def initialize_agent_for_session():
    """Função de fábrica para inicializar o agente."""
    return ToolAgent(llm_adapter=GeminiLLMAdapter())
