import streamlit as st
from datetime import datetime
import logging
from core.security.input_validator import validate_password_strength

logger = logging.getLogger(__name__)

# Verificação de autenticação
if st.session_state.get("authenticated"):
    st.set_page_config(
        page_title="Alterar Senha",
        page_icon="🔐",
        layout="centered"
    )

    st.markdown("<h1 class='main-header'>🔐 Alterar Senha</h1>", unsafe_allow_html=True)
    st.markdown("<p class='sub-header'>Altere sua senha de acesso ao sistema</p>", unsafe_allow_html=True)

    # Importar auth_db
    try:
        from core.database import sql_server_auth_db as auth_db
        DB_AVAILABLE = True
    except:
        DB_AVAILABLE = False

    auth_mode = st.session_state.get("auth_mode", "cloud_fallback")

    if auth_mode == "cloud_fallback":
        st.warning("⚠️ Alteração de senha não disponível no modo Cloud.")
        st.info("💡 Para alterar senha, conecte ao SQL Server ou entre em contato com o administrador.")
        st.stop()

    if not DB_AVAILABLE:
        st.error("❌ Banco de dados não disponível. Não é possível alterar a senha.")
        st.stop()

    username = st.session_state.get("username")

    st.info(f"👤 Usuário: **{username}**")

    with st.form("change_password_form"):
        st.markdown("### Digite as senhas")

        current_password = st.text_input(
            "Senha Atual",
            type="password",
            placeholder="Digite sua senha atual",
            help="Digite a senha que você usa atualmente"
        )

        new_password = st.text_input(
            "Nova Senha",
            type="password",
            placeholder="Digite a nova senha",
            help="A senha deve ter: 8+ caracteres, maiúsculas, minúsculas, números e caracteres especiais"
        )

        confirm_password = st.text_input(
            "Confirmar Nova Senha",
            type="password",
            placeholder="Digite a nova senha novamente",
            help="Confirme a nova senha"
        )

        st.markdown("---")

        col1, col2 = st.columns([1, 1])
        with col1:
            submit = st.form_submit_button("🔒 Alterar Senha", use_container_width=True, type="primary")
        with col2:
            cancel = st.form_submit_button("❌ Cancelar", use_container_width=True)

        if cancel:
            st.info("Operação cancelada.")
            st.stop()

        if submit:
            # Validações
            if not current_password:
                st.error("❌ Digite sua senha atual.")
            elif not new_password:
                st.error("❌ Digite a nova senha.")
            elif not confirm_password:
                st.error("❌ Confirme a nova senha.")
            elif new_password != confirm_password:
                st.error("❌ As senhas não coincidem.")
            elif current_password == new_password:
                st.error("❌ A nova senha deve ser diferente da atual.")
            else:
                # Validar força da senha
                is_valid, error_msg = validate_password_strength(new_password)
                if not is_valid:
                    st.error(f"❌ {error_msg}")
                    logger.warning(f"Tentativa de senha fraca para {username}: {error_msg}")
                    st.stop()
                # Verificar senha atual
                try:
                    role, erro = auth_db.autenticar_usuario(username, current_password)

                    if not role:
                        st.error("❌ Senha atual incorreta.")
                        logger.warning(f"Tentativa de alteração de senha com senha incorreta: {username}")
                    else:
                        # Alterar senha
                        try:
                            # Obter ID do usuário
                            users = auth_db.get_all_users()
                            user_data = next((u for u in users if u['username'] == username), None)

                            if user_data and user_data.get('id'):
                                # Chamar função de alteração de senha
                                success = auth_db.alterar_senha_usuario(user_data['id'], new_password)
                                if success:
                                    st.success("✅ Senha alterada com sucesso!")
                                    logger.info(f"Senha alterada com sucesso para o usuário: {username}")
                                    st.balloons()

                                    # Limpar campos
                                    st.info("🔄 Por segurança, você será desconectado. Faça login novamente com a nova senha.")
                                    import time
                                    time.sleep(2)

                                    # Logout
                                    st.session_state.clear()
                                    st.rerun()
                                else:
                                    st.error("❌ Erro ao alterar senha no banco.")
                            else:
                                st.error("❌ Alteração de senha disponível apenas com SQL Server conectado.")
                                st.info("💡 No modo Cloud, entre em contato com o administrador.")
                        except Exception as e:
                            st.error(f"❌ Erro ao alterar senha: {str(e)}")
                            logger.error(f"Erro ao alterar senha para {username}: {e}")

                except Exception as e:
                    st.error(f"❌ Erro ao verificar senha atual: {str(e)}")
                    logger.error(f"Erro ao verificar senha para {username}: {e}")

    st.markdown("---")
    st.markdown("### 💡 Dicas de Segurança")
    st.markdown("""
    - Use senhas com pelo menos 8 caracteres
    - Combine letras maiúsculas e minúsculas
    - Inclua números e caracteres especiais
    - Não compartilhe sua senha com ninguém
    - Troque sua senha regularmente
    """)

    st.markdown(
        f"<div class='footer'>Desenvolvido para Análise de Dados Caçula © {datetime.now().year}</div>",
        unsafe_allow_html=True,
    )

else:
    st.error("❌ Acesso negado. Faça login para acessar esta página.")
    st.stop()
