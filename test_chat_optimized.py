"""
Teste do ChatBI Otimizado
"""
import requests
import time
import json
import sys

# Force UTF-8 encoding
sys.stdout.reconfigure(encoding='utf-8')

# Login primeiro
login_url = "http://127.0.0.1:8000/api/v1/auth/login"
chat_url = "http://127.0.0.1:8000/api/v1/chat"

print("=" * 60)
print("FAZENDO LOGIN...")
print("=" * 60)

login_data = {
    "username": "admin",
    "password": "Admin@2024"
}

response = requests.post(login_url, json=login_data)
if response.status_code != 200:
    print(f"❌ Erro no login: {response.status_code}")
    print(response.text)
    exit(1)

token = response.json()["access_token"]
print(f"OK! Login realizado. Token obtido.")

# Testar chat com pergunta do usuario
headers = {
    "Authorization": f"Bearer {token}",
    "Content-Type": "application/json"
}

query = "qual é o preço do produto 369947"

print("\n" + "=" * 60)
print(f"TESTE CHATBI: '{query}'")
print("=" * 60)

start_time = time.time()

try:
    response = requests.post(
        chat_url,
        json={"query": query},
        headers=headers,
        timeout=30
    )

    elapsed = time.time() - start_time

    print(f"\nTEMPO DE RESPOSTA: {elapsed:.2f}s")
    print(f"STATUS CODE: {response.status_code}")

    if response.status_code == 200:
        data = response.json()
        print(f"\nRESPOSTA:")
        print("-" * 60)
        print(data.get("response", "Sem resposta"))
        print("-" * 60)
    else:
        print(f"\nERRO: {response.status_code}")
        print(response.text)

except requests.exceptions.Timeout:
    elapsed = time.time() - start_time
    print(f"\nTIMEOUT apos {elapsed:.2f}s")
    print("Agente nao respondeu a tempo")

except Exception as e:
    elapsed = time.time() - start_time
    print(f"\nERRO apos {elapsed:.2f}s")
    print(f"Excecao: {e}")

print("\n" + "=" * 60)
print("TESTE CONCLUIDO")
print("=" * 60)
