"""
Verificacao Final Completa - Agent Solution BI
Certifica que tudo está integrado corretamente
"""

import os
import sys
from pathlib import Path

print("="*70)
print("VERIFICACAO FINAL - INTEGRACAO COMPLETA")
print("="*70)

verificacoes = []
avisos = []
erros = []

# ============================================================================
# 1. ARQUIVOS PRINCIPAIS
# ============================================================================
print("\n[1/10] Verificando arquivos principais...")

arquivos_principais = {
    "api_server.py": "API FastAPI",
    "streamlit_app.py": "Streamlit App",
    "start_all.py": "Launcher Principal",
    "start.bat": "Launcher Windows",
    "start.sh": "Launcher Linux/Mac",
    ".env": "Variaveis de ambiente"
}

for arquivo, descricao in arquivos_principais.items():
    if os.path.exists(arquivo):
        print(f"OK - {arquivo} ({descricao})")
        verificacoes.append(f"{descricao}: OK")
    else:
        msg = f"FALTA - {arquivo} ({descricao})"
        print(msg)
        if arquivo == ".env":
            avisos.append(msg)
        else:
            erros.append(msg)

# ============================================================================
# 2. FRONTEND REACT
# ============================================================================
print("\n[2/10] Verificando frontend React...")

frontend_files = {
    "frontend/package.json": "Package JSON",
    "frontend/vite.config.ts": "Vite Config",
    "frontend/src/App.tsx": "App principal",
    "frontend/src/main.tsx": "Entry point",
    "frontend/src/index.css": "Estilos globais"
}

for arquivo, descricao in frontend_files.items():
    if os.path.exists(arquivo):
        print(f"OK - {arquivo}")
        verificacoes.append(f"Frontend - {descricao}: OK")
    else:
        msg = f"FALTA - {arquivo}"
        print(msg)
        erros.append(msg)

# Verificar paginas
paginas = [
    "Index.tsx", "GraficosSalvos.tsx", "Monitoramento.tsx",
    "Metricas.tsx", "Exemplos.tsx", "Admin.tsx", "Ajuda.tsx",
    "Transferencias.tsx", "RelatorioTransferencias.tsx",
    "DiagnosticoDB.tsx", "GeminiPlayground.tsx", "AlterarSenha.tsx",
    "SistemaAprendizado.tsx", "NotFound.tsx"
]

paginas_encontradas = 0
for pagina in paginas:
    if os.path.exists(f"frontend/src/pages/{pagina}"):
        paginas_encontradas += 1

print(f"OK - {paginas_encontradas}/14 paginas React encontradas")
if paginas_encontradas == 14:
    verificacoes.append("Todas as 14 paginas React: OK")
else:
    avisos.append(f"Apenas {paginas_encontradas}/14 paginas encontradas")

# ============================================================================
# 3. PROXY VITE
# ============================================================================
print("\n[3/10] Verificando proxy Vite...")

if os.path.exists("frontend/vite.config.ts"):
    with open("frontend/vite.config.ts", "r", encoding="utf-8") as f:
        content = f.read()
        if "proxy" in content and "5000" in content:
            print("OK - Proxy configurado para API (port 5000)")
            verificacoes.append("Proxy Vite: OK")
        else:
            msg = "Proxy Vite nao configurado corretamente"
            print(f"AVISO - {msg}")
            avisos.append(msg)

# ============================================================================
# 4. BACKEND CORE
# ============================================================================
print("\n[4/10] Verificando backend core...")

backend_dirs = [
    "core/agents",
    "core/business_intelligence",
    "core/connectivity",
    "core/factory",
    "core/graph",
    "core/utils"
]

for dir_path in backend_dirs:
    if os.path.exists(dir_path):
        print(f"OK - {dir_path}/")
        verificacoes.append(f"Backend {dir_path}: OK")
    else:
        msg = f"FALTA - {dir_path}/"
        print(msg)
        erros.append(msg)

# ============================================================================
# 5. IMPORTS CRITICOS
# ============================================================================
print("\n[5/10] Verificando imports criticos...")

try:
    import fastapi
    print(f"OK - FastAPI v{fastapi.__version__}")
    verificacoes.append(f"FastAPI: OK (v{fastapi.__version__})")
except ImportError:
    msg = "FastAPI nao instalado"
    print(f"ERRO - {msg}")
    erros.append(msg)

try:
    import uvicorn
    print(f"OK - Uvicorn v{uvicorn.__version__}")
    verificacoes.append(f"Uvicorn: OK (v{uvicorn.__version__})")
except ImportError:
    msg = "Uvicorn nao instalado"
    print(f"ERRO - {msg}")
    erros.append(msg)

try:
    import streamlit
    print(f"OK - Streamlit v{streamlit.__version__}")
    verificacoes.append(f"Streamlit: OK (v{streamlit.__version__})")
except ImportError:
    msg = "Streamlit nao instalado"
    print(f"ERRO - {msg}")
    erros.append(msg)

# ============================================================================
# 6. API FASTAPI
# ============================================================================
print("\n[6/10] Verificando API FastAPI...")

try:
    from scripts.api_server import app
    routes = [r.path for r in app.routes]
    api_routes = [r for r in routes if r.startswith('/api')]
    print(f"OK - API carregada com {len(api_routes)} rotas /api/*")
    verificacoes.append(f"API FastAPI: OK ({len(api_routes)} endpoints)")

    # Verificar endpoints essenciais
    essenciais = ['/api/health', '/api/chat', '/api/metrics']
    for endpoint in essenciais:
        if endpoint in routes:
            print(f"OK - Endpoint {endpoint} encontrado")
        else:
            msg = f"Endpoint {endpoint} nao encontrado"
            print(f"AVISO - {msg}")
            avisos.append(msg)

