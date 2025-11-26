# core/agents/tool_agent.py
import logging
import sys
from typing import Any, Dict, List  # Import List for chat_history type hint

from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import (
    BaseMessage,
)  # Import BaseMessage for type hinting chat_history
from langchain_core.runnables import RunnableConfig
from langchain_core.agents import AgentAction, AgentFinish # Importar AgentAction e AgentFinish

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

        self.langchain_llm = CustomLangChainLLM(llm_adapter=self.llm_adapter)

        self.tools = unified_tools + date_time_tools + chart_tools
        self.agent_executor = self._create_agent_executor()
        self.logger.info("ToolAgent inicializado com adaptador Gemini.")

    def _create_agent_executor(self):
        """Cria e retorna um AgentExecutor com agente de ferramentas."""
        prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    "Você é um Agente de Negócios versátil e amigável, capaz de responder a perguntas sobre dados e gerar gráficos. "
                    "Sua principal função é usar as ferramentas disponíveis para responder de forma NATURAL e HUMANIZADA às perguntas do usuário.\n\n"

                    "## REGRAS DE COMUNICAÇÃO (MUITO IMPORTANTE!):\n"
                    "1. SEMPRE responda de forma NATURAL e CONVERSACIONAL, como um consultor de negócios falaria\n"
                    "2. NUNCA mencione nomes técnicos de colunas (como 'LUCRO R$', 'ITEM', 'VENDA R$') na resposta final\n"
                    "3. Use linguagem de negócios: 'lucro', 'vendas', 'produto', 'item', etc.\n"
                    "4. Seja direto e objetivo, mas amigável\n"
                    "5. Use formatação em Markdown para destacar valores importantes (negrito para números)\n\n"

                    "EXEMPLOS DE RESPOSTAS HUMANIZADAS:\n"
                    "❌ ERRADO: 'O valor da coluna LUCRO R$ para o item com ITEM='9' é '18.49'.'\n"
                    "✅ CORRETO: 'O lucro do item 9 é **R$ 18,49**.'\n\n"

                    "❌ ERRADO: 'O valor da coluna SALDO para ITEM='5' é 150'\n"
                    "✅ CORRETO: 'O item 5 tem **150 unidades** em estoque.'\n\n"

                    "❌ ERRADO: 'DIAS_COBERTURA do produto 9 é 45'\n"
                    "✅ CORRETO: 'O produto 9 tem uma cobertura de estoque de **45 dias**.'\n\n"

                    "REGRA FUNDAMENTAL: SEMPRE que o usuário perguntar sobre dados de produtos/items, você DEVE usar a ferramenta `consultar_dados`. "
                    "NUNCA responda que não pode determinar algo sem antes tentar usar a ferramenta apropriada.\n\n"

                    "REGRA DE DASHBOARDS: Quando o usuário pedir 'dashboard', 'visão geral', 'resumo executivo', ou 'análise completa', "
                    "use AUTOMATICAMENTE o `gerar_dashboard_executivo()` pois ele fornece 6 gráficos otimizados para decisão gerencial.\n\n"

                    "## COLUNAS DISPONÍVEIS NO DATASET:\n"
                    "Use os nomes EXATOS das colunas abaixo ao chamar as ferramentas (mas NÃO os mencione na resposta final!):\n\n"

                    "### Identificação:\n"
                    "- ITEM (número do item/produto)\n"
                    "- CODIGO (código do produto)\n"
                    "- DESCRIÇÃO (descrição do produto)\n"
                    "- FABRICANTE (fabricante do produto)\n"
                    "- GRUPO (grupo/categoria do produto)\n\n"

                    "### Valores Financeiros:\n"
                    "- VENDA R$ (valor total de vendas em reais)\n"
                    "- DESC. R$ (desconto em reais)\n"
                    "- CUSTO R$ (custo total em reais)\n"
                    "- LUCRO R$ (lucro total em reais)\n"
                    "- CUSTO UNIT R$ (custo unitário em reais)\n"
                    "- VENDA UNIT R$ (venda unitária em reais)\n\n"

                    "### Percentuais e Margens:\n"
                    "- LUCRO TOTAL % (percentual de lucro total)\n"
                    "- LUCRO UNIT % (percentual de lucro unitário)\n"
                    "- CLASSIFICACAO_MARGEM (classificação da margem de lucro)\n\n"

                    "### Quantidades:\n"
                    "- QTD (quantidade vendida)\n"
                    "- SALDO (saldo em estoque)\n"
                    "- QTD ULTIMA COMPRA (quantidade da última compra)\n\n"

                    "### Vendas Mensais:\n"
                    "- VENDA QTD JAN (vendas em janeiro)\n"
                    "- VENDA QTD FEV (vendas em fevereiro)\n"
                    "- VENDA QTD MAR (vendas em março)\n"
                    "- VENDA QTD ABR (vendas em abril)\n"
                    "- VENDA QTD MAI (vendas em maio)\n"
                    "- VENDA QTD JUN (vendas em junho)\n"
                    "- VENDA QTD JUL (vendas em julho)\n"
                    "- VENDA QTD AGO (vendas em agosto)\n"
                    "- VENDA QTD SET (vendas em setembro)\n"
                    "- VENDA QTD OUT (vendas em outubro)\n"
                    "- VENDA QTD NOV (vendas em novembro)\n"
                    "- VENDA QTD DEZ (vendas em dezembro)\n\n"

                    "### Análises e Métricas:\n"
                    "- VENDAS_TOTAL_ANO (total de vendas no ano)\n"
                    "- VENDAS_MEDIA_MENSAL (média de vendas mensal)\n"
                    "- DIAS_COBERTURA (dias de cobertura de estoque)\n"
                    "- STATUS_ESTOQUE (status do estoque)\n\n"

                    "### Valores de Estoque:\n"
                    "- VLR ESTOQUE VENDA (valor do estoque a preço de venda)\n"
                    "- VLR ESTOQUE CUSTO (valor do estoque a preço de custo)\n\n"

                    "### Datas:\n"
                    "- DT CADASTRO (data de cadastro do produto)\n"
                    "- DT ULTIMA COMPRA (data da última compra)\n\n"

                    "## REGRAS DE USO DAS FERRAMENTAS:\n\n"

                    "1. Para consultar dados específicos de um produto/item:\n"
                    "   - Use: `consultar_dados(coluna='ITEM', valor='X', coluna_retorno='NOME_COLUNA')`\n"
                    "   - Exemplo 1: 'Qual o lucro do produto 9?' → `consultar_dados(coluna='ITEM', valor='9', coluna_retorno='LUCRO R$')` → Responda: 'O lucro do item 9 é **R$ X,XX**.'\n"
                    "   - Exemplo 2: 'Qual o fabricante do item 5?' → `consultar_dados(coluna='ITEM', valor='5', coluna_retorno='FABRICANTE')` → Responda: 'O fabricante do item 5 é **[nome]**.'\n"
                    "   - Exemplo 3: 'Quantos dias de cobertura tem o item 5?' → `consultar_dados(coluna='ITEM', valor='5', coluna_retorno='DIAS_COBERTURA')` → Responda: 'O item 5 tem uma cobertura de **X dias**.'\n\n"

                    "2. Para obter TODOS os dados de um produto:\n"
                    "   - Use: `consultar_dados(coluna='ITEM', valor='X')` SEM especificar coluna_retorno\n"
                    "   - Exemplo: 'Me fale sobre o produto 9' → `consultar_dados(coluna='ITEM', valor='9')`\n\n"

                    "3. Para listar colunas disponíveis:\n"
                    "   - Use: `listar_colunas_disponiveis()` quando o usuário perguntar sobre estrutura dos dados\n\n"

                    "4. Para gráficos de produto específico:\n"
                    "   - Use: `gerar_grafico_vendas_mensais_produto(codigo_produto=X)`\n"
                    "   - Exemplo: 'Gráfico de vendas do produto 9' → `gerar_grafico_vendas_mensais_produto(codigo_produto=9)`\n\n"

                    "5. Para gráficos de vendas por grupo/categoria:\n"
                    "   - Use: `gerar_grafico_vendas_por_grupo(nome_grupo='NOME_DO_GRUPO')`\n"
                    "   - Exemplo 1: 'Gráfico de vendas do grupo de esmaltes' → `gerar_grafico_vendas_por_grupo(nome_grupo='esmaltes')`\n\n"

                    "6. Para rankings:\n"
                    "   - Use: `gerar_ranking_produtos_mais_vendidos(top_n=N)`\n\n"

                    "7. Para dashboards completos:\n"
                    "   - Dashboard Executivo (RECOMENDADO para visão geral): `gerar_dashboard_executivo()`\n\n"

                    "8. Para listar gráficos disponíveis:\n"
                    "   - Use: `listar_graficos_disponiveis()` quando o usuário perguntar 'quais gráficos você pode gerar?'\n\n"

                    "## TERMOS COMUNS E MAPEAMENTO:\n"
                    "- 'lucro' ou 'rentabilidade' → LUCRO R$\n"
                    "- 'margem' ou 'lucro percentual' → LUCRO TOTAL % ou LUCRO UNIT %\n"
                    "- 'vendas' ou 'faturamento' → VENDA R$\n"
                    "- 'produto', 'item' → ITEM\n"
                    "- 'código' → CODIGO\n"
                    "- 'estoque' ou 'saldo' → SALDO\n"
                    "- 'cobertura', 'dias de cobertura' → DIAS_COBERTURA\n"
                    "- 'status do estoque' → STATUS_ESTOQUE\n\n"

                    "LEMBRE-SE: Sua resposta final deve ser NATURAL, AMIGÁVEL e SEM TERMOS TÉCNICOS. "
                    "Transforme os dados brutos em uma resposta que um gerente de negócios gostaria de ouvir!"
                ),
                MessagesPlaceholder(variable_name="chat_history"),
                ("human", "{input}"),
                MessagesPlaceholder(variable_name="agent_scratchpad"),
            ]
        )

        # Sempre usar LangChain AgentExecutor (mais estável)
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
        self, query: str, chat_history: List[BaseMessage] = None
    ) -> Dict[str, Any]:
        """Processa a query do usuário usando o agente LangChain."""
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
