import sys
import os

try:
    import langchain
    print(f"Langchain version: {langchain.__version__}")
    
    try:
        from langchain.agents import AgentExecutor
        print("✅ AgentExecutor found in langchain.agents")
    except ImportError:
        print("❌ AgentExecutor NOT found in langchain.agents")
        
    try:
        from langchain.agents.agent import AgentExecutor
        print("✅ AgentExecutor found in langchain.agents.agent")
    except ImportError:
        print("❌ AgentExecutor NOT found in langchain.agents.agent")

    try:
        from langchain.agents import create_tool_calling_agent
        print("✅ create_tool_calling_agent found in langchain.agents")
    except ImportError:
        print("❌ create_tool_calling_agent NOT found in langchain.agents")

except Exception as e:
    print(f"Error: {e}")
