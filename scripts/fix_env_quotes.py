import os

env_path = ".env"

print("Corrigindo arquivo .env...\n")

# Ler arquivo
with open(env_path, "r", encoding="utf-8") as f:
    lines = f.readlines()

# Corrigir linhas
new_lines = []
fixed = False

for line in lines:
    if line.strip().startswith("GEMINI_API_KEY"):
        # Extrair chave sem aspas
        if "=" in line:
            key_part = line.split("=", 1)[1].strip()
            # Remover aspas
            key_part = key_part.strip('"').strip("'")
            # Remover quebras de linha e espaços
            key_part = key_part.strip()
            
            new_line = f"GEMINI_API_KEY={key_part}\n"
            new_lines.append(new_line)
            
            print(f"Original: {repr(line)}")
            print(f"Corrigida: {repr(new_line)}")
            print(f"Chave: {key_part[:10]}...{key_part[-10:]}")
            fixed = True
        else:
            new_lines.append(line)
    else:
        new_lines.append(line)

if not fixed:
    print("❌ Linha GEMINI_API_KEY não encontrada!")
    exit(1)

# Escrever de volta
with open(env_path, "w", encoding="utf-8") as f:
    f.writelines(new_lines)

print("\n✅ Arquivo .env corrigido!")
print("Execute: python tests/test_simple.py")
