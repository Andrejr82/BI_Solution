import sys
import os

# Force reload of .env
if os.path.exists(".env"):
    os.environ.clear()
    from dotenv import load_dotenv
    load_dotenv(override=True)

# Add project root to path
sys.path.insert(0, os.path.abspath("."))

# Force reload of settings
from core.config import safe_settings
safe_settings.reset_safe_settings_cache()

from core.factory.component_factory import ComponentFactory
from core.agents.conversational_reasoning_node import ConversationalReasoningEngine
from core.agent_state import AgentState

print("\n[TEST] Teste de Conversação com Reload Forçado\n")

# Get LLM
try:
    llm_adapter = ComponentFactory.get_intent_classification_llm()
    print(f"✅ LLM Adapter: {type(llm_adapter).__name__}")
    print(f"✅ Modelo: {llm_adapter.model_name}")
    print(f"✅ Temperatura: {llm_adapter.temperature}")
except Exception as e:
    print(f"❌ Erro ao obter LLM: {e}")
    exit(1)

# Initialize engine
engine = ConversationalReasoningEngine(llm_adapter)
print("✅ Engine inicializado\n")

# Test message
state = AgentState(
    messages=[{"role": "user", "content": "Olá! Como você está?"}],
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

print("[INPUT] 'Olá! Como você está?'\n")

try:
    # Reasoning
    mode, result = engine.reason_about_user_intent(state)
    print(f"[REASONING] Mode: {mode}")
    print(f"[REASONING] Emotion: {result.get('emotional_tone')}\n")
    
    if mode == "conversational":
        # Generate response
        response = engine.generate_conversational_response(result, state)
        
        if response and len(response) > 0:
            print(f"[RESPONSE]:\n{response}\n")
            print("🎉 TESTE PASSOU! O agente está conversando!")
        else:
            print("❌ Resposta vazia")
    else:
        print(f"⚠️  Mode inesperado: {mode}")
        
except Exception as e:
    print(f"❌ Erro: {e}")
    import traceback
    traceback.print_exc()
