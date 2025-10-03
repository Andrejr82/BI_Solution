"""
Página de Exemplos de Perguntas de Negócio
Mostra as 80 perguntas categorizadas com opção de testar cada uma
"""

import streamlit as st
import sys
from pathlib import Path

# Adicionar diretório raiz ao path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Configuração da página
st.set_page_config(
    page_title="Exemplos de Perguntas",
    page_icon="📚",
    layout="wide"
)

# Título
st.title("📚 Exemplos de Perguntas de Negócio")
st.markdown("Explore 80 exemplos de perguntas que você pode fazer ao Agent_BI")

# Sidebar com filtros
st.sidebar.header("🔍 Filtros")
todas_categorias = [
    "Todas",
    "🎯 Vendas por Produto",
    "🏪 Análises por Segmento",
    "🏬 Análises por UNE/Loja",
    "📈 Análises Temporais",
    "💰 Performance e ABC",
    "📦 Estoque e Logística",
    "🏭 Análises por Fabricante",
    "🎨 Categoria/Grupo",
    "📊 Dashboards Executivos",
    "🔍 Análises Específicas"
]
categoria_selecionada = st.sidebar.selectbox("Categoria", todas_categorias)

# Perguntas organizadas por categoria
perguntas = {
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

# Função para enviar pergunta ao chat
def enviar_pergunta(pergunta):
    """Envia pergunta para o chat principal"""
    # Armazenar pergunta no session state para uso no chat
    st.session_state['pergunta_selecionada'] = pergunta
    st.info(f"💬 Pergunta selecionada: '{pergunta}'")
    st.info("⬅️ Volte para a página 'Chat BI' para ver a resposta")

# Estatísticas gerais
col1, col2, col3 = st.columns(3)
with col1:
    st.metric("📊 Total de Perguntas", "80")
with col2:
    st.metric("📁 Categorias", "10")
with col3:
    total_perguntas_filtradas = sum(len(perguntas[cat]) for cat in perguntas.keys() if categoria_selecionada == "Todas" or cat == categoria_selecionada)
    st.metric("🔍 Exibindo", total_perguntas_filtradas)

st.divider()

# Exibir perguntas por categoria
categorias_exibir = list(perguntas.keys()) if categoria_selecionada == "Todas" else [categoria_selecionada]

for categoria in categorias_exibir:
    if categoria not in perguntas:
        continue

    with st.expander(f"{categoria} ({len(perguntas[categoria])} perguntas)", expanded=(categoria_selecionada != "Todas")):
        for idx, pergunta in enumerate(perguntas[categoria], 1):
            col1, col2 = st.columns([5, 1])
            with col1:
                st.markdown(f"**{idx}.** {pergunta}")
            with col2:
                if st.button("🚀 Testar", key=f"{categoria}_{idx}"):
                    enviar_pergunta(pergunta)

st.divider()

# Dicas de uso
st.subheader("💡 Dicas de Uso")
col1, col2 = st.columns(2)

with col1:
    st.markdown("""
    **Como usar:**
    1. Navegue pelas categorias
    2. Clique em "🚀 Testar" para experimentar
    3. Volte ao Chat BI para ver a resposta
    4. Adapte as perguntas ao seu contexto
    """)

with col2:
    st.markdown("""
    **Personalize suas perguntas:**
    - Troque códigos de produto (ex: 369947)
    - Troque nomes de UNE (ex: SCR, MAD, 261)
    - Troque nomes de segmento (ex: TECIDOS)
    - Ajuste períodos e limites
    """)

# Footer
st.divider()
st.caption("📚 Total de 80 perguntas disponíveis | 🔄 Atualizado em 03/10/2025")
