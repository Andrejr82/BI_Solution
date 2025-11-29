"""
Teste simplificado para diagnosticar o travamento.
"""

import requests
import json
import time

BASE_URL = "http://127.0.0.1:8000"

def test_simple_query():
    """Testa uma consulta simples."""
    print("="*60)
    print("🧪 TESTE SIMPLIFICADO - Produto 369947")
    print("="*60)
    
    # Login
    print("\n1. Fazendo login...")
    login_response = requests.post(
        f"{BASE_URL}/api/v1/auth/login",
        json={"username": "admin", "password": "Admin@2024"}
    )
    
    if login_response.status_code != 200:
        print(f"❌ Erro no login: {login_response.status_code}")
        return
    
    token = login_response.json()["access_token"]
    print("✅ Login OK")
    
    # Teste 1: Consulta de preço
    print("\n2. Testando: 'qual é o preço do produto 369947?'")
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        response = requests.get(
            f"{BASE_URL}/api/v1/chat/stream",
            params={"q": "qual é o preço do produto 369947?", "token": token},
            headers=headers,
            stream=True,
            timeout=30  # Timeout de 30 segundos
        )
        
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            print("\n📝 Resposta:")
            print("-" * 60)
            
            start_time = time.time()
            last_event_time = start_time
            text_received = False
            
            for line in response.iter_lines():
                if line:
                    current_time = time.time()
                    elapsed = current_time - start_time
                    since_last = current_time - last_event_time
                    last_event_time = current_time
                    
                    line_str = line.decode('utf-8')
                    
                    if line_str.startswith('data: '):
                        try:
                            data = json.loads(line_str[6:])
                            event_type = data.get('type', 'unknown')
                            
                            print(f"[{elapsed:.1f}s | +{since_last:.1f}s] {event_type}: ", end='')
                            
                            if event_type == 'text':
                                content = data.get('content', '')
                                print(content)
                                text_received = True
                            elif event_type == 'tool_call':
                                tool = data.get('tool', '')
                                params = data.get('input', {})
                                print(f"{tool} - {params}")
                            elif event_type == 'tool_result':
                                result = data.get('result', '')
                                print(f"{result[:100]}...")
                            elif event_type == 'error':
                                error = data.get('content', '')
                                print(f"❌ {error}")
                            elif event_type == 'done':
                                print("✅ Concluído")
                                break
                            else:
                                print(data)
                                
                        except json.JSONDecodeError as e:
                            print(f"Erro ao decodificar JSON: {e}")
                    
                    # Timeout de segurança - se não receber nada por 10s
                    if elapsed > 30:
                        print(f"\n⏱️ Timeout após {elapsed:.1f}s")
                        break
            
            print("-" * 60)
            
            if text_received:
                print("\n✅ SUCESSO: Resposta recebida!")
            else:
                print("\n⚠️ PROBLEMA: Nenhum texto recebido, possível travamento")
                
        else:
            print(f"❌ Erro HTTP: {response.status_code}")
            print(response.text)
            
    except requests.exceptions.Timeout:
        print("\n❌ TIMEOUT: A requisição demorou mais de 30 segundos")
    except Exception as e:
        print(f"\n❌ ERRO: {e}")

if __name__ == "__main__":
    test_simple_query()
