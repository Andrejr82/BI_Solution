"""
Página de Métricas do Sistema - Agent Solution BI

Esta página exibe métricas de desempenho, sucesso e cache do sistema de BI.
Permite análise de tendências e identificação de problemas de performance.

Autor: Code Agent
Data: 2025-10-18
"""

import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from core.monitoring.metrics_dashboard import MetricsDashboard

# Configuração da página
st.set_page_config(
    page_title="Métricas do Sistema",
    page_icon="📊",
    layout="wide"
)

st.title("📊 Métricas do Sistema")
st.markdown("---")

# Inicializar dashboard de métricas
try:
    dashboard = MetricsDashboard()
except Exception as e:
    st.error(f"Erro ao inicializar dashboard de métricas: {str(e)}")
    st.stop()

# Sidebar - Controles de filtro
st.sidebar.header("Filtros")
days = st.sidebar.slider(
    "Período (dias)",
    min_value=1,
    max_value=30,
    value=7,
    help="Selecione o período para análise das métricas"
)

refresh = st.sidebar.button("🔄 Atualizar Métricas")

# Obter métricas do período selecionado
try:
    metrics = dashboard.get_metrics(days=days)
except Exception as e:
    st.error(f"Erro ao obter métricas: {str(e)}")
    st.stop()

# Seção 1: Métricas Principais (KPIs)
st.subheader("📈 Indicadores Principais")

col1, col2, col3, col4 = st.columns(4)

with col1:
    success_rate = metrics.get('success_rate', 0.0)
    st.metric(
        "Taxa de Sucesso",
        f"{success_rate:.1%}",
        delta=f"{metrics.get('success_rate_delta', 0):.1%}" if 'success_rate_delta' in metrics else None,
        help="Percentual de queries executadas com sucesso"
    )

with col2:
    avg_response_time = metrics.get('avg_response_time', 0.0)
    st.metric(
        "Tempo Médio",
        f"{avg_response_time:.1f}s",
        delta=f"{metrics.get('response_time_delta', 0):.1f}s" if 'response_time_delta' in metrics else None,
        delta_color="inverse",
        help="Tempo médio de resposta das queries"
    )

with col3:
    cache_hit_rate = metrics.get('cache_hit_rate', 0.0)
    st.metric(
        "Cache Hit",
        f"{cache_hit_rate:.1%}",
        delta=f"{metrics.get('cache_hit_delta', 0):.1%}" if 'cache_hit_delta' in metrics else None,
        help="Percentual de queries servidas do cache"
    )

with col4:
    total_queries = metrics.get('total_queries', 0)
    st.metric(
        "Total Queries",
        f"{total_queries:,}",
        delta=f"{metrics.get('queries_delta', 0):+,}" if 'queries_delta' in metrics else None,
        help="Número total de queries executadas"
    )

st.markdown("---")

# Seção 2: Gráfico de Tendência de Erros
st.subheader("📉 Tendência de Erros")

if 'error_trend' in metrics and len(metrics['error_trend']) > 0:
    error_df = pd.DataFrame(metrics['error_trend'])

    # Verificar se há colunas necessárias
    if 'date' in error_df.columns and 'error_count' in error_df.columns:
        error_df['date'] = pd.to_datetime(error_df['date'])
        error_df = error_df.set_index('date')

        st.line_chart(
            error_df['error_count'],
            use_container_width=True
        )
    else:
        st.info("Dados de tendência de erros não disponíveis no formato esperado")
else:
    st.info("Nenhum erro registrado no período selecionado")

st.markdown("---")

# Seção 3: Top Queries Executadas
st.subheader("🔝 Top Queries Executadas")

if 'top_queries' in metrics and len(metrics['top_queries']) > 0:
    top_queries_df = pd.DataFrame(metrics['top_queries'])

    # Formatar DataFrame para exibição
    if not top_queries_df.empty:
        st.dataframe(
            top_queries_df,
            use_container_width=True,
            hide_index=True,
            column_config={
                "query": st.column_config.TextColumn("Query", width="large"),
                "executions": st.column_config.NumberColumn("Execuções", format="%d"),
                "avg_time": st.column_config.NumberColumn("Tempo Médio (s)", format="%.2f"),
                "success_rate": st.column_config.ProgressColumn("Taxa Sucesso", format="%.1f%%", min_value=0, max_value=100)
            }
        )
    else:
        st.info("Nenhuma query executada no período selecionado")
else:
    st.info("Dados de queries não disponíveis")

st.markdown("---")

# Seção 4: Estatísticas Detalhadas
st.subheader("📊 Estatísticas Detalhadas")

col1, col2 = st.columns(2)

with col1:
    st.write("**Performance**")
    perf_data = {
        "Métrica": ["Queries/dia", "Tempo mínimo", "Tempo máximo", "Mediana"],
        "Valor": [
            f"{metrics.get('queries_per_day', 0):.1f}",
            f"{metrics.get('min_response_time', 0):.2f}s",
            f"{metrics.get('max_response_time', 0):.2f}s",
            f"{metrics.get('median_response_time', 0):.2f}s"
        ]
    }
    st.dataframe(pd.DataFrame(perf_data), hide_index=True, use_container_width=True)

with col2:
    st.write("**Cache & Erros**")
    cache_data = {
        "Métrica": ["Cache Hits", "Cache Misses", "Total Erros", "Taxa de Erro"],
        "Valor": [
            f"{metrics.get('cache_hits', 0):,}",
            f"{metrics.get('cache_misses', 0):,}",
            f"{metrics.get('total_errors', 0):,}",
            f"{metrics.get('error_rate', 0):.2%}"
        ]
    }
    st.dataframe(pd.DataFrame(cache_data), hide_index=True, use_container_width=True)

# Footer
st.markdown("---")
st.caption(f"Última atualização: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | Período: {days} dias")
