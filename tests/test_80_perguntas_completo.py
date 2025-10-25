"""
Script de Teste Completo das 80 Perguntas de Negócio
USA 100% LLM - GraphBuilder com Agent Graph (ZERO DirectQueryEngine)
Testa cada pergunta e gera relatório detalhado de cobertura
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Fix encoding para Windows
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

import time
import json
from datetime import datetime

# ✅ USAR 100% LLM - GraphBuilder
from core.config.safe_settings import get_safe_settings
from core.connectivity.hybrid_adapter import HybridDataAdapter
from core.llm_adapter import GeminiLLMAdapter
from core.agents.code_gen_agent import CodeGenAgent
from core.graph.graph_builder import GraphBuilder

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
        "Identifique UNEs com maior potencial de crescimento",
        "UNEs com maior diversidade de produtos vendidos",
        "Análise de concentração: dependência de produtos específicos por UNE",
        "UNEs com melhor desempenho em produtos promocionais",
        "Comparativo de eficiência de vendas entre UNEs similares"
    ],
    "📈 Análises Temporais": [
        "Análise de sazonalidade: quais meses vendem mais no segmento FESTAS?",
        "Tendência de vendas dos últimos 6 meses por categoria",
        "Identifique produtos com padrão de vendas decrescente",
        "Quais produtos tiveram pico de vendas no último mês?",
        "Produtos com ciclo de vendas consistente vs irregular",
        "Impacto sazonal por segmento: comparativo ano vs ano",
        "Previsão de vendas baseada no histórico dos últimos 12 meses",
        "Produtos que precisam de ação comercial urgente (tendência negativa)"
    ],
    "💰 Performance e ABC": [
        "Produtos classificados como ABC 'A' no segmento TECIDOS",
        "Análise ABC: distribuição de produtos por classificação",
        "Migração ABC: produtos que mudaram de classificação",
        "Produtos ABC 'C' com potencial para 'B'",
        "Produtos com maior frequency de vendas nas últimas 5 semanas",
        "Top 10 produtos por média de vendas semanal",
        "Produtos com vendas regulares vs esporádicas",
        "Análise de consistência: produtos vendidos em todas as semanas"
    ],
    "📦 Estoque e Logística": [
        "Produtos com estoque baixo vs alta demanda",
        "Análise de ponto de pedido: produtos próximos ao limite",
        "Produtos com maior leadtime vs performance de vendas",
        "Identificar produtos com excesso de estoque",
        "Produtos com maior rotação de estoque",
        "Análise de exposição: produtos com exposição mínima vs vendas",
        "Produtos pendentes de solicitação há mais de X dias",
        "Eficiência logística: relação entre estoque CD vs vendas"
    ],
    "🏭 Análises por Fabricante": [
        "Ranking de fabricantes por volume de vendas",
        "Compare performance de diferentes fabricantes no segmento TECIDOS",
        "Fabricantes com maior diversidade de produtos",
        "Análise de concentração: dependência de fabricantes específicos",
        "Fabricantes com produtos de maior margem",
        "Novos fabricantes vs estabelecidos: performance comparativa",
        "Fabricantes exclusivos vs multimarca por UNE",
        "Oportunidades de cross-selling por fabricante"
    ],
    "🎨 Categoria/Grupo": [
        "Performance por categoria dentro do segmento ARMARINHO E CONFECÇÃO",
        "Grupos de produtos com maior margem de crescimento",
        "Análise cross-selling: produtos frequentemente vendidos juntos",
        "Subgrupos mais rentáveis por segmento",
        "Categorias com menor penetração que têm potencial",
        "Gap analysis: categorias ausentes em UNEs específicas",
        "Produtos complementares com baixa correlação de vendas",
        "Oportunidades de expansão de linha por categoria"
    ],
    "📊 Dashboards Executivos": [
        "Dashboard executivo: KPIs principais por segmento",
        "Relatório de performance mensal consolidado",
        "Scorecard de vendas: top/bottom performers",
        "Métricas de eficiência operacional por UNE",
        "Alertas: produtos que precisam de atenção (baixa rotação, estoque alto)",
        "Monitor de tendências: produtos em ascensão vs declínio",
        "Relatório de exceções: performance fora do padrão",
        "Indicadores de saúde do negócio por segmento"
    ],
    "🔍 Análises Específicas": [
        "Análise de canibalização: produtos que competem entre si",
        "Impacto de promoções: antes vs durante vs depois",
        "Produtos fora de linha: análise de descontinuação",
        "Oportunidades de bundle: produtos com sinergia de vendas",
        "Produtos com risco de ruptura baseado em tendências",
        "Previsão de demanda para próximos 3 meses",
        "Simulação: impacto de mudanças de preço/exposição",
        "Análise de cenários: melhor/pior caso por produto"
    ]
}

def classificar_resultado(resultado):
    """Classifica o resultado do teste - 100% LLM"""
    if not resultado:
        return "ERROR", "Resultado vazio ou None"

    result_type = resultado.get("type", "unknown")

    # ✅ 100% LLM - Não há mais FALLBACK (tudo é processado pela LLM)
    if result_type == "error":
        return "ERROR", resultado.get("error", "Erro desconhecido")
    elif result_type == "clarification":
        return "SUCCESS", "Clarificação solicitada (interação necessária)"
    elif result_type in ["chart", "table", "text", "product_info"]:
        return "SUCCESS", f"Processado como {result_type}"
    elif result_type == "data":
        # ✅ Validar respostas tipo 'data' (DataFrames convertidos)
        content = resultado.get("content", [])
        if isinstance(content, list) and len(content) > 0:
            return "SUCCESS", f"Dados retornados: {len(content)} registros"
        else:
            return "ERROR", "Dados vazios ou inválidos"
    else:
        return "UNKNOWN", f"Tipo desconhecido: {result_type}"

def _gerar_relatorio_markdown(relatorio, resultados, stats, total_perguntas, output_file):
    """Gera relatório em formato Markdown"""

    # Calcular métricas
    taxa_sucesso = (stats['SUCCESS'] / total_perguntas * 100) if total_perguntas > 0 else 0
    taxa_erro = (stats['ERROR'] / total_perguntas * 100) if total_perguntas > 0 else 0

    # Tempo médio
    tempos = [r['tempo_processamento'] for r in resultados if r['tempo_processamento']]
    tempo_medio = sum(tempos) / len(tempos) if tempos else 0

    # Agrupar por categoria
    por_categoria = {}
    for r in resultados:
        cat = r['categoria']
        if cat not in por_categoria:
            por_categoria[cat] = {'total': 0, 'success': 0, 'error': 0, 'fallback': 0, 'unknown': 0}
        por_categoria[cat]['total'] += 1
        por_categoria[cat][r['status'].lower()] += 1

    md_content = f"""# 📊 Relatório de Teste - 80 Perguntas de Negócio

