"""
Módulo para core/agent_state.py. Define a classe principal 'AgentState'.
"""

from __future__ import annotations

import operator
from typing import TypedDict, Annotated, List, Union, Literal, TYPE_CHECKING, Sequence, Optional, Dict, Any

from langchain_core.messages import BaseMessage
from plotly.graph_objects import Figure as PlotlyFigure

import core  # Adicionado para garantir que 'core' esteja no escopo global para avaliação de tipos em string
# Importar RouteDecision diretamente para uso em anotações de tipo
RouteDecision = Literal["tool", "code"]

# O bloco TYPE_CHECKING anterior para RouteDecision não é mais estritamente necessário
# para esta anotação específica, pois RouteDecision é importado diretamente.
# Mantendo o bloco TYPE_CHECKING caso seja usado para outras importações condicionais.
if TYPE_CHECKING:
    pass  # Pode ser usado para outras importações apenas de checagem de tipo


class AgentState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], operator.add]
    retrieved_data: Optional[List[Dict[str, Any]]]
    chart_code: Optional[str]
    plotly_fig: Optional[PlotlyFigure]
    plotly_spec: Optional[Dict[str, Any]]
    route_decision: Optional["RouteDecision"]  # Usar string para anotação de tipo
    sql_query: Optional[str]
    parquet_filters: Optional[Dict[str, Any]]
    final_response: Optional[Dict[str, Any]] # Adicionar esta linha # Adicionar esta linha
    intent: Optional[str]
    # 🧠 Conversational Reasoning Fields (v3.0)
    reasoning_mode: Optional[str]  # "conversational" ou "analytical"
    reasoning_result: Optional[Dict[str, Any]]  # Resultado completo da análise de raciocínio
