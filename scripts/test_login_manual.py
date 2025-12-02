import requests
import sys

BASE_URL = "http://127.0.0.1:8000/api/v1"

def test_login_and_metrics():
    print("Tentando login com admin...")
    try:
        # 1. Login
        resp = requests.post(
            f"{BASE_URL}/auth/login",
            json={"username": "admin", "password": "Admin@2024"}
        )
        
        if resp.status_code != 200:
            print(f"❌ Falha no login: {resp.status_code} - {resp.text}")
            return False
            
        data = resp.json()
        token = data.get("access_token")
        if not token:
            print("❌ Token não retornado!")
            return False
            
        print(f"✅ Login com sucesso! Token obtido.")
        
        # 2. Testar Metrics
        print("Testando /metrics/summary...")
        headers = {"Authorization": f"Bearer {token}"}
        resp_metrics = requests.get(f"{BASE_URL}/metrics/summary", headers=headers)
        
        if resp_metrics.status_code == 200:
            print("✅ Metrics OK!")
            print(resp_metrics.json())
            return True
        else:
            print(f"❌ Falha em metrics: {resp_metrics.status_code} - {resp_metrics.text}")
            return False
            
    except Exception as e:
        print(f"❌ Exceção: {e}")
        return False

if __name__ == "__main__":
    success = test_login_and_metrics()
    sys.exit(0 if success else 1)
