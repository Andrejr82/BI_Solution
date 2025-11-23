import sys
import os

# Limpar variáveis de ambiente
for key in list(os.environ.keys()):
    if "GEMINI" in key or "LLM" in key or "MODEL" in key:
        del os.environ[key]

# Adicionar ao path
sys.path.insert(0, os.path.abspath("."))

# Recarregar .env
from dotenv import load_dotenv
load_dotenv(override=True)

# Verificar chave carregada
api_key = os.getenv("GEMINI_API_KEY", "")
print(f"[KEY CHECK] {api_key[:10]}...{api_key[-10:]}")
print(f"[KEY LENGTH] {len(api_key)}")
print()

# Resetar cache de settings
from core.config import safe_settings
safe_settings.reset_safe_settings_cache()

# Importar factory
from core.factory.component_factory import ComponentFactory
from core.agents.conversational_reasoning_node import ConversationalReasoningEngine
from core.agent_state import AgentState

print("[TEST] Teste de Conversacao com Reset Total\n")

# Get LLM
llm_adapter = ComponentFactory.get_intent_classification_llm()
print(f"[INFO] Modelo: {llm_adapter.model_name}")
print(f"[INFO] Temperatura: {llm_adapter.temperature}")

# Verificar chave do adapter
if hasattr(llm_adapter, 'client') and hasattr(llm_adapter.client, 'api_key'):
    adapter_key = llm_adapter.client.api_key
    print(f"[INFO] Chave do adapter: {adapter_key[:10]}...{adapter_key[-10:]}")
print()

# Initialize engine
engine = ConversationalReasoningEngine(llm_adapter)
print("[INFO] Engine inicializado\n")

# Test
state = AgentState(
    messages=[{"role": "user", "content": "Ola! Tudo bem?"}],
    final_response=None,
    intent=None,
    plan=None,
    parquet_filters=None,
    retrieved_data=None,
    plotly_spec=None,
    clarification_needed=False,
    reasoning_mode=None,
    reasoning_result=None
)

print("[INPUT] 'Ola! Tudo bem?'\n")

# Reasoning
mode, result = engine.reason_about_user_intent(state)
print(f"[RESULT] Mode: {mode}")
print(f"[RESULT] Emotion: {result.get('emotional_tone')}\n")

# Response
if mode == "conversational":
    response = engine.generate_conversational_response(result, state)
    
    if response and len(response) > 0:
        print(f"[RESPONSE]:\n{response}\n")
        print("[SUCCESS] TESTE PASSOU!")
    else:
        print("[FAIL] Resposta vazia")
