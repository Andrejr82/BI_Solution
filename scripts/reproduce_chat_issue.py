import asyncio
import httpx
import sys
import json

# Configuração
BASE_URL = "http://localhost:8000/api/v1"
USERNAME = "admin"
PASSWORD = "Admin@2024"  # Senha padrão do seed_admin.py ou similar

async def reproduce():
    async with httpx.AsyncClient(timeout=30.0) as client:
        print(f"1. Autenticando como {USERNAME}...")
        try:
            # Tentar login para pegar token (Endpoint JSON)
            response = await client.post(
                f"{BASE_URL}/auth/login",
                json={"username": USERNAME, "password": PASSWORD},
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code != 200:
                print(f"❌ Falha no login: {response.text}")
                return

            token = response.json()["access_token"]
            print("✅ Login sucesso! Token obtido.")
            
        except Exception as e:
            print(f"❌ Erro ao conectar: {e}")
            return

        # 2. Testar Query Problemática
        query = "boa noite, preciso saber o prooeço do produto 59294"
        print(f"\n2. Enviando query: '{query}'")
        print(f"   URL: {BASE_URL}/chat/stream?q={query}&token={token[:10]}...")

        try:
            async with client.stream("GET", f"{BASE_URL}/chat/stream", params={"q": query, "token": token}) as response:
                print(f"   Status Code: {response.status_code}")
                
                if response.status_code != 200:
                    print(f"❌ Erro no endpoint: {await response.aread()}")
                    return

                print("   Recebendo stream...")
                async for line in response.aiter_lines():
                    if line:
                        print(f"   << {line}")
        except Exception as e:
            print(f"❌ Erro durante streaming: {e}")

if __name__ == "__main__":
    # Verificar se o backend está rodando
    try:
        import socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        result = sock.connect_ex(('localhost', 8000))
        if result != 0:
            print("⚠️ Backend não parece estar rodando na porta 8000!")
            sys.exit(1)
        sock.close()
    except:
        pass
        
    asyncio.run(reproduce())
