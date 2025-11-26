"""Testar login alternativo (Síncrono)"""
import requests
import json

url = "http://localhost:8000/api/v1/auth-alt/login"
data = {"username": "admin", "password": "admin123"}

print(f"🔐 Testando login ALTERNATIVO em {url}...")
print(f"Dados: {data}\n")

try:
    r = requests.post(url, json=data, timeout=10)
    print(f"Status: {r.status_code}")
    print(f"Response: {r.text}\n")
    
    if r.status_code == 200:
        print("✅✅✅ LOGIN ALTERNATIVO FUNCIONOU! ✅✅✅")
        print(f"Token: {r.json().get('access_token')[:20]}...")
    else:
        print(f"❌ Falhou: {r.json()}")
except Exception as e:
    print(f"❌ Erro: {e}")
