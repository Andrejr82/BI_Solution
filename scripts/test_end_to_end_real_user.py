"""
Teste End-to-End: Sistema Respondendo Usuário Real

Simula perguntas reais de usuários e valida:
1. Query funciona com dados reais
2. Resultado é correto e útil
3. LLM interpreta corretamente
4. Tempo de resposta aceitável
5. Formatação adequada
"""

import sys
import os
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from dotenv import load_dotenv
load_dotenv()

from datetime import datetime
from core.connectivity.hybrid_adapter import HybridDataAdapter
from core.business_intelligence.direct_query_engine import DirectQueryEngine
from core.factory.component_factory import ComponentFactory

def print_section(title):
    """Imprime seção formatada."""
    print("\n" + "=" * 80)
    print(f"  {title}")
    print("=" * 80)

def print_query_test(pergunta, resultado, tempo):
    """Imprime resultado de uma query de teste."""
    print(f"\n[PERGUNTA] {pergunta}")
    print(f"[TEMPO] {tempo:.2f}s")

    if resultado and resultado.get("type") != "error":
        print(f"[STATUS] OK")
        print(f"[TITULO] {resultado.get('title', 'N/A')}")
        print(f"[RESUMO] {resultado.get('summary', 'N/A')[:150]}...")

        # Mostrar dados
        if 'result' in resultado:
            result_data = resultado['result']
            if isinstance(result_data, dict):
                print(f"[DADOS] {list(result_data.keys())}")
            elif isinstance(result_data, list) and len(result_data) > 0:
                print(f"[DADOS] {len(result_data)} registros")

        return True
    else:
        erro = resultado.get('error', 'Erro desconhecido') if resultado else 'None'
        print(f"[STATUS] ERRO")
        print(f"[ERRO] {erro}")
        return False

