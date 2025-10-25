#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
SCRIPT DE AUDITORIA URGENTE - Sistema de Logs
Data: 2025-10-21
Objetivo: Identificar e corrigir problemas de logging
"""

import os
import sys
import json
from pathlib import Path
from datetime import datetime

def audit_logging():
    """Executa auditoria completa do sistema de logs"""

    base_path = Path("C:/Users/André/Documents/Agent_Solution_BI")
    results = {
        "timestamp": datetime.now().isoformat(),
        "problemas_encontrados": [],
        "correcoes_aplicadas": [],
        "logs_criados": [],
        "validacao": {
            "setup_logging_presente": False,
            "logs_ativos": False,
            "plano_a_instrumentado": False
        },
        "detalhes": {}
    }

    # 1. Verificar logging_config.py
    print("[1] Analisando core/config/logging_config.py...")
    logging_config_path = base_path / "core" / "config" / "logging_config.py"

    if logging_config_path.exists():
        with open(logging_config_path, 'r', encoding='utf-8') as f:
            content = f.read()

        has_setup_logging = 'def setup_logging' in content
        has_file_handler = 'FileHandler' in content
        has_logging_dir = 'logs' in content and 'makedirs' in content

        results["validacao"]["setup_logging_presente"] = has_setup_logging
        results["detalhes"]["logging_config"] = {
            "existe": True,
            "tem_setup_logging": has_setup_logging,
            "tem_file_handler": has_file_handler,
            "tem_logs_dir": has_logging_dir
        }

        if not has_setup_logging:
            results["problemas_encontrados"].append("logging_config.py não possui função setup_logging()")
        if not has_file_handler:
            results["problemas_encontrados"].append("logging_config.py não possui FileHandler")
    else:
        results["problemas_encontrados"].append("logging_config.py não encontrado!")
        results["detalhes"]["logging_config"] = {"existe": False}

    # 2. Verificar streamlit_app.py
    print("[2] Analisando streamlit_app.py...")
    streamlit_path = base_path / "streamlit_app.py"

    if streamlit_path.exists():
        with open(streamlit_path, 'r', encoding='utf-8') as f:
            content = f.read()

        has_setup_call = 'setup_logging()' in content or 'setup_logging(' in content
        imports_logging = 'from core.config.logging_config import' in content or 'import logging' in content

        results["detalhes"]["streamlit_app"] = {
            "existe": True,
            "chama_setup_logging": has_setup_call,
            "imports_logging": imports_logging
        }

        if not has_setup_call:
            results["problemas_encontrados"].append("streamlit_app.py NÃO chama setup_logging()")
        if not imports_logging:
            results["problemas_encontrados"].append("streamlit_app.py não importa logging")
    else:
        results["problemas_encontrados"].append("streamlit_app.py não encontrado!")

    # 3. Verificar diretório de logs
    print("[3] Verificando diretório de logs...")
    logs_dir = base_path / "logs"

    if logs_dir.exists():
        log_files = list(logs_dir.glob("*.log"))
        results["detalhes"]["logs_dir"] = {
            "existe": True,
            "arquivos": len(log_files),
            "arquivos_recentes": [f.name for f in sorted(log_files, key=lambda x: x.stat().st_mtime, reverse=True)[:5]]
        }

        if log_files:
            results["validacao"]["logs_ativos"] = True
    else:
        results["detalhes"]["logs_dir"] = {"existe": False}
        results["problemas_encontrados"].append("Diretório logs/ não existe!")

    # 4. Verificar learning logs
    print("[4] Verificando data/learning/ logs...")
    learning_dir = base_path / "data" / "learning"

    if learning_dir.exists():
        learning_files = list(learning_dir.glob("*.json*"))
        results["detalhes"]["learning_logs"] = {
            "existe": True,
            "arquivos": len(learning_files),
            "arquivos": [f.name for f in sorted(learning_files, key=lambda x: x.stat().st_mtime, reverse=True)[:5]]
        }
    else:
        results["detalhes"]["learning_logs"] = {"existe": False}

    # 5. Verificar agents por instrumentação de logs
    print("[5] Verificando instrumentação em agents...")
    agents_dir = base_path / "core" / "agents"

    agents_checked = {}
    if agents_dir.exists():
        for agent_file in agents_dir.glob("*.py"):
            if agent_file.name.startswith("__"):
                continue
            with open(agent_file, 'r', encoding='utf-8') as f:
                agent_content = f.read()

            has_logging = 'logger' in agent_content or 'logging.info' in agent_content
            agents_checked[agent_file.name] = has_logging

    results["detalhes"]["agents_instrumented"] = agents_checked

    # 6. Verificar business_intelligence por Plano A
    print("[6] Verificando Plano A em business_intelligence...")
    bi_dir = base_path / "core" / "business_intelligence"
    plano_a_logs = False

    if bi_dir.exists():
        for bi_file in bi_dir.glob("*.py"):
            with open(bi_file, 'r', encoding='utf-8') as f:
                bi_content = f.read()

            # Verificar instrumentação de load_data
            if 'def load_data' in bi_content:
                has_filter_log = 'logger' in bi_content and ('filter' in bi_content.lower())
                has_performance_log = 'logger' in bi_content and ('time' in bi_content or 'duration' in bi_content)

                if has_filter_log or has_performance_log:
                    plano_a_logs = True

    results["validacao"]["plano_a_instrumentado"] = plano_a_logs

    if not plano_a_logs:
        results["problemas_encontrados"].append("Plano A não está instrumentado com logs")

    return results

if __name__ == "__main__":
    print("=" * 60)
    print("AUDITORIA URGENTE - SISTEMA DE LOGS")
    print("Data: 2025-10-21")
    print("=" * 60)

    results = audit_logging()

    print("\n" + "=" * 60)
    print("RESULTADOS:")
    print("=" * 60)
    print(json.dumps(results, indent=2, ensure_ascii=False))

    # Salvar resultados
    output_path = Path("C:/Users/André/Documents/Agent_Solution_BI/AUDIT_LOGS_RESULTS.json")
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)

    print(f"\nResultados salvos em: {output_path}")
