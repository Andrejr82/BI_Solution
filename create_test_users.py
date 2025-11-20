
import sys
from pathlib import Path
import streamlit as st
import os

# Adicionar diretório raiz ao path
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.database import sql_server_auth_db
from core.utils.db_connection import is_database_configured

def create_test_users():
    st.set_page_config(page_title="Criar Usuários de Teste", layout="centered")
    st.title("🛠️ Criar Usuários de Teste para Segmentação")
    st.warning("⚠️ Este script deve ser executado APENAS em ambiente de desenvolvimento/teste.")

    if not is_database_configured():
        st.error("❌ O banco de dados SQL Server não está configurado. Este script só funciona com o banco de dados configurado.")
        st.info("Por favor, configure o arquivo `.env` com as credenciais do SQL Server e tente novamente.")
        return

    st.markdown("---")
    st.subheader("Usuários a serem criados:")
    st.write("- **comprador_tecidos**: Senha `123`, Papel `user`, Segmento `ARMARINHO E CONFECÇÃO`")
    st.write("- **comprador_artes**: Senha `123`, Papel `user`, Segmento `ARTESANATO`")
    st.write("- **admin_segmentos**: Senha `admin123`, Papel `admin`, Segmento `Todos` (ou `None`)")
    st.markdown("---")

    if st.button("Criar Usuários Agora", type="primary"):
        try:
            # Inicializar o banco de dados para garantir que a tabela 'usuarios' e a coluna 'segmento' existam
            sql_server_auth_db.init_db()
            st.success("✅ Banco de dados inicializado/verificado.")

            users_to_create = [
                ("comprador_tecidos", "123", "user", "ARMARINHO E CONFECÇÃO"),
                ("comprador_artes", "123", "user", "ARTESANATO"),
                ("admin_segmentos", "admin123", "admin", None) # Admin pode ver todos os segmentos
            ]

            for username, password, role, segmento in users_to_create:
                try:
                    sql_server_auth_db.criar_usuario(username, password, role, cloud_enabled=False, segmento=segmento)
                    st.success(f"✅ Usuário '{username}' ({segmento if segmento else 'Todos'}) criado com sucesso!")
                except ValueError as ve:
                    st.info(f"ℹ️ Usuário '{username}' já existe. Pulando criação. ({ve})")
                except Exception as e:
                    st.error(f"❌ Erro ao criar usuário '{username}': {e}")
            
            st.success("🎉 Processo de criação de usuários concluído!")
            st.info("Agora você pode fazer login com esses usuários para testar o isolamento de dados.")

        except Exception as e:
            st.error(f"❌ Erro geral durante a criação de usuários: {e}")
            st.warning("Certifique-se de que o SQL Server está acessível e as credenciais no `.env` estão corretas.")

if __name__ == "__main__":
    create_test_users()
