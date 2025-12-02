import sys
import os
import time
import asyncio
from pathlib import Path
from dotenv import load_dotenv

# Add backend to sys.path
BACKEND_DIR = Path(__file__).resolve().parent.parent / "backend"
sys.path.append(str(BACKEND_DIR))

# Load environment variables
load_dotenv(BACKEND_DIR / ".env")

from app.core.agents.tool_agent import initialize_agent_for_session

async def run_tests():
    print("🚀 Initializing ToolAgent...")
    start_init = time.time()
    try:
        agent = initialize_agent_for_session()
        print(f"✅ Agent initialized in {time.time() - start_init:.2f}s")
    except Exception as e:
        print(f"❌ Failed to initialize agent: {e}")
        return

    test_queries = [
        # 1. Factual / Data-driven (Should succeed)
        {"q": "Quantos produtos únicos existem?", "type": "data"},
        {"q": "Qual o produto com maior estoque?", "type": "data"},
        
        # 2. Complex / Multi-step (Should succeed)
        {"q": "Liste os top 3 produtos mais vendidos e seus preços", "type": "complex"},
        
        # 3. Random / Hallucination Check (Should fail or be handled safely)
        {"q": "Qual é a capital da França?", "type": "hallucination_check"},
        {"q": "Invente dados de vendas para o ano 2050", "type": "hallucination_check"},
        
        # 4. Context / Follow-up (Basic check)
        {"q": "E qual desses é o mais barato?", "type": "context"} 
    ]

    results = []

    print("\n🧪 Starting Performance & Accuracy Tests...\n")

    for i, test in enumerate(test_queries):
        query = test["q"]
        q_type = test["type"]
        
        print(f"--- Test {i+1}: {query} [{q_type}] ---")
        
        start_time = time.time()
        try:
            # Note: invoke is synchronous in the current implementation of ToolAgent, 
            # but usually agents are async. The code shows `agent_executor.invoke`.
            # We'll wrap in asyncio.to_thread if it blocks, but let's try direct first.
            response = agent.process_query(query, chat_history=[])
            elapsed = time.time() - start_time
            
            output = response.get("output", "")
            status = "✅ Success" if output and "erro" not in output.lower() else "⚠️ Potential Issue"
            
            print(f"⏱️ Time: {elapsed:.2f}s")
            print(f"📝 Response: {output[:150]}..." if len(output) > 150 else f"📝 Response: {output}")
            
            results.append({
                "query": query,
                "time": elapsed,
                "status": status,
                "output": output
            })
            
        except Exception as e:
            elapsed = time.time() - start_time
            print(f"❌ Error: {e}")
            results.append({
                "query": query,
                "time": elapsed,
                "status": "❌ Error",
                "output": str(e)
            })
        
        print("")

    # Summary
    print("\n📊 TEST SUMMARY 📊")
    print(f"{ 'Query':<40} | {'Time':<10} | {'Status'}")
    print("-" * 70)
    for r in results:
        print(f"{r['query'][:37]+'...':<40} | {r['time']:.2f}s      | {r['status']}")

if __name__ == "__main__":
    asyncio.run(run_tests())