**Data:** {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}
**Versão do Sistema:** Agent Solution BI v2.0

---

## 📈 Resumo Executivo

| Métrica | Valor |
|---------|-------|
| **Total de Perguntas** | {total_perguntas} |
| **✅ Sucesso** | {stats['SUCCESS']} ({taxa_sucesso:.1f}%) |
| **❌ Erros** | {stats['ERROR']} ({taxa_erro:.1f}%) |
| **⚠️ Fallback** | {stats['FALLBACK']} ({stats['FALLBACK']/total_perguntas*100:.1f}%) |
| **❓ Desconhecido** | {stats['UNKNOWN']} ({stats['UNKNOWN']/total_perguntas*100:.1f}%) |
| **⏱️ Tempo Médio** | {tempo_medio:.2f}s |

---

## 🎯 Performance por Categoria

"""

    # Adicionar tabela por categoria
    md_content += "| Categoria | Total | ✅ Sucesso | ❌ Erro | ⚠️ Fallback | ❓ Desconhecido | Taxa Sucesso |\n"
    md_content += "|-----------|-------|------------|---------|-------------|----------------|-------------|\n"

    for cat, metrics in por_categoria.items():
        taxa_cat = (metrics['success'] / metrics['total'] * 100) if metrics['total'] > 0 else 0
        # Limpar emojis da categoria para a tabela
        cat_clean = cat.split(']')[1].strip() if ']' in cat else cat
        md_content += f"| {cat_clean} | {metrics['total']} | {metrics['success']} | {metrics['error']} | {metrics['fallback']} | {metrics['unknown']} | {taxa_cat:.1f}% |\n"

    md_content += "\n---\n\n## 📝 Resultados Detalhados\n\n"

    # Agrupar resultados por categoria
    categoria_atual = None
    for r in resultados:
        if r['categoria'] != categoria_atual:
            categoria_atual = r['categoria']
            md_content += f"\n### {categoria_atual}\n\n"

        # Ícone baseado no status
        icone = "✅" if r['status'] == "SUCCESS" else "❌" if r['status'] == "ERROR" else "⚠️" if r['status'] == "FALLBACK" else "❓"

        md_content += f"#### {icone} [{r['id']}/{total_perguntas}] {r['pergunta']}\n\n"
        md_content += f"- **Status:** `{r['status']}`\n"
        md_content += f"- **Tipo:** `{r['tipo_resultado']}`\n"
        md_content += f"- **Mensagem:** {r['mensagem']}\n"
        md_content += f"- **Tempo:** {r['tempo_processamento']:.2f}s\n"

        if r['status'] == 'ERROR':
            md_content += f"- **⚠️ Erro:** `{r['mensagem']}`\n"

        md_content += "\n"

    md_content += "---\n\n## 🔍 Análise de Erros\n\n"

    # Listar todos os erros
    erros = [r for r in resultados if r['status'] == 'ERROR']
    if erros:
        md_content += f"**Total de Erros:** {len(erros)}\n\n"
        for erro in erros:
            md_content += f"- **[{erro['id']}]** {erro['pergunta']}\n"
            md_content += f"  - Erro: `{erro['mensagem'][:200]}`\n\n"
    else:
        md_content += "✅ **Nenhum erro encontrado!**\n\n"

    md_content += "---\n\n## ⚠️ Perguntas que Requerem Fallback (LLM)\n\n"

    # Listar fallbacks
    fallbacks = [r for r in resultados if r['status'] == 'FALLBACK']
    if fallbacks:
        md_content += f"**Total de Fallbacks:** {len(fallbacks)}\n\n"
        for fb in fallbacks:
            md_content += f"- **[{fb['id']}]** {fb['pergunta']}\n"
    else:
        md_content += "✅ **Nenhum fallback necessário!**\n\n"

    # === NOVA SEÇÃO: Análise de Performance Detalhada ===
    md_content += "---\n\n## ⚡ Análise de Performance Detalhada\n\n"

    # Calcular métricas de performance
    tempos = [r.get('tempo_execucao', 0) for r in resultados if r.get('tempo_execucao')]
    if tempos:
        tempo_min = min(tempos)
        tempo_max = max(tempos)
        tempo_p50 = sorted(tempos)[len(tempos)//2] if tempos else 0
        tempo_p90 = sorted(tempos)[int(len(tempos)*0.9)] if tempos else 0

        md_content += "### 📊 Estatísticas de Tempo de Resposta\n\n"
        md_content += "| Métrica | Valor |\n"
        md_content += "|---------|-------|\n"
        md_content += f"| **Mínimo** | {tempo_min:.2f}s |\n"
        md_content += f"| **Médio** | {tempo_medio:.2f}s |\n"
        md_content += f"| **Mediana (P50)** | {tempo_p50:.2f}s |\n"
        md_content += f"| **P90** | {tempo_p90:.2f}s |\n"
        md_content += f"| **Máximo** | {tempo_max:.2f}s |\n\n"

        # Queries mais lentas
        queries_lentas = sorted(resultados, key=lambda x: x.get('tempo_execucao', 0), reverse=True)[:5]
        md_content += "### 🐌 Top 5 Queries Mais Lentas\n\n"
        md_content += "| Rank | Query | Tempo | Status |\n"
        md_content += "|------|-------|-------|--------|\n"
        for idx, q in enumerate(queries_lentas, 1):
            tempo = q.get('tempo_execucao', 0)
            pergunta = q.get('pergunta', '')[:60] + '...' if len(q.get('pergunta', '')) > 60 else q.get('pergunta', '')
            status = q.get('status', 'UNKNOWN')
            md_content += f"| {idx} | {pergunta} | {tempo:.2f}s | {status} |\n"

        # Queries mais rápidas
        queries_rapidas = sorted(resultados, key=lambda x: x.get('tempo_execucao', 0))[:5]
        md_content += "\n### ⚡ Top 5 Queries Mais Rápidas\n\n"
        md_content += "| Rank | Query | Tempo | Status |\n"
        md_content += "|------|-------|-------|--------|\n"
        for idx, q in enumerate(queries_rapidas, 1):
            tempo = q.get('tempo_execucao', 0)
            pergunta = q.get('pergunta', '')[:60] + '...' if len(q.get('pergunta', '')) > 60 else q.get('pergunta', '')
            status = q.get('status', 'UNKNOWN')
            md_content += f"| {idx} | {pergunta} | {tempo:.2f}s | {status} |\n"

        md_content += "\n"

    md_content += "---\n\n## 📊 Distribuição de Tipos de Resposta\n\n"

    # Contar tipos
    tipos = {}
    for r in resultados:
        tipo = r['tipo_resultado'] or 'null'
        tipos[tipo] = tipos.get(tipo, 0) + 1

    md_content += "| Tipo | Quantidade | Percentual |\n"
    md_content += "|------|------------|------------|\n"
    for tipo, count in sorted(tipos.items(), key=lambda x: x[1], reverse=True):
        perc = (count / total_perguntas * 100) if total_perguntas > 0 else 0
        md_content += f"| `{tipo}` | {count} | {perc:.1f}% |\n"

    md_content += f"\n---\n\n## 🎯 Conclusões\n\n"

    if taxa_sucesso >= 90:
        md_content += "### ✅ **EXCELENTE!**\n\n"
        md_content += f"O sistema alcançou {taxa_sucesso:.1f}% de taxa de sucesso, demonstrando alta confiabilidade.\n\n"
    elif taxa_sucesso >= 70:
        md_content += "### ✅ **BOM**\n\n"
        md_content += f"O sistema alcançou {taxa_sucesso:.1f}% de taxa de sucesso. Há espaço para melhorias.\n\n"
    elif taxa_sucesso >= 50:
        md_content += "### ⚠️ **REGULAR**\n\n"
        md_content += f"O sistema alcançou {taxa_sucesso:.1f}% de taxa de sucesso. Correções necessárias.\n\n"
    else:
        md_content += "### ❌ **CRÍTICO**\n\n"
        md_content += f"O sistema alcançou apenas {taxa_sucesso:.1f}% de taxa de sucesso. Revisão urgente necessária.\n\n"

    md_content += "### Recomendações:\n\n"

    if stats['ERROR'] > 0:
        md_content += f"1. ⚠️ Investigar e corrigir {stats['ERROR']} erros identificados\n"

    if stats['UNKNOWN'] > 0:
        md_content += f"2. 🔍 Classificar {stats['UNKNOWN']} respostas de tipo desconhecido\n"

    if stats['FALLBACK'] > 0:
        md_content += f"3. 💡 Otimizar {stats['FALLBACK']} queries que requerem fallback para LLM\n"

    if tempo_medio > 5:
        md_content += f"4. ⏱️ Otimizar performance (tempo médio: {tempo_medio:.2f}s)\n"

    md_content += "\n---\n\n"
    md_content += f"**Relatório gerado automaticamente pelo Agent Solution BI**  \n"
    md_content += f"*Timestamp: {relatorio['metadata']['timestamp']}*\n"

    # Salvar arquivo
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(md_content)

def executar_teste():
    """Executa o teste completo das 80 perguntas - 100% LLM"""
    print("=" * 80)
    print("TESTE COMPLETO DAS 80 PERGUNTAS - 100% LLM (GraphBuilder)")
    print("=" * 80)
    print(f"Início: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

    # ✅ Inicializar sistema com 100% LLM
    print("Inicializando GraphBuilder (100% LLM)...")

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
        print(f"[ERRO] Falha ao inicializar GraphBuilder: {e}")
        import traceback
        traceback.print_exc()
        return None

    # Resultados
    resultados = []
    stats = {
        "SUCCESS": 0,
        "ERROR": 0,
        "FALLBACK": 0,
        "UNKNOWN": 0
    }

    total_perguntas = sum(len(perguntas) for perguntas in PERGUNTAS.values())
    contador = 0

    # Processar cada categoria
    for categoria, perguntas in PERGUNTAS.items():
        # Tratamento de encoding para Windows - manter emojis se possível
        try:
            print(f"\n{'=' * 80}")
            print(f"[CATEGORIA] {categoria}")
            print(f"{'=' * 80}")
        except UnicodeEncodeError:
            # Fallback: remover emojis se o terminal não suportar
            categoria_clean = categoria.encode('ascii', 'ignore').decode('ascii').strip()
            if not categoria_clean:
                categoria_clean = "Categoria sem nome"
            print(f"\n{'=' * 80}")
            print(f"[CATEGORIA] {categoria_clean}")
            print(f"{'=' * 80}")

        for idx, pergunta in enumerate(perguntas, 1):
            contador += 1
            print(f"\n[{contador}/{total_perguntas}] Testando: {pergunta[:70]}...")

            start_time = time.time()
            try:
                # ✅ Usar GraphBuilder (100% LLM)
                result_state = grafo.invoke({
                    "messages": [{"role": "user", "content": pergunta}]
                })

                # Extrair resposta final
                resultado = result_state.get("final_response", {})
                elapsed = time.time() - start_time

                status, mensagem = classificar_resultado(resultado)
                stats[status] += 1

                # Exibir resultado
                icon = "[OK]" if status == "SUCCESS" else "[ERROR]" if status == "ERROR" else "[FALLBACK]" if status == "FALLBACK" else "[?]"
                print(f"{icon} {status}: {mensagem} ({elapsed:.2f}s)")

                # Armazenar resultado
                resultados.append({
                    "id": contador,
                    "categoria": categoria,
                    "pergunta": pergunta,
                    "status": status,
                    "mensagem": mensagem,
                    "tipo_resultado": resultado.get("type") if resultado else None,
                    "tempo_processamento": elapsed,
                    "timestamp": datetime.now().isoformat()
                })

            except Exception as e:
                elapsed = time.time() - start_time
                stats["ERROR"] += 1
                print(f"[ERROR] EXCEPTION: {str(e)[:100]} ({elapsed:.2f}s)")

                resultados.append({
                    "id": contador,
                    "categoria": categoria,
                    "pergunta": pergunta,
                    "status": "ERROR",
                    "mensagem": str(e),
                    "tipo_resultado": None,
                    "tempo_processamento": elapsed,
                    "timestamp": datetime.now().isoformat()
                })

    # Estatísticas finais
    print(f"\n\n{'=' * 80}")
    print("ESTATÍSTICAS FINAIS")
    print(f"{'=' * 80}")
    print(f"Total de perguntas testadas: {total_perguntas}")
    print(f"[OK] Sucesso (SUCCESS):        {stats['SUCCESS']} ({stats['SUCCESS']/total_perguntas*100:.1f}%)")
    print(f"[>>] Fallback necessario:      {stats['FALLBACK']} ({stats['FALLBACK']/total_perguntas*100:.1f}%)")
    print(f"[XX] Erros (ERROR):            {stats['ERROR']} ({stats['ERROR']/total_perguntas*100:.1f}%)")
    print(f"[??] Desconhecido (UNKNOWN):   {stats['UNKNOWN']} ({stats['UNKNOWN']/total_perguntas*100:.1f}%)")

    # Salvar relatório JSON
    relatorio = {
        "metadata": {
            "timestamp": datetime.now().isoformat(),
            "total_perguntas": total_perguntas,
            "total_categorias": len(PERGUNTAS)
        },
        "estatisticas": stats,
        "resultados": resultados
    }

    # Salvar relatório no diretório tests
    output_dir = Path(__file__).parent
    timestamp_str = datetime.now().strftime('%Y%m%d_%H%M%S')

    # Salvar JSON
    output_file_json = output_dir / f"relatorio_teste_80_perguntas_{timestamp_str}.json"
    with open(output_file_json, 'w', encoding='utf-8') as f:
        json.dump(relatorio, f, ensure_ascii=False, indent=2)

    # Salvar Markdown
    output_file_md = output_dir / f"relatorio_teste_80_perguntas_{timestamp_str}.md"
    _gerar_relatorio_markdown(relatorio, resultados, stats, total_perguntas, output_file_md)

    print(f"\n[SAVE] Relatorio JSON salvo em: {output_file_json}")
    print(f"[SAVE] Relatorio MD salvo em: {output_file_md}")

    # Mostrar perguntas que falharam
    if stats['ERROR'] > 0:
        print(f"\n\n{'=' * 80}")
        print("PERGUNTAS COM ERRO")
        print(f"{'=' * 80}")
        for r in resultados:
            if r['status'] == 'ERROR':
                print(f"\n[ERROR] [{r['id']}] {r['pergunta']}")
                print(f"   Erro: {r['mensagem'][:100]}")

    # Mostrar perguntas que precisam fallback
    if stats['FALLBACK'] > 0:
        print(f"\n\n{'=' * 80}")
        print("PERGUNTAS QUE PRECISAM FALLBACK (LLM)")
        print(f"{'=' * 80}")
        for r in resultados:
            if r['status'] == 'FALLBACK':
                print(f"\n[FALLBACK] [{r['id']}] {r['pergunta']}")

    print(f"\n{'=' * 80}")
    print(f"Fim: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'=' * 80}\n")

    return relatorio

if __name__ == "__main__":
    relatorio = executar_teste()
