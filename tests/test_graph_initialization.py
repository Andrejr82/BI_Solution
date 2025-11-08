#!/usr/bin/env python3
"""
Teste simples de inicialização do GraphBuilder.
Verifica se o módulo langgraph.checkpoint.sqlite está disponível.
"""

import sys
import os

# Adicionar o diretório raiz ao path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

print("="*60)
print("TESTE DE INICIALIZACAO DO GRAPHBUILDER")
print("="*60)

try:
    print("\n1. Testando import de langgraph.checkpoint.sqlite...")
    from langgraph.checkpoint.sqlite import SqliteSaver
    print("   OK: SqliteSaver importado com sucesso")
    print(f"   Classe: {SqliteSaver}")

    print("\n2. Testando import do GraphBuilder...")
    from core.graph.graph_builder import GraphBuilder
    print("   OK: GraphBuilder importado com sucesso")
    print(f"   Classe: {GraphBuilder}")

    print("\n3. Testando criacao de instancia do SqliteSaver...")
    # Criar um SqliteSaver em memória para teste
    checkpointer = SqliteSaver.from_conn_string(":memory:")
    print("   OK: SqliteSaver criado em memoria")
    print(f"   Instancia: {checkpointer}")

    print("\n" + "="*60)
    print("TODOS OS TESTES PASSARAM!")
    print("="*60)
    print("\nO sistema esta pronto para usar o GraphBuilder com SqliteSaver.")
    print("O erro 'No module named langgraph.checkpoint.sqlite' foi RESOLVIDO.")

except ImportError as e:
    print(f"\n   ERRO: {e}")
    print("\n" + "="*60)
    print("TESTE FALHOU!")
    print("="*60)
    sys.exit(1)
except Exception as e:
    print(f"\n   ERRO INESPERADO: {e}")
    print("\n" + "="*60)
    print("TESTE FALHOU!")
    print("="*60)
    sys.exit(1)
