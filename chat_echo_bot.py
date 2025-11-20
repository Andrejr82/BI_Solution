
import streamlit as st

# Título da página
st.set_page_config(page_title="Exemplo 1: Echo Bot")
st.title("🤖 Echo Bot")

# Inicializa o histórico da conversa no st.session_state
# st.session_state é um dicionário que persiste entre os reruns da aplicação
if "messages" not in st.session_state:
    st.session_state.messages = []

# Exibe as mensagens do histórico a cada rerun do app
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Captura a entrada do usuário usando st.chat_input
if prompt := st.chat_input("Qual a sua mensagem?"):
    # Adiciona a mensagem do usuário ao histórico
    st.session_state.messages.append({"role": "user", "content": prompt})
    # Exibe a mensagem do usuário na tela
    with st.chat_message("user"):
        st.markdown(prompt)

    # Lógica do "Echo Bot"
    response = f"Echo: {prompt}"
    
    # Adiciona a resposta do bot ao histórico
    st.session_state.messages.append({"role": "assistant", "content": response})
    # Exibe a resposta do bot na tela
    with st.chat_message("assistant"):
        st.markdown(response)
