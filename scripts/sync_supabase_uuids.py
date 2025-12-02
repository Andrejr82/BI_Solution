import pandas as pd
import polars as pl
import sys
from pathlib import Path

# Adicionar o diretório raiz ao path para importações se necessário, 
# mas aqui usaremos manipulação direta de arquivo
PROJECT_ROOT = Path(__file__).resolve().parent.parent
BACKEND_DATA_DIR = PROJECT_ROOT / "backend" / "data" / "parquet"
ROOT_DATA_DIR = PROJECT_ROOT / "data" / "parquet"

USERS_FILES = [
    BACKEND_DATA_DIR / "users.parquet",
    ROOT_DATA_DIR / "users.parquet"
]

ADMIN_UUID = "4291b79d-d43d-4a09-a88a-c51d2cbffc7f"
USER_UUID = "b71ad1a4-9b2e-4227-927d-209ba7f5a1f2"

def sync_uuids():
    for USERS_FILE in USERS_FILES:
        print(f"\nProcessando arquivo: {USERS_FILE}")
        
        if not USERS_FILE.exists():
            print(f"ERRO: Arquivo não encontrado: {USERS_FILE}")
            continue

        try:
            df = pd.read_parquet(USERS_FILE)
            print("Dados atuais:")
            print(df[['username', 'id', 'email']])

            # Atualizar Admin
            mask_admin = df['username'] == 'admin'
            if mask_admin.any():
                print(f"Atualizando UUID do admin para {ADMIN_UUID}")
                df.loc[mask_admin, 'id'] = ADMIN_UUID
            else:
                print("AVISO: Usuário 'admin' não encontrado no Parquet.")

            # Atualizar User (se existir)
            mask_user = df['username'] == 'user'
            if mask_user.any():
                print(f"Atualizando UUID do user para {USER_UUID}")
                df.loc[mask_user, 'id'] = USER_UUID
            else:
                print("AVISO: Usuário 'user' não encontrado no Parquet.")

            # Salvar
            df.to_parquet(USERS_FILE, index=False)
            print("✅ UUIDs sincronizados com sucesso!")
            
            # Verificar leitura
            df_new = pd.read_parquet(USERS_FILE)
            print("Dados atualizados:")
            print(df_new[['username', 'id']])

        except Exception as e:
            print(f"ERRO ao processar Parquet: {e}")

if __name__ == "__main__":
    sync_uuids()