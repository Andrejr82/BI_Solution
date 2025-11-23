import os

env_path = ".env"
if os.path.exists(env_path):
    try:
        with open(env_path, "r", encoding="utf-8") as f:
            content = f.read()
        print("--- START ENV ---")
        print(content)
        print("--- END ENV ---")
    except Exception as e:
        print(f"Error reading .env: {e}")
else:
    print(".env not found")
