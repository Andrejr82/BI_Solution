#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Analisador de Arquivos Críticos - Auditoria de Logs
Foca em: logging_config.py, streamlit_app.py, direct_query_engine.py
"""

import json
from pathlib import Path
from datetime import datetime

BASE = Path("C:/Users/André/Documents/Agent_Solution_BI")

ARQUIVOS = {
    "logging_config": BASE / "core" / "config" / "logging_config.py",
    "streamlit_app": BASE / "streamlit_app.py",
    "direct_query_engine": BASE / "core" / "business_intelligence" / "direct_query_engine.py",
    "parquet_adapter": BASE / "core" / "connectivity" / "parquet_adapter.py",
}

def analisar_arquivo(chave, caminho):
    """Analisa um arquivo específico"""

    resultado = {
        "chave": chave,
        "arquivo": str(caminho),
        "existe": caminho.exists(),
        "tamanho_bytes": 0,
        "linhas": 0,
        "conteudo_preview": "",
        "verificacoes": {},
        "problemas": [],
        "oportunidades": []
    }

    if not caminho.exists():
        resultado["problemas"].append(f"ARQUIVO NAO EXISTE: {caminho}")
        return resultado

    # Ler arquivo
    try:
        with open(caminho, 'r', encoding='utf-8') as f:
            conteudo = f.read()
        linhas = conteudo.splitlines()

        resultado["tamanho_bytes"] = len(conteudo.encode('utf-8'))
        resultado["linhas"] = len(linhas)
        resultado["conteudo_preview"] = '\n'.join(linhas[:40])

    except Exception as e:
        resultado["problemas"].append(f"Erro ao ler: {e}")
        return resultado

    # ===== VERIFICAÇÕES POR TIPO =====

    if chave == "logging_config":
        resultado["verificacoes"] = {
            "tem_setup_logging": "def setup_logging" in conteudo,
            "tem_filehandler": "FileHandler" in conteudo,
            "tem_logging_import": "import logging" in conteudo,
            "tem_rotatinghandler": "RotatingFileHandler" in conteudo,
            "tem_logs_dir": "'logs'" in conteudo or '"logs"' in conteudo,
            "tem_get_logger": "def get_logger" in conteudo,
            "tem_plan_a_logging": "plan_a" in conteudo.lower() or "plano_a" in conteudo.lower(),
        }

        if not resultado["verificacoes"]["tem_setup_logging"]:
            resultado["problemas"].append("CRITICO: Nao tem funcao setup_logging()")
        if not resultado["verificacoes"]["tem_filehandler"]:
            resultado["problemas"].append("CRITICO: Nao tem FileHandler")
        if not resultado["verificacoes"]["tem_rotatinghandler"]:
            resultado["oportunidades"].append("Considerar RotatingFileHandler para melhor gerenciamento")

    elif chave == "streamlit_app":
        resultado["verificacoes"] = {
            "tem_import_logging": "from core.config.logging_config import" in conteudo or "import logging" in conteudo,
            "chama_setup_logging": "setup_logging()" in conteudo,
            "tem_logging_call": "logger." in conteudo or "logging." in conteudo,
            "primeira_30_linhas": '\n'.join(linhas[:30])
        }

        if not resultado["verificacoes"]["chama_setup_logging"]:
            resultado["problemas"].append("CRITICO: Nao chama setup_logging() no início")
            resultado["oportunidades"].append("Adicionar setup_logging() logo no início de main()")

    elif chave == "direct_query_engine":
        resultado["verificacoes"] = {
            "tem_logger": "logger" in conteudo or "logging" in conteudo,
            "tem_load_data": "def load_data" in conteudo,
            "log_filters": "filter" in conteudo and ("logger" in conteudo or "logging" in conteudo),
            "log_performance": "time" in conteudo and ("logger" in conteudo or "logging" in conteudo),
            "log_fallback": "fallback" in conteudo.lower() and ("logger" in conteudo or "logging" in conteudo),
        }

        if not resultado["verificacoes"]["tem_logger"]:
            resultado["problemas"].append("Plano A: Nao tem logger instrumentado")
        if not resultado["verificacoes"]["log_filters"]:
            resultado["oportunidades"].append("Plano A: Adicionar log quando load_data recebe filtros")
        if not resultado["verificacoes"]["log_performance"]:
            resultado["oportunidades"].append("Plano A: Adicionar log de performance (tempo, linhas)")
        if not resultado["verificacoes"]["log_fallback"]:
            resultado["oportunidades"].append("Plano A: Adicionar log de fallback")

    elif chave == "parquet_adapter":
        resultado["verificacoes"] = {
            "tem_logger": "logger" in conteudo or "logging" in conteudo,
            "tem_load_data": "def load_data" in conteudo,
        }

    return resultado


def main():
    """Executa análise completa"""

    print("\n" + "="*80)
    print("AUDITORIA DE SISTEMA DE LOGS - 2025-10-21")
    print("="*80 + "\n")

    resultados = {}

    for chave, caminho in ARQUIVOS.items():
        print(f"[ANALISANDO] {chave}...")
        resultado = analisar_arquivo(chave, caminho)
        resultados[chave] = resultado

        if resultado["existe"]:
            print(f"  - Existe: SIM ({resultado['linhas']} linhas, {resultado['tamanho_bytes']} bytes)")

            # Mostrar verificações
            if resultado["verificacoes"]:
                print(f"  - Verificações:")
                for k, v in resultado["verificacoes"].items():
                    status = "✓" if v else "✗"
                    print(f"    {status} {k}: {v}")

            # Mostrar problemas
            if resultado["problemas"]:
                print(f"  - PROBLEMAS:")
                for p in resultado["problemas"]:
                    print(f"    ! {p}")

            # Mostrar oportunidades
            if resultado["oportunidades"]:
                print(f"  - OPORTUNIDADES:")
                for o in resultado["oportunidades"]:
                    print(f"    ~ {o}")
        else:
            print(f"  - Existe: NAO - {resultado['problemas']}")

        print()

    # Resumo
    print("="*80)
    print("RESUMO")
    print("="*80 + "\n")

    logs_dir = BASE / "logs"
    print(f"Diretório logs/: {logs_dir.exists()}")
    if logs_dir.exists():
        log_files = list(logs_dir.glob("*.log"))
        print(f"Arquivos .log: {len(log_files)}")

    learning_dir = BASE / "data" / "learning"
    print(f"Diretório data/learning/: {learning_dir.exists()}")
    if learning_dir.exists():
        learning_files = list(learning_dir.glob("*.json*"))
        print(f"Arquivos de learning: {len(learning_files)}")

    # Salvar resultados em JSON
    output_file = BASE / "AUDIT_RESULTS_2025_10_21.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(resultados, f, indent=2, ensure_ascii=False, default=str)

    print(f"\nResultados salvos em: {output_file}")

    # Retornar para possível uso
    return resultados


if __name__ == "__main__":
    resultados = main()
    print("\nAnalise concluida!")
