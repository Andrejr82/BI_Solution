import pandas as pd
import pyarrow.parquet as pq
import pyarrow as pa
import uuid
from datetime import datetime, timezone

# Lê o arquivo Parquet
table = pq.read_table('data/parquet/users.parquet')
df = table.to_pandas()

print("📊 Usuários atuais:")
print(df[['username', 'role']])

# Verifica se user já existe
if 'user' in df['username'].values:
    print("\n✅ Usuário 'user' já existe!")
else:
    print("\n➕ Criando usuário 'user'...")
    
    # Pega o admin como template
    admin_row = df[df['username'] == 'admin'].iloc[0].to_dict()
    
    # Modifica para criar o user
    user_row = admin_row.copy()
    user_row['id'] = str(uuid.uuid4())
    user_row['username'] = 'user'
    user_row['email'] = 'user@agentbi.com'
    user_row['hashed_password'] = '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYIFj8Q7ppe'
    user_row['full_name'] = 'Test User'
    user_row['role'] = 'user'
    user_row['is_superuser'] = False
    user_row['created_at'] = datetime.now(timezone.utc).isoformat()
    user_row['updated_at'] = datetime.now(timezone.utc).isoformat()
    
    # Adiciona ao DataFrame
    df = pd.concat([df, pd.DataFrame([user_row])], ignore_index=True)
    
    # Converte de volta para Arrow Table e salva
    table = pa.Table.from_pandas(df)
    pq.write_table(table, 'data/parquet/users.parquet')
    
    print("✅ Usuário 'user' criado com sucesso!")
    print("\n📊 Usuários finais:")
    print(df[['username', 'role', 'email']])
