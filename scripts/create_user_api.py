import requests
import json

# Dados do novo usuário
user_data = {
    "username": "user",
    "email": "user@agentbi.com",
    "password": "User@2024",
    "full_name": "Test User",
    "role": "user"
}

# Primeiro, fazer login como admin para obter token
login_response = requests.post(
    "http://127.0.0.1:8000/api/v1/auth/login",
    json={"username": "admin", "password": "Admin@2024"}
)

if login_response.status_code == 200:
    token = login_response.json()["access_token"]
    print(f"✅ Login como admin bem-sucedido")
    
    # Criar usuário
    headers = {"Authorization": f"Bearer {token}"}
    create_response = requests.post(
        "http://127.0.0.1:8000/api/v1/admin/users",
        json=user_data,
        headers=headers
    )
    
    if create_response.status_code == 201:
        print(f"✅ Usuário 'user' criado com sucesso!")
        print(json.dumps(create_response.json(), indent=2))
    elif create_response.status_code == 400:
        print(f"⚠️ Usuário já existe")
        print(create_response.json())
    else:
        print(f"❌ Erro ao criar usuário: {create_response.status_code}")
        print(create_response.text)
else:
    print(f"❌ Erro no login: {login_response.status_code}")
    print(login_response.text)
