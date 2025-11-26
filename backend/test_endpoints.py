"""
Script de teste para os endpoints criados
Testa /api/v1/metrics/summary e /api/v1/chat
"""

import requests
import json

BASE_URL = "http://localhost:8000"

def test_login():
    """Testa login e retorna token"""
    print("🔐 Testando login...")
    url = f"{BASE_URL}/api/v1/auth-alt/login"
    data = {
        "username": "admin",
        "password": "admin123"
    }
    
    try:
        response = requests.post(url, json=data, timeout=5)
        if response.status_code == 200:
            result = response.json()
            print("✅ Login bem-sucedido!")
            print(f"   Token: {result['access_token'][:50]}...")
            print(f"   User: {result['user']['username']} ({result['user']['role']})")
            return result['access_token']
        else:
            print(f"❌ Login falhou: {response.status_code}")
            print(f"   Resposta: {response.text}")
            return None
    except Exception as e:
        print(f"❌ Erro ao fazer login: {e}")
        return None


def test_metrics(token):
    """Testa endpoint de métricas"""
    print("\n📊 Testando endpoint de métricas...")
    url = f"{BASE_URL}/api/v1/metrics/summary"
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        response = requests.get(url, headers=headers, timeout=5)
        if response.status_code == 200:
            metrics = response.json()
            print("✅ Métricas obtidas com sucesso!")
            print(f"   Total de Vendas: {metrics['totalSales']:,}")
            print(f"   Total de Usuários: {metrics['totalUsers']:,}")
            print(f"   Receita: R$ {metrics['revenue']:,.2f}")
            print(f"   Produtos: {metrics['productsCount']}")
            print(f"   Crescimento Vendas: {metrics['salesGrowth']}%")
            print(f"   Crescimento Usuários: {metrics['usersGrowth']}%")
            return True
        else:
            print(f"❌ Falha ao obter métricas: {response.status_code}")
            print(f"   Resposta: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Erro ao obter métricas: {e}")
        return False


def test_chat(token):
    """Testa endpoint de chat"""
    print("\n💬 Testando endpoint de chat...")
    url = f"{BASE_URL}/api/v1/chat"
    headers = {"Authorization": f"Bearer {token}"}
    
    queries = [
        "Quantas vendas tivemos?",
        "Qual foi a receita total?",
        "Quantos produtos temos?",
        "Análise de usuários ativos"
    ]
    
    success_count = 0
    for query in queries:
        print(f"\n   Pergunta: '{query}'")
        data = {"query": query}
        
        try:
            response = requests.post(url, headers=headers, json=data, timeout=5)
            if response.status_code == 200:
                result = response.json()
                print(f"   ✅ Resposta: {result['response'][:100]}...")
                success_count += 1
            else:
                print(f"   ❌ Falha: {response.status_code}")
        except Exception as e:
            print(f"   ❌ Erro: {e}")
    
    print(f"\n✅ Chat respondeu {success_count}/{len(queries)} perguntas")
    return success_count == len(queries)


def main():
    print("=" * 60)
    print("TESTE DOS ENDPOINTS DO BACKEND")
    print("=" * 60)
    
    # Teste 1: Login
    token = test_login()
    if not token:
        print("\n❌ Não foi possível obter token. Abortando testes.")
        return
    
    # Teste 2: Métricas
    metrics_ok = test_metrics(token)
    
    # Teste 3: Chat
    chat_ok = test_chat(token)
    
    # Resumo
    print("\n" + "=" * 60)
    print("RESUMO DOS TESTES")
    print("=" * 60)
    print(f"Login: ✅")
    print(f"Métricas: {'✅' if metrics_ok else '❌'}")
    print(f"Chat: {'✅' if chat_ok else '❌'}")
    print("=" * 60)


if __name__ == "__main__":
    main()
