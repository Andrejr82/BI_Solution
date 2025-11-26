# core/agents/supervisor_agent.py
import logging
from typing import Dict, Any


class SupervisorAgent:
    """
    Agente supervisor simplificado que roteia consultas para o ToolAgent.
    REMOVIDA importação circular com tool_agent.
    """

    CHART_KEYWORDS = [
        "gráfico",
        "gráficos",
        "grafico",
        "graficos",
        "visualizar",
        "visualização",
        "visualizacao",
        "mostrar",
        "chart",
        "charts",
        "vendas",
        "estoque",
        "distribuição",
        "distribuicao",
        "análise",
        "analise",
        "comparação",
        "comparacao",
        "pizza",
        "barras",
        "linha",
        "histograma",
        "dashboard",
        "plot",
        "plotar",
        "desenhar",
        "temporal",
        "série",
        "serie",
        "evolução",
        "evolucao",
        "mensal",
        "mês",
        "mes",
        "semanal",
        "trend",
        "tendência",
        "tendencia",
        "produto",
        "sku",
        "código",
        "codigo",
    ]

    def __init__(self, gemini_adapter):
        """
        Inicializa o supervisor.
        NOTA: ToolAgent agora é inicializado sob demanda para evitar importação circular.
        """
        self.logger = logging.getLogger(__name__)
        self.gemini_adapter = gemini_adapter
        self._tool_agent = None  # Lazy initialization
        self.logger.info("SupervisorAgent inicializado.")

    @property
    def tool_agent(self):
        """Lazy initialization do ToolAgent para evitar importação circular."""
        if self._tool_agent is None:
            # Importação local para evitar circular dependency
            from app.core.agents.tool_agent import ToolAgent
            self._tool_agent = ToolAgent(llm_adapter=self.gemini_adapter)
            self.logger.info("ToolAgent inicializado (lazy)")
        return self._tool_agent

    def _detect_chart_intent(self, query: str) -> bool:
        """
        Detecta se a consulta tem intenção de gerar gráficos.

        Args:
            query: Consulta do usuário

        Returns:
            True se detecta intenção de gráfico, False caso contrário
        """
        query_lower = query.lower()

        # Verificar se contém palavras-chave de gráficos
        for keyword in self.CHART_KEYWORDS:
            if keyword in query_lower:
                self.logger.info(f"Intenção de gráfico detectada: '{keyword}'")
                return True

        return False

    def route_query(self, query: str) -> Dict[str, Any]:
        """
        Roteia a consulta para o ToolAgent.

        Args:
            query: Consulta do usuário

        Returns:
            Resposta do ToolAgent
        """
        # Detectar se é requisição de gráfico
        is_chart_request = self._detect_chart_intent(query)

        if is_chart_request:
            self.logger.info(f"Roteando consulta de gráfico para ToolAgent: '{query}'")
        else:
            self.logger.info(f"Roteando consulta padrão para ToolAgent: '{query}'")

        # Ambos os tipos vão para ToolAgent que decidirá qual ferramenta usar
        return self.tool_agent.process_query(query)