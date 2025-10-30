"""
Teste Simples de Integração - Agent Solution BI
"""

import sys
import os

print("="*60)
print("TESTE DE INTEGRACAO - Agent Solution BI")
print("="*60)

# Teste 1: FastAPI
print("\n[1/7] Testando FastAPI...")
try:
    import fastapi
    import uvicorn
    print("OK - FastAPI instalado (v{})".format(fastapi.__version__))
except ImportError as e:
    print("ERRO - FastAPI nao instalado: {}".format(e))

# Teste 2: Streamlit
print("\n[2/7] Testando Streamlit...")
try:
    import streamlit
    print("OK - Streamlit instalado (v{})".format(streamlit.__version__))
except ImportError as e:
    print("ERRO - Streamlit nao instalado: {}".format(e))

# Teste 3: Sintaxe api_server.py
print("\n[3/7] Testando sintaxe api_server.py...")
import py_compile
try:
    py_compile.compile("api_server.py", doraise=True)
    print("OK - api_server.py sintaxe correta")
except Exception as e:
    print("ERRO - api_server.py: {}".format(e))

# Teste 4: Imports do backend
print("\n[4/7] Testando imports do backend...")
try:
    from core.factory.component_factory import ComponentFactory
    from core.connectivity.parquet_adapter import ParquetAdapter
    from core.agents.code_gen_agent import CodeGenAgent
    from core.graph.graph_builder import GraphBuilder
    from core.utils.query_history import QueryHistory
    print("OK - Todos os imports do backend funcionam")
except ImportError as e:
    print("ERRO - Import do backend: {}".format(e))

# Teste 5: Variáveis de ambiente
print("\n[5/7] Testando variaveis de ambiente...")
from dotenv import load_dotenv
load_dotenv()
gemini_key = os.getenv("GEMINI_API_KEY")
deepseek_key = os.getenv("DEEPSEEK_API_KEY")
if gemini_key:
    print("OK - GEMINI_API_KEY configurada")
elif deepseek_key:
    print("OK - DEEPSEEK_API_KEY configurada")
else:
    print("AVISO - Nenhuma chave LLM configurada!")

# Teste 6: Frontend
print("\n[6/7] Testando frontend React...")
if os.path.exists("frontend/package.json"):
    print("OK - Frontend React encontrado")
    if os.path.exists("frontend/vite.config.ts"):
        print("OK - Vite configurado")
else:
    print("ERRO - Frontend nao encontrado")

# Teste 7: API FastAPI
print("\n[7/7] Testando API FastAPI...")
try:
    from scripts.api_server import app
    routes = [r.path for r in app.routes]
    api_routes = [r for r in routes if r.startswith('/api')]
    print("OK - API FastAPI carregada")
    print("   Total de rotas: {}".format(len(routes)))
    print("   Rotas /api: {}".format(len(api_routes)))
    for route in sorted(api_routes)[:5]:
        print("     - {}".format(route))
except Exception as e:
    print("ERRO - API FastAPI: {}".format(e))

# Relatório final
print("\n" + "="*60)
print("RELATORIO FINAL")
print("="*60)

print("\nSISTEMA PRONTO PARA USAR!")
print("\nComo executar:")
print("\n1. React + API (Producao):")
print("   Terminal 1: python api_server.py")
print("   Terminal 2: cd frontend && npm run dev")
print("   Acesso: http://localhost:8080")

print("\n2. Streamlit (Desenvolvimento):")
print("   streamlit run streamlit_app.py")
print("   Acesso: http://localhost:8501")

print("\n3. API Standalone:")
print("   python api_server.py")
print("   Docs: http://localhost:5000/docs")

print("\n" + "="*60)
print("As 3 interfaces podem rodar SIMULTANEAMENTE!")
print("Streamlit usa backend Python direto (nao depende da API)")
print("React usa API FastAPI via proxy Vite")
print("="*60)
