import os

env_path = ".env"

# Ler arquivo
with open(env_path, "r", encoding="utf-8") as f:
    lines = f.readlines()

# Verificar se já existe
has_llm_model_name = any("LLM_MODEL_NAME" in line for line in lines)

if has_llm_model_name:
    print("[INFO] LLM_MODEL_NAME ja existe no .env")
else:
    print("[INFO] Adicionando LLM_MODEL_NAME ao .env...")
    
    # Adicionar após GEMINI_API_KEY
    new_lines = []
    added = False
    
    for line in lines:
        new_lines.append(line)
        if "GEMINI_API_KEY" in line and not added:
            new_lines.append("LLM_MODEL_NAME=models/gemini-2.5-flash\n")
            added = True
    
    # Se não adicionou ainda (não encontrou GEMINI_API_KEY), adicionar no fim
    if not added:
        new_lines.append("\n# Modelo LLM Principal\n")
        new_lines.append("LLM_MODEL_NAME=models/gemini-2.5-flash\n")
    
    # Escrever de volta
    with open(env_path, "w", encoding="utf-8") as f:
        f.writelines(new_lines)
    
    print("[OK] LLM_MODEL_NAME adicionado!")

print("\n[INFO] Variaveis de modelo no .env:")
print("  LLM_MODEL_NAME=models/gemini-2.5-flash")
print("  INTENT_CLASSIFICATION_MODEL=models/gemini-2.5-flash")
print("  CODE_GENERATION_MODEL=models/gemini-2.5-pro")
