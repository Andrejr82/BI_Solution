"""
Teste Rápido - 100% LLM
Testa 5 perguntas usando GraphBuilder (100% LLM, ZERO DirectQueryEngine)
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Fix encoding para Windows
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

import time
from datetime import datetime

# ✅ USAR 100% LLM
from core.config.safe_settings import get_safe_settings
from core.connectivity.hybrid_adapter import HybridDataAdapter
from core.llm_adapter import GeminiLLMAdapter
from core.agents.code_gen_agent import CodeGenAgent
from core.graph.graph_builder import GraphBuilder

# 5 Perguntas para teste rápido
PERGUNTAS_TESTE = [
    "Quais são os 5 produtos mais vendidos na UNE SCR?",
    "Compare as vendas do produto 369947 entre todas as UNEs",
    "Quais são os 10 produtos que mais vendem no segmento TECIDOS?",
    "Ranking de performance de vendas por UNE no segmento TECIDOS",
    "Identifique UNEs com maior potencial de crescimento"
]

def main():
    print("=" * 80)
    print("TESTE RÁPIDO - 100% LLM (GraphBuilder)")
    print("=" * 80)
    print(f"Início: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

    # Inicializar sistema
    print("Inicializando GraphBuilder (100% LLM)...\n")

    try:
        # Configurar
        settings = get_safe_settings()

        # Criar adaptadores
        llm_adapter = GeminiLLMAdapter(
            api_key=settings.GEMINI_API_KEY,
            model_name=settings.GEMINI_MODEL_NAME
        )
        data_adapter = HybridDataAdapter()

        # Criar agente
        code_gen_agent = CodeGenAgent(
            llm_adapter=llm_adapter,
            data_adapter=data_adapter
        )

        # Criar graph builder
        graph_builder = GraphBuilder(
            llm_adapter=llm_adapter,
            parquet_adapter=data_adapter,
            code_gen_agent=code_gen_agent
        )

        # Compilar grafo
        grafo = graph_builder.build()

        print("[OK] GraphBuilder inicializado (100% LLM ativo)\n")

    except Exception as e:
        print(f"[ERRO] Falha ao inicializar: {e}")
        import traceback
        traceback.print_exc()
        return

    # Executar testes
    resultados = []
    sucesso = 0
    erro = 0

    for idx, pergunta in enumerate(PERGUNTAS_TESTE, 1):
        print(f"\n[{idx}/{len(PERGUNTAS_TESTE)}] Testando: {pergunta}")
        print("-" * 80)

        start_time = time.time()

        try:
            # ✅ Usar GraphBuilder (100% LLM)
            result_state = grafo.invoke({
                "messages": [{"role": "user", "content": pergunta}]
            })

            # Extrair resposta final
            resultado = result_state.get("final_response", {})
            elapsed = time.time() - start_time

            tipo = resultado.get("type", "unknown")

            if tipo == "data":
                content = resultado.get("content", [])
                if isinstance(content, list) and len(content) > 0:
                    print(f"✅ SUCESSO - Tipo: {tipo} - {len(content)} registros - {elapsed:.2f}s")
                    sucesso += 1
                else:
                    print(f"❌ ERRO - Dados vazios - {elapsed:.2f}s")
                    erro += 1
            elif tipo in ["chart", "text", "clarification"]:
                print(f"✅ SUCESSO - Tipo: {tipo} - {elapsed:.2f}s")
                sucesso += 1
            elif tipo == "error":
                print(f"❌ ERRO - {resultado.get('error', 'Erro desconhecido')} - {elapsed:.2f}s")
                erro += 1
            else:
                print(f"❓ DESCONHECIDO - Tipo: {tipo} - {elapsed:.2f}s")

            resultados.append({
                "pergunta": pergunta,
                "tipo": tipo,
                "sucesso": tipo in ["data", "chart", "text", "clarification"],
                "tempo": elapsed
            })

        except Exception as e:
            elapsed = time.time() - start_time
            print(f"❌ EXCEÇÃO - {str(e)[:100]} - {elapsed:.2f}s")
            erro += 1
            resultados.append({
                "pergunta": pergunta,
                "tipo": "exception",
                "sucesso": False,
                "tempo": elapsed
            })

    # Resumo
    print("\n" + "=" * 80)
    print("RESUMO DO TESTE")
    print("=" * 80)
    print(f"\n✅ Sucesso: {sucesso}/{len(PERGUNTAS_TESTE)} ({sucesso/len(PERGUNTAS_TESTE)*100:.1f}%)")
    print(f"❌ Erro: {erro}/{len(PERGUNTAS_TESTE)} ({erro/len(PERGUNTAS_TESTE)*100:.1f}%)")

    tempo_total = sum(r['tempo'] for r in resultados)
    tempo_medio = tempo_total / len(resultados) if resultados else 0
    print(f"⏱️  Tempo total: {tempo_total:.2f}s")
    print(f"⏱️  Tempo médio: {tempo_medio:.2f}s/query")

    print("\n" + "=" * 80)
    print(f"Fim: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)

    # Status final
    if sucesso == len(PERGUNTAS_TESTE):
        print("\n✅ TODOS OS TESTES PASSARAM! Sistema 100% LLM funcionando perfeitamente.\n")
        return 0
    elif sucesso >= len(PERGUNTAS_TESTE) * 0.8:
        print(f"\n⚠️  MAIORIA DOS TESTES PASSOU ({sucesso}/{len(PERGUNTAS_TESTE)}). Verifique os erros.\n")
        return 1
    else:
        print(f"\n❌ MUITOS TESTES FALHARAM ({erro}/{len(PERGUNTAS_TESTE)}). Revisão necessária.\n")
        return 1

if __name__ == "__main__":
    try:
        exit_code = main()
        sys.exit(exit_code or 0)
    except Exception as e:
        print(f"\n❌ ERRO FATAL: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
