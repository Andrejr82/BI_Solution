import os

print("=" * 60)
print("ATUALIZAÇÃO DA CHAVE DE API DO GEMINI")
print("=" * 60)
print()
print("Cole sua NOVA chave de API do Gemini abaixo.")
print("(A chave deve começar com 'AIza' e ter cerca de 39 caracteres)")
print()

new_key = input("Nova chave: ").strip()

if not new_key:
    print("\n❌ Nenhuma chave fornecida. Cancelando.")
    exit(1)

if not new_key.startswith("AIza"):
    print("\n⚠️  Aviso: A chave não começa com 'AIza'. Tem certeza que está correta?")
    confirm = input("Continuar mesmo assim? (s/n): ").strip().lower()
    if confirm != 's':
        print("Cancelado.")
        exit(1)

# Update .env
env_path = ".env"
with open(env_path, "r", encoding="utf-8") as f:
    lines = f.readlines()

new_lines = []
updated = False

for line in lines:
    if line.startswith("GEMINI_API_KEY="):
        new_lines.append(f"GEMINI_API_KEY={new_key}\n")
        updated = True
        print(f"\n✅ Chave atualizada!")
    else:
        new_lines.append(line)

if not updated:
    new_lines.append(f"\nGEMINI_API_KEY={new_key}\n")
    print(f"\n✅ Chave adicionada ao .env!")

with open(env_path, "w", encoding="utf-8") as f:
    f.writelines(new_lines)

print(f"\n✅ Arquivo .env atualizado com sucesso!")
print(f"\nAgora execute: python tests/test_simple.py")
