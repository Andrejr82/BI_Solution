"""
Script de debug para identificar o problema no fluxo de mensagens
"""
import json

# Simular estrutura de mensagem do Streamlit
streamlit_user_message = {
    "role": "user",
    "content": {
        "type": "text",
        "content": "Olá, quem é você?"
    }
}

# Simular estrutura de mensagem do LangChain (que vai para o agente)
from langchain_core.messages import HumanMessage, AIMessage

langchain_user_message = HumanMessage(content="Olá, quem é você?")

print("=" * 80)
print("ESTRUTURAS DE MENSAGEM")
print("=" * 80)

print("\n1. MENSAGEM DO STREAMLIT (user):")
print(json.dumps(streamlit_user_message, indent=2))

print("\n2. MENSAGEM LANGCHAIN (HumanMessage):")
print(f"  - type: {langchain_user_message.type}")
print(f"  - content: {langchain_user_message.content}")
print(f"  - content type: {type(langchain_user_message.content)}")

print("\n3. PROBLEMA NO GRAPH_BUILDER (linha 151):")
print("  Código: state['messages'][-1].content")
print(f"  Se state['messages'][-1] for HumanMessage:")
print(f"    → .content retorna: '{langchain_user_message.content}' (STRING ✅)")
print(f"\n  Se state['messages'][-1] for dicionário do Streamlit:")
print(f"    → .content retorna: {streamlit_user_message.get('content')} (DICT ❌)")

print("\n4. SOLUÇÃO:")
print("  A linha 151 do graph_builder.py deve extrair o conteúdo corretamente:")
print("  - Para HumanMessage: usar .content diretamente")
print("  - Para dicionário: extrair content['content'] se for dict")

print("\n" + "=" * 80)
print("TESTE DE ACESSO")
print("=" * 80)

# Testar acesso como seria no graph_builder
class MockState:
    def __init__(self, messages):
        self.messages = messages

    def get(self, key, default=None):
        return getattr(self, key, default)

    def __getitem__(self, key):
        return getattr(self, key)

# Teste 1: Com HumanMessage
state1 = MockState([langchain_user_message])
try:
    user_query = state1["messages"][-1].content if state1.get("messages") else ""
    print(f"\n✅ Com HumanMessage: user_query = '{user_query}' (tipo: {type(user_query).__name__})")
except Exception as e:
    print(f"\n❌ Com HumanMessage: ERRO - {e}")

# Teste 2: Com dicionário (simular problema)
class DictMessage:
    def __init__(self, data):
        self.content = data['content']
        self.role = data['role']

dict_msg = DictMessage(streamlit_user_message)
state2 = MockState([dict_msg])
try:
    user_query = state2["messages"][-1].content if state2.get("messages") else ""
    print(f"\n⚠️  Com dicionário: user_query = {user_query} (tipo: {type(user_query).__name__})")
    if isinstance(user_query, dict):
        print(f"    → Isso causaria ERRO no Streamlit porque espera STRING!")
except Exception as e:
    print(f"\n❌ Com dicionário: ERRO - {e}")

print("\n" + "=" * 80)
print("ANÁLISE DO PROBLEMA")
print("=" * 80)
print("""
PROBLEMA IDENTIFICADO:
No graph_builder.py linha 151, o código faz:
    "user_query": state["messages"][-1].content

Se state["messages"][-1].content retornar um dicionário (estrutura do Streamlit),
então a resposta final terá:
    {
        "type": "text",
        "content": "resposta do agente",
        "user_query": {"type": "text", "content": "pergunta"}  ← DICT ❌
    }

SOLUÇÃO:
Precisamos garantir que user_query seja sempre uma string, extraindo o conteúdo
corretamente independente se a mensagem for do LangChain ou do Streamlit.

Código corrigido:
    def extract_text_content(msg):
        content = msg.content if hasattr(msg, 'content') else msg.get('content', '')
        if isinstance(content, dict):
            return content.get('content', str(content))
        return str(content)

    "user_query": extract_text_content(state["messages"][-1]) if state.get("messages") else ""
""")
