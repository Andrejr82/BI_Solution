"""
Teste comparativo de importacao: Streamlit vs Python normal
"""

import sys
import os

print("=" * 80)
print("DIAGNOSTICO DE AMBIENTE - STREAMLIT VS PYTHON")
print("=" * 80)

print(f"\n1. Interpretador Python:")
print(f"   {sys.executable}")

print(f"\n2. Versao Python:")
print(f"   {sys.version}")

print(f"\n3. sys.path (primeiros 10 itens):")
for i, path in enumerate(sys.path[:10]):
    print(f"   [{i}] {path}")

print(f"\n4. Verificando onde langgraph esta instalado:")
try:
    import langgraph
    if hasattr(langgraph, '__file__'):
        print(f"   langgraph: {langgraph.__file__}")
    elif hasattr(langgraph, '__path__'):
        print(f"   langgraph: {list(langgraph.__path__)}")
    else:
        print(f"   langgraph: (sem __file__ ou __path__)")
except ImportError as e:
    print(f"   ERRO: {e}")

print(f"\n5. Verificando onde langgraph.checkpoint esta instalado:")
try:
    import langgraph.checkpoint
    if hasattr(langgraph.checkpoint, '__file__'):
        print(f"   langgraph.checkpoint: {langgraph.checkpoint.__file__}")
    elif hasattr(langgraph.checkpoint, '__path__'):
        print(f"   langgraph.checkpoint: {list(langgraph.checkpoint.__path__)}")
    else:
        print(f"   langgraph.checkpoint: (sem __file__ ou __path__)")
except ImportError as e:
    print(f"   ERRO: {e}")

print(f"\n6. Listando conteudo do diretorio langgraph.checkpoint:")
try:
    import langgraph.checkpoint
    checkpoint_path = list(langgraph.checkpoint.__path__)[0]
    print(f"   Diretorio: {checkpoint_path}")

    if os.path.exists(checkpoint_path):
        files = os.listdir(checkpoint_path)
        print(f"   Arquivos/diretorios encontrados:")
        for f in files:
            full_path = os.path.join(checkpoint_path, f)
            if os.path.isdir(full_path):
                print(f"      [DIR]  {f}")
            else:
                print(f"      [FILE] {f}")
    else:
        print(f"   ERRO: Diretorio nao existe!")
except Exception as e:
    print(f"   ERRO: {e}")

print(f"\n7. Tentando importar langgraph.checkpoint.sqlite:")
try:
    import langgraph.checkpoint.sqlite
    print(f"   OK: Importacao bem-sucedida!")
    print(f"   Localizacao: {langgraph.checkpoint.sqlite.__file__ if hasattr(langgraph.checkpoint.sqlite, '__file__') else 'N/A'}")
except ImportError as e:
    print(f"   ERRO: {type(e).__name__}: {e}")

    # Diagnostico adicional
    print(f"\n   Diagnostico adicional:")
    import importlib.util
    spec = importlib.util.find_spec("langgraph.checkpoint.sqlite")
    print(f"   importlib.util.find_spec result: {spec}")

print(f"\n8. Verificando variavel de ambiente PYTHONPATH:")
pythonpath = os.environ.get('PYTHONPATH', '(nao definida)')
print(f"   PYTHONPATH: {pythonpath}")

print(f"\n9. Verificando se existe arquivo sqlite.py ou diretorio sqlite/:")
try:
    import langgraph.checkpoint
    checkpoint_path = list(langgraph.checkpoint.__path__)[0]

    sqlite_py = os.path.join(checkpoint_path, "sqlite.py")
    sqlite_dir = os.path.join(checkpoint_path, "sqlite")

    print(f"   sqlite.py existe? {os.path.exists(sqlite_py)}")
    print(f"   sqlite/ existe? {os.path.exists(sqlite_dir)}")

    if os.path.exists(sqlite_dir):
        print(f"   Conteudo de sqlite/:")
        for f in os.listdir(sqlite_dir):
            print(f"      - {f}")
except Exception as e:
    print(f"   ERRO: {e}")

print("\n" + "=" * 80)
print("FIM DO DIAGNOSTICO")
print("=" * 80)
