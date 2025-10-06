"""
Script de teste: 10 perguntas pré-apresentação
Testa queries críticas e mede performance
"""
import sys
import os
from pathlib import Path
import time
from datetime import datetime

# Adicionar path do projeto
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.connectivity.hybrid_adapter import HybridDataAdapter
from core.business_intelligence.direct_query_engine import DirectQueryEngine

def test_10_perguntas():
    """Executa 10 perguntas críticas e gera relatório"""

    print("\n" + "="*70)
    print("TESTE: 10 PERGUNTAS PRÉ-APRESENTAÇÃO")
    print("="*70 + "\n")

    # Inicializar adapter e engine
    print("1. Inicializando sistema...")
    try:
        adapter = HybridDataAdapter()
        engine = DirectQueryEngine(adapter)
        print(f"   [OK] Sistema inicializado - Fonte: {adapter.get_status()['current_source'].upper()}")
    except Exception as e:
        print(f"   [ERRO] ao inicializar: {e}")
        return False

    # Lista de 10 perguntas críticas
    perguntas = [
        "Produto mais vendido",
        "Top 10 produtos UNE 2720",
        "Ranking de vendas por UNE",
        "Vendas totais de cada UNE",
        "Top 10 produtos segmento TECIDOS",
        "Evolução vendas últimos 12 meses",
        "Produtos sem movimento",
        "Análise ABC",
        "Comparação de segmentos",
        "Produtos com estoque alto"
    ]

    print(f"\n2. Executando {len(perguntas)} perguntas...\n")

    resultados = []
    total_tempo = 0
    sucesso_count = 0
    erro_count = 0

    for i, pergunta in enumerate(perguntas, 1):
        print(f"   [{i}/10] Pergunta: {pergunta}")

        start_time = time.time()
        try:
            result = engine.process_query(pergunta)
            elapsed = time.time() - start_time
            total_tempo += elapsed

            # Verificar se retornou dados (DirectQueryEngine retorna type != "error")
            if result and result.get('type') != 'error':
                sucesso_count += 1
                status = "[OK]"
                # Detalhes podem estar em 'result', 'summary', ou 'title'
                summary = result.get('summary', result.get('title', 'OK'))
                detalhes = summary[:100] if summary else "Sucesso"
            else:
                erro_count += 1
                status = "[SEM DADOS]"
                detalhes = result.get('error', result.get('summary', 'Resposta vazia'))

            resultados.append({
                'pergunta': pergunta,
                'status': status,
                'tempo': elapsed,
                'detalhes': detalhes
            })

            print(f"      {status} | Tempo: {elapsed:.2f}s | {detalhes}")

        except Exception as e:
            elapsed = time.time() - start_time
            total_tempo += elapsed
            erro_count += 1
            status = "[ERRO]"
            detalhes = str(e)[:100]

            resultados.append({
                'pergunta': pergunta,
                'status': status,
                'tempo': elapsed,
                'detalhes': detalhes
            })

            print(f"      {status} | Tempo: {elapsed:.2f}s | Erro: {detalhes}")

    # Relatório final
    print("\n" + "="*70)
    print("RELATÓRIO DE TESTES")
    print("="*70 + "\n")

    print(f"RESUMO:")
    print(f"   Total de perguntas: {len(perguntas)}")
    print(f"   Sucessos: {sucesso_count}")
    print(f"   Erros/Sem dados: {erro_count}")
    print(f"   Taxa de sucesso: {(sucesso_count/len(perguntas)*100):.1f}%")
    print(f"   Tempo total: {total_tempo:.2f}s")
    print(f"   Tempo médio: {total_tempo/len(perguntas):.2f}s")

    print(f"\nPERFORMANCE:")
    tempos_ok = [r['tempo'] for r in resultados if '[OK]' in r['status']]
    if tempos_ok:
        print(f"   Mais rápida: {min(tempos_ok):.2f}s")
        print(f"   Mais lenta: {max(tempos_ok):.2f}s")
        print(f"   Média (sucessos): {sum(tempos_ok)/len(tempos_ok):.2f}s")

    print(f"\nDETALHES:")
    for i, r in enumerate(resultados, 1):
        print(f"   {i}. {r['pergunta'][:40]:40} | {r['status']} | {r['tempo']:.2f}s")

    # Verificar se passou no critério de sucesso
    print("\n" + "="*70)
    if sucesso_count >= 8 and (total_tempo / len(perguntas)) < 2.0:
        print("[OK] TESTE PASSOU!")
        print("   Criterio: >=8 sucessos + tempo medio <2s")
    else:
        print("[AVISO] TESTE PARCIAL")
        if sucesso_count < 8:
            print(f"   Sucessos: {sucesso_count}/10 (minimo: 8)")
        if (total_tempo / len(perguntas)) >= 2.0:
            print(f"   Tempo medio: {total_tempo/len(perguntas):.2f}s (maximo: 2s)")
    print("="*70 + "\n")

    # Salvar relatório
    report_path = Path(__file__).parent.parent / 'data' / 'test_reports'
    report_path.mkdir(exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_file = report_path / f"test_10_perguntas_{timestamp}.txt"

    with open(report_file, 'w', encoding='utf-8') as f:
        f.write(f"TESTE: 10 PERGUNTAS PRÉ-APRESENTAÇÃO\n")
        f.write(f"Data: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"="*70 + "\n\n")
        f.write(f"RESUMO:\n")
        f.write(f"  Total: {len(perguntas)}\n")
        f.write(f"  Sucessos: {sucesso_count}\n")
        f.write(f"  Erros: {erro_count}\n")
        f.write(f"  Taxa sucesso: {(sucesso_count/len(perguntas)*100):.1f}%\n")
        f.write(f"  Tempo total: {total_tempo:.2f}s\n")
        f.write(f"  Tempo médio: {total_tempo/len(perguntas):.2f}s\n\n")
        f.write(f"DETALHES:\n")
        for i, r in enumerate(resultados, 1):
            f.write(f"  {i}. {r['pergunta']}\n")
            f.write(f"     Status: {r['status']}\n")
            f.write(f"     Tempo: {r['tempo']:.2f}s\n")
            f.write(f"     Detalhes: {r['detalhes']}\n\n")

    print(f"Relatorio salvo: {report_file.name}")

    return sucesso_count >= 8

if __name__ == "__main__":
    success = test_10_perguntas()
    sys.exit(0 if success else 1)
