
import streamlit as st
import time

# Título da página
st.set_page_config(page_title="Exemplo 2: Bot Interativo")
st.title("🤖 Bot Interativo com Botões")

# Inicializa o histórico da conversa
if "messages_interactive" not in st.session_state:
    st.session_state.messages_interactive = [{"role": "assistant", "content": "Olá! Como posso ajudar? Você gostaria de ver o status de um pedido ou falar com um atendente?"}]

# Função para simular o clique no botão e adicionar a resposta
def handle_button_click(choice):
    st.session_state.messages_interactive.append({"role": "user", "content": choice})
    
    with st.chat_message("user"):
        st.markdown(choice)
    
    with st.chat_message("assistant"):
        with st.spinner("Pensando..."):
            time.sleep(1)
        if "status" in choice.lower():
            st.write("Por favor, insira o número do seu pedido.")
            st.session_state.messages_interactive.append({"role": "assistant", "content": "Por favor, insira o número do seu pedido."})
        elif "atendente" in choice.lower():
            st.write("Ok, transferindo para um atendente. Por favor, aguarde.")
            st.session_state.messages_interactive.append({"role": "assistant", "content": "Ok, transferindo para um atendente. Por favor, aguarde."})


# Exibe as mensagens do histórico
for message in st.session_state.messages_interactive:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])


# Layout dos botões em colunas para não poluir o chat principal
# A interação acontece aqui, fora do loop de chat principal
col1, col2 = st.columns(2)
with col1:
    if st.button("Ver status do Pedido", key="status_button", use_container_width=True):
        handle_button_click("Quero ver o status do pedido")

with col2:
    if st.button("Falar com Atendente", key="agent_button", use_container_width=True):
        handle_button_click("Quero falar com um atendente")


# Captura a entrada de texto do usuário
if prompt := st.chat_input("Insira o número do pedido ou sua mensagem."):
    # Adiciona a mensagem do usuário ao histórico
    st.session_state.messages_interactive.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Lógica de resposta do bot
    with st.chat_message("assistant"):
        with st.spinner("Analisando..."):
            time.sleep(1)
        
        # Simula uma verificação de número de pedido
        if any(char.isdigit() for char in prompt):
            response = f"Verificando o pedido `{prompt}`... Encontrei! O pedido está a caminho."
        else:
            response = "Desculpe, não entendi. Você pode tentar uma das opções acima?"
        
        st.write(response)
        st.session_state.messages_interactive.append({"role": "assistant", "content": response})

