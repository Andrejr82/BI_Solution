import sys
import os

# Limpar env
for key in list(os.environ.keys()):
    if "GEMINI" in key or "LLM" in key or "MODEL" in key:
        del os.environ[key]

sys.path.insert(0, os.path.abspath("."))

from dotenv import load_dotenv
load_dotenv(override=True)

from core.config import safe_settings
safe_settings.reset_safe_settings_cache()

from core.factory.component_factory import ComponentFactory
from core.agents.conversational_reasoning_node import ConversationalReasoningEngine
from core.agent_state import AgentState

print("=" * 60)
print("TESTE FINAL DE CONVERSACAO")
print("=" * 60)

# Verificar chave
api_key = os.getenv("GEMINI_API_KEY", "")
print(f"[KEY] {api_key[:10]}...{api_key[-10:]}")
print()

# Get LLM
llm_adapter = ComponentFactory.get_intent_classification_llm()
print(f"[MODEL] {llm_adapter.model_name}")
print(f"[TEMP] {llm_adapter.temperature}")

if hasattr(llm_adapter, 'client') and hasattr(llm_adapter.client, 'api_key'):
    print(f"[ADAPTER KEY] {llm_adapter.client.api_key[:10]}...{llm_adapter.client.api_key[-10:]}")
print()

# Engine
engine = ConversationalReasoningEngine(llm_adapter)

# State
state = AgentState(
    messages=[{"role": "user", "content": "Ola! Como voce esta?"}],
    final_response=None, intent=None, plan=None,
    parquet_filters=None, retrieved_data=None,
    plotly_spec=None, clarification_needed=False,
    reasoning_mode=None, reasoning_result=None
)

print("[INPUT] 'Ola! Como voce esta?'")
print()

try:
    # Reasoning
    mode, result = engine.reason_about_user_intent(state)
    print(f"[MODE] {mode}")
    print(f"[EMOTION] {result.get('emotional_tone')}")
    print()
    
    if mode == "conversational":
        # Response
        response = engine.generate_conversational_response(result, state)
        
        if response and len(response) > 0:
            print("[RESPONSE]")
            print(response)
            print()
            print("=" * 60)
            print("[SUCCESS] TESTE PASSOU!")
            print("=" * 60)
        else:
            print("[FAIL] Resposta vazia")
    else:
        print(f"[WARN] Mode inesperado: {mode}")
        
except Exception as e:
    print(f"[ERROR] {e}")
    import traceback
    traceback.print_exc()
