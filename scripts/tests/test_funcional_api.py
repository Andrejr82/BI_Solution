"""
Teste Funcional da API FastAPI
Testa todos os endpoints e verifica respostas
"""

import requests
import json
import sys
import time

API_BASE = "http://localhost:5000"

print("="*70)
print("TESTE FUNCIONAL - API FastAPI")
print("="*70)

# Cores
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    END = '\033[0m'

def test_endpoint(name, method, url, data=None, expected_status=200):
    """Testa um endpoint"""
    try:
        print(f"\n[TEST] {name}...", end=" ")

        if method == "GET":
            response = requests.get(url, timeout=10)
        elif method == "POST":
            response = requests.post(url, json=data, timeout=10)
        else:
            raise ValueError(f"Método não suportado: {method}")

        if response.status_code == expected_status:
            print(f"{Colors.GREEN}OK{Colors.END} ({response.status_code})")
            try:
                result = response.json()
                print(f"  Resposta: {json.dumps(result, indent=2, ensure_ascii=False)[:200]}...")
                return True, result
            except:
                print(f"  Resposta: {response.text[:100]}...")
                return True, response.text
        else:
            print(f"{Colors.RED}ERRO{Colors.END} (esperado {expected_status}, recebido {response.status_code})")
            return False, None

    except requests.exceptions.ConnectionError:
        print(f"{Colors.RED}ERRO{Colors.END} - API não está rodando!")
        print(f"  Execute: python api_server.py")
        return False, None
    except Exception as e:
        print(f"{Colors.RED}ERRO{Colors.END} - {e}")
        return False, None

# Lista de testes
tests_passed = 0
tests_failed = 0

print("\n" + "="*70)
print("VERIFICANDO SE API ESTA RODANDO")
print("="*70)

# Aguardar API ficar disponível
max_retries = 5
for i in range(max_retries):
    try:
        response = requests.get(f"{API_BASE}/api/health", timeout=2)
        if response.status_code == 200:
            print(f"{Colors.GREEN}OK{Colors.END} - API está respondendo!")
            break
    except:
        if i < max_retries - 1:
            print(f"Tentativa {i+1}/{max_retries}... aguardando...")
            time.sleep(2)
        else:
            print(f"{Colors.RED}ERRO{Colors.END} - API não respondeu após {max_retries} tentativas")
            print("\nCOMO INICIAR A API:")
            print("  1. Abra outro terminal")
            print("  2. Execute: python api_server.py")
            print("  3. Aguarde ~30 segundos")
            print("  4. Execute este teste novamente")
            sys.exit(1)

print("\n" + "="*70)
print("TESTANDO ENDPOINTS")
print("="*70)

# 1. Health Check
success, data = test_endpoint(
    "Health Check",
    "GET",
    f"{API_BASE}/api/health"
)
if success:
    tests_passed += 1
else:
    tests_failed += 1

# 2. Metrics
success, data = test_endpoint(
    "Metrics",
    "GET",
    f"{API_BASE}/api/metrics"
)
if success:
    tests_passed += 1
else:
    tests_failed += 1

# 3. Examples
success, data = test_endpoint(
    "Examples",
    "GET",
    f"{API_BASE}/api/examples"
)
if success:
    tests_passed += 1
    if data and "examples" in data:
        print(f"  Total de exemplos: {len(data['examples'])}")
else:
    tests_failed += 1

# 4. Query History
success, data = test_endpoint(
    "Query History",
    "GET",
    f"{API_BASE}/api/queries/history?limit=5"
)
if success:
    tests_passed += 1
else:
    tests_failed += 1

# 5. Chat (teste simples)
success, data = test_endpoint(
    "Chat - Query simples",
    "POST",
    f"{API_BASE}/api/chat",
    data={
        "message": "Quantas UNEs existem?",
        "model": "gemini"
    }
)
if success:
    tests_passed += 1
    if data and "response" in data:
        resp_str = json.dumps(data['response'], ensure_ascii=False)
        print(f"  Resposta da IA: {resp_str[:100]}...")
else:
    tests_failed += 1

# 6. Feedback
success, data = test_endpoint(
    "Feedback",
    "POST",
    f"{API_BASE}/api/feedback",
    data={
        "type": "positive",
        "query": "SELECT * FROM test",
        "code": "df.head()",
        "comment": "Teste funcional - funcionou!"
    }
)
if success:
    tests_passed += 1
else:
    tests_failed += 1

# 7. Save Chart
success, data = test_endpoint(
    "Save Chart",
    "POST",
    f"{API_BASE}/api/save-chart",
    data={
        "title": "Teste Chart",
        "query": "SELECT * FROM test",
        "chart_type": "bar",
        "chart_data": {"data": [1, 2, 3]}
    }
)
if success:
    tests_passed += 1
else:
    tests_failed += 1

# 8. Database Diagnostics
success, data = test_endpoint(
    "Database Diagnostics",
    "GET",
    f"{API_BASE}/api/diagnostics/db"
)
if success:
    tests_passed += 1
else:
    tests_failed += 1

# 9. Learning Metrics
success, data = test_endpoint(
    "Learning Metrics",
    "GET",
    f"{API_BASE}/api/learning/metrics"
)
if success:
    tests_passed += 1
else:
    tests_failed += 1

# 10. Documentação Swagger
success, data = test_endpoint(
    "Swagger Docs",
    "GET",
    f"{API_BASE}/docs",
    expected_status=200
)
if success:
    tests_passed += 1
else:
    tests_failed += 1

# Relatório Final
print("\n" + "="*70)
print("RELATORIO FINAL")
print("="*70)

print(f"\n{Colors.GREEN}Testes Passaram:{Colors.END} {tests_passed}")
print(f"{Colors.RED}Testes Falharam:{Colors.END} {tests_failed}")
print(f"Total: {tests_passed + tests_failed}")

if tests_failed == 0:
    print(f"\n{Colors.GREEN}SUCESSO - Todos os testes passaram!{Colors.END}")
    print("\nAPI está 100% funcional e pronta para uso!")
    sys.exit(0)
else:
    print(f"\n{Colors.YELLOW}ATENCAO - Alguns testes falharam{Colors.END}")
    print("\nVerifique os erros acima e corrija antes de usar em producao.")
    sys.exit(1)
