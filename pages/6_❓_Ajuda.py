"""
Página de Ajuda do Agent_BI
Guia de uso, FAQ e troubleshooting
"""

import streamlit as st
import sys
from pathlib import Path

# Adicionar diretório raiz ao path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Configuração da página
st.set_page_config(
    page_title="Ajuda",
    page_icon="❓",
    layout="wide"
)

# Título
st.title("❓ Central de Ajuda - Agent_BI")
st.markdown("Aprenda a usar o Agent_BI e tire suas dúvidas")

# Tabs principais
tab1, tab2, tab3, tab4 = st.tabs(["📖 Guia Rápido", "❓ FAQ", "🔧 Troubleshooting", "📊 Dados Disponíveis"])

# TAB 1: Guia Rápido
with tab1:
    st.header("📖 Guia Rápido de Uso")

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("🚀 Primeiros Passos")
        st.markdown("""
        1. **Acesse o Chat BI** na página principal
        2. **Digite sua pergunta** em linguagem natural
        3. **Aguarde a resposta** com dados e gráficos
        4. **Explore os resultados** interativos
        5. **Salve gráficos** importantes no Dashboard
        """)

        st.subheader("💡 Dicas de Perguntas")
        st.markdown("""
        **Seja específico:**
        - ✅ "Top 10 produtos da UNE SCR"
        - ❌ "Produtos"

        **Use códigos reais:**
        - ✅ "Vendas do produto 369947"
        - ❌ "Vendas de um produto"

        **Especifique período:**
        - ✅ "Vendas no último mês"
        - ✅ "Evolução dos últimos 12 meses"
        """)

    with col2:
        st.subheader("📊 Tipos de Análises")
        st.markdown("""
        **Ranking e Comparações:**
        - Top N produtos/UNEs/segmentos
        - Comparativo entre períodos
        - Performance relativa

        **Análises Temporais:**
        - Evolução mensal
        - Sazonalidade
        - Tendências

        **Análises de Estoque:**
        - Produtos em ruptura
        - Estoque vs demanda
        - Rotação de estoque

        **Análises ABC:**
        - Classificação ABC
        - Migração de classe
        - Concentração de vendas
        """)

        st.subheader("🎯 Estrutura de Perguntas")
        st.code("""
[AÇÃO] + [MÉTRICA] + [DIMENSÃO] + [FILTRO] + [PERÍODO]

Exemplos:
- Mostre [as vendas] [do produto 369947] [na UNE SCR] [em janeiro]
- Quais [os 10 produtos] [mais vendidos] [no segmento TECIDOS]?
- Compare [vendas] [entre UNE SCR e MAD] [no último trimestre]
        """)

# TAB 2: FAQ
with tab2:
    st.header("❓ Perguntas Frequentes (FAQ)")

    faqs = [
        {
            "pergunta": "Como faço para ver produtos mais vendidos?",
            "resposta": """
            Use perguntas como:
            - "Top 10 produtos mais vendidos"
            - "Quais os 5 produtos que mais vendem?"
            - "Ranking de produtos por vendas"

            Você pode adicionar filtros:
            - "Top 10 produtos da UNE SCR"
            - "Top 5 produtos do segmento TECIDOS"
            """
        },
        {
            "pergunta": "Como especificar uma UNE?",
            "resposta": """
            Use o nome ou código da UNE:
            - "vendas na UNE SCR"
            - "produtos da une 261"
            - "performance da filial MAD"

            UNEs disponíveis: SCR, MAD, TIJ, BAR, 261, entre outras
            """
        },
        {
            "pergunta": "Como ver evolução temporal?",
            "resposta": """
            Use termos temporais:
            - "evolução dos últimos 12 meses"
            - "vendas mês a mês"
            - "histórico mensal"
            - "tendência de vendas"

            Exemplo completo:
            "Mostre a evolução de vendas do produto 369947 nos últimos 6 meses"
            """
        },
        {
            "pergunta": "Como salvar um gráfico?",
            "resposta": """
            1. Após gerar um gráfico, clique em "💾 Salvar no Dashboard"
            2. Ou clique em "📥 Download PNG/HTML" para baixar
            3. Gráficos são salvos automaticamente em `reports/charts/`
            4. Acesse o Dashboard para ver todos os gráficos salvos
            """
        },
        {
            "pergunta": "O sistema não entendeu minha pergunta. O que fazer?",
            "resposta": """
            Tente:
            1. **Reformular** a pergunta de forma mais direta
            2. **Consultar Exemplos** na página "📚 Exemplos de Perguntas"
            3. **Ser mais específico** com códigos e nomes exatos
            4. **Simplificar** - faça perguntas menores e mais diretas

            Se o problema persistir, consulte o Troubleshooting
            """
        },
        {
            "pergunta": "Quais segmentos estão disponíveis?",
            "resposta": """
            17 segmentos disponíveis:
            - TECIDOS
            - ARMARINHO E CONFECÇÃO
            - PAPELARIA
            - FESTAS
            - CAMA MESA BANHO
            - Entre outros...

            Para ver todos: "Quais segmentos estão disponíveis?"
            """
        },
        {
            "pergunta": "Como comparar UNEs?",
            "resposta": """
            Use perguntas comparativas:
            - "Compare vendas entre UNE SCR e MAD"
            - "Performance da UNE 261 vs outras UNEs"
            - "Ranking de todas as UNEs"
            """
        },
        {
            "pergunta": "Como ver análise ABC?",
            "resposta": """
            Pergunte sobre classificação ABC:
            - "Produtos classificados como ABC 'A'"
            - "Distribuição ABC de produtos"
            - "Produtos ABC 'C' com potencial"
            """
        }
    ]

    for idx, faq in enumerate(faqs, 1):
        with st.expander(f"**{idx}. {faq['pergunta']}**"):
            st.markdown(faq['resposta'])