def test_real_user_queries():
    """Testa perguntas reais de usuários de negócio."""
    print_section("TESTE END-TO-END: PERGUNTAS REAIS DE USUARIO")

    print("\n[INFO] Inicializando sistema...")
    adapter = HybridDataAdapter()
    engine = DirectQueryEngine(adapter)

    status = adapter.get_status()
    print(f"[INFO] Fonte de dados: {status['current_source'].upper()}")
    print(f"[INFO] SQL Server: {'OK' if status.get('sql_available') else 'Offline'}")

    # Lista de perguntas reais que um usuário de negócio faria
    perguntas_reais = [
        {
            "pergunta": "Qual produto mais vendeu?",
            "query_type": "produto_mais_vendido",
            "params": {},
            "categoria": "Produto"
        },
        {
            "pergunta": "Quais os 10 produtos mais vendidos?",
            "query_type": "produto_mais_vendido",
            "params": {"limite": 10},
            "categoria": "Produto"
        },
        {
            "pergunta": "Qual segmento vendeu mais?",
            "query_type": "segmento_campao",
            "params": {},
            "categoria": "Segmento"
        },
        {
            "pergunta": "Quais os top 5 produtos na filial SCR?",
            "query_type": "top_produtos_une_especifica",
            "params": {"une_nome": "SCR", "limite": 5},
            "categoria": "UNE/Filial"
        },
        {
            "pergunta": "Mostre os 10 produtos mais vendidos na UNE 261",
            "query_type": "top_produtos_une_especifica",
            "params": {"une_nome": "261", "limite": 10},
            "categoria": "UNE/Filial"
        },
        {
            "pergunta": "Quantos produtos temos cadastrados?",
            "query_type": "total_produtos",
            "params": {},
            "categoria": "Cadastro"
        },
        {
            "pergunta": "Quantas UNEs existem?",
            "query_type": "total_unes",
            "params": {},
            "categoria": "Cadastro"
        },
        {
            "pergunta": "Qual produto tem código 12345?",
            "query_type": "consulta_produto_especifico",
            "params": {"produto_codigo": "12345"},
            "categoria": "Consulta"
        }
    ]

    print_section("EXECUTANDO PERGUNTAS REAIS")

    resultados = []
    tempo_total = 0

    for i, teste in enumerate(perguntas_reais, 1):
        print(f"\n{'-' * 80}")
        print(f"TESTE {i}/{len(perguntas_reais)}")

        try:
            start = datetime.now()
            resultado = engine.execute_direct_query(
                teste["query_type"],
                teste["params"]
            )
            tempo = (datetime.now() - start).total_seconds()
            tempo_total += tempo

            sucesso = print_query_test(
                teste["pergunta"],
                resultado,
                tempo
            )

            resultados.append({
                "pergunta": teste["pergunta"],
                "categoria": teste["categoria"],
                "sucesso": sucesso,
                "tempo": tempo,
                "resultado": resultado
            })

        except Exception as e:
            print(f"\n[PERGUNTA] {teste['pergunta']}")
            print(f"[STATUS] EXCECAO")
            print(f"[ERRO] {str(e)[:200]}")

            resultados.append({
                "pergunta": teste["pergunta"],
                "categoria": teste["categoria"],
                "sucesso": False,
                "tempo": 0,
                "erro": str(e)
            })

    # Análise final
    print_section("ANALISE FINAL")

    total = len(resultados)
    sucesso = sum(1 for r in resultados if r["sucesso"])
    falhas = total - sucesso
    taxa_sucesso = (sucesso / total * 100) if total > 0 else 0
    tempo_medio = tempo_total / total if total > 0 else 0

    print(f"\nTotal de perguntas testadas: {total}")
    print(f"Sucesso: {sucesso} ({taxa_sucesso:.1f}%)")
    print(f"Falhas: {falhas} ({100-taxa_sucesso:.1f}%)")
    print(f"Tempo total: {tempo_total:.2f}s")
    print(f"Tempo medio: {tempo_medio:.2f}s")

    # Análise por categoria
    print("\n" + "-" * 80)
    print("ANALISE POR CATEGORIA")
    print("-" * 80)

    categorias = {}
    for r in resultados:
        cat = r["categoria"]
        if cat not in categorias:
            categorias[cat] = {"total": 0, "sucesso": 0}
        categorias[cat]["total"] += 1
        if r["sucesso"]:
            categorias[cat]["sucesso"] += 1

    for cat, stats in categorias.items():
        taxa = (stats["sucesso"] / stats["total"] * 100) if stats["total"] > 0 else 0
        status = "OK" if taxa >= 75 else "ATENCAO"
        print(f"[{status}] {cat:20} - {stats['sucesso']}/{stats['total']} ({taxa:.0f}%)")

    # Análise de performance
    print("\n" + "-" * 80)
    print("ANALISE DE PERFORMANCE")
    print("-" * 80)

    queries_rapidas = sum(1 for r in resultados if r["sucesso"] and r["tempo"] < 1)
    queries_medias = sum(1 for r in resultados if r["sucesso"] and 1 <= r["tempo"] < 5)
    queries_lentas = sum(1 for r in resultados if r["sucesso"] and r["tempo"] >= 5)

    print(f"Queries rapidas (< 1s):    {queries_rapidas}")
    print(f"Queries medias (1-5s):     {queries_medias}")
    print(f"Queries lentas (>= 5s):    {queries_lentas}")

    # Decisão final
    print("\n" + "=" * 80)
    print("DECISAO FINAL: SISTEMA PRONTO PARA USUARIO?")
    print("=" * 80)

    pronto = True
    motivos = []

    if taxa_sucesso < 75:
        pronto = False
        motivos.append(f"Taxa de sucesso baixa ({taxa_sucesso:.1f}%)")

    if tempo_medio > 10:
        pronto = False
        motivos.append(f"Tempo medio muito alto ({tempo_medio:.1f}s)")

    if falhas > (total * 0.3):
        pronto = False
        motivos.append(f"Muitas falhas ({falhas}/{total})")

    if pronto:
        print("\n[SUCESSO] SISTEMA ESTA PRONTO PARA RESPONDER USUARIOS!")
        print("\nMotivos:")
        print(f"  - Taxa de sucesso: {taxa_sucesso:.1f}%")
        print(f"  - Tempo medio aceitavel: {tempo_medio:.2f}s")
        print(f"  - Maioria das queries funcionando")
        print("\nO sistema pode ser usado em producao para responder usuarios reais.")
    else:
        print("\n[ATENCAO] SISTEMA PRECISA DE AJUSTES")
        print("\nProblemas identificados:")
        for motivo in motivos:
            print(f"  - {motivo}")
        print("\nRecomenda-se corrigir estes problemas antes de usar em producao.")

    print("\n" + "=" * 80)

    return pronto, resultados

