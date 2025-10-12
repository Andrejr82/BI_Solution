"""
Componente de UI para coletar feedback do usuário no Streamlit.
"""

import streamlit as st
from core.learning.feedback_system import FeedbackSystem


def render_feedback_buttons(
    query: str,
    code: str,
    result_rows: int = 0,
    session_id: str = None,
    user_id: str = None,
    key_suffix: str = ""
):
    """
    Renderiza botões de feedback (👍👎) no Streamlit.

    Args:
        query: Query original do usuário
        code: Código gerado
        result_rows: Número de linhas retornadas
        session_id: ID da sessão
        user_id: ID do usuário
        key_suffix: Sufixo para keys dos componentes Streamlit (evitar duplicatas)
    """
    # Inicializar sistema de feedback
    feedback_system = FeedbackSystem()

    # Container para feedback
    st.markdown("---")
    st.markdown("### 📊 Como foi esta resposta?")

    col1, col2, col3, col4 = st.columns([1, 1, 1, 3])

    with col1:
        if st.button("👍 Ótima", key=f"feedback_positive_{key_suffix}", use_container_width=True):
            feedback_system.record_feedback(
                query=query,
                code=code,
                feedback_type="positive",
                result_rows=result_rows,
                session_id=session_id,
                user_id=user_id
            )
            st.success("✅ Obrigado! Isso me ajuda a melhorar.")
            st.session_state[f'feedback_given_{key_suffix}'] = True

    with col2:
        if st.button("👎 Ruim", key=f"feedback_negative_{key_suffix}", use_container_width=True):
            st.session_state[f'show_comment_{key_suffix}'] = True

    with col3:
        if st.button("⚠️ Parcial", key=f"feedback_partial_{key_suffix}", use_container_width=True):
            feedback_system.record_feedback(
                query=query,
                code=code,
                feedback_type="partial",
                user_comment="Resposta parcialmente correta",
                result_rows=result_rows,
                session_id=session_id,
                user_id=user_id
            )
            st.info("✅ Feedback registrado. Continuarei melhorando!")
            st.session_state[f'feedback_given_{key_suffix}'] = True

    # Formulário para feedback negativo com comentário
    if st.session_state.get(f'show_comment_{key_suffix}', False):
        with st.form(key=f"negative_feedback_form_{key_suffix}"):
            st.write("**O que estava errado?**")
            reason = st.text_area(
                "Descreva o problema (opcional):",
                placeholder="Ex: Retornou produtos errados, faltaram dados, etc.",
                key=f"reason_text_{key_suffix}"
            )

            col_submit, col_cancel = st.columns(2)

            with col_submit:
                submitted = st.form_submit_button("Enviar", use_container_width=True)
                if submitted:
                    feedback_system.record_feedback(
                        query=query,
                        code=code,
                        feedback_type="negative",
                        user_comment=reason if reason else "Sem comentário",
                        result_rows=result_rows,
                        session_id=session_id,
                        user_id=user_id
                    )
                    st.success("✅ Obrigado pelo feedback detalhado!")
                    st.session_state[f'show_comment_{key_suffix}'] = False
                    st.session_state[f'feedback_given_{key_suffix}'] = True

            with col_cancel:
                if st.form_submit_button("Cancelar", use_container_width=True):
                    st.session_state[f'show_comment_{key_suffix}'] = False


