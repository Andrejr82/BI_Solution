#!/usr/bin/env python3
"""
Diagnostic Detalhado - Identifica exatamente onde Streamlit está travando
"""

import sys
import os
from pathlib import Path

# Adiciona ao path
sys.path.insert(0, "C:\\Users\\André\\Documents\\Agent_Solution_BI")

def diagnose_streamlit():
    """Diagnóstico do streamlit_app.py"""

    print("\n" + "="*80)
    print("DIAGNOSTIC: STREAMLIT_APP.PY")
    print("="*80 + "\n")

    app_path = Path("C:\\Users\\André\\Documents\\Agent_Solution_BI\\streamlit_app.py")

    try:
        with open(app_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()

        print("[1] VERIFICANDO IMPORTS DE MÓDULO (linhas 1-50)\n")
        for i, line in enumerate(lines[:50], 1):
            if line.strip() and not line.strip().startswith('#'):
                print(f"    {i:3d}: {line.rstrip()}")

        print("\n[2] DETECTANDO CÓDIGO DE MÓDULO FORA DE FUNÇÕES\n")
        in_function = False
        module_code_lines = []

        for i, line in enumerate(lines, 1):
            stripped = line.strip()

            # Detecta definição de função/classe
            if stripped.startswith(('def ', 'class ', '@')):
                in_function = True

            # Se não está em função e há código executável
            if not in_function and stripped and not stripped.startswith('#') and not stripped.startswith('import') and not stripped.startswith('from'):
                if 'st.' in line or 'graph' in line or 'llm' in line or '=' in line and 'import' not in line:
                    module_code_lines.append((i, line.rstrip()))

        if module_code_lines:
            print("ENCONTRADO CÓDIGO NO NÍVEL DE MÓDULO:")
            for line_num, code in module_code_lines[:20]:
                print(f"    Linha {line_num}: {code}")
        else:
            print("    OK: Sem código crítico no nível de módulo")

        print("\n[3] BUSCANDO INICIALIZAÇÕES BLOQUEANTES\n")
        blocking_patterns = [
            'graph_builder',
            'initialize',
            'load_model',
            'connect_db',
            'setup',
            'st.set_page_config',
            'st.session_state',
            'build_graph',
            'Graph(',
            'AgentGraph'
        ]

        blocking_lines = []
        for i, line in enumerate(lines, 1):
            if any(pattern in line for pattern in blocking_patterns):
                if not line.strip().startswith('#'):
                    blocking_lines.append((i, line.rstrip()))

        print(f"Inicializações encontradas: {len(blocking_lines)}\n")
        for line_num, code in blocking_lines[:15]:
            print(f"    Linha {line_num}: {code}")

        print("\n[4] ANALISANDO SESSION_STATE E LOOPS\n")
        session_lines = []
        for i, line in enumerate(lines, 1):
            if 'session_state' in line or 'st.session_state' in line:
                session_lines.append((i, line.rstrip()))

        print(f"Session state acessos: {len(session_lines)}\n")
        for line_num, code in session_lines[:10]:
            print(f"    Linha {line_num}: {code}")

    except Exception as e:
        print(f"ERRO: {e}")


def diagnose_graph_builder():
    """Diagnóstico do graph_builder.py"""

    print("\n" + "="*80)
    print("DIAGNOSTIC: GRAPH_BUILDER.PY")
    print("="*80 + "\n")

    gb_path = Path("C:\\Users\\André\\Documents\\Agent_Solution_BI\\core\\graph\\graph_builder.py")

    try:
        with open(gb_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()

        print("[1] IMPORTS E DEPENDÊNCIAS\n")
        for i, line in enumerate(lines[:40], 1):
            if 'import' in line or 'from' in line:
                print(f"    {i:3d}: {line.rstrip()}")

        print("\n[2] MÉTODOS DE INICIALIZAÇÃO\n")
        for i, line in enumerate(lines, 1):
            if 'def ' in line and any(x in line for x in ['__init__', 'build', 'initialize', 'setup']):
                print(f"    Linha {i}: {line.rstrip()}")

        print("\n[3] CHAMADAS BLOQUEANTES (await, sleep, requests)\n")
        blocking = []
        for i, line in enumerate(lines, 1):
            if any(x in line for x in ['await ', 'sleep(', 'requests.', 'time.sleep', '.invoke(', 'compile(']):
                blocking.append((i, line.rstrip()))

        if blocking:
            for line_num, code in blocking[:10]:
                print(f"    Linha {line_num}: {code}")
        else:
            print("    OK: Sem chamadas bloqueantes óbvias")

        print("\n[4] DEPENDENCIES/IMPORTS CIRCULARES\n")
        circular = []
        for i, line in enumerate(lines, 1):
            if 'from core.' in line and 'import' in line:
                circular.append((i, line.rstrip()))

        if circular:
            for line_num, code in circular[:10]:
                print(f"    Linha {line_num}: {code}")

    except Exception as e:
        print(f"ERRO: {e}")


def diagnose_config():
    """Diagnóstico de config.toml"""

    print("\n" + "="*80)
    print("DIAGNOSTIC: .streamlit/config.toml")
    print("="*80 + "\n")

    config_path = Path("C:\\Users\\André\\Documents\\Agent_Solution_BI\\.streamlit\\config.toml")

    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            content = f.read()

        print(content)

        print("\n[ANALISE]\n")
        issues = []

        if 'client.runOnSave = true' in content:
            issues.append("PROBLEMA: runOnSave=true causa re-execução contínua")

        if 'maxCachedMessageSize' not in content:
            issues.append("AVISO: maxCachedMessageSize não configurado")

        if 'client.showErrorDetails' not in content:
            issues.append("INFO: showErrorDetails não configurado")

        if issues:
            for issue in issues:
                print(f"  {issue}")
        else:
            print("  OK: Config parece válida")

    except FileNotFoundError:
        print("ARQUIVO NÃO ENCONTRADO")
    except Exception as e:
        print(f"ERRO: {e}")


def check_imports():
    """Tenta importar módulos para detectar erros"""

    print("\n" + "="*80)
    print("DIAGNOSTIC: IMPORTS E DEPENDÊNCIAS")
    print("="*80 + "\n")

    modules_to_check = [
        ('streamlit', 'Streamlit'),
        ('langgraph', 'LangGraph'),
        ('langchain', 'LangChain'),
        ('polars', 'Polars'),
        ('pandas', 'Pandas'),
    ]

    for module_name, display_name in modules_to_check:
        try:
            __import__(module_name)
            print(f"  [OK] {display_name} - importado com sucesso")
        except ImportError as e:
            print(f"  [ERRO] {display_name} - {e}")
        except Exception as e:
            print(f"  [AVISO] {display_name} - {e}")


if __name__ == "__main__":
    print("\n" + "="*80)
    print("AUDIT AGENT - DIAGNÓSTICO DE CARREGAMENTO INFINITO")
    print("="*80)

    diagnose_streamlit()
    diagnose_graph_builder()
    diagnose_config()
    check_imports()

    print("\n" + "="*80)
    print("DIAGNÓSTICO CONCLUÍDO")
    print("="*80 + "\n")
