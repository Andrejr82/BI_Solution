
import streamlit as st
import time
import random

# Título da página
st.set_page_config(page_title="Exemplo 3: Bot com Memória")
st.title("🤖 Bot com Memória")

# Inicializa o histórico e a 'memória' do bot
if "messages_memory" not in st.session_state:
    st.session_state.messages_memory = [{"role": "assistant", "content": "Olá! Eu sou um bot com memória. Tente dizer o seu nome."}]
if "memory" not in st.session_state:
    st.session_state.memory = {}

# Exibe as mensagens do histórico
for message in st.session_state.messages_memory:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Captura a entrada do usuário
if prompt := st.chat_input("Qual o seu nome?"):
    # Adiciona e exibe a mensagem do usuário
    st.session_state.messages_memory.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Lógica do bot com memória
    with st.chat_message("assistant"):
        with st.spinner("Processando..."):
            time.sleep(1)
            
            response = ""
            # Verifica se o usuário está perguntando o próprio nome que já foi salvo
            if ("qual" in prompt.lower() and "meu nome" in prompt.lower()) or \
               ("como" in prompt.lower() and "me chamo" in prompt.lower()):
                
                if "user_name" in st.session_state.memory:
                    response = f"Claro, seu nome é {st.session_state.memory['user_name']}. Eu me lembrei!"
                else:
                    response = "Uhm, parece que você ainda não me disse seu nome."
            
            # Verifica se o usuário está informando o nome
            elif "meu nome é" in prompt.lower() or "me chamo" in prompt.lower():
                # Extrai o nome da string (de uma forma simples)
                try:
                    user_name = prompt.split("é")[-1].strip() if "é" in prompt else prompt.split("chamo")[-1].strip()
                    if not user_name: # Tenta outra variação
                         user_name = prompt.split("is")[-1].strip()
                    
                    st.session_state.memory["user_name"] = user_name.title()
                    response = f"Que legal, {st.session_state.memory['user_name']}! Guardei essa informação."
                except Exception as e:
                    response = "Não consegui entender o nome. Pode repetir, por favor?"

            # Resposta padrão
            else:
                if "user_name" in st.session_state.memory:
                    response = f"Olá {st.session_state.memory['user_name']}! Como posso te ajudar hoje?"
                else:
                    respostas_padrao = [
                        "Interessante. Conte-me mais.",
                        "Não tenho certeza de como responder a isso. Você pode me dizer seu nome?",
                        "Entendido. E qual seria o seu nome?"
                    ]
                    response = random.choice(respostas_padrao)

            st.markdown(response)
            st.session_state.messages_memory.append({"role": "assistant", "content": response})
