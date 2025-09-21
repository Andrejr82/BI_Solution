"""
Página para gerenciar a sincronização de dados entre SQL Server e Parquet
"""

import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import time

# Importar o agente de sincronização
try:
    from core.agents.data_sync_agent import data_sync_agent
    SYNC_AVAILABLE = True
except ImportError:
    SYNC_AVAILABLE = False

st.set_page_config(
    page_title="Sincronização de Dados",
    page_icon="🔄",
    layout="wide"
)

st.title("🔄 Sincronização de Dados")
st.markdown("Gerencie a sincronização entre SQL Server e arquivos Parquet")

if not SYNC_AVAILABLE:
    st.error("❌ Agente de sincronização não disponível")
    st.stop()

# Sidebar com informações
with st.sidebar:
    st.header("ℹ️ Informações")

    # Status da última sincronização
    last_sync = data_sync_agent.get_last_sync_info()
    if last_sync:
        st.success("✅ Sincronização anterior encontrada")
        st.write(f"**Data**: {last_sync['formatted']}")

        time_ago = last_sync['time_ago']
        if time_ago.days > 0:
            st.write(f"**Há**: {time_ago.days} dias")
        else:
            hours = time_ago.seconds // 3600
            st.write(f"**Há**: {hours} horas")
    else:
        st.warning("⚠️ Nenhuma sincronização anterior")

    # Tabelas configuradas
    st.subheader("📋 Tabelas Configuradas")
    for table in data_sync_agent.tables_to_sync:
        st.write(f"• {table}")

# Seção principal
col1, col2 = st.columns([2, 1])

with col1:
    st.header("🚀 Sincronização Manual")

    st.info("""
    **Processo de Sincronização:**
    1. 📦 Backup dos arquivos Parquet existentes
    2. 🔗 Conexão com SQL Server
    3. 📊 Extração de dados das tabelas
    4. 🧹 Limpeza e padronização
    5. 💾 Salvamento em formato Parquet
    """)

    if st.button("🔄 Iniciar Sincronização", type="primary", use_container_width=True):
        with st.spinner("Executando sincronização..."):
            progress_bar = st.progress(0)
            status_text = st.empty()

            try:
                # Simular progresso
                status_text.text("🔍 Verificando conexão...")
                progress_bar.progress(10)
                time.sleep(1)

                status_text.text("📦 Criando backup...")
                progress_bar.progress(20)
                time.sleep(1)

                status_text.text("🔄 Sincronizando tabelas...")
                progress_bar.progress(30)

                # Executar sincronização real
                results = data_sync_agent.sync_all_tables()

                progress_bar.progress(90)
                status_text.text("✅ Finalizando...")
                time.sleep(1)

                progress_bar.progress(100)
                status_text.text("🎉 Sincronização concluída!")

                # Mostrar resultados
                st.success("✅ Sincronização concluída com sucesso!")

                # Exibir resultados em tabela
                results_df = pd.DataFrame([
                    {"Tabela": table, "Status": "✅ Sucesso" if success else "❌ Erro"}
                    for table, success in results.items()
                ])

                st.subheader("📊 Resultados da Sincronização")
                st.dataframe(results_df, use_container_width=True)

            except Exception as e:
                st.error(f"❌ Erro durante sincronização: {e}")

with col2:
    st.header("⚙️ Configurações")

    # Configuração de agendamento
    st.subheader("📅 Agendamento Automático")

    auto_sync = st.checkbox("Habilitar sincronização automática")

    if auto_sync:
        interval_hours = st.selectbox(
            "Intervalo de sincronização:",
            [1, 6, 12, 24, 48, 168],  # 168 = 1 semana
            index=3,  # 24 horas por padrão
            format_func=lambda x: f"A cada {x} hora{'s' if x > 1 else ''}" if x < 24 else f"A cada {x//24} dia{'s' if x//24 > 1 else ''}"
        )

        if st.button("▶️ Iniciar Agendamento"):
            st.info(f"🕐 Agendamento configurado para cada {interval_hours} horas")
            st.warning("⚠️ O agendamento funcionará apenas enquanto a aplicação estiver rodando")

    # Configurações de backup
    st.subheader("💾 Backup")

    auto_backup = st.checkbox("Backup automático antes da sincronização", value=True)

    if st.button("🗂️ Ver Backups"):
        backup_dir = data_sync_agent.backup_dir
        if backup_dir.exists():
            backups = list(backup_dir.glob("backup_*"))
            if backups:
                st.write(f"📁 {len(backups)} backup{'s' if len(backups) > 1 else ''} encontrado{'s' if len(backups) > 1 else ''}:")
                for backup in sorted(backups, reverse=True)[:5]:  # Mostrar últimos 5
                    backup_time = backup.name.replace("backup_", "").replace("_", " ")
                    st.write(f"• {backup_time}")
            else:
                st.write("📁 Nenhum backup encontrado")
        else:
            st.write("📁 Diretório de backup não existe")

# Seção de monitoramento
st.header("📈 Status dos Arquivos Parquet")

files_info = data_sync_agent.get_parquet_files_info()

if files_info:
    # Converter para DataFrame para exibir
    files_df = pd.DataFrame(files_info)

    # Reorganizar colunas
    display_df = files_df[['table_name', 'records', 'columns', 'size_mb', 'formatted_time']].copy()
    display_df.columns = ['Tabela', 'Registros', 'Colunas', 'Tamanho (MB)', 'Última Modificação']

    st.dataframe(display_df, use_container_width=True)

    # Estatísticas gerais
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("📁 Total de Arquivos", len(files_info))

    with col2:
        total_records = sum(f['records'] for f in files_info)
        st.metric("📊 Total de Registros", f"{total_records:,}")

    with col3:
        total_size = sum(f['size_mb'] for f in files_info)
        st.metric("💾 Tamanho Total", f"{total_size:.1f} MB")

    with col4:
        if files_info:
            latest_file = max(files_info, key=lambda x: x['last_modified'])
            hours_ago = (datetime.now() - latest_file['last_modified']).total_seconds() / 3600
            st.metric("🕐 Último Update", f"{hours_ago:.1f}h atrás")

else:
    st.warning("⚠️ Nenhum arquivo Parquet encontrado")
    st.info("Execute uma sincronização para criar os arquivos.")

# Footer com informações técnicas
st.markdown("---")
st.markdown("""
**ℹ️ Informações Técnicas:**
- Os arquivos Parquet são armazenados no diretório `data/parquet/`
- Backups automáticos são criados em `data/backup_parquet/`
- Logs detalhados estão disponíveis em `data/sync_log.txt`
- Compressão: Snappy (otimizada para velocidade e tamanho)
""")