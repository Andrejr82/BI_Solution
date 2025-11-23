import sys
import os
import logging
import traceback

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Force reload of settings to pick up .env changes
from core.config import safe_settings
safe_settings.reset_safe_settings_cache()

from core.factory.component_factory import ComponentFactory
from core.agents.conversational_reasoning_node import ConversationalReasoningEngine
from core.agent_state import AgentState

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_conversational_engine():
    print("\n[TEST] Testing Conversational Reasoning Engine V2...")

    # 1. Get LLM Adapter (Use Intent Classification Model)
    try:
        # Force factory to reload settings if needed (it uses safe_settings)
        llm_adapter = ComponentFactory.get_intent_classification_llm()
    except Exception as e:
        print(f"[ERROR] Failed to get LLM Adapter: {e}")
        return

    if not llm_adapter:
        print("[ERROR] Failed to get LLM Adapter (None returned)")
        return

    print(f"[INFO] LLM Adapter obtained: {type(llm_adapter).__name__}")
    if hasattr(llm_adapter, 'model_name'):
        print(f"[INFO] Model: {llm_adapter.model_name}")
    if hasattr(llm_adapter, 'temperature'):
        print(f"[INFO] Temperature: {llm_adapter.temperature}")

    # 2. Initialize Engine
    engine = ConversationalReasoningEngine(llm_adapter)
    print("[INFO] Engine initialized")

    # 3. Test Case: "Ola, tudo bem?"
    state = AgentState(
        messages=[{"role": "user", "content": "Ola, tudo bem? Sou o Andre."}],
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

    print("\n[INPUT] 'Ola, tudo bem? Sou o Andre.'")
    
    # 4. Run Reasoning
    try:
        print("[INFO] Calling reason_about_user_intent...")
        mode, result = engine.reason_about_user_intent(state)
        print(f"[RESULT] Mode: {mode}")
        print(f"[RESULT] Reasoning: {result.get('reasoning')}")
        print(f"[RESULT] Emotion: {result.get('emotional_tone')}")
        
        if mode == "conversational":
            # 5. Generate Response
            print("[INFO] Generating conversational response...")
            response = engine.generate_conversational_response(result, state)
            print(f"\n[RESPONSE]:\n{response}")
        else:
            print("\n[WARN] Unexpected mode: analytical (should be conversational)")

    except Exception as e:
        print(f"\n[ERROR] Error during execution: {e}")
        traceback.print_exc()

if __name__ == "__main__":
    test_conversational_engine()
