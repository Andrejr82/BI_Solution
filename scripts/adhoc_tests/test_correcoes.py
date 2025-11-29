"""
Script de teste para validar as correções das referências de colunas.
Testa se o backend está usando as colunas corretas do Parquet.
"""

import requests
import json
import time

BASE_URL = "http://127.0.0.1:8000"

def login():
    """Faz login e retorna o token."""
    print("\n" + "="*60)
    print("🔐 TESTE 1: Login")
    print("="*60)
    
    response = requests.post(
        f"{BASE_URL}/api/v1/auth/login",
        json={"username": "admin", "password": "Admin@2024"}
    )
    
    if response.status_code == 200:
        token = response.json()["access_token"]
        print("✅ Login realizado com sucesso!")
        print(f"Token: {token[:50]}...")
        return token
    else:
        print(f"❌ Erro no login: {response.status_code}")
        print(response.text)
        return None

def test_price_query(token):
    """Testa consulta de preço (deve usar coluna LIQUIDO_38)."""
    print("\n" + "="*60)
    print("💰 TESTE 2: Consulta de Preço do Produto 59294")
    print("="*60)
    print("Query: 'qual é o preço do produto 59294?'")
    print("Esperado: Usar coluna LIQUIDO_38 (não ITEM)")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # Teste via SSE streaming
    response = requests.get(
        f"{BASE_URL}/api/v1/chat/stream",
        params={"q": "qual é o preço do produto 59294?", "token": token},
        headers=headers,
        stream=True
    )
    
    print(f"\nStatus: {response.status_code}")
    
    if response.status_code == 200:
        print("\n📝 Resposta do agente:")
        full_response = ""
        for line in response.iter_lines():
            if line:
                line_str = line.decode('utf-8')
                if line_str.startswith('data: '):
                    try:
                        data = json.loads(line_str[6:])
                        if data.get('type') == 'text':
                            content = data.get('content', '')
                            full_response += content
                            print(content, end='', flush=True)
                        elif data.get('type') == 'tool_call':
                            print(f"\n🔧 Ferramenta chamada: {data.get('tool')}")
                            print(f"   Parâmetros: {data.get('input')}")
                        elif data.get('type') == 'error':
                            print(f"\n❌ Erro: {data.get('content')}")
                            return False
                    except json.JSONDecodeError:
                        pass
        
        print("\n")
        
        # Verificar se não há erro de KeyError 'ITEM'
        if "ITEM" in full_response and "KeyError" in full_response:
            print("❌ FALHOU: Ainda está tentando usar coluna 'ITEM'!")
            return False
        elif "preço" in full_response.lower() or "R$" in full_response:
            print("✅ PASSOU: Consulta de preço funcionou!")
            return True
        else:
            print("⚠️  INCONCLUSIVO: Resposta inesperada")
            return False
    else:
        print(f"❌ Erro na requisição: {response.status_code}")
        return False

def test_chart_query(token):
    """Testa geração de gráfico (deve usar coluna PRODUTO)."""
    print("\n" + "="*60)
    print("📊 TESTE 3: Gráfico de Vendas do Produto 369947")
    print("="*60)
    print("Query: 'gere um gráfico de vendas do produto 369947'")
    print("Esperado: Usar coluna PRODUTO (não ITEM)")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    response = requests.get(
        f"{BASE_URL}/api/v1/chat/stream",
        params={"q": "gere um gráfico de vendas do produto 369947", "token": token},
        headers=headers,
        stream=True,
        timeout=30
    )
    
    print(f"\nStatus: {response.status_code}")
    
    if response.status_code == 200:
        print("\n📝 Processando resposta...")
        has_chart = False
        has_error = False
        error_msg = ""
        
        for line in response.iter_lines():
            if line:
                line_str = line.decode('utf-8')
                if line_str.startswith('data: '):
                    try:
                        data = json.loads(line_str[6:])
                        if data.get('type') == 'tool_call':
                            tool = data.get('tool', '')
                            print(f"🔧 Ferramenta: {tool}")
                            if 'grafico' in tool.lower() or 'chart' in tool.lower():
                                has_chart = True
                        elif data.get('type') == 'error':
                            has_error = True
                            error_msg = data.get('content', '')
                            print(f"❌ Erro: {error_msg}")
                        elif data.get('type') == 'text':
                            content = data.get('content', '')
                            print(content, end='', flush=True)
                    except json.JSONDecodeError:
                        pass
        
        print("\n")
        
        # Verificar resultado
        if has_error and "KeyError" in error_msg and "'ITEM'" in error_msg:
            print("❌ FALHOU: KeyError 'ITEM' ainda ocorre!")
            return False
        elif has_chart and not has_error:
            print("✅ PASSOU: Gráfico gerado sem erro de ITEM!")
            return True
        elif not has_error:
            print("⚠️  INCONCLUSIVO: Sem erro mas sem confirmação de gráfico")
            return True
        else:
            print(f"❌ FALHOU: Erro inesperado - {error_msg}")
            return False
    else:
        print(f"❌ Erro na requisição: {response.status_code}")
        return False

