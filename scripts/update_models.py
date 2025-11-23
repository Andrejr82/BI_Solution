import os

env_path = ".env"

# Ler arquivo atual
with open(env_path, "r", encoding="utf-8") as f:
    lines = f.readlines()

# Atualizar linhas
new_lines = []
for line in lines:
    if line.startswith("INTENT_CLASSIFICATION_MODEL="):
        new_lines.append("INTENT_CLASSIFICATION_MODEL=gemini-2.0-flash-exp\n")
        print("✅ Atualizado: INTENT_CLASSIFICATION_MODEL=gemini-2.0-flash-exp")
    elif line.startswith("CODE_GENERATION_MODEL="):
        new_lines.append("CODE_GENERATION_MODEL=gemini-2.0-flash-exp\n")
        print("✅ Atualizado: CODE_GENERATION_MODEL=gemini-2.0-flash-exp")
    else:
        new_lines.append(line)

# Escrever de volta
with open(env_path, "w", encoding="utf-8") as f:
    f.writelines(new_lines)

print("\n✅ Arquivo .env atualizado com sucesso!")
