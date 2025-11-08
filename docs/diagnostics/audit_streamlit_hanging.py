#!/usr/bin/env python3
"""
Audit Agent - Análise de Carregamento Infinito no Streamlit
Objetivo: Identificar causa raiz de travamento no streamlit_app.py
"""

import os
import re
from pathlib import Path
from typing import Dict, List, Tuple

def read_file(path: str) -> str:
    """Lê arquivo com tratamento de erro"""
    try:
        with open(path, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        return f"ERRO_LEITURA: {e}"

def analyze_streamlit_app() -> Dict:
    """Analisa streamlit_app.py para código de módulo problemático"""
    path = "C:\\Users\\André\\Documents\\Agent_Solution_BI\\streamlit_app.py"
    content = read_file(path)

    issues = {
        "module_level_code": [],
        "heavy_imports": [],
        "blocking_initializations": [],
        "session_state_issues": []
    }

    lines = content.split('\n')

    # Busca por imports pesados no nível de módulo
    import_section = True
    function_started = False

    for i, line in enumerate(lines, 1):
        # Detecta início de funções/classes
        if line.strip().startswith(('def ', 'class ', '@st.')):
            function_started = True
            import_section = False

        # Se ainda não entrou em funções, é código de módulo
        if not function_started and not import_section:
            if line.strip() and not line.strip().startswith('#') and not line.strip().startswith('import') and not line.strip().startswith('from'):
                issues["module_level_code"].append((i, line.strip()))

        # Identifica imports pesados
        if 'import' in line and any(heavy in line for heavy in ['langgraph', 'langchain', 'polars', 'dask', 'sql']):
            issues["heavy_imports"].append((i, line.strip()))

        # Busca por inicializações que bloqueiam
        if any(blocking in line for blocking in ['graph_builder', 'initialize', 'load_model', 'connect_db', 'setup_llm']):
            if not line.strip().startswith('#'):
                issues["blocking_initializations"].append((i, line.strip()))

        # Session state que pode causar loops
        if 'st.session_state' in line:
            issues["session_state_issues"].append((i, line.strip()))

    return issues

def analyze_config() -> Dict:
    """Analisa .streamlit/config.toml"""
    path = "C:\\Users\\André\\Documents\\Agent_Solution_BI\\.streamlit\\config.toml"
    content = read_file(path)

    issues = {
        "config_content": content[:500],
        "potential_problems": []
    }

    # Verifica configurações problemáticas
    if 'client.runOnSave = true' in content:
        issues["potential_problems"].append("client.runOnSave=true causa re-execução contínua")

    if 'logger.level' not in content:
        issues["potential_problems"].append("Logger level não configurado")

    return issues

def analyze_graph_builder() -> Dict:
    """Analisa graph_builder.py para problemas de inicialização"""
    path = "C:\\Users\\André\\Documents\\Agent_Solution_BI\\core\\graph\\graph_builder.py"
    content = read_file(path)

    issues = {
        "init_blocking_calls": [],
        "async_issues": [],
        "circular_dependencies": []
    }

    lines = content.split('\n')

    for i, line in enumerate(lines, 1):
        # Busca por await e sleep que podem travar
        if 'await' in line or 'time.sleep' in line:
            issues["init_blocking_calls"].append((i, line.strip()))

        # Imports circulares
        if 'from core.' in line and 'import' in line:
            issues["circular_dependencies"].append((i, line.strip()))

    return issues

def analyze_llm_adapter() -> Dict:
    """Analisa llm_adapter.py para bloqueios"""
    path = "C:\\Users\\André\\Documents\\Agent_Solution_BI\\core\\llm_adapter.py"
    content = read_file(path)

    issues = {
        "blocking_calls": [],
        "model_loading": [],
        "api_calls": []
    }

    lines = content.split('\n')

    for i, line in enumerate(lines, 1):
        # Busca por chamadas bloqueantes
        if any(blocking in line for blocking in ['requests.', 'urllib', '.invoke(', 'load_model']):
            issues["blocking_calls"].append((i, line.strip()))

        # Model loading
        if 'model' in line.lower() and '=' in line:
            issues["model_loading"].append((i, line.strip()))

        # API calls
        if 'api' in line.lower() or 'claude' in line.lower():
            issues["api_calls"].append((i, line.strip()))

    return issues

def print_report(streamlit_issues, config_issues, graph_issues, llm_issues):
    """Gera relatório formatado"""

    report = """
====================================================================
AUDIT AGENT - RELATÓRIO DE ANÁLISE: STREAMLIT CARREGAMENTO INFINITO
====================================================================

TIMESTAMP: 2025-11-07
STATUS: ANÁLISE EM PROGRESSO

--------------------------------------------------------------------
1. ANALISE: streamlit_app.py
--------------------------------------------------------------------
"""

    if streamlit_issues["module_level_code"]:
        report += "\n[CRITICO] Código no nível de módulo detectado:\n"
        for line_num, code in streamlit_issues["module_level_code"][:10]:
            report += f"  Linha {line_num}: {code}\n"

    if streamlit_issues["blocking_initializations"]:
        report += "\n[ALTO] Inicializações bloqueantes:\n"
        for line_num, code in streamlit_issues["blocking_initializations"][:10]:
            report += f"  Linha {line_num}: {code}\n"

    report += f"\n[INFO] Session State acessos: {len(streamlit_issues['session_state_issues'])}\n"

    report += "\n--------------------------------------------------------------------\n"
    report += "2. ANALISE: .streamlit/config.toml\n"
    report += "--------------------------------------------------------------------\n"

    if config_issues["potential_problems"]:
        report += "\n[AVISO] Problemas de configuração:\n"
        for problem in config_issues["potential_problems"]:
            report += f"  - {problem}\n"

    report += "\n--------------------------------------------------------------------\n"
    report += "3. ANALISE: core/graph/graph_builder.py\n"
    report += "--------------------------------------------------------------------\n"

    if graph_issues["init_blocking_calls"]:
        report += "\n[ALTO] Calls bloqueantes na inicialização:\n"
        for line_num, code in graph_issues["init_blocking_calls"][:5]:
            report += f"  Linha {line_num}: {code}\n"

    report += "\n--------------------------------------------------------------------\n"
    report += "4. ANALISE: core/llm_adapter.py\n"
    report += "--------------------------------------------------------------------\n"

    if llm_issues["blocking_calls"]:
        report += "\n[ALTO] Chamadas bloqueantes detectadas:\n"
        for line_num, code in llm_issues["blocking_calls"][:5]:
            report += f"  Linha {line_num}: {code}\n"

    report += "\n" + "="*68 + "\n"

    return report

if __name__ == "__main__":
    print("\n[INICIANDO] Análise de carregamento infinito do Streamlit...")

    streamlit_issues = analyze_streamlit_app()
    config_issues = analyze_config()
    graph_issues = analyze_graph_builder()
    llm_issues = analyze_llm_adapter()

    report = print_report(streamlit_issues, config_issues, graph_issues, llm_issues)
    print(report)

    # Salva relatório
    with open("C:\\Users\\André\\Documents\\Agent_Solution_BI\\audit_report_hanging.txt", 'w', encoding='utf-8') as f:
        f.write(report)

    print("\n[OK] Relatório salvo em: audit_report_hanging.txt")