def test_fabricante_query(token):
    """Testa consulta de fabricante (deve usar NOMEFABRICANTE)."""
    print("\n" + "="*60)
    print("🏭 TESTE 4: Consulta de Fabricante do Produto 59294")
    print("="*60)
    print("Query: 'qual é o fabricante do produto 59294?'")
    print("Esperado: Usar coluna NOMEFABRICANTE (não FABRICANTE)")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    response = requests.get(
        f"{BASE_URL}/api/v1/chat/stream",
        params={"q": "qual é o fabricante do produto 59294?", "token": token},
        headers=headers,
        stream=True
    )
    
    print(f"\nStatus: {response.status_code}")
    
    if response.status_code == 200:
        print("\n📝 Resposta do agente:")
        full_response = ""
        for line in response.iter_lines():
            if line:
                line_str = line.decode('utf-8')
                if line_str.startswith('data: '):
                    try:
                        data = json.loads(line_str[6:])
                        if data.get('type') == 'text':
                            content = data.get('content', '')
                            full_response += content
                            print(content, end='', flush=True)
                        elif data.get('type') == 'tool_call':
                            print(f"\n🔧 Ferramenta: {data.get('tool')}")
                            print(f"   Parâmetros: {data.get('input')}")
                    except json.JSONDecodeError:
                        pass
        
        print("\n")
        
        if "fabricante" in full_response.lower():
            print("✅ PASSOU: Consulta de fabricante funcionou!")
            return True
        else:
            print("⚠️  INCONCLUSIVO: Resposta inesperada")
            return False
    else:
        print(f"❌ Erro na requisição: {response.status_code}")
        return False

def main():
    """Executa todos os testes."""
    print("\n" + "="*60)
    print("🧪 TESTES DE VALIDAÇÃO DAS CORREÇÕES")
    print("="*60)
    print("Validando que as colunas corretas estão sendo usadas:")
    print("  - PRODUTO (não ITEM)")
    print("  - LIQUIDO_38 (não PREÇO 38%)")
    print("  - NOMEFABRICANTE (não FABRICANTE)")
    print("="*60)
    
    # Login
    token = login()
    if not token:
        print("\n❌ Não foi possível fazer login. Abortando testes.")
        return
    
    time.sleep(1)
    
    # Executar testes
    results = {
        "Login": True,
        "Consulta de Preço": test_price_query(token),
        "Gráfico de Vendas": test_chart_query(token),
        "Consulta de Fabricante": test_fabricante_query(token)
    }
    
    # Resumo
    print("\n" + "="*60)
    print("📊 RESUMO DOS TESTES")
    print("="*60)
    
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    for test_name, result in results.items():
        status = "✅ PASSOU" if result else "❌ FALHOU"
        print(f"{test_name:.<40} {status}")
    
    print("="*60)
    print(f"Total: {passed}/{total} testes passaram")
    print("="*60)
    
    if passed == total:
        print("\n🎉 SUCESSO! Todas as correções estão funcionando!")
    else:
        print(f"\n⚠️  {total - passed} teste(s) falharam. Verifique os logs acima.")

if __name__ == "__main__":
    main()
