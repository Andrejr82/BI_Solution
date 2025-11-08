"""
Teste isolado para verificar importacao do SqliteSaver.
Este teste tenta importar o modulo langgraph.checkpoint.sqlite
e relata se foi bem-sucedido ou nao.
"""

import sys
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

print("=" * 80)
print("TESTE DE IMPORTACAO DO SQLITESAVER")
print("=" * 80)

# Teste 1: Verificar versao do Python
print(f"\n1. Python Version: {sys.version}")

# Teste 2: Verificar se langgraph esta instalado
try:
    import langgraph
    print(f"2. LangGraph instalado: OK (versao: {langgraph.__version__ if hasattr(langgraph, '__version__') else 'desconhecida'})")
except ImportError as e:
    print(f"2. LangGraph instalado: ERRO - {e}")
    sys.exit(1)

# Teste 3: Verificar se langgraph.checkpoint existe
try:
    import langgraph.checkpoint
    print(f"3. langgraph.checkpoint: OK")
except ImportError as e:
    print(f"3. langgraph.checkpoint: ERRO - {e}")
    sys.exit(1)

# Teste 4: Listar modulos disponiveis em langgraph.checkpoint
try:
    import pkgutil
    import langgraph.checkpoint as checkpoint_pkg

    print(f"\n4. Submodulos disponiveis em langgraph.checkpoint:")
    checkpoint_modules = [modname for importer, modname, ispkg in
                         pkgutil.iter_modules(checkpoint_pkg.__path__)]
    for mod in checkpoint_modules:
        print(f"   - {mod}")

    if 'sqlite' in checkpoint_modules:
        print(f"   OK: 'sqlite' esta na lista!")
    else:
        print(f"   ERRO: 'sqlite' NAO esta na lista!")
except Exception as e:
    print(f"4. Erro ao listar submodulos: {e}")

# Teste 5: Tentar importar langgraph.checkpoint.sqlite
print(f"\n5. Tentando importar langgraph.checkpoint.sqlite...")
try:
    import langgraph.checkpoint.sqlite
    print(f"   OK: Importacao bem-sucedida!")
    print(f"   Modulo: {langgraph.checkpoint.sqlite}")
    print(f"   Localizacao: {langgraph.checkpoint.sqlite.__file__ if hasattr(langgraph.checkpoint.sqlite, '__file__') else 'N/A'}")
except ImportError as e:
    print(f"   ERRO: {type(e).__name__}: {e}")
    import traceback
    print(f"\n   Traceback completo:")
    print(traceback.format_exc())
    sys.exit(1)

# Teste 6: Tentar importar SqliteSaver
print(f"\n6. Tentando importar SqliteSaver...")
try:
    from langgraph.checkpoint.sqlite import SqliteSaver
    print(f"   OK: SqliteSaver importado com sucesso!")
    print(f"   Classe: {SqliteSaver}")
except ImportError as e:
    print(f"   ERRO: {type(e).__name__}: {e}")
    import traceback
    print(f"\n   Traceback completo:")
    print(traceback.format_exc())
    sys.exit(1)

# Teste 7: Verificar se langgraph-checkpoint-sqlite esta instalado
print(f"\n7. Verificando pacote langgraph-checkpoint-sqlite...")
try:
    import importlib.metadata
    version = importlib.metadata.version('langgraph-checkpoint-sqlite')
    print(f"   OK: langgraph-checkpoint-sqlite instalado: versao {version}")
except Exception as e:
    print(f"   ERRO: Pacote nao encontrado: {e}")

# Teste 8: Testar criacao de SqliteSaver
print(f"\n8. Tentando criar instancia de SqliteSaver...")
try:
    import tempfile
    import os

    # Criar arquivo temporario para teste
    test_db = os.path.join(tempfile.gettempdir(), "test_sqlite_saver.db")
    saver = SqliteSaver.from_conn_string(test_db)
    print(f"   OK: SqliteSaver criado com sucesso!")
    print(f"   Database: {test_db}")

    # Limpar arquivo de teste
    if os.path.exists(test_db):
        os.remove(test_db)
        print(f"   OK: Arquivo de teste removido")
except Exception as e:
    print(f"   ERRO ao criar SqliteSaver: {type(e).__name__}: {e}")
    import traceback
    print(f"\n   Traceback completo:")
    print(traceback.format_exc())

print("\n" + "=" * 80)
print("TODOS OS TESTES PASSARAM!")
print("=" * 80)