# TAB 3: Troubleshooting
with tab3:
    st.header("🔧 Troubleshooting")

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("⚠️ Problemas Comuns")

        st.markdown("**1. 'Produto não encontrado'**")
        st.info("""
        **Causa:** Código de produto inválido ou não existe na base

        **Solução:**
        - Verifique se o código está correto (5-7 dígitos)
        - Tente buscar pelo nome do produto
        - Consulte a lista de produtos disponíveis
        """)

        st.markdown("**2. 'UNE não encontrada'**")
        st.info("""
        **Causa:** Nome/código de UNE incorreto

        **Solução:**
        - Use códigos válidos: SCR, MAD, TIJ, BAR, 261
        - Verifique maiúsculas/minúsculas
        - Tente "ranking de todas as UNEs" para ver opções
        """)

        st.markdown("**3. 'Dados não disponíveis'**")
        st.info("""
        **Causa:** Dados não carregados ou período inválido

        **Solução:**
        - Verifique se o período solicitado existe na base
        - Tente períodos mais recentes
        - Consulte "Dados Disponíveis" nesta página
        """)

    with col2:
        st.subheader("🐛 Erros Técnicos")

        st.markdown("**1. Gráfico não aparece**")
        st.info("""
        **Solução:**
        - Atualize a página (F5)
        - Limpe o cache do navegador
        - Tente uma pergunta mais simples
        """)

        st.markdown("**2. Sistema lento**")
        st.info("""
        **Solução:**
        - Aguarde consultas complexas terminarem
        - Reduza o número de registros (use Top 10 ao invés de Top 100)
        - Evite múltiplas perguntas simultâneas
        """)

        st.markdown("**3. Resposta inesperada**")
        st.info("""
        **Solução:**
        - Reformule a pergunta de forma mais clara
        - Seja mais específico nos filtros
        - Consulte exemplos de perguntas similares
        - Use modo Debug (para admins)
        """)

# TAB 4: Dados Disponíveis
with tab4:
    st.header("📊 Dados Disponíveis")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("📦 Total de Registros", "1.113.822")
        st.metric("🏬 UNEs (Lojas)", "38")
        st.metric("📁 Segmentos", "17")

    with col2:
        st.metric("🏷️ Produtos Únicos", "~50.000")
        st.metric("📅 Meses de Dados", "12")
        st.metric("📊 Colunas", "95")

    with col3:
        st.metric("🏭 Fabricantes", "~500")
        st.metric("📈 Categorias", "~200")
        st.metric("🎨 Grupos", "~100")

    st.divider()

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("📋 Campos Principais")
        st.markdown("""
        **Identificação:**
        - `codigo` - Código do produto
        - `nome_produto` - Nome do produto
        - `une` - Código da UNE
        - `une_nome` - Nome da UNE

        **Classificação:**
        - `nomesegmento` - Segmento do produto
        - `categoria` - Categoria do produto
        - `grupo` - Grupo do produto
        - `fabricante` - Fabricante

        **Vendas:**
        - `mes_01` a `mes_12` - Vendas mensais
        - `vendas_total` - Total anual
        - `abc` - Classificação ABC

        **Estoque:**
        - `estoque_atual` - Estoque disponível
        - `estoque_cd` - Estoque no CD
        - `leadtime` - Tempo de reposição
        """)

    with col2:
        st.subheader("🏬 UNEs Disponíveis")
        st.markdown("""
        **Principais UNEs:**
        - SCR - Sacomã
        - MAD - Mooca/Madeira
        - TIJ - Tijuca
        - BAR - Barra
        - 261 - Loja 261

        E mais 33 outras UNEs...

        **Segmentos Principais:**
        - TECIDOS
        - ARMARINHO E CONFECÇÃO
        - PAPELARIA
        - FESTAS
        - CAMA MESA BANHO
        - UTILIDADES DOMESTICAS

        E mais 11 outros segmentos...
        """)

    st.divider()

    st.subheader("📅 Período de Dados")
    st.info("""
    **Dados disponíveis:** 12 meses completos (mes_01 a mes_12)

    **Nota:** Os meses correspondem ao ano fiscal da empresa.
    Consulte o administrador para saber o período exato.
    """)

# Footer
st.divider()
st.markdown("""
**Precisa de mais ajuda?**
- 📚 Consulte [Exemplos de Perguntas](./5_📚_Exemplos_Perguntas)
- 💬 Entre em contato com o suporte
- 📖 Leia a documentação completa no README
""")
