"""
Página de métricas do sistema de aprendizado (Fase 1)
Apenas acessível para administradores.
"""

import streamlit as st
from core.learning.feedback_system import FeedbackSystem
from core.learning.error_analyzer import ErrorAnalyzer

st.set_page_config(page_title="Sistema de Aprendizado", page_icon="📊", layout="wide")

# Verificar autenticação
if not st.session_state.get('authenticated', False):
    st.warning("⚠️ Faça login para acessar esta página")
    st.stop()

# Apenas admin pode ver métricas
if st.session_state.get('role', '') != 'admin':
    st.warning("⚠️ Apenas administradores podem acessar esta página")
    st.stop()

st.title("📊 Sistema de Aprendizado - Fase 1")

st.info("""
**Sistema de Aprendizado LLM** implementado com:
- ✅ CodeValidator (validação automática)
- ✅ PatternMatcher (20 padrões de queries)
- ✅ FeedbackSystem (coleta de feedback)
- ✅ ErrorAnalyzer (análise de padrões)
- ✅ 130+ testes (87% coverage)
""")

# Tabs
tab1, tab2, tab3 = st.tabs(["📈 Feedback", "🐛 Erros", "📚 Padrões"])

with tab1:
    st.header("Estatísticas de Feedback")

    try:
        feedback_system = FeedbackSystem()

        col1, col2 = st.columns(2)

        with col1:
            days = st.slider("Período (dias)", 1, 30, 7)

        with col2:
            if st.button("🔄 Atualizar"):
                st.rerun()

        stats = feedback_system.get_feedback_stats(days=days)

        # Métricas principais
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric("Total de Feedbacks", stats['total'])
        with col2:
            st.metric("👍 Positivos", stats['positive'],
                     delta=f"{stats['success_rate']:.1f}%")
        with col3:
            st.metric("👎 Negativos", stats['negative'])
        with col4:
            st.metric("⚠️ Parciais", stats['partial'])

        # Gráfico de tendência
        if stats['total'] > 0:
            st.divider()
            st.subheader("📊 Taxa de Sucesso")

            import plotly.graph_objects as go

            fig = go.Figure()

            fig.add_trace(go.Indicator(
                mode="gauge+number+delta",
                value=stats['success_rate'],
                domain={'x': [0, 1], 'y': [0, 1]},
                title={'text': "Taxa de Sucesso (%)"},
                delta={'reference': 70},
                gauge={
                    'axis': {'range': [None, 100]},
                    'bar': {'color': "darkgreen"},
                    'steps': [
                        {'range': [0, 50], 'color': "lightgray"},
                        {'range': [50, 70], 'color': "yellow"},
                        {'range': [70, 85], 'color': "lightgreen"},
                        {'range': [85, 100], 'color': "green"}
                    ],
                    'threshold': {
                        'line': {'color': "red", 'width': 4},
                        'thickness': 0.75,
                        'value': 90
                    }
                }
            ))

            fig.update_layout(height=300)
            st.plotly_chart(fig, use_container_width=True)

        # Queries problemáticas
        if stats.get('problematic_queries'):
            st.divider()
            st.subheader("🔍 Queries Problemáticas")

            for query_info in stats['problematic_queries'][:10]:
                with st.expander(f"❌ {query_info['query'][:60]}..."):
                    st.write(f"**Query:** {query_info['query']}")
                    st.write(f"**Ocorrências:** {query_info['count']}")
                    st.write(f"**Feedback negativo:** {query_info.get('negative_count', 0)}")

                    if query_info.get('negative_count', 0) > 0:
                        st.warning("💡 **Sugestão:** Revisar este padrão de query para melhorar respostas futuras")
        else:
            st.success("✅ Nenhuma query problemática identificada!")

    except Exception as e:
        st.error(f"Erro ao carregar estatísticas: {e}")
        if st.checkbox("Mostrar detalhes do erro"):
            st.exception(e)

