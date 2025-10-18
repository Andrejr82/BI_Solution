"""Teste rápido das ferramentas UNE com HybridAdapter"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.tools.une_tools import validar_transferencia_produto, sugerir_transferencias_automaticas

print("="*70)
print("TESTE: Validação de Transferência com HybridAdapter")
print("="*70)

resultado = validar_transferencia_produto.invoke({
    'produto_id': 369947,
    'une_origem': 2586,
    'une_destino': 2720,
    'quantidade': 10
})

print(f"\nValido: {resultado.get('valido')}")
print(f"Prioridade: {resultado.get('prioridade', 'N/A')}")
print(f"Score: {resultado.get('score_prioridade', 'N/A')}/100")
print(f"Quantidade recomendada: {resultado.get('quantidade_recomendada', 'N/A')}")

if resultado.get('valido'):
    print(f"\nDetalhes Origem (UNE {resultado['une_origem']}):")
    origem = resultado['detalhes_origem']
    print(f"  Estoque: {origem['estoque_atual']:.1f}")
    print(f"  Linha Verde: {origem['linha_verde']:.1f}")
    print(f"  Percentual: {origem['percentual_linha_verde']:.1f}%")

print("\n" + "="*70)
print("TESTE: Sugestões Automáticas")
print("="*70)

resultado2 = sugerir_transferencias_automaticas.invoke({'limite': 5})

print(f"\nTotal de sugestões: {resultado2.get('total_sugestoes', 0)}")

if resultado2.get('total_sugestoes', 0) > 0:
    stats = resultado2.get('estatisticas', {})
    print(f"Urgentes: {stats.get('urgentes', 0)}")
    print(f"Altas: {stats.get('altas', 0)}")
    print(f"Normais: {stats.get('normais', 0)}")

    if resultado2.get('sugestoes'):
        print(f"\nPrimeira sugestão:")
        sug = resultado2['sugestoes'][0]
        print(f"  Produto: {sug.get('nome_produto', 'N/A')[:40]}")
        print(f"  UNE {sug.get('une_origem')} -> UNE {sug.get('une_destino')}")
        print(f"  Quantidade: {sug.get('quantidade_sugerida')}")
        print(f"  Prioridade: {sug.get('prioridade')}")

print("\n" + "="*70)
print("TESTES CONCLUIDOS")
print("="*70)
