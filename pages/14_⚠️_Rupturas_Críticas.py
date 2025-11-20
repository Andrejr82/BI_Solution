import streamlit as st
import pandas as pd
import sys
from pathlib import Path

# Adicionar diretório raiz ao path para importações
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from core.tools.une_tools import encontrar_rupturas_criticas

# Configuração da página
st.set_page_config(
    page_title="Análise de Rupturas Críticas",
    page_icon="⚠️",
    layout="wide"
)

# Verificar autenticação
if not st.session_state.get("authenticated"):
    st.warning("⚠️ Por favor, faça login na página principal para acessar esta funcionalidade.")
    st.stop()

st.title("⚠️ Análise de Rupturas Críticas")
st.markdown("""
Esta página identifica produtos na situação mais crítica de estoque, onde o risco de indisponibilidade para o cliente final é máximo.
""")

with st.expander("O que é uma Ruptura Crítica?", expanded=True):
    st.info("""
    Uma **Ruptura Crítica** ocorre quando duas condições acontecem ao mesmo tempo:
    
    1.  **Estoque no Centro de Distribuição (CD) é zero:** Não há estoque de segurança para reposição.
    2.  **Estoque na Loja (UNE) está abaixo da Linha Verde:** A loja já está com menos produto do que o recomendado para sua operação.
    
    Essa combinação representa o maior risco para o negócio, pois a loja não tem estoque suficiente e não há de onde repor rapidamente.
    """)

st.markdown("---")

# Botão para executar a análise
if st.button("🔍 Executar Análise de Rupturas Críticas", type="primary", use_container_width=True):
    with st.spinner("Analisando todo o estoque em busca de rupturas críticas... Isso pode levar um momento."):
        try:
            # Chamar a nova ferramenta
            resultado = encontrar_rupturas_criticas.invoke({"limite": None}) # Sem limite para pegar todos os casos
            
            if resultado.get("error"):
                st.error(f"Ocorreu um erro ao executar a análise: {resultado['error']}")
            elif resultado['total_criticos'] == 0:
                st.success("✅ Nenhuma ruptura crítica encontrada!")
                st.info(resultado.get("mensagem", "Todos os produtos com estoque abaixo da linha verde nas lojas possuem cobertura no Centro de Distribuição."))
                st.balloons()
            else:
                # Guardar resultados no session_state para permitir filtragem
                st.session_state['rupturas_criticas_resultado'] = resultado
                st.rerun() # Rerun para mostrar os resultados e filtros

        except Exception as e:
            st.error(f"Falha ao chamar a ferramenta de análise: {e}")


# --- Exibição dos Resultados ---
if 'rupturas_criticas_resultado' in st.session_state:
    
    resultado = st.session_state['rupturas_criticas_resultado']
    total_criticos = resultado['total_criticos']
    produtos_criticos = resultado['produtos_criticos']
    
    st.subheader(f"📊 Resultados: {total_criticos} situações de ruptura crítica encontradas")

    df = pd.DataFrame(produtos_criticos)

    # --- Filtros ---
    st.sidebar.header("Filtros de Visualização")
    
    # Filtro por Segmento
    segmentos_unicos = sorted(df['segmento'].unique())
    segmento_selecionado = st.sidebar.multiselect(
        "Filtrar por Segmento",
        options=segmentos_unicos,
        default=[]
    )

    # Filtro por UNE
    unes_unicas = sorted(df['une_afetada_nome'].unique())
    une_selecionada = st.sidebar.multiselect(
        "Filtrar por UNE Afetada",
        options=unes_unicas,
        default=[]
    )

    # Aplicar filtros
    df_filtrado = df.copy()
    if segmento_selecionado:
        df_filtrado = df_filtrado[df_filtrado['segmento'].isin(segmento_selecionado)]
    if une_selecionada:
        df_filtrado = df_filtrado[df_filtrado['une_afetada_nome'].isin(une_selecionada)]

    st.metric("Situações Críticas Exibidas", f"{len(df_filtrado)} de {total_criticos}")

    if len(df_filtrado) == 0:
        st.warning("Nenhum resultado corresponde aos filtros selecionados.")
    else:
        # Renomear e reordenar colunas para melhor visualização
        df_display = df_filtrado.rename(columns={
            'codigo': 'Código',
            'nome_produto': 'Produto',
            'segmento': 'Segmento',
            'une_afetada_nome': 'UNE Afetada',
            'estoque_na_une': 'Estoque na UNE',
            'linha_verde_na_une': 'Linha Verde',
            'necessidade_na_une': 'Necessidade (un)',
        })
        
        # Adicionar coluna de criticidade
        df_display['Criticidade (%)'] = (df_display['Estoque na UNE'] / df_display['Linha Verde'] * 100).fillna(0)

        st.dataframe(
            df_display[[
                'Código', 'Produto', 'Segmento', 'UNE Afetada', 
                'Estoque na UNE', 'Linha Verde', 'Necessidade (un)', 'Criticidade (%)'
            ]],
            use_container_width=True,
            hide_index=True,
            column_config={
                "Necessidade (un)": st.column_config.NumberColumn(
                    "Necessidade (un)",
                    help="Quantas unidades faltam para atingir a Linha Verde.",
                    format="%d un"
                ),
                "Criticidade (%)": st.column_config.ProgressColumn(
                    "Criticidade (%)",
                    help="Percentual do estoque atual em relação à Linha Verde. Quanto menor, mais crítico.",
                    format="%.1f%%",
                    min_value=0,
                    max_value=100,
                ),
            }
        )

        # Adicionar botão de download
        csv_data = df_display.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Baixar Resultados Filtrados (CSV)",
            data=csv_data,
            file_name="rupturas_criticas_filtradas.csv",
            mime="text/csv",
            use_container_width=True
        )

    if st.button("Limpar Resultados"):
        del st.session_state['rupturas_criticas_resultado']
        st.rerun()
