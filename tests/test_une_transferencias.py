"""
Testes para ferramentas de transferências UNE
Valida as novas funcionalidades de validação e sugestão de transferências
"""

import sys
from pathlib import Path

# Adicionar diretório raiz ao path
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.tools.une_tools import (
    validar_transferencia_produto,
    sugerir_transferencias_automaticas
)


def test_validar_transferencia():
    """Testa validação de transferência de produto"""
    print("\n" + "="*70)
    print("TESTE 1: Validacao de Transferencia")
    print("="*70)

    # Testar com produto real da base (produto 2172 existe em UNEs 2599 e 2720)
    resultado = validar_transferencia_produto.invoke({
        "produto_id": 2172,
        "une_origem": 2599,
        "une_destino": 2720,
        "quantidade": 1
    })

    print(f"\nResultado da validação:")
    print(f"  Válido: {resultado.get('valido', False)}")

    if resultado.get('valido'):
        print(f"  Prioridade: {resultado['prioridade']}")
        print(f"  Score: {resultado['score_prioridade']}/100")
        print(f"  Quantidade recomendada: {resultado['quantidade_recomendada']}")
        print(f"  Motivo: {resultado['motivo']}")

        print(f"\n  Origem (UNE {resultado['une_origem']}):")
        origem = resultado['detalhes_origem']
        print(f"    Estoque atual: {origem['estoque_atual']:.0f}")
        print(f"    Linha verde: {origem['linha_verde']:.0f}")
        print(f"    Percentual: {origem['percentual_linha_verde']:.1f}%")
        print(f"    Após transferência: {origem['estoque_apos_transferencia']:.0f} ({origem['percentual_apos']:.1f}%)")

        print(f"\n  Destino (UNE {resultado['une_destino']}):")
        destino = resultado['detalhes_destino']
        print(f"    Estoque atual: {destino['estoque_atual']:.0f}")
        print(f"    Linha verde: {destino['linha_verde']:.0f}")
        print(f"    Percentual: {destino['percentual_linha_verde']:.1f}%")
        print(f"    Após transferência: {destino['estoque_apos_transferencia']:.0f} ({destino['percentual_apos']:.1f}%)")

        print(f"\n  Recomendações:")
        for rec in resultado.get('recomendacoes', []):
            print(f"    - {rec}")
    else:
        print(f"  Motivo: {resultado.get('motivo', 'Erro desconhecido')}")
        if 'error' in resultado:
            print(f"  Erro: {resultado['error']}")


def test_validar_transferencia_invalida():
    """Testa validação de transferência inválida"""
    print("\n" + "="*70)
    print("TESTE 2: Validacao de Transferencia Invalida (quantidade excessiva)")
    print("="*70)

    resultado = validar_transferencia_produto.invoke({
        "produto_id": 2172,
        "une_origem": 2599,
        "une_destino": 2720,
        "quantidade": 999999  # Quantidade impossível
    })

    print(f"\nResultado da validação:")
    print(f"  Válido: {resultado.get('valido', False)}")
    print(f"  Motivo: {resultado.get('motivo', 'N/A')}")

    if not resultado.get('valido'):
        print("  OK: Validacao funcionou corretamente (rejeitou transferencia invalida)")


def test_sugestoes_automaticas():
    """Testa sugestões automáticas de transferências"""
    print("\n" + "="*70)
    print("TESTE 3: Sugestoes Automaticas de Transferencias")
    print("="*70)

    resultado = sugerir_transferencias_automaticas.invoke({"limite": 10})

    if 'error' in resultado:
        print(f"\nERRO: {resultado['error']}")
        return

    total = resultado.get('total_sugestoes', 0)
    print(f"\nTotal de sugestoes geradas: {total}")

    if total == 0:
        print(f"  Mensagem: {resultado.get('mensagem', 'N/A')}")
        stats = resultado.get('estatisticas', {})
        print(f"  Produtos com excesso: {stats.get('produtos_com_excesso', 0)}")
        print(f"  Produtos com falta: {stats.get('produtos_com_falta', 0)}")
        return

    stats = resultado.get('estatisticas', {})
    print(f"\nEstatisticas:")
    print(f"  Urgentes: {stats.get('urgentes', 0)}")
    print(f"  Altas: {stats.get('altas', 0)}")
    print(f"  Normais: {stats.get('normais', 0)}")
    print(f"  Baixas: {stats.get('baixas', 0)}")
    print(f"  Total de unidades: {stats.get('total_unidades', 0)}")
    print(f"  Produtos unicos: {stats.get('produtos_unicos', 0)}")
    print(f"  UNEs origem: {stats.get('unes_origem', 0)}")
    print(f"  UNEs destino: {stats.get('unes_destino', 0)}")

    print(f"\nTop 5 Sugestoes:")
    print("-" * 70)

    for i, sug in enumerate(resultado.get('sugestoes', [])[:5], 1):
        print(f"\n{i}. Produto: {sug['nome_produto']} (ID: {sug['produto_id']})")
        print(f"   Segmento: {sug['segmento']}")
        print(f"   Transferencia: UNE {sug['une_origem']} -> UNE {sug['une_destino']}")
        print(f"   Quantidade: {sug['quantidade_sugerida']} unidades")
        print(f"   Prioridade: {sug['prioridade']} (Score: {sug['score']:.1f})")
        print(f"   Motivo: {sug['motivo']}")
        print(f"   Beneficio: {sug['beneficio_estimado']}")

        # Detalhes
        det = sug.get('detalhes', {})
        if 'origem' in det and 'destino' in det:
            origem = det['origem']
            destino = det['destino']
            print(f"   Origem: {origem['estoque']:.0f}/{origem['linha_verde']:.0f} ({origem['percentual']:.1f}% LV)")
            print(f"   Destino: {destino['estoque']:.0f}/{destino['linha_verde']:.0f} ({destino['percentual']:.1f}% LV)")


def test_validar_mesma_une():
    """Testa validação quando origem = destino (deve falhar)"""
    print("\n" + "="*70)
    print("TESTE 4: Validacao com Origem = Destino (deve falhar)")
    print("="*70)

    resultado = validar_transferencia_produto.invoke({
        "produto_id": 2172,
        "une_origem": 2599,
        "une_destino": 2599,  # Mesma UNE
        "quantidade": 10
    })

    print(f"\nResultado da validação:")
    print(f"  Válido: {resultado.get('valido', False)}")
    print(f"  Erro esperado: {resultado.get('error', 'N/A')}")

    if not resultado.get('valido') and 'nao podem ser iguais' in resultado.get('error', ''):
        print("  OK: Validacao funcionou corretamente")


def main():
    """Executa todos os testes"""
    print("\n" + "="*70)
    print("TESTES DE FERRAMENTAS DE TRANSFERENCIAS UNE")
    print("="*70)

    try:
        # Teste 1: Validacao basica
        test_validar_transferencia()

        # Teste 2: Validacao com quantidade invalida
        test_validar_transferencia_invalida()

        # Teste 3: Sugestoes automaticas
        test_sugestoes_automaticas()

        # Teste 4: Mesma UNE origem/destino
        test_validar_mesma_une()

        print("\n" + "="*70)
        print("OK: TODOS OS TESTES CONCLUIDOS")
        print("="*70 + "\n")

    except Exception as e:
        print(f"\nERRO durante execucao dos testes: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
