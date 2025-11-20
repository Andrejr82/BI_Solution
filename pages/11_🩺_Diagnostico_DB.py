"""
Módulo para pages/9_Diagnostico_DB.py. Define componentes da interface de utilizador (UI).
"""

import streamlit as st
import logging

# Verificar se é admin
if st.session_state.get("role") != "admin":
    st.error("❌ Acesso negado. Esta página é restrita a administradores.")
    st.stop()

st.set_page_config(
    page_title="Diagnóstico de Banco de Dados",
    page_icon="🔍",
    layout="wide"
)

st.title("🔍 Diagnóstico de Banco de Dados")
st.markdown("Verifique a conectividade com SQL Server no Streamlit Cloud")

# Carregar configurações
try:
    from core.config.safe_settings import get_safe_settings
    settings = get_safe_settings()

    st.success("✅ Módulo de configurações carregado")

    # Mostrar configurações (sem expor senhas)
    st.subheader("📋 Configurações Detectadas")

    col1, col2 = st.columns(2)

    with col1:
        st.metric("DB_SERVER", settings.DB_SERVER if settings.DB_SERVER else "❌ Não configurado")
        st.metric("DB_NAME", settings.DB_NAME if settings.DB_NAME else "❌ Não configurado")
        st.metric("DB_USER", settings.DB_USER if settings.DB_USER else "❌ Não configurado")

    with col2:
        st.metric("DB_PASSWORD", "✅ Configurado" if settings.DB_PASSWORD else "❌ Não configurado")
        st.metric("DB_DRIVER", settings.DB_DRIVER)
        st.metric("Trust Certificate", settings.DB_TRUST_SERVER_CERTIFICATE)

    # Verificar se todas as credenciais estão presentes
    st.markdown("---")
    st.subheader("🔐 Validação de Credenciais")

    credentials_complete = all([
        settings.DB_SERVER,
        settings.DB_NAME,
        settings.DB_USER,
        settings.DB_PASSWORD
    ])

    if credentials_complete:
        st.success("✅ Todas as credenciais SQL Server estão configuradas!")

        # Mostrar strings de conexão (mascaradas)
        st.subheader("🔗 Strings de Conexão")

        sql_conn = settings.get_sql_connection_string()
        pyodbc_conn = settings.get_pyodbc_connection_string()

        if sql_conn:
            # Mascarar senha na exibição
            masked_sql = sql_conn.replace(settings.DB_PASSWORD, "***")
            st.code(masked_sql, language="text")

        # Testar conectividade
        st.markdown("---")
        st.subheader("🧪 Teste de Conectividade")

        if st.button("🔌 Testar Conexão com SQL Server", type="primary"):
            with st.spinner("Testando conexão..."):
                try:
                    # Verificar se pyodbc está disponível
                    import pyodbc
                    st.info("✅ Módulo pyodbc disponível")

                    # Tentar conectar
                    conn = pyodbc.connect(pyodbc_conn, timeout=10)
                    cursor = conn.cursor()

                    # Executar query simples
                    cursor.execute("SELECT @@VERSION")
                    version = cursor.fetchone()[0]

                    st.success("✅ **Conexão estabelecida com sucesso!**")
                    st.info(f"**Versão do SQL Server:**\n\n{version[:100]}...")

                    # Listar tabelas disponíveis
                    cursor.execute("""
                        SELECT TABLE_NAME
                        FROM INFORMATION_SCHEMA.TABLES
                        WHERE TABLE_TYPE = 'BASE TABLE'
                        ORDER BY TABLE_NAME
                    """)
                    tables = [row[0] for row in cursor.fetchall()]

                    if tables:
                        st.success(f"✅ **{len(tables)} tabelas encontradas:**")
                        st.write(", ".join(tables[:10]))
                        if len(tables) > 10:
                            st.caption(f"... e mais {len(tables) - 10} tabelas")
                    else:
                        st.warning("⚠️ Nenhuma tabela encontrada no banco")

                    conn.close()

                except ImportError as e:
                    st.error(f"❌ **Módulo pyodbc não disponível**")
                    st.info("""
                    **Para habilitar SQL Server no Streamlit Cloud:**
                    1. Adicione `pyodbc` ao `requirements.txt`
                    2. Faça commit e push
                    3. Aguarde redeploy automático
                    """)

                except pyodbc.Error as e:
                    st.error(f"❌ **Erro de conexão SQL Server:**")
                    st.code(str(e))
                    st.info("""
                    **Possíveis causas:**
                    - Credenciais incorretas nos Secrets
                    - Firewall bloqueando conexão do Streamlit Cloud
                    - Servidor SQL indisponível
                    - Driver ODBC não instalado no ambiente
                    """)

                except Exception as e:
                    st.error(f"❌ **Erro inesperado:** {str(e)}")
                    logging.error(f"Erro ao testar conexão DB: {e}", exc_info=True)

    else:
        st.error("❌ Credenciais SQL Server incompletas!")
        st.warning("""
        **Para configurar no Streamlit Cloud:**

        1. Acesse as configurações do app
        2. Vá em **Secrets**
        3. Adicione as seguintes variáveis:

        ```toml
        DB_SERVER = "seu_servidor.database.windows.net"
        DB_NAME = "nome_do_banco"
        DB_USER = "usuario"
        DB_PASSWORD = "senha"
        DB_DRIVER = "ODBC Driver 17 for SQL Server"
        DB_TRUST_SERVER_CERTIFICATE = "yes"
        ```
        """)

        # Mostrar quais estão faltando
        missing = []
        if not settings.DB_SERVER:
            missing.append("DB_SERVER")
        if not settings.DB_NAME:
            missing.append("DB_NAME")
        if not settings.DB_USER:
            missing.append("DB_USER")
        if not settings.DB_PASSWORD:
            missing.append("DB_PASSWORD")

        if missing:
            st.error(f"**Faltando:** {', '.join(missing)}")

    # Modo de operação
    st.markdown("---")
    st.subheader("⚙️ Modo de Operação")

    if settings.is_database_available():
        st.success("🗄️ **Modo SQL Server** - Banco de dados disponível")
    else:
        st.info("🌤️ **Modo Cloud** - Usando autenticação hardcoded")

except ImportError as e:
    st.error(f"❌ Erro ao importar módulo de configurações: {e}")
    st.code(str(e))

except Exception as e:
    st.error(f"❌ Erro inesperado: {e}")
    logging.error(f"Erro em diagnóstico DB: {e}", exc_info=True)

# Footer
st.markdown("---")
st.caption("""
💡 **Dica:** No Streamlit Cloud, as variáveis de ambiente são configuradas através do menu **Secrets**
nas configurações do app, não através de arquivo `.env`.
""")
