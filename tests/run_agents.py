#!/usr/bin/env python3
# run_agents.py
import sys
import os

# ================================
# Ajuste do path para localizar os agentes Python
# ================================
current_dir = os.path.dirname(os.path.abspath(__file__))
core_agents_path = os.path.join(current_dir, "core", "agents")
if core_agents_path not in sys.path:
    sys.path.append(core_agents_path)

# ================================
# Importação dos agentes Python reais
# ================================
try:
    # Se houver import de LLM que não existe, comente dentro do agente
    from caculinha_bi_agent import CACULINHA_BI_AGENT
    from caculinha_dev_agent import CACULINHA_DEV_AGENT
    from data_sync_agent import DATA_SYNC_AGENT
except ImportError as e:
    print("Erro ao importar agentes. Verifique se os arquivos existem em core/agents/")
    print("Detalhes do erro:", e)
    sys.exit(1)

# ================================
# Menu interativo para escolher agente
# ================================
TEST_REQUESTS = {
    "1": [
        "gerar relatório semanal de vendas",
        "analisar produtos com ruptura no PDV da semana",
        "calcular KPI de vendas por região"
    ],
    "2": [
        "criar script para enviar relatório de vendas diário por email",
        "criar função Python para atualizar planilha de estoque automaticamente",
        "gerar script Python para copiar arquivos CSV de uma pasta para outra"
    ],
    "3": [
        "sincronizar tabela de vendas da semana para SQL Server",
        "limpar dados de estoque, remover duplicatas e preencher valores nulos",
        "converter CSV de produtos para Parquet e salvar na pasta processed_data"
    ]
}

AGENT_MAPPING = {
    "1": ("CACULINHA_BI_AGENT", CACULINHA_BI_AGENT.run),
    "2": ("CACULINHA_DEV_AGENT", CACULINHA_DEV_AGENT.run),
    "3": ("DATA_SYNC_AGENT", DATA_SYNC_AGENT.run)
}

def main():
    print("=== Python Agents Simulator ===")
    print("Escolha o agente para executar:")
    print("1 - bi-agent (CACULINHA_BI_AGENT)")
    print("2 - code-agent (CACULINHA_DEV_AGENT)")
    print("3 - data-agent (DATA_SYNC_AGENT)")

    choice = input("Digite o número do agente: ").strip()
    agent_info = AGENT_MAPPING.get(choice)

    if not agent_info:
        print("Agente inválido.")
        return

    agent_name, agent_func = agent_info
    print(f"\nVocê escolheu: {agent_name}")
    
    # Mostra requests de teste disponíveis
    print("Requests de teste disponíveis:")
    for i, r in enumerate(TEST_REQUESTS[choice], start=1):
        print(f"{i} - {r}")

    test_choice = input("Escolha o número do request ou digite um request customizado: ").strip()
    
    if test_choice.isdigit() and 1 <= int(test_choice) <= len(TEST_REQUESTS[choice]):
        request = TEST_REQUESTS[choice][int(test_choice)-1]
    else:
        request = test_choice

    print(f"\nExecutando request: {request}")
    result = agent_func(request)
    print(f"\n=== Resultado ===\n{result}")


# ================================
# Entrada principal
# ================================
if __name__ == "__main__":
    main()
