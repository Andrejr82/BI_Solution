import os

# Nova chave e modelos corretos
NEW_API_KEY = "AIzaSyBKhX93M-x2aOBJRF1DYZCqk9eUToJ7vDQ"
INTENT_MODEL = "models/gemini-2.5-flash"
CODE_GEN_MODEL = "models/gemini-2.5-pro"
LLM_MODEL = "models/gemini-2.5-flash"

print("=" * 70)
print("ATUALIZANDO SECRETS.TOML E .ENV")
print("=" * 70)
print(f"API Key: {NEW_API_KEY[:10]}...{NEW_API_KEY[-10:]}")
print(f"LLM Model: {LLM_MODEL}")
print(f"Intent Model: {INTENT_MODEL}")
print(f"Code Gen Model: {CODE_GEN_MODEL}")
print()

# 1. Atualizar secrets.toml
secrets_path = ".streamlit/secrets.toml"
if os.path.exists(secrets_path):
    print(f"[1] Atualizando {secrets_path}...")
    
    with open(secrets_path, "r", encoding="utf-8") as f:
        lines = f.readlines()
    
    new_lines = []
    for line in lines:
        if line.startswith("GEMINI_API_KEY"):
            new_lines.append(f'GEMINI_API_KEY = "{NEW_API_KEY}"\n')
            print(f"    [OK] GEMINI_API_KEY atualizada")
        elif line.startswith("LLM_MODEL_NAME"):
            new_lines.append(f'LLM_MODEL_NAME = "{LLM_MODEL}"\n')
            print(f"    [OK] LLM_MODEL_NAME atualizado")
        else:
            new_lines.append(line)
    
    # Adicionar novos modelos se não existirem
    has_intent = any("INTENT_CLASSIFICATION_MODEL" in line for line in new_lines)
    has_code_gen = any("CODE_GENERATION_MODEL" in line for line in new_lines)
    
    if not has_intent:
        new_lines.append(f'\nINTENT_CLASSIFICATION_MODEL = "{INTENT_MODEL}"\n')
        print(f"    [OK] INTENT_CLASSIFICATION_MODEL adicionado")
    
    if not has_code_gen:
        new_lines.append(f'CODE_GENERATION_MODEL = "{CODE_GEN_MODEL}"\n')
        print(f"    [OK] CODE_GENERATION_MODEL adicionado")
    
    with open(secrets_path, "w", encoding="utf-8") as f:
        f.writelines(new_lines)
    
    print(f"    [DONE]")
else:
    print(f"[1] {secrets_path} nao encontrado")

# 2. Atualizar .env
env_path = ".env"
print(f"\n[2] Atualizando {env_path}...")

with open(env_path, "r", encoding="utf-8") as f:
    lines = f.readlines()

new_lines = []
for line in lines:
    if line.startswith("GEMINI_API_KEY"):
        new_lines.append(f'GEMINI_API_KEY="{NEW_API_KEY}"\n')
        print(f"    [OK] GEMINI_API_KEY atualizada")
    elif line.startswith("LLM_MODEL_NAME"):
        new_lines.append(f'LLM_MODEL_NAME="{LLM_MODEL}"\n')
        print(f"    [OK] LLM_MODEL_NAME atualizado")
    elif line.startswith("INTENT_CLASSIFICATION_MODEL"):
        new_lines.append(f'INTENT_CLASSIFICATION_MODEL="{INTENT_MODEL}"\n')
        print(f"    [OK] INTENT_CLASSIFICATION_MODEL atualizado")
    elif line.startswith("CODE_GENERATION_MODEL"):
        new_lines.append(f'CODE_GENERATION_MODEL="{CODE_GEN_MODEL}"\n')
        print(f"    [OK] CODE_GENERATION_MODEL atualizado")
    else:
        new_lines.append(line)

# Adicionar novos se não existirem
has_intent = any("INTENT_CLASSIFICATION_MODEL" in line for line in new_lines)
has_code_gen = any("CODE_GENERATION_MODEL" in line for line in new_lines)

if not has_intent:
    new_lines.append(f'\nINTENT_CLASSIFICATION_MODEL="{INTENT_MODEL}"\n')
    print(f"    [OK] INTENT_CLASSIFICATION_MODEL adicionado")

if not has_code_gen:
    new_lines.append(f'CODE_GENERATION_MODEL="{CODE_GEN_MODEL}"\n')
    print(f"    [OK] CODE_GENERATION_MODEL adicionado")

with open(env_path, "w", encoding="utf-8") as f:
    f.writelines(new_lines)

print(f"    [DONE]")

print("\n" + "=" * 70)
print("ATUALIZACAO CONCLUIDA")
print("=" * 70)
print("\n[NEXT] Execute: python tests/test_with_reset.py")
