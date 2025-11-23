import sys
import os
import logging

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from core.factory.component_factory import ComponentFactory
from core.agents.conversational_reasoning_node import ConversationalReasoningEngine
from core.agent_state import AgentState

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_conversational_engine():
    print("\n🧪 Testing Conversational Reasoning Engine...")

    # 1. Get LLM Adapter
    llm_adapter = ComponentFactory.get_llm_adapter()
    if not llm_adapter:
        print("❌ Failed to get LLM Adapter")
        return

    print(f"✅ LLM Adapter obtained: {type(llm_adapter).__name__}")

    # 2. Initialize Engine
    engine = ConversationalReasoningEngine(llm_adapter)
    print("✅ Engine initialized")

    # 3. Test Case: "Olá, tudo bem?"
    state = AgentState(
        messages=[{"role": "user", "content": "Olá, tudo bem? Sou o André."}],
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

    print("\n🗣️  Input: 'Olá, tudo bem? Sou o André.'")
    
    # 4. Run Reasoning
    try:
        mode, result = engine.reason_about_user_intent(state)
        print(f"🎯 Mode: {mode}")
        print(f"💭 Reasoning: {result.get('reasoning')}")
        print(f"😊 Emotion: {result.get('emotional_tone')}")
        
        if mode == "conversational":
            # 5. Generate Response
            response = engine.generate_conversational_response(result, state)
            print(f"\n💬 Response:\n{response}")
        else:
            print("\n⚠️ Unexpected mode: analytical (should be conversational)")

    except Exception as e:
        print(f"\n❌ Error during execution: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_conversational_engine()
