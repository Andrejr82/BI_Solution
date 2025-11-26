import requests
import json

url = "http://localhost:8000/api/v1/auth/login"
data = {"username": "admin", "password": "admin123"}

print(f"🔐 Testando login em {url}...")
print(f"Dados: {data}\n")

try:
    r = requests.post(url, json=data, timeout=5)
    print(f"Status: {r.status_code}")
    print(f"Response: {r.text}\n")
    
    if r.status_code == 200:
        print("✅✅✅ LOGIN FUNCIONOU! ✅✅✅")
        print("\n🎉 TESTE NO NAVEGADOR AGORA:")
        print("   http://localhost:3000/login")
        print("   Username: admin")
        print("   Password: admin123")
    else:
        print(f"❌ Falhou: {r.json()}")
except Exception as e:
    print(f"❌ Erro: {e}")
