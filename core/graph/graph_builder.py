"""Graph Builder - Context7 Agent Orquestrador BI.

Este módulo implementa o construtor de grafo de estados para o agente BI.

Author: devAndreJr
Version: 2.2.1
"""
from __future__ import annotations

# Standard library
from functools import partial
from typing import Any, Protocol, Union, cast

from core.config.logging_config import get_logger

# LangGraph
from langgraph.graph import StateGraph

# Project imports
import core.agents.bi_agent_nodes as bi_nodes
from core.agent_state import AgentState
from core.agents.code_gen_agent import CodeGenAgent
from core.agents.conversational_reasoning_node import ConversationalReasoningEngine
from core.connectivity.hybrid_adapter import HybridDataAdapter
from core.connectivity.parquet_adapter import ParquetAdapter
# safe_parquet_adapter intentionally not imported here to avoid circular deps
from core.llm_base import BaseLLMAdapter

logger = get_logger(__name__)


class DataAdapter(Protocol):
    """Protocol para adaptadores de dados usados pelo GraphBuilder."""

    def query(self, *args: Any, **kwargs: Any) -> Any: ...


# logger already configured via core.config.logging_config.get_logger


class GraphBuilder:
    """Constrói o StateGraph que define o fluxo do agente BI.

    Esta implementação é deliberadamente conservadora: monta nós usando
    as funções existentes em `core.agents.bi_agent_nodes` e retorna um
    StateGraph mínimo pronto para uso nos fluxos do projeto.
    """

    def __init__(
        self,
        llm_adapter: BaseLLMAdapter,
        parquet_adapter: Union[ParquetAdapter, HybridDataAdapter],
        code_gen_agent: CodeGenAgent,
    ) -> None:
        self.llm_adapter = llm_adapter
        self.parquet_adapter = cast(ParquetAdapter, parquet_adapter)
        self.code_gen_agent = code_gen_agent

    def _decide_after_reasoning(self, state: AgentState) -> str:
        """Decide o próximo nó baseado no modo de raciocínio."""
        reasoning_mode = state.get("reasoning_mode", "analytical")
        logger.info("routing.reasoning_mode", mode=reasoning_mode)

        if reasoning_mode == "conversational":
            logger.info(
                "routing.decided",
                reasoning_mode=reasoning_mode,
                route="conversational_response",
            )
            return "conversational_response"
        else:
            # Modo analítico: segue para classificação de intent tradicional
            logger.info(
                "routing.decided",
                reasoning_mode=reasoning_mode,
                route="classify_intent",
            )
            return "classify_intent"

    def _decide_after_intent_classification(self, state: AgentState) -> str:
        intent = state.get("intent")
        logger.info("routing.intent", intent=intent)

        if intent == "une_operation":
            logger.info(
                "routing.decided",
                intent=intent,
                route="execute_une_tool",
            )
            return "execute_une_tool"

        if intent in ("python_analysis", "gerar_grafico"):
            logger.info(
                "routing.decided",
                intent=intent,
                route="generate_plotly_spec",
            )
            return "generate_plotly_spec"

        logger.info(
            "routing.decided",
            intent=intent,
            route="generate_parquet_query",
        )
        return "generate_parquet_query"

    def _decide_after_clarification(self, state: AgentState) -> str:
        needs = state.get("clarification_needed", False)
        if needs:
            logger.info("routing.clarify", reason="requires_user_input")
            return "format_final_response"
        logger.info("routing.continue", reason="no_clarification_needed")
        # Quando não é necessária clarificação, prosseguimos para execução da
        # query parquet criada pelo nó anterior.
        return "execute_query"

    def _decide_after_query_execution(self, state: AgentState) -> str:
        intent = state.get("intent")
        if intent == "gerar_grafico":
            logger.info("routing.visualize", intent=intent)
            return "generate_plotly_spec"
        logger.info("routing.finalize", intent=intent)
        return "format_final_response"

    def build(self) -> object:
        """Cria um StateGraph com os nós básicos usados pelo agente."""
        workflow = StateGraph(AgentState)

        # 🧠 Conversational Reasoning Nodes (v3.0)
        reasoning_engine = ConversationalReasoningEngine(self.llm_adapter)

        def reasoning_node(state: AgentState) -> dict:
            """Nó de raciocínio: analisa intenção e contexto emocional"""
            mode, reasoning_result = reasoning_engine.reason_about_user_intent(state)
            return {
                "reasoning_mode": mode,
                "reasoning_result": reasoning_result
            }

        def conversational_response_node(state: AgentState) -> dict:
            """Nó de resposta conversacional: gera respostas naturais"""
            reasoning_result = state.get("reasoning_result", {})
            response_text = reasoning_engine.generate_conversational_response(
                reasoning_result,
                state
            )
            return {
                "final_response": {
                    "type": "text",
                    "content": response_text,
                    "user_query": state["messages"][-1].content if state.get("messages") else ""
                }
            }

        # Analytical Nodes (existing)
        classify_intent_node = partial(
            bi_nodes.classify_intent,
            llm_adapter=self.llm_adapter,
        )

        generate_parquet_query_node = partial(
            bi_nodes.generate_parquet_query,
            llm_adapter=self.llm_adapter,
            parquet_adapter=self.parquet_adapter,
        )

        execute_query_node = partial(
            bi_nodes.execute_query,
            parquet_adapter=self.parquet_adapter,
        )

        generate_plotly_spec_node = partial(
            bi_nodes.generate_plotly_spec,
            llm_adapter=self.llm_adapter,
            code_gen_agent=self.code_gen_agent,
        )

        format_final_response_node = partial(bi_nodes.format_final_response)

        # Registramos nós como funções parcials.
        # A API do StateGraph consumirá esses callables conforme necessário.

        # 🧠 Conversational Reasoning Nodes (NEW)
        workflow.add_node("reasoning", reasoning_node)
        workflow.add_node("conversational_response", conversational_response_node)

        # Analytical Nodes (existing)
        workflow.add_node("classify_intent", classify_intent_node)
        workflow.add_node(
            "generate_parquet_query",
            generate_parquet_query_node,
        )
        workflow.add_node("execute_query", execute_query_node)
        workflow.add_node("generate_plotly_spec", generate_plotly_spec_node)
        workflow.add_node("format_final_response", format_final_response_node)

        # Transições de exemplo (nomeadas conforme os nossos métodos decide_*)
        # Algumas versões do StateGraph não aceitam kwargs em add_edge;
        # aqui registramos transições básicas sem condicional para manter
        # compatibilidade com implementações variadas de StateGraph.
        workflow.add_edge("classify_intent", "generate_parquet_query")
        workflow.add_edge("generate_parquet_query", "execute_query")
        workflow.add_edge("execute_query", "generate_plotly_spec")
        workflow.add_edge("execute_query", "format_final_response")

        # Nota: Checkpointing pode ser configurado externamente pelo
        # orquestrador que consome este StateGraph.

        # Compat executor: algumas versões do `StateGraph` são apenas
        # definidoras (sem runtime). Para os testes unitários precisamos
        # de um objeto com `invoke(state)` que execute os nós que
        # definimos acima. Implementamos um executor simples e
        # determinístico que chama os nós em sequência usando as
        # funções de decisão já disponíveis neste builder.

        nodes = {
            # 🧠 Conversational Reasoning Nodes (v3.0)
            "reasoning": reasoning_node,
            "conversational_response": conversational_response_node,
            # Analytical Nodes (existing)
            "classify_intent": classify_intent_node,
            "generate_parquet_query": generate_parquet_query_node,
            "execute_query": execute_query_node,
            "generate_plotly_spec": generate_plotly_spec_node,
            "format_final_response": format_final_response_node,
            "execute_une_tool": partial(bi_nodes.execute_une_tool, llm_adapter=self.llm_adapter),
        }

        class _SimpleExecutor:
            def __init__(self, nodes_map: dict, builder: "GraphBuilder"):
                self._nodes = nodes_map
                self._builder = builder

            def invoke(self, initial_state: dict, config: dict = None) -> dict:
                # Make a shallow copy to avoid mutating caller's dict
                state = dict(initial_state)
                # Ensure messages exist
                state.setdefault("messages", [])

                # 🧠 Start at reasoning node (v3.0 - Conversational AI)
                current = "reasoning"
                max_steps = 20
                steps = 0

                while steps < max_steps:
                    steps += 1
                    node_fn = self._nodes.get(current)
                    if node_fn is None:
                        break

                    try:
                        result = node_fn(state)
                        if isinstance(result, dict):
                            state.update(result)
                    except Exception as e:
                        # Bubble up errors as part of final_response for tests
                        logger.error(f"Error in node {current}: {e}", exc_info=True)
                        return {"final_response": {"type": "error", "content": str(e)}}

                    # Decide next step based on state
                    if current == "reasoning":
                        # 🧠 NEW: Route based on reasoning_mode
                        current = self._builder._decide_after_reasoning(state)
                        continue

                    if current == "conversational_response":
                        # Terminal node for conversational mode
                        if state.get("final_response"):
                            return state
                        break

                    if current == "classify_intent":
                        current = self._builder._decide_after_intent_classification(state)
                        continue

                    if current == "generate_parquet_query":
                        current = self._builder._decide_after_clarification(state)
                        continue

                    if current == "execute_query":
                        current = self._builder._decide_after_query_execution(state)
                        continue

                    # ✅ FIX: Route from generate_plotly_spec to format_final_response
                    if current == "generate_plotly_spec":
                        # After generating spec, always format the final response
                        current = "format_final_response"
                        continue

                    if current in ("format_final_response", "execute_une_tool"):
                        # These nodes are truly terminal
                        if state.get("final_response"):
                            return state
                        break

                # Fallback: return whatever state we have
                return state

        return _SimpleExecutor(nodes, self)
