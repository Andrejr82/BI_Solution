import os
from dotenv import load_dotenv
from llama_index.llms.gemini import Gemini
import logging

logging.basicConfig(level=logging.INFO)
load_dotenv("backend/.env")

api_key = os.getenv("GEMINI_API_KEY")

print("Testing Gemini initialization...")

try:
    print("Attempt 1: using 'model' parameter")
    llm = Gemini(
        model="models/gemini-2.0-flash",
        api_key=api_key
    )
    print("Success with 'model'")
except Exception as e:
    print(f"Failed with 'model': {e}")

try:
    print("\nAttempt 2: using 'model_name' parameter")
    llm = Gemini(
        model_name="models/gemini-2.0-flash",
        api_key=api_key
    )
    print("Success with 'model_name'")
except Exception as e:
    print(f"Failed with 'model_name': {e}")
