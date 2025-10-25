"""
Script de Teste REAL das 80 Perguntas - Usando GraphBuilder
Este teste replica exatamente o que acontece no Streamlit
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import time
import json
from datetime import datetime
import os

# Carregar variáveis de ambiente
try:
    from dotenv import load_dotenv
    env_file = Path(__file__).parent.parent / '.env'
    if env_file.exists():
        load_dotenv(env_file)
        print(f"[INFO] Variáveis carregadas de {env_file}")
except ImportError:
    print("[WARN] python-dotenv não instalado")

# Importar sistema REAL usado no Streamlit
from core.graph.graph_builder import GraphBuilder
from core.factory.component_factory import ComponentFactory
from core.connectivity.parquet_adapter import ParquetAdapter
from langchain_core.messages import HumanMessage

# 80 Perguntas organizadas por categoria
PERGUNTAS = {
    "🎯 Vendas por Produto": [
        "Gere um gráfico de vendas do produto 369947 na UNE SCR",
        "Mostre a evolução de vendas mensais do produto 369947 nos últimos 12 meses",
        "Compare as vendas do produto 369947 entre todas as UNEs",
        "Quais são os 5 produtos mais vendidos na UNE SCR no último mês?",
        "Análise de performance: produtos com vendas acima da média no segmento TECIDOS",
        "Identifique produtos com variação de vendas superior a 20% mês a mês",
        "Top 10 produtos por margem de crescimento nos últimos 3 meses",
        "Produtos com padrão de vendas sazonal no segmento FESTAS"
    ],
    "🏪 Análises por Segmento": [
        "Quais são os 10 produtos que mais vendem no segmento TECIDOS?",
        "Compare as vendas entre os segmentos ARMARINHO E CONFECÇÃO vs TECIDOS",
        "Ranking dos segmentos por volume de vendas no último trimestre",
        "Qual segmento teve maior crescimento percentual mês a mês?",
        "Distribuição de vendas por categoria dentro do segmento PAPELARIA",
        "Segmentos com maior concentração de produtos ABC 'A'",
        "Análise de penetração: quantos produtos únicos vendidos por segmento",
        "Segmentos mais afetados por sazonalidade"
    ],
    "🏬 Análises por UNE/Loja": [
        "Ranking de performance de vendas por UNE no segmento TECIDOS",
        "Qual UNE vende mais produtos do segmento PAPELARIA?",
        "Compare a performance da UNE SCR vs outras UNEs principais",
        "Identifique UNEs com maior potencial de crescimento"
    ]
    # Reduzindo para 20 perguntas iniciais para teste rápido
}

def classificar_resultado(resultado, tempo_processamento):
    """Classifica o resultado REAL do sistema"""
    if not resultado:
        return "ERROR", "Resposta vazia ou None", None

    # Analisar resposta do GraphBuilder
    result_type = resultado.get("type", "unknown")

    if result_type == "error":
        error_msg = resultado.get("error", "Erro desconhecido")
        return "ERROR", f"Erro: {error_msg}", None

    elif result_type == "chart":
        chart_data = resultado.get("chart_data", {})
        if chart_data:
            return "SUCCESS", f"Gráfico gerado com dados", "chart"
        else:
            return "ERROR", "Gráfico sem dados", None

    elif result_type == "table":
        data = resultado.get("data", [])
        if data:
            return "SUCCESS", f"Tabela com {len(data)} registros", "table"
        else:
            return "ERROR", "Tabela vazia", None

    elif result_type == "text":
        content = resultado.get("content", "")
        if len(content) > 50:
            return "SUCCESS", f"Resposta textual ({len(content)} chars)", "text"
        else:
            return "PARTIAL", "Resposta textual curta", "text"

    else:
        return "UNKNOWN", f"Tipo desconhecido: {result_type}", None

def executar_teste():
    """Executa o teste REAL usando GraphBuilder"""
    print("=" * 80)
    print("TESTE REAL DAS PERGUNTAS - USANDO GRAPHBUILDER (SISTEMA STREAMLIT)")
    print("=" * 80)
    print(f"Início: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

    # Inicializar sistema REAL (igual ao Streamlit)
    print("Inicializando GraphBuilder...")

    try:
        # Obter LLM adapter
        llm_adapter = ComponentFactory.get_llm_adapter("gemini")
        print("[OK] LLM Adapter: Gemini")

        # Usar HybridDataAdapter (igual ao Streamlit)
        from core.connectivity.hybrid_adapter import HybridDataAdapter

        data_adapter = HybridDataAdapter()
        adapter_status = data_adapter.get_status()
        print(f"[OK] Data Adapter: {adapter_status['current_source'].upper()}")

        # Para compatibilidade, criar alias
        parquet_adapter = data_adapter

        # Criar CodeGenAgent (necessário para o GraphBuilder)
        from core.agents.code_gen_agent import CodeGenAgent
        code_gen_agent = CodeGenAgent(llm_adapter=llm_adapter, data_adapter=parquet_adapter)
        print(f"[OK] CodeGenAgent inicializado")

        # Criar GraphBuilder (igual ao Streamlit)
        graph_builder = GraphBuilder(
            llm_adapter=llm_adapter,
            parquet_adapter=parquet_adapter,
            code_gen_agent=code_gen_agent
        )
        agent_graph = graph_builder.build()
        print("[OK] GraphBuilder inicializado\n")

    except Exception as e:
        print(f"[ERRO] Falha ao inicializar: {e}")
        import traceback
        traceback.print_exc()
        return None

    # Resultados
    resultados = []
    stats = {
        "SUCCESS": 0,
        "ERROR": 0,
        "PARTIAL": 0,
        "UNKNOWN": 0,
        "TIMEOUT": 0
    }

    tipos_resposta = {
        "chart": 0,
        "table": 0,
        "text": 0
    }

    total_perguntas = sum(len(perguntas) for perguntas in PERGUNTAS.values())
    contador = 0

    # Processar cada categoria
    for categoria, perguntas in PERGUNTAS.items():
        # Tratamento de encoding
        try:
            print(f"\n{'=' * 80}")
            print(f"[CATEGORIA] {categoria}")
            print(f"{'=' * 80}")
        except UnicodeEncodeError:
            categoria_clean = categoria.encode('ascii', 'ignore').decode('ascii').strip()
            print(f"\n{'=' * 80}")
            print(f"[CATEGORIA] {categoria_clean}")
            print(f"{'=' * 80}")

        for idx, pergunta in enumerate(perguntas, 1):
            contador += 1
            print(f"\n[{contador}/{total_perguntas}] Testando: {pergunta[:70]}...")

            start_time = time.time()
            try:
                # Processar EXATAMENTE como no Streamlit
                initial_state = {
                    "messages": [HumanMessage(content=pergunta)]
                }

                # Invocar o grafo (sistema real)
                final_state = agent_graph.invoke(initial_state)
                elapsed = time.time() - start_time

                # Extrair resposta
                response = final_state.get("final_response", {})

                status, mensagem, tipo = classificar_resultado(response, elapsed)
                stats[status] += 1

                if tipo:
                    tipos_resposta[tipo] = tipos_resposta.get(tipo, 0) + 1

                # Exibir resultado
                icon = "[OK]" if status == "SUCCESS" else "[ERROR]" if status == "ERROR" else "[PARTIAL]" if status == "PARTIAL" else "[?]"
                print(f"{icon} {status}: {mensagem} ({elapsed:.2f}s)")

                # Debug: mostrar detalhes da resposta
                if status != "SUCCESS":
                    print(f"   Debug: {response}")

                # Armazenar resultado
                resultados.append({
                    "id": contador,
                    "categoria": categoria,
                    "pergunta": pergunta,
                    "status": status,
                    "mensagem": mensagem,
                    "tipo_resposta": tipo,
                    "tempo_processamento": elapsed,
                    "timestamp": datetime.now().isoformat(),
                    "resposta_completa": response
                })

            except Exception as e:
                elapsed = time.time() - start_time

                # Verificar se foi timeout
                if elapsed > 60:
                    stats["TIMEOUT"] += 1
                    status = "TIMEOUT"
                else:
                    stats["ERROR"] += 1
                    status = "ERROR"

                print(f"[{status}] EXCEPTION: {str(e)[:100]} ({elapsed:.2f}s)")

                # Debug completo
                import traceback
                print(f"   Traceback: {traceback.format_exc()[:200]}")

                resultados.append({
                    "id": contador,
                    "categoria": categoria,
                    "pergunta": pergunta,
                    "status": status,
                    "mensagem": str(e),
                    "tipo_resposta": None,
                    "tempo_processamento": elapsed,
                    "timestamp": datetime.now().isoformat(),
                    "resposta_completa": None
                })

    # Estatísticas finais
    print(f"\n\n{'=' * 80}")
    print("ESTATÍSTICAS FINAIS")
    print(f"{'=' * 80}")
    print(f"Total de perguntas testadas: {total_perguntas}")
    print(f"[OK] Sucesso (SUCCESS):        {stats['SUCCESS']} ({stats['SUCCESS']/total_perguntas*100:.1f}%)")
    print(f"[~]  Parcial (PARTIAL):        {stats['PARTIAL']} ({stats['PARTIAL']/total_perguntas*100:.1f}%)")
    print(f"[XX] Erros (ERROR):            {stats['ERROR']} ({stats['ERROR']/total_perguntas*100:.1f}%)")
    print(f"[TO] Timeout:                  {stats['TIMEOUT']} ({stats['TIMEOUT']/total_perguntas*100:.1f}%)")
    print(f"[??] Desconhecido (UNKNOWN):   {stats['UNKNOWN']} ({stats['UNKNOWN']/total_perguntas*100:.1f}%)")

    print(f"\n{'=' * 80}")
    print("TIPOS DE RESPOSTA")
    print(f"{'=' * 80}")
    for tipo, count in tipos_resposta.items():
        print(f"{tipo.upper():10} : {count} ({count/total_perguntas*100:.1f}%)")

    # Salvar relatório JSON
    relatorio = {
        "metadata": {
            "timestamp": datetime.now().isoformat(),
            "total_perguntas": total_perguntas,
            "total_categorias": len(PERGUNTAS),
            "sistema": "GraphBuilder (Sistema Real Streamlit)",
            "modo": "100% Sistema Real"
        },
        "estatisticas": {
            **stats,
            "tipos_resposta": tipos_resposta
        },
        "resultados": resultados
    }

    # Salvar relatório
    output_dir = Path(__file__).parent
    output_file = output_dir / f"relatorio_teste_REAL_80_perguntas_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(relatorio, f, ensure_ascii=False, indent=2)

    print(f"\n[SAVE] Relatorio salvo em: {output_file}")

    # Mostrar perguntas que falharam
    if stats['ERROR'] > 0:
        print(f"\n\n{'=' * 80}")
        print("PERGUNTAS COM ERRO")
        print(f"{'=' * 80}")
        for r in resultados:
            if r['status'] == 'ERROR':
                print(f"\n[ERROR] [{r['id']}] {r['pergunta']}")
                print(f"   Erro: {r['mensagem'][:100]}")

    print(f"\n{'=' * 80}")
    print(f"Fim: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'=' * 80}\n")

    return relatorio

if __name__ == "__main__":
    relatorio = executar_teste()
