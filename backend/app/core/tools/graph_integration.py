import logging
import os
from typing import Any, Dict

import pandas as pd

from app.core.tools.visualization_tools import generate_plotly_chart_code

# Importa as funcionalidades de visualização existentes

# Importa a função de processamento de gráficos do novo módulo

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    filename="logs/graph_integration.log",
    filemode="a",
)
logger = logging.getLogger("graph_integration")

# Diretório para salvar gráficos do agente_visual
PLOT_DIR = "outputs/plots"
os.makedirs(PLOT_DIR, exist_ok=True)

# Diretório para salvar gráficos do sistema existente
CHART_OUTPUT_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "generated_charts"
)
os.makedirs(CHART_OUTPUT_DIR, exist_ok=True)


def processar_resposta_com_grafico(resposta: Any) -> Dict[str, Any]:
    """
    Processa a resposta do agente e gera gráfico se apropriado,
    integrando as funcionalidades do agente_visual.py com o sistema existente.

    Args:
        resposta: Resposta do agente (pode ser dict, string ou objeto)

    Returns:
        Dict com a resposta processada e caminho do gráfico se gerado
    """
    try:
        # Converte para formato padrão se não for um dicionário
        if not isinstance(resposta, dict):
            resultado = {"output": str(resposta), "type": "text"}
        else:
            resultado = resposta

        # Extrai o texto da resposta
        texto = resultado.get("output", str(resposta))

        # Verifica se há intenção de visualizar gráfico
        termos_grafico = [
            "gráfico",
            "visualizar",
            "tendência",
            "mostrar gráfico",
            "exibir gráfico",
        ]
        if any(termo in texto.lower() for termo in termos_grafico):
            # Tenta obter DataFrame da resposta
            df = None

            # Verifica se há um DataFrame na resposta
            if hasattr(resposta, "result") and isinstance(
                resposta.result, pd.DataFrame
            ):
                df = resposta.result
            elif isinstance(resposta, dict):
                if "result" in resposta and isinstance(
                    resposta["result"], pd.DataFrame
                ):
                    df = resposta["result"]
                elif "data" in resposta and isinstance(resposta["data"], list):
                    df = pd.DataFrame(resposta["data"])
                elif "output" in resposta and isinstance(resposta["output"], list):
                    df = pd.DataFrame(resposta["output"])

            # Se encontrou dados, gera o gráfico
            if df is not None and not df.empty:
                # Tenta gerar o gráfico usando o agente_visual
                # Importa dinamicamente a função gerar_grafico para evitar importação circular
                try:
                    from agente_visual import gerar_grafico

                    caminho_grafico = gerar_grafico(df, "Visualização de Dados")
                except ImportError as e:
                    logger.error(f"Erro ao importar função gerar_grafico: {e}")
                    caminho_grafico = None

                if caminho_grafico:
                    # Adiciona o caminho do gráfico à resposta
                    resultado["chart"] = caminho_grafico
                    resultado["chart_type"] = "matplotlib"
                    resultado["output"] = (
                        f"{texto}\n\n[Grafico gerado]: {caminho_grafico}"
                    )

                    logger.info(f"Gráfico gerado com matplotlib: {caminho_grafico}")
                    return resultado
                else:
                    # Fallback: tenta gerar com Plotly se o matplotlib falhar
                    try:
                        # Gera código para o gráfico Plotly
                        chart_description = "Gerar visualização dos dados fornecidos"
                        plotly_code = generate_plotly_chart_code(df, chart_description)

                        # Executa o código e salva o gráfico
                        chart_result = execute_chart_code_and_save(plotly_code)

                        if "Gráfico gerado e salvo com sucesso" in chart_result:
                            # Extrai o caminho do gráfico da mensagem
                            caminho = chart_result.split("sucesso em: ")[1]
                            resultado["chart"] = caminho
                            resultado["chart_type"] = "plotly"
                            resultado["output"] = (
                                f"{texto}\n\n[Grafico gerado]: {caminho}"
                            )

                            logger.info(f"Gráfico gerado com Plotly: {caminho}")
                            return resultado
                    except Exception as e:
                        logger.error(f"Erro ao gerar gráfico com Plotly: {e}")

            # Se chegou aqui, não conseguiu gerar o gráfico
            resultado["output"] = (
                f"{texto}\n\n[Aviso]: Não foi possível gerar um gráfico com os dados fornecidos."
            )
            return resultado

        # Se não há intenção de gráfico, retorna a resposta original
        return resultado

    except Exception as e:
        logger.error(f"Erro ao processar resposta com gráfico: {e}")
        return {
            "output": f"{str(resposta)}\n\n[Erro] ao processar gráfico: {e}",
            "error": str(e),
        }


if __name__ == "__main__":
    print("Rodando como script...")
    
    # Teste simples da função
    test_response = {
        "output": "Por favor, gere um gráfico das vendas de tecidos.",
        "data": [
            {"Categoria": "Tecidos", "Vendas": 1500},
            {"Categoria": "Papelaria", "Vendas": 1200},
            {"Categoria": "Pintura", "Vendas": 800}
        ]
    }
    
    print("Processando resposta de teste...")
    result = processar_resposta_com_grafico(test_response)
    print("Resultado:", result)