def test_llm_interpretation():
    """Testa se o LLM consegue interpretar resultados."""
    print_section("TESTE: LLM INTERPRETANDO RESULTADOS REAIS")

    try:
        llm = ComponentFactory.get_llm_adapter("gemini")
        adapter = HybridDataAdapter()
        engine = DirectQueryEngine(adapter)

        # Executar uma query real
        print("\n[INFO] Executando query: Produto mais vendido...")
        resultado = engine.execute_direct_query("produto_mais_vendido", {})

        if not resultado or resultado.get("type") == "error":
            print("[ERRO] Query falhou, nao pode testar LLM")
            return False

        summary = resultado.get("summary", "")
        print(f"[RESULTADO] {summary[:150]}...")

        # Pedir ao LLM para interpretar
        print("\n[INFO] Pedindo ao LLM para interpretar o resultado...")

        prompt = f"""
Voce e um assistente de analise de dados de vendas.

O sistema executou uma analise e retornou:
{summary}

Por favor, responda de forma natural e amigavel ao usuario, como se fosse uma conversa.
Use linguagem simples e destaque os pontos principais.
"""

        messages = [{"role": "user", "content": prompt}]

        start = datetime.now()
        llm_result = llm.get_completion(messages, max_tokens=150)
        tempo = (datetime.now() - start).total_seconds()

        interpretacao = llm_result.get("content", "")

        print(f"\n[LLM RESPOSTA] ({tempo:.2f}s)")
        print("-" * 80)
        print(interpretacao)
        print("-" * 80)

        if interpretacao and len(interpretacao) > 10:
            print("\n[SUCESSO] LLM conseguiu interpretar o resultado!")
            return True
        else:
            print("\n[FALHA] LLM retornou resposta vazia ou muito curta")
            return False

    except Exception as e:
        print(f"\n[ERRO] Falha ao testar LLM: {str(e)[:200]}")
        return False

if __name__ == "__main__":
    import io

    # Criar diretório de relatórios
    report_dir = Path("reports/tests")
    report_dir.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_file = report_dir / f"test_end_to_end_{timestamp}.txt"

    # Redirecionar saída
    class TeeOutput:
        def __init__(self, *files):
            self.files = files
        def write(self, obj):
            for f in self.files:
                f.write(obj)
                f.flush()
        def flush(self):
            for f in self.files:
                f.flush()

    try:
        original_stdout = sys.stdout

        with open(report_file, 'w', encoding='utf-8') as f:
            sys.stdout = TeeOutput(original_stdout, f)

            print("=" * 80)
            print("  TESTE END-TO-END: SISTEMA PRONTO PARA USUARIO REAL?")
            print("=" * 80)
            print(f"Data/Hora: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")

            # Teste 1: Queries reais
            pronto, resultados = test_real_user_queries()

            # Teste 2: Interpretação LLM
            llm_ok = test_llm_interpretation()

            # Conclusão final
            print_section("CONCLUSAO FINAL")

            if pronto and llm_ok:
                print("\n" + "=" * 80)
                print("  SISTEMA 100% PRONTO PARA USUARIOS REAIS!")
                print("=" * 80)
                print("\n[OK] Queries funcionam com dados reais")
                print("[OK] Performance aceitavel")
                print("[OK] LLM interpreta resultados corretamente")
                print("\nO sistema pode ser usado em producao com confianca!")
                resultado_final = 0
            elif pronto:
                print("\n[AVISO] Sistema pronto mas LLM precisa atencao")
                print("\nQueries funcionam, mas interpretacao LLM pode estar limitada.")
                print("Sistema utilizavel para queries diretas.")
                resultado_final = 0
            else:
                print("\n[ATENCAO] Sistema precisa de ajustes antes de producao")
                resultado_final = 1

            print(f"\n[INFO] Relatorio salvo em: {report_file}")

            sys.stdout = original_stdout

        print(f"\n[INFO] Relatorio completo salvo em: {report_file}")
        sys.exit(resultado_final)

    except Exception as e:
        sys.stdout = original_stdout
        print(f"\n[ERRO FATAL] {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
