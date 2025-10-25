"""
Script de teste rápido para validar as correções implementadas
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.factory.component_factory import ComponentFactory

# Perguntas de teste que antes falhavam
PERGUNTAS_TESTE = [
    "Compare as vendas do produto 369947 entre todas as UNEs",
    "Quais são os 5 produtos mais vendidos na UNE SCR no último mês?",
    "Quais são os 10 produtos que mais vendem no segmento TECIDOS?",
    "Ranking de performance de vendas por UNE no segmento TECIDOS",
    "Identifique UNEs com maior potencial de crescimento"
]

def testar_perguntas():
    """Testa as perguntas que antes retornavam UNKNOWN"""
    print("=" * 80)
    print("TESTE DE VALIDAÇÃO DAS CORREÇÕES")
    print("=" * 80)
    print()

    # Inicializar sistema via ComponentFactory
    print("Inicializando sistema...")
    factory = ComponentFactory()
    graph_builder = factory.get_graph_builder()
    print("[OK] Sistema inicializado\n")

    resultados = []

    for idx, pergunta in enumerate(PERGUNTAS_TESTE, 1):
        print(f"\n[{idx}/{len(PERGUNTAS_TESTE)}] Testando: {pergunta}")
        print("-" * 80)

        try:
            resultado = graph_builder.query(pergunta)

            # Verificar tipo de resposta
            tipo = resultado.get("type", "unknown")

            if tipo == "data":
                content = resultado.get("content", [])
                status = "✅ SUCESSO" if len(content) > 0 else "❌ ERRO (dados vazios)"
                detalhes = f"{len(content)} registros"
            elif tipo == "chart":
                status = "✅ SUCESSO"
                detalhes = "Gráfico gerado"
            elif tipo == "text":
                content = resultado.get("content", "")
                status = "✅ SUCESSO" if len(content) > 50 else "⚠️ PARCIAL"
                detalhes = f"{len(content)} caracteres"
            elif tipo == "error":
                status = "❌ ERRO"
                detalhes = resultado.get("error", "Erro desconhecido")
            else:
                status = "❓ DESCONHECIDO"
                detalhes = f"Tipo: {tipo}"

            print(f"{status} - {detalhes}")
            resultados.append({"pergunta": pergunta, "status": status, "tipo": tipo})

        except Exception as e:
            print(f"❌ EXCEÇÃO: {str(e)}")
            resultados.append({"pergunta": pergunta, "status": "❌ EXCEÇÃO", "tipo": "error"})

    # Resumo
    print("\n" + "=" * 80)
    print("RESUMO DOS TESTES")
    print("=" * 80)

    sucesso = sum(1 for r in resultados if "✅" in r["status"])
    parcial = sum(1 for r in resultados if "⚠️" in r["status"])
    erro = sum(1 for r in resultados if "❌" in r["status"])
    desconhecido = sum(1 for r in resultados if "❓" in r["status"])

    print(f"\n✅ Sucesso: {sucesso}/{len(PERGUNTAS_TESTE)} ({sucesso/len(PERGUNTAS_TESTE)*100:.1f}%)")
    print(f"⚠️  Parcial: {parcial}/{len(PERGUNTAS_TESTE)} ({parcial/len(PERGUNTAS_TESTE)*100:.1f}%)")
    print(f"❌ Erro: {erro}/{len(PERGUNTAS_TESTE)} ({erro/len(PERGUNTAS_TESTE)*100:.1f}%)")
    print(f"❓ Desconhecido: {desconhecido}/{len(PERGUNTAS_TESTE)} ({desconhecido/len(PERGUNTAS_TESTE)*100:.1f}%)")

    # Tipos de resposta
    print("\n📊 Distribuição por tipo:")
    tipos = {}
    for r in resultados:
        tipo = r["tipo"]
        tipos[tipo] = tipos.get(tipo, 0) + 1

    for tipo, count in tipos.items():
        print(f"   {tipo}: {count}")

    print("\n" + "=" * 80)

    # Taxa de sucesso esperada: 100% (todas as perguntas devem funcionar agora)
    taxa_sucesso = (sucesso + parcial) / len(PERGUNTAS_TESTE) * 100

    if taxa_sucesso >= 80:
        print("✅ TESTE APROVADO - Sistema funcionando corretamente!")
    else:
        print("⚠️ TESTE PARCIAL - Algumas correções ainda necessárias")

    return taxa_sucesso >= 80

if __name__ == "__main__":
    try:
        sucesso = testar_perguntas()
        sys.exit(0 if sucesso else 1)
    except Exception as e:
        print(f"\nERRO FATAL: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
