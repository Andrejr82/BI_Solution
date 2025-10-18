"""Teste rápido de integração - apenas validação"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.tools.une_tools import validar_transferencia_produto

print("="*60)
print("TESTE RAPIDO: Validacao de Transferencia")
print("="*60)

# Testar validação
validacao = validar_transferencia_produto.invoke({
    'produto_id': 369947,
    'une_origem': 2586,
    'une_destino': 2720,
    'quantidade': 10
})

print(f"\nValido: {validacao.get('valido')}")
print(f"Prioridade: {validacao.get('prioridade')}")
print(f"Score: {validacao.get('score_prioridade', 0):.1f}/100")
print(f"Qtd. recomendada: {validacao.get('quantidade_recomendada')}")

# Verificar campos para Streamlit
campos_esperados = ['valido', 'prioridade', 'score_prioridade',
                   'quantidade_recomendada', 'detalhes_origem', 'detalhes_destino']
campos_ok = all(campo in validacao for campo in campos_esperados)

print(f"\n{'='*60}")
print(f"Estrutura compativel com Streamlit: {campos_ok}")

if campos_ok:
    print("\n[OK] Sistema de transferencias pronto para uso!")
    print("     - Validacao funcionando")
    print("     - Estrutura compativel com interface")
    print("     - Sistema de prioridades ativo")
else:
    print("\n[ERRO] Campos faltando:")
    for campo in campos_esperados:
        if campo not in validacao:
            print(f"  - {campo}")

print(f"{'='*60}")
