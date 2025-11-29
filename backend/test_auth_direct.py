"""
Script para testar autenticação diretamente
"""
import sys
import asyncio
from pathlib import Path

# Adicionar o diretório backend ao path
sys.path.insert(0, str(Path(__file__).parent))

async def test_auth():
    from app.core.auth_service import auth_service
    
    print("=" * 60)
    print("TESTANDO AUTENTICAÇÃO DIRETA")
    print("=" * 60)
    
    username = "admin"
    password = "Admin@2024"
    
    print(f"\nUsuário: {username}")
    print(f"Senha: {password}")
    print(f"Parquet path: {auth_service.parquet_path}")
    print(f"Parquet exists: {auth_service.parquet_path.exists()}")
    
    # Testar autenticação
    print("\n" + "=" * 60)
    print("TENTANDO AUTENTICAR...")
    print("=" * 60)
    
    result = await auth_service.authenticate_user(username, password, db=None)
    
    if result:
        print("\n✅ AUTENTICAÇÃO BEM-SUCEDIDA!")
        print(f"User ID: {result['id']}")
        print(f"Username: {result['username']}")
        print(f"Email: {result['email']}")
        print(f"Role: {result['role']}")
        print(f"Is Active: {result['is_active']}")
    else:
        print("\n❌ AUTENTICAÇÃO FALHOU!")
        print("Verifique os logs acima para detalhes do erro")

if __name__ == "__main__":
    asyncio.run(test_auth())