except Exception as e:
    msg = f"Erro ao carregar API: {e}"
    print(f"ERRO - {msg}")
    erros.append(msg)

# ============================================================================
# 7. INTEGRACAO BACKEND
# ============================================================================
print("\n[7/10] Verificando integracao com backend...")

try:
    from core.factory.component_factory import ComponentFactory
    print("OK - ComponentFactory importado")
    verificacoes.append("ComponentFactory: OK")
except Exception as e:
    msg = f"ComponentFactory: {e}"
    print(f"ERRO - {msg}")
    erros.append(msg)

try:
    from core.connectivity.parquet_adapter import ParquetAdapter
    print("OK - ParquetAdapter importado")
    verificacoes.append("ParquetAdapter: OK")
except Exception as e:
    msg = f"ParquetAdapter: {e}"
    print(f"ERRO - {msg}")
    erros.append(msg)

try:
    from core.graph.graph_builder import GraphBuilder
    print("OK - GraphBuilder importado")
    verificacoes.append("GraphBuilder: OK")
except Exception as e:
    msg = f"GraphBuilder: {e}"
    print(f"ERRO - {msg}")
    erros.append(msg)

# ============================================================================
# 8. DOCUMENTACAO
# ============================================================================
print("\n[8/10] Verificando documentacao...")

docs = [
    "ARQUITETURA_MULTI_INTERFACE.md",
    "QUICK_START_ATUALIZADO.md",
    "RESULTADOS_TESTES.md",
    "DOCUMENTACAO_LAUNCHER.md",
    "COMO_USAR.md",
    "COMECE_AQUI.md",
    "RESUMO_FINAL_COMPLETO.md"
]

docs_encontrados = 0
for doc in docs:
    if os.path.exists(doc):
        docs_encontrados += 1

print(f"OK - {docs_encontrados}/{len(docs)} documentos encontrados")
if docs_encontrados >= 5:
    verificacoes.append(f"Documentacao: OK ({docs_encontrados} docs)")
else:
    avisos.append(f"Apenas {docs_encontrados} docs encontrados")

# ============================================================================
# 9. ESTRUTURA DE DADOS
# ============================================================================
print("\n[9/10] Verificando estrutura de dados...")

data_dirs = ["data/parquet", "data/query_history"]
for dir_path in data_dirs:
    if os.path.exists(dir_path):
        print(f"OK - {dir_path}/")
        verificacoes.append(f"{dir_path}: OK")
    else:
        msg = f"{dir_path}/ sera criado automaticamente"
        print(f"INFO - {msg}")
        avisos.append(msg)

# ============================================================================
# 10. VARIÁVEIS DE AMBIENTE
# ============================================================================
print("\n[10/10] Verificando variaveis de ambiente...")

if os.path.exists(".env"):
    from dotenv import load_dotenv
    load_dotenv()

    gemini_key = os.getenv("GEMINI_API_KEY")
    deepseek_key = os.getenv("DEEPSEEK_API_KEY")

    if gemini_key:
        print("OK - GEMINI_API_KEY configurada")
        verificacoes.append("GEMINI_API_KEY: OK")
    elif deepseek_key:
        print("OK - DEEPSEEK_API_KEY configurada")
        verificacoes.append("DEEPSEEK_API_KEY: OK")
    else:
        msg = "Nenhuma API key configurada no .env"
        print(f"AVISO - {msg}")
        avisos.append(msg)
else:
    msg = "Arquivo .env nao encontrado"
    print(f"AVISO - {msg}")
    avisos.append(msg)

# ============================================================================
# RELATORIO FINAL
# ============================================================================
print("\n" + "="*70)
print("RELATORIO FINAL DA INTEGRACAO")
print("="*70)

print(f"\nVERIFICACOES BEM-SUCEDIDAS: {len(verificacoes)}")
print(f"AVISOS: {len(avisos)}")
print(f"ERROS CRITICOS: {len(erros)}")

if erros:
    print("\n⚠ ERROS CRITICOS ENCONTRADOS:")
    for erro in erros:
        print(f"  - {erro}")

if avisos:
    print("\n⚠ AVISOS:")
    for aviso in avisos:
        print(f"  - {aviso}")

# Status final
print("\n" + "="*70)
if len(erros) == 0:
    if len(avisos) == 0:
        print("STATUS: ✓ INTEGRACAO 100% COMPLETA")
        print("\nSistema totalmente integrado e pronto para uso!")
    else:
        print("STATUS: ✓ INTEGRACAO COMPLETA COM AVISOS")
        print(f"\nSistema funcional, mas com {len(avisos)} avisos.")
        print("Avisos nao impedem o funcionamento.")
else:
    print("STATUS: ✗ INTEGRACAO INCOMPLETA")
    print(f"\n{len(erros)} erros criticos encontrados!")
    print("Corrija os erros antes de usar o sistema.")

print("="*70)

# Instrucoes finais
print("\nPROXIMOS PASSOS:")
if len(erros) == 0:
    print("  1. Execute: python start_all.py")
    print("  2. Escolha a interface desejada")
    print("  3. Comece a usar!")
else:
    print("  1. Corrija os erros listados acima")
    print("  2. Execute este script novamente")
    print("  3. Quando tudo estiver OK, execute: python start_all.py")

print("\nDOCUMENTACAO:")
print("  - COMECE_AQUI.md - Guia rapido")
print("  - COMO_USAR.md - Como usar o launcher")
print("  - RESUMO_FINAL_COMPLETO.md - Documentacao completa")

print("\n" + "="*70)

# Exit code
sys.exit(0 if len(erros) == 0 else 1)
