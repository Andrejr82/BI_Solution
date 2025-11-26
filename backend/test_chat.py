import requests
import json

BASE_URL = "http://localhost:8000/api/v1"

def test_chat():
    # 1. Login
    print("Tentando login...")
    login_data = {
        "username": "admin",
        "password": "Admin@2024"
    }
    try:
        response = requests.post(f"{BASE_URL}/auth/login", json=login_data)
        if response.status_code != 200:
            print(f"Erro no login: {response.status_code} - {response.text}")
            # Tentar senha alternativa
            login_data["password"] = "admin123"
            print("Tentando senha alternativa...")
            response = requests.post(f"{BASE_URL}/auth/login", json=login_data)
            
        if response.status_code != 200:
            print("Falha no login com ambas as senhas.")
            return

        token = response.json()["access_token"]
        print("Login com sucesso! Token obtido.")

        # 2. Chat
        print("\nEnviando pergunta ao chat: 'qual é o preço do produto 369947'")
        headers = {"Authorization": f"Bearer {token}"}
        chat_data = {"query": "qual é o preço do produto 369947"}
        
        chat_response = requests.post(f"{BASE_URL}/chat", json=chat_data, headers=headers)
        
        if chat_response.status_code == 200:
            print("\nRESPOSTA DO CHAT:")
            print("-" * 50)
            print(chat_response.json()["response"])
            print("-" * 50)
        else:
            print(f"Erro no chat: {chat_response.status_code} - {chat_response.text}")

    except Exception as e:
        print(f"Erro na execução: {e}")

if __name__ == "__main__":
    test_chat()
