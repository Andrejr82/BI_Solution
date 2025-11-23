import sys
import os

# Add project root
sys.path.insert(0, os.path.abspath("."))

# Reload settings
from core.config import safe_settings
safe_settings.reset_safe_settings_cache()

from core.factory.component_factory import ComponentFactory
from core.agents.conversational_reasoning_node import ConversationalReasoningEngine
from core.agent_state import AgentState

print("\n=== TESTE DE CONVERSAÇÃO ===\n")

# Get LLM
llm_adapter = ComponentFactory.get_intent_classification_llm()
print(f"Modelo: {llm_adapter.model_name}")
print(f"Temperatura: {llm_adapter.temperature}\n")

# Initialize engine
engine = ConversationalReasoningEngine(llm_adapter)

# Test
state = AgentState(
    messages=[{"role": "user", "content": "Olá! Tudo bem?"}],
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

print("Input: 'Olá! Tudo bem?'\n")

# Reasoning
mode, result = engine.reason_about_user_intent(state)
print(f"Mode: {mode}")
print(f"Emotion: {result.get('emotional_tone')}\n")

# Response
if mode == "conversational":
    response = engine.generate_conversational_response(result, state)
    
    if response and len(response) > 0:
        print(f"Resposta:\n{response}\n")
        print("✅ TESTE PASSOU!")
    else:
        print("❌ Resposta vazia")