with tab2:
    st.header("Análise de Erros")

    try:
        analyzer = ErrorAnalyzer()

        days_errors = st.slider("Período para análise", 1, 30, 7, key="error_days")

        analysis = analyzer.analyze_errors(days=days_errors)

        # Estatísticas
        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric("Total de Erros", analysis['total_errors'])

        with col2:
            st.metric("Tipos de Erro", len(analysis['most_common_errors']))

        with col3:
            if analysis['total_errors'] > 0:
                avg_per_day = analysis['total_errors'] / days_errors
                st.metric("Média/Dia", f"{avg_per_day:.1f}")
            else:
                st.metric("Média/Dia", "0")

        # Erros mais comuns
        if analysis['most_common_errors']:
            st.divider()
            st.subheader("Erros Mais Frequentes")

            # Gráfico de barras
            import plotly.graph_objects as go

            error_types = [e['type'] for e in analysis['most_common_errors'][:10]]
            error_counts = [e['count'] for e in analysis['most_common_errors'][:10]]

            fig = go.Figure()
            fig.add_trace(go.Bar(
                x=error_types,
                y=error_counts,
                marker_color='indianred',
                text=error_counts,
                textposition='outside'
            ))

            fig.update_layout(
                title="Top 10 Tipos de Erro",
                xaxis_title="Tipo de Erro",
                yaxis_title="Quantidade",
                height=400
            )

            st.plotly_chart(fig, use_container_width=True)

            # Tabela detalhada
            st.subheader("Detalhes dos Erros")
            for error in analysis['most_common_errors'][:10]:
                col1, col2 = st.columns([3, 1])
                with col1:
                    st.write(f"**{error['type']}** - {error['count']} ocorrências")
                    if error.get('example_query'):
                        st.caption(f"Exemplo: {error['example_query'][:80]}...")
                with col2:
                    st.progress(error['percentage'] / 100)
                    st.caption(f"{error['percentage']:.1f}%")

        # Sugestões
        if analysis['suggested_improvements']:
            st.divider()
            st.subheader("💡 Sugestões de Melhoria")

            for suggestion in analysis['suggested_improvements']:
                priority_color = {
                    'HIGH': '🔴',
                    'MEDIUM': '🟡',
                    'LOW': '🟢'
                }.get(suggestion['priority'], '⚪')

                with st.expander(f"{priority_color} {suggestion['issue'][:60]}..."):
                    st.write(f"**Problema:** {suggestion['issue']}")
                    st.write(f"**Solução:** {suggestion['solution']}")
                    st.write(f"**Prioridade:** {suggestion['priority']}")

        # Botão para gerar relatório
        st.divider()
        col1, col2 = st.columns(2)

        with col1:
            if st.button("📄 Gerar Relatório Completo"):
                report = analyzer.generate_report(days=days_errors)
                st.download_button(
                    "⬇️ Download Relatório Markdown",
                    report,
                    f"relatorio_erros_{days_errors}d.md",
                    "text/markdown"
                )

        with col2:
            if st.button("🧹 Limpar Logs Antigos"):
                st.warning("⚠️ Funcionalidade em desenvolvimento")

        if analysis['total_errors'] == 0:
            st.success("✅ Nenhum erro registrado no período selecionado!")

    except Exception as e:
        st.error(f"Erro ao analisar erros: {e}")
        if st.checkbox("Mostrar detalhes do erro", key="error_details"):
            st.exception(e)

with tab3:
    st.header("Padrões de Queries")

    from core.learning.pattern_matcher import PatternMatcher

    try:
        matcher = PatternMatcher()
        patterns = matcher.patterns

        st.metric("Total de Padrões Cadastrados", len(patterns))

        # Filtro
        search = st.text_input("🔍 Buscar padrão", "")

        # Listar padrões
        filtered_patterns = {
            k: v for k, v in patterns.items()
            if search.lower() in k.lower() or search.lower() in str(v.get('description', '')).lower()
        } if search else patterns

        st.write(f"**Exibindo:** {len(filtered_patterns)} padrões")

        for pattern_name, pattern_data in filtered_patterns.items():
            with st.expander(f"📋 {pattern_name}"):
                st.write(f"**Descrição:** {pattern_data.get('description', 'N/A')}")

                # Keywords
                keywords = pattern_data.get('keywords', [])
                if keywords:
                    st.write("**Keywords:**")
                    st.code(", ".join(keywords))

                # Colunas sugeridas
                columns = pattern_data.get('suggested_columns', [])
                if columns:
                    st.write("**Colunas sugeridas:**")
                    st.code(", ".join(columns))

                # Exemplos
                if pattern_data.get('examples'):
                    st.write("**Exemplos:**")
                    for i, example in enumerate(pattern_data['examples'][:3], 1):
                        st.markdown(f"**{i}.** {example.get('user_query', 'N/A')}")
                        if example.get('code'):
                            with st.expander("Ver código"):
                                st.code(example.get('code', ''), language='python')

        # Estatísticas
        st.divider()
        st.subheader("📊 Estatísticas de Padrões")

        total_examples = sum(len(p.get('examples', [])) for p in patterns.values())

        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric("Total de Padrões", len(patterns))
        with col2:
            st.metric("Total de Exemplos", total_examples)
        with col3:
            avg_examples = total_examples / len(patterns) if patterns else 0
            st.metric("Média Exemplos/Padrão", f"{avg_examples:.1f}")

    except Exception as e:
        st.error(f"Erro ao carregar padrões: {e}")
        if st.checkbox("Mostrar detalhes do erro", key="pattern_details"):
            st.exception(e)

# Footer
st.divider()
col1, col2, col3 = st.columns(3)

with col1:
    st.caption("🎯 Fase 1 Completa")
with col2:
    st.caption("130+ testes | 87% coverage")
with col3:
    if st.button("📚 Ver Documentação"):
        st.info("""
        **Documentação completa:**
        - docs/FASE1_TREINAMENTO_LLM_COMPLETA.md
        - docs/GUIA_RAPIDO_FASE1.md
        - docs/TESTES_FASE1.md
        - docs/RESUMO_FINAL_COMPLETO.md
        """)

# Informações de debug para admin
with st.expander("🔧 Debug Info"):
    st.write("**Session State:**")
    st.json({
        "authenticated": st.session_state.get('authenticated', False),
        "username": st.session_state.get('username', 'N/A'),
        "role": st.session_state.get('role', 'N/A'),
        "session_id": st.session_state.get('session_id', 'N/A')[:8] + "..."
    })
