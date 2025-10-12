"""
Módulo para pages/6_Painel_de_Administração.py. Define componentes da interface de utilizador (UI).
"""

import streamlit as st
from datetime import datetime
import logging
from core.security.input_validator import validate_password_strength, sanitize_username

# Importação condicional para funcionar no cloud
try:
    from core.database import sql_server_auth_db as auth_db
    DB_AVAILABLE = True
except Exception as e:
    logging.warning(f"Database components não disponíveis: {e}")
    DB_AVAILABLE = False

audit_logger = logging.getLogger("audit")

# --- Verificação de Autenticação e Permissão ---
if st.session_state.get("authenticated") and st.session_state.get("role") == "admin":
    # --- Configuração da Página ---
    st.set_page_config(
        page_title="Painel de Administração",
        page_icon="⚙️",
        layout="wide"
    )

    st.markdown(
        "<h1 class='main-header'>⚙️ Painel de Administração</h1>",
        unsafe_allow_html=True,
    )
    st.markdown(
        "<p class='sub-header'>Gerencie usuários, configurações e monitore o sistema.</p>",
        unsafe_allow_html=True,
    )

    # --- Tabs para organizar ---
    tab1, tab2 = st.tabs(["👥 Usuários", "🔐 Permissões"])

    with tab1:
        # --- Gerenciamento de Usuários ---
        st.subheader("👥 Gerenciamento de Usuários")

    # Adicionar Novo Usuário
    with st.expander("➕ Adicionar Novo Usuário"):
        with st.form("add_user_form"):
            new_username = st.text_input("Nome de Usuário")
            new_password = st.text_input("Senha", type="password")
            new_role = st.selectbox("Papel", ["user", "admin"])
            add_user_submitted = st.form_submit_button("Adicionar Usuário")

            if add_user_submitted:
                if not DB_AVAILABLE:
                    st.warning("⚠️ Funcionalidade não disponível no modo cloud. Use autenticação local.")
                else:
                    # Validações de segurança
                    if not new_username or not new_password:
                        st.error("❌ Preencha todos os campos.")
                    else:
                        # Sanitizar username
                        sanitized_username = sanitize_username(new_username)
                        if sanitized_username != new_username:
                            st.warning(f"⚠️ Username sanitizado: '{new_username}' → '{sanitized_username}'")

                        # Validar força da senha
                        is_valid, error_msg = validate_password_strength(new_password)
                        if not is_valid:
                            st.error(f"❌ {error_msg}")
                        else:
                            try:
                                auth_db.criar_usuario(sanitized_username, new_password, new_role)
                                st.success(f"Usuário '{sanitized_username}' adicionado com sucesso!")
                                audit_logger.info(f"Admin {st.session_state.get('username')} adicionou o usuário {sanitized_username} com papel {new_role}.")
                                st.rerun()
                            except ValueError as e:
                                st.error(f"Erro ao adicionar usuário: {e}")
                            except Exception as e:
                                st.error(f"Ocorreu um erro inesperado: {e}")

    # Listar e Gerenciar Usuários Existentes
    st.markdown("---")
    st.subheader("Lista de Usuários")

    if not DB_AVAILABLE:
        st.info("🌤️ **Modo Cloud:** Usuários hardcoded disponíveis")
        # Mostrar usuários do core/auth.py
        from core.auth import CLOUD_USERS
        users = [
            {
                "id": i,
                "username": username,
                "role": data["role"],
                "ativo": True
            }
            for i, (username, data) in enumerate(CLOUD_USERS.items())
        ]
    else:
        try:
            users = auth_db.get_all_users()
        except AttributeError as e:
            st.error(f"❌ Erro ao acessar usuários: Função get_all_users não disponível")
            logging.error(f"AttributeError em get_all_users: {e}")
            users = []
        except Exception as e:
            st.error(f"❌ Erro ao carregar usuários: {str(e)}")
            logging.error(f"Erro em get_all_users: {e}")
            users = []

    if users:
        df_users = st.dataframe(users, use_container_width=True)

        st.markdown("---")
        st.subheader("Editar Usuário Existente")
        selected_username = st.selectbox("Selecione o Usuário para Editar", [u['username'] for u in users])

        if selected_username:
            selected_user = next((u for u in users if u['username'] == selected_username), None)
            if selected_user:
                user_id = selected_user.get('id', 0)  # Fallback para modo cloud
                
                with st.form(f"edit_user_form_{user_id}"):
                    current_role = selected_user.get('role', 'user')
                    current_status = selected_user.get('ativo', True)
                    
                    edited_role = st.selectbox("Papel", ["user", "admin"], index=["user", "admin"].index(current_role))
                    edited_status = st.checkbox("Ativo", value=current_status)
                    
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        update_submitted = st.form_submit_button("Atualizar Papel/Status")
                    with col2:
                        reset_password_submitted = st.form_submit_button("Redefinir Senha")
                    with col3:
                        delete_submitted = st.form_submit_button("Excluir Usuário", type="secondary")

                    if update_submitted:
                        if DB_AVAILABLE and user_id > 0:
                            if edited_role != current_role:
                                auth_db.update_user_role(user_id, edited_role)
                                st.success(f"Papel do usuário '{selected_username}' atualizado para '{edited_role}'.")
                                audit_logger.info(f"Admin {st.session_state.get('username')} atualizou o papel do usuário {selected_username} para {edited_role}.")
                            if edited_status != current_status:
                                auth_db.set_user_status(user_id, edited_status)
                                st.success(f"Status do usuário '{selected_username}' atualizado para {'Ativo' if edited_status else 'Inativo'}.")
                                audit_logger.info(f"Admin {st.session_state.get('username')} atualizou o status do usuário {selected_username} para {'Ativo' if edited_status else 'Inativo'}.")
                            st.rerun()
                        else:
                            st.warning("⚠️ Modo Cloud: Edição de usuários não disponível. Use SQL Server para gerenciar usuários.")

                    if reset_password_submitted:
                        if DB_AVAILABLE and user_id > 0:
                            st.markdown("---")
                            st.warning(f"⚠️ Resetar senha para: **{selected_username}**")

                            with st.container():
                                new_temp_password = st.text_input(
                                    "Nova Senha Temporária",
                                    type="password",
                                    key=f"temp_pass_{user_id}",
                                    help="Digite a nova senha temporária para o usuário"
                                )
                                confirm_temp = st.text_input(
                                    "Confirme a Senha",
                                    type="password",
                                    key=f"confirm_temp_{user_id}",
                                    help="Digite novamente a senha"
                                )

                                if st.button("🔑 Confirmar Reset", key=f"confirm_reset_{user_id}", type="primary"):
                                    if not new_temp_password:
                                        st.error("❌ Digite a nova senha.")
                                    elif new_temp_password != confirm_temp:
                                        st.error("❌ As senhas não coincidem.")
                                    else:
                                        # Validar força da senha
                                        is_valid, error_msg = validate_password_strength(new_temp_password)
                                        if not is_valid:
                                            st.error(f"❌ {error_msg}")
                                        else:
                                            success = auth_db.reset_user_password(user_id, new_temp_password)
                                            if success:
                                                st.success(f"✅ Senha resetada para '{selected_username}'!")
                                                audit_logger.info(f"Admin {st.session_state.get('username')} resetou senha de {selected_username}.")
                                                st.info("💡 Informe o usuário sobre a nova senha temporária.")
                                                import time
                                                time.sleep(2)
                                                st.rerun()
                                            else:
                                                st.error("❌ Erro ao resetar senha.")
                        else:
                            st.warning("⚠️ Reset de senha não disponível no modo Cloud.")

                    if delete_submitted:
                        if st.checkbox(f"Confirmar exclusão de {selected_username}?", key=f"confirm_delete_{user_id}"):
                            if st.form_submit_button("Sim, Excluir Permanentemente", type="danger"):
                                auth_db.delete_user(user_id)
                                st.success(f"Usuário '{selected_username}' excluído permanentemente.")
                                audit_logger.info(f"Admin {st.session_state.get('username')} excluiu o usuário {selected_username}.")
                                st.rerun()
    else:
        st.info("Nenhum usuário cadastrado ainda.")

    with tab2:
        # --- Gerenciamento de Permissões ---
        st.subheader("🔐 Gerenciar Permissões de Páginas")

        from core.permissions import AVAILABLE_PAGES, get_user_permissions, set_user_permissions

        if users:
            selected_user_perms = st.selectbox(
                "Selecione o Usuário",
                [u['username'] for u in users if u['role'] != 'admin'],
                key="perms_user_select"
            )

            if selected_user_perms:
                user_data = next((u for u in users if u['username'] == selected_user_perms), None)

                if user_data:
                    st.info(f"👤 Configurando permissões para: **{selected_user_perms}** ({user_data['role']})")

                    # Obter permissões atuais
                    current_perms = get_user_permissions(selected_user_perms, user_data['role'])

                    st.markdown("### Páginas Disponíveis")
                    st.caption("Marque as páginas que o usuário pode acessar:")

                    selected_pages = []

                    # Criar checkboxes para cada página
                    for page_file, page_name in AVAILABLE_PAGES.items():
                        # Admins sempre têm acesso total (não mostrar)
                        if "Painel_de_Administração" in page_file or "Gemini_Playground" in page_file:
                            continue

                        is_checked = page_file in current_perms
                        if st.checkbox(page_name, value=is_checked, key=f"perm_{page_file}"):
                            selected_pages.append(page_file)

                    st.markdown("---")

                    col_save, col_reset = st.columns([1, 1])

                    with col_save:
                        if st.button("💾 Salvar Permissões", use_container_width=True, type="primary"):
                            set_user_permissions(selected_user_perms, selected_pages)
                            st.success(f"✅ Permissões atualizadas para {selected_user_perms}!")
                            st.info(f"📄 {len(selected_pages)} páginas liberadas")
                            audit_logger.info(f"Admin {st.session_state.get('username')} atualizou permissões de {selected_user_perms}")
                            import time
                            time.sleep(1)
                            st.rerun()

                    with col_reset:
                        if st.button("🔄 Resetar para Padrão", use_container_width=True):
                            # Remover permissões customizadas
                            if f"permissions_{selected_user_perms}" in st.session_state:
                                del st.session_state[f"permissions_{selected_user_perms}"]
                            st.success("✅ Permissões resetadas para o padrão!")
                            st.rerun()

                    # Mostrar resumo
                    st.markdown("---")
                    st.markdown("### 📋 Resumo Atual")
                    if current_perms:
                        st.write(f"**{len(current_perms)} páginas** com acesso:")
                        for page in current_perms:
                            page_name = AVAILABLE_PAGES.get(page, page)
                            st.write(f"- {page_name}")
                    else:
                        st.warning("Nenhuma página com acesso")
        else:
            st.info("Nenhum usuário disponível para gerenciar permissões.")

    st.markdown(
        f"<div class='footer'>Desenvolvido para Análise de Dados Caçula © {datetime.now().year}</div>",
        unsafe_allow_html=True,
    )

# Se não for admin, mostra uma mensagem de erro e oculta o conteúdo.
elif st.session_state.get("authenticated"):
    st.error("Acesso negado. Você não tem permissão para acessar esta página.")
    st.stop()

# Se não estiver logado, redireciona para o login
else:
    st.error("Acesso negado. Por favor, faça o login na página principal para acessar esta área.")
    st.stop()
