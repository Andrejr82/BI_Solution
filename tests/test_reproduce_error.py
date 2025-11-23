import sys
import os
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO)

# Limpar env para garantir nova chave
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
print("TESTE DE REPRODUCAO DE ERRO (MAX_TOKENS)")
print("=" * 60)

# Get LLM
llm_adapter = ComponentFactory.get_intent_classification_llm()
print(f"[MODEL] {llm_adapter.model_name}")

# Engine
engine = ConversationalReasoningEngine(llm_adapter)

# State com mensagem que gerou erro (provavelmente)
state = AgentState(
    messages=[{"role": "user", "content": "quero um grafico de barras, do ano todo"}],
    final_response=None, intent=None, plan=None,
    parquet_filters=None, retrieved_data=None,
    plotly_spec=None, clarification_needed=False,
    reasoning_mode=None, reasoning_result=None
)

print("[INPUT] 'quero um grafico de barras, do ano todo'")
print()

try:
    # Tentar reproduzir o erro de max_tokens=2000
    print("[TEST] Executando reason_about_user_intent (max_tokens=2000)...")
    mode, result = engine.reason_about_user_intent(state)
    print(f"[RESULT] Mode: {mode}")
    print(f"[RESULT] Reasoning: {result.get('reasoning')}")
    print("[SUCCESS] reason_about_user_intent funcionou!")
    
except Exception as e:
    print(f"[ERROR] Falha em reason_about_user_intent: {e}")
    import traceback
    traceback.print_exc()

print("-" * 60)

try:
    # Se passar, testar geração de resposta (max_tokens=800)
    if 'result' in locals():
        print("[TEST] Executando generate_conversational_response (max_tokens=800)...")
        response = engine.generate_conversational_response(result, state)
        print(f"[RESULT] Response: {response}")
        print("[SUCCESS] generate_conversational_response funcionou!")

except Exception as e:
    print(f"[ERROR] Falha em generate_conversational_response: {e}")
    import traceback
    traceback.print_exc()