def show_feedback_stats():
    """
    Exibe estatísticas de feedback (para admin/dashboard).
    """
    feedback_system = FeedbackSystem()

    st.markdown("## 📊 Estatísticas de Feedback")

    # Seletor de período
    days = st.selectbox(
        "Período de análise:",
        options=[7, 14, 30, 60],
        format_func=lambda x: f"Últimos {x} dias",
        index=0
    )

    # Obter estatísticas
    stats = feedback_system.get_feedback_stats(days=days)

    if stats['total'] == 0:
        st.info("Nenhum feedback registrado no período selecionado.")
        return

    # Métricas principais
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("Total de Feedbacks", stats['total'])

    with col2:
        st.metric("👍 Positivos", stats['positive'])

    with col3:
        st.metric("👎 Negativos", stats['negative'])

    with col4:
        st.metric(
            "Taxa de Sucesso",
            f"{stats['success_rate']:.1f}%",
            delta=f"{stats['success_rate'] - 70:.1f}% vs meta" if stats['success_rate'] > 0 else None
        )

    # Gráfico de distribuição
    if stats['total'] > 0:
        st.markdown("### Distribuição de Feedback")

        import plotly.graph_objects as go

        fig = go.Figure(data=[
            go.Bar(
                x=['Positivo', 'Negativo', 'Parcial'],
                y=[stats['positive'], stats['negative'], stats['partial']],
                marker_color=['green', 'red', 'orange']
            )
        ])

        fig.update_layout(
            title="Distribuição de Feedback",
            yaxis_title="Quantidade",
            height=300
        )

        st.plotly_chart(fig, use_container_width=True)

    # Problemas comuns
    if stats.get('common_issues'):
        st.markdown("### ⚠️ Problemas Relatados")
        for i, issue in enumerate(stats['common_issues'][:5], 1):
            st.text(f"{i}. {issue}")

    # Queries problemáticas
    problematic = feedback_system.get_problematic_queries(limit=10)
    if problematic:
        st.markdown("### 🔴 Queries com Mais Problemas")
        for i, query_info in enumerate(problematic, 1):
            st.write(f"{i}. \"{query_info['query']}\" - {query_info['negative_count']} feedbacks negativos")


def show_error_analysis():
    """
    Exibe análise de erros (para admin/dashboard).
    """
    from core.learning.error_analyzer import ErrorAnalyzer

    analyzer = ErrorAnalyzer()

    st.markdown("## 🔍 Análise de Erros")

    # Seletor de período
    days = st.selectbox(
        "Período de análise:",
        options=[7, 14, 30],
        format_func=lambda x: f"Últimos {x} dias",
        index=0,
        key="error_days"
    )

    # Obter análise
    analysis = analyzer.analyze_errors(days=days)

    if analysis['total_errors'] == 0:
        st.success("✅ Nenhum erro registrado no período!")
        return

    # Métricas
    col1, col2 = st.columns(2)

    with col1:
        st.metric("Total de Erros", analysis['total_errors'])

    with col2:
        st.metric("Tipos de Erro", len(analysis['most_common_errors']))

    # Erros mais comuns
    st.markdown("### 🔴 Erros Mais Comuns")

    for i, error in enumerate(analysis['most_common_errors'][:5], 1):
        with st.expander(f"{i}. {error['type']} - {error['count']} ocorrências ({error['percentage']:.1f}%)"):
            st.write(f"**Exemplo de query:** {error['example_query']}")
            st.code(error['example_error'][:300], language=None)

    # Sugestões de melhoria
    if analysis.get('suggested_improvements'):
        st.markdown("### 💡 Sugestões de Melhoria")

        for i, suggestion in enumerate(analysis['suggested_improvements'][:5], 1):
            priority_color = {
                'HIGH': '🔴',
                'MEDIUM': '🟡',
                'LOW': '🟢'
            }.get(suggestion['priority'], '⚪')

            st.markdown(
                f"{priority_color} **{suggestion['issue']}**  \n"
                f"*Solução:* {suggestion['solution']}  \n"
                f"*Ocorrências:* {suggestion['occurrences']}"
            )

    # Botão para gerar relatório
    if st.button("📄 Gerar Relatório Completo"):
        report = analyzer.generate_report(days=days)
        st.text_area("Relatório:", report, height=400)

        # Opção de download
        st.download_button(
            label="⬇️ Baixar Relatório",
            data=report,
            file_name=f"relatorio_erros_{days}dias.md",
            mime="text/markdown"
        )
