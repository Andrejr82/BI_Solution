import os
from dotenv import load_dotenv

print("=== DIAGNÓSTICO DO ARQUIVO .ENV ===\n")

# Ler arquivo diretamente
env_path = ".env"
if not os.path.exists(env_path):
    print("❌ Arquivo .env não encontrado!")
    exit(1)

print("1. Lendo arquivo .env diretamente...\n")
with open(env_path, "r", encoding="utf-8") as f:
    lines = f.readlines()

# Procurar linha da chave
gem_line = None
gem_line_num = None
for i, line in enumerate(lines, 1):
    if line.strip().startswith("GEMINI_API_KEY"):
        gem_line = line
        gem_line_num = i
        break

if not gem_line:
    print("❌ Linha GEMINI_API_KEY não encontrada no .env!")
    exit(1)

print(f"✅ Linha encontrada (linha {gem_line_num}):")
print(f"   Conteúdo bruto: {repr(gem_line)}")
print()

# Extrair chave
if "=" in gem_line:
    key_part = gem_line.split("=", 1)[1].strip()
    print(f"2. Chave extraída: {repr(key_part)}")
    print(f"   Tamanho: {len(key_part)} caracteres")
    print(f"   Primeiros 10: {key_part[:10]}")
    print(f"   Últimos 10: {key_part[-10:]}")
    print()
    
    # Verificar problemas comuns
    problems = []
    
    if key_part.startswith('"') or key_part.startswith("'"):
        problems.append("⚠️  Chave tem aspas no início")
    
    if key_part.endswith('"') or key_part.endswith("'"):
        problems.append("⚠️  Chave tem aspas no final")
    
    if " " in key_part:
        problems.append("⚠️  Chave tem espaços")
    
    if "\t" in key_part:
        problems.append("⚠️  Chave tem tabs")
    
    if "\r" in key_part or "\n" in key_part:
        problems.append("⚠️  Chave tem quebras de linha")
    
    if not key_part:
        problems.append("❌ Chave está vazia!")
    
    if key_part == "COLE_SUA_NOVA_CHAVE_AQUI":
        problems.append("❌ Chave ainda é o placeholder!")
    
    if problems:
        print("3. Problemas encontrados:")
        for p in problems:
            print(f"   {p}")
        print()
        print("SOLUÇÃO: Remova aspas, espaços e quebras de linha da chave")
    else:
        print("3. ✅ Formato da chave parece correto")
    print()

# Testar com dotenv
print("4. Testando com python-dotenv...\n")
load_dotenv(override=True)
key_from_env = os.getenv("GEMINI_API_KEY", "")

if not key_from_env:
    print("❌ python-dotenv NÃO conseguiu carregar a chave!")
elif key_from_env != key_part.strip('"').strip("'"):
    print(f"⚠️  python-dotenv carregou diferente:")
    print(f"   Esperado: {key_part[:10]}...{key_part[-10:]}")
    print(f"   Carregado: {key_from_env[:10]}...{key_from_env[-10:]}")
else:
    print(f"✅ python-dotenv carregou corretamente:")
    print(f"   {key_from_env[:10]}...{key_from_env[-10:]}")
    print(f"   Tamanho: {len(key_from_env)} caracteres")

print()
print("=" * 60)
