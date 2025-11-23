import os
from dotenv import load_dotenv

# Recarregar .env
load_dotenv(override=True)

key = os.getenv("GEMINI_API_KEY", "")

if not key:
    print("❌ GEMINI_API_KEY não encontrada no .env")
elif key == "COLE_SUA_NOVA_CHAVE_AQUI":
    print("⚠️  GEMINI_API_KEY ainda está com o valor placeholder")
    print("   Por favor, edite o .env e cole sua chave real")
else:
    # Mostrar apenas início e fim da chave
    masked = key[:10] + "..." + key[-10:] if len(key) > 20 else "CHAVE_MUITO_CURTA"
    print(f"✅ GEMINI_API_KEY encontrada: {masked}")
    print(f"   Tamanho: {len(key)} caracteres")
    
    # Verificar se parece com uma chave do Google
    if key.startswith("AIza"):
        print("   ✅ Formato parece correto (começa com 'AIza')")
    else:
        print("   ⚠️  Formato pode estar incorreto (chaves Google geralmente começam com 'AIza')")
