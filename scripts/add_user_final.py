import pandas as pd
import json

# Lê o arquivo atual
df = pd.read_parquet('data/parquet/users.parquet')

# Pega o admin como referência
admin = df.iloc[0].to_dict()

print("Admin user:")
print(json.dumps({k: str(v) for k, v in admin.items()}, indent=2))

# Cria novo usuário baseado no admin
import uuid
user_data = {
    'id': str(uuid.uuid4()),
    'username': 'user',
    'email': 'user@agentbi.com',
    'hashed_password': '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYIFj8Q7ppe',  # Hash de 'User@2024'
    'full_name': 'Test User',
    'role': 'user',
    'is_active': admin['is_active'],  # Mesmo tipo que admin
    'is_superuser': False,
    'created_at': admin['created_at'],  # Mesmo tipo que admin
    'updated_at': admin['updated_at'],  # Mesmo tipo que admin
    'last_login': admin['last_login']  # Mesmo tipo que admin (None)
}

# Adiciona ao DataFrame mantendo os tipos
new_row = pd.DataFrame([user_data])
df_final = pd.concat([df, new_row], ignore_index=True)

# Salva
df_final.to_parquet('data/parquet/users.parquet', index=False)

print("\n✅ Usuário 'user' criado!")
print("\nUsuários finais:")
print(df_final[['username', 'role', 'email']])
