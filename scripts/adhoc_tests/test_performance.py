"""
Teste RÁPIDO de performance do ChatBI
Objetivo: Resposta em < 5 segundos
"""

import requests
import time

def test_quick():
    print("="*60)
    print("⚡ TESTE RÁPIDO DE PERFORMANCE")
    print("="*60)
    
    # Login
    start = time.time()
    login_resp = requests.post(
        "http://127.0.0.1:8000/api/v1/auth/login",
        json={"username": "admin", "password": "Admin@2024"},
        timeout=5
    )
    token = login_resp.json()["access_token"]
    print(f"✅ Login: {time.time() - start:.2f}s")
    
    # Teste consulta
    query = "qual é o preço do produto 369947?"
    print(f"\n📝 Query: {query}")
    print("⏱️  Aguardando resposta...")
    
    start = time.time()
    resp = requests.get(
        "http://127.0.0.1:8000/api/v1/chat/stream",
        params={"q": query, "token": token},
        headers={"Authorization": f"Bearer {token}"},
        stream=True,
        timeout=30
    )
    
    first_token_time = None
    full_response = ""
    
    for line in resp.iter_lines():
        if line and line.startswith(b'data: '):
            import json
            try:
                data = json.loads(line[6:])
                if data.get('type') == 'text' and not first_token_time:
                    first_token_time = time.time() - start
                    print(f"⚡ Primeiro token: {first_token_time:.2f}s")
                
                if data.get('type') == 'text':
                    full_response += data.get('content', '')
                
                if data.get('done'):
                    break
            except:
                pass
    
    total_time = time.time() - start
    
    print(f"\n{'='*60}")
    print(f"⏱️  Tempo total: {total_time:.2f}s")
    print(f"⚡ Primeiro token: {first_token_time:.2f}s" if first_token_time else "❌ Sem resposta")
    print(f"📝 Resposta: {full_response[:100]}...")
    print(f"{'='*60}")
    
    if total_time < 5:
        print("✅ PERFORMANCE OK!")
    elif total_time < 10:
        print("⚠️  PERFORMANCE ACEITÁVEL")
    else:
        print("❌ PERFORMANCE RUIM - PRECISA OTIMIZAR")

if __name__ == "__main__":
    test_quick()
