"""
Utilitários para parsear e processar respostas do agente.
Detecta gráficos, dataframes e textos nas respostas.
"""

import json
import logging
from typing import Dict, Any, Tuple
import plotly.graph_objects as go

logger = logging.getLogger(__name__)


def parse_agent_response(response: str) -> Tuple[str, Dict[str, Any]]:
    """
    Parseia a resposta do agente e extrai dados estruturados.

    Args:
        response: String da resposta do agente

    Returns:
        Tupla (tipo, dados_processados)
        Tipos: "chart", "text", "error"
    """
    if not response:
        return "text", {"output": "Nenhuma resposta recebida."}

    response_lower = response.lower()

    # Detectar se contém informações de gráfico
    if any(
        keyword in response_lower
        for keyword in [
            "gráfico",
            "grafico",
            "chart",
            "plotly",
            "chart_data",
            "chart_type",
            "visualiza",
        ]
    ):
        logger.debug("Detectada resposta tipo gráfico")
        return _extract_chart_from_response(response)

    # Caso contrário, retornar como texto
    logger.debug("Resposta processada como texto")
    return "text", {"output": response}


def _extract_chart_from_response(response: str) -> Tuple[str, Dict[str, Any]]:
    """
    Extrai dados de gráfico de uma resposta de ferramenta.

    Args:
        response: String contendo dados do gráfico

    Returns:
        Tupla (tipo, figura_plotly ou erro)
    """
    try:
        # Tentar parsear como JSON
        if response.startswith("{"):
            data = json.loads(response)
        else:
            # Se não for JSON puro, tomar o primeiro JSON encontrado
            import re

            json_match = re.search(r"\{.*\}", response, re.DOTALL)
            if json_match:
                data = json.loads(json_match.group())
            else:
                return "text", {"output": response}

        # Verificar se é resposta de ferramenta de gráfico
        if "chart_data" in data and "status" in data:
            if data.get("status") == "success":
                try:
                    # chart_data já vem como JSON string de Plotly
                    chart_json = data["chart_data"]
                    if isinstance(chart_json, str):
                        chart_json = json.loads(chart_json)

                    # Converter JSON para figura Plotly
                    fig = go.Figure(chart_json)

                    logger.info(
                        f"Gráfico tipo '{data.get('chart_type', 'unknown')}' "
                        f"extraído com sucesso"
                    )

                    return "chart", {
                        "output": fig,
                        "summary": data.get("summary", {}),
                        "chart_type": data.get("chart_type", "unknown"),
                    }

                except Exception as e:
                    logger.warning(f"Erro ao processar chart_data: {e}")
                    # Retornar como texto se falhar
                    summary = data.get("summary", {})
                    msg = "Gráfico gerado com sucesso.\n\n**Sumário:**\n"
                    for key, value in summary.items():
                        msg += f"- **{key}**: {value}\n"
                    return "text", {"output": msg}

            else:
                error_msg = data.get("message", "Erro ao gerar gráfico")
                logger.warning(f"Gráfico retornou erro: {error_msg}")
                return "text", {"output": f"❌ {error_msg}"}

        # Se não tem estrutura de gráfico, retornar como texto
        return "text", {"output": response}

    except json.JSONDecodeError:
        logger.debug("Resposta não é JSON, retornando como texto")
        return "text", {"output": response}
    except Exception as e:
        logger.error(f"Erro ao extrair gráfico: {e}", exc_info=True)
        return "text", {"output": response}


def detect_dataframe_response(response: Any) -> bool:
    """
    Detecta se a resposta é um DataFrame.

    Args:
        response: Resposta a verificar

    Returns:
        True se for DataFrame, False caso contrário
    """
    try:
        import pandas as pd

        return isinstance(response, pd.DataFrame)
    except Exception:
        return False
