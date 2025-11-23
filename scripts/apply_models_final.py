import os
import re

# Modelos corretos baseados no teste
INTENT_MODEL = "models/gemini-2.5-flash"  # Rapido para classificacao
CODE_GEN_MODEL = "models/gemini-2.5-pro"   # Mais potente para geracao

print("=" * 70)
print("ATUALIZANDO SISTEMA COM MODELOS CORRETOS")
print("=" * 70)
print(f"  INTENT_CLASSIFICATION_MODEL = {INTENT_MODEL}")
print(f"  CODE_GENERATION_MODEL = {CODE_GEN_MODEL}")
print()

files_updated = []

# 1. .env
env_path = ".env"
print(f"[1] Atualizando {env_path}...")
with open(env_path, "r", encoding="utf-8") as f:
    content = f.read()

content = re.sub(r'INTENT_CLASSIFICATION_MODEL=.*', f'INTENT_CLASSIFICATION_MODEL={INTENT_MODEL}', content)
content = re.sub(r'CODE_GENERATION_MODEL=.*', f'CODE_GENERATION_MODEL={CODE_GEN_MODEL}', content)

with open(env_path, "w", encoding="utf-8") as f:
    f.write(content)
files_updated.append(env_path)
print(f"    [OK]")

# 2. safe_settings.py
path = "core/config/safe_settings.py"
print(f"[2] Atualizando {path}...")
with open(path, "r", encoding="utf-8") as f:
    content = f.read()

content = re.sub(
    r'self\.INTENT_CLASSIFICATION_MODEL = self\._get_secret_or_env\("INTENT_CLASSIFICATION_MODEL", "[^"]+"\)',
    f'self.INTENT_CLASSIFICATION_MODEL = self._get_secret_or_env("INTENT_CLASSIFICATION_MODEL", "{INTENT_MODEL}")',
    content
)
content = re.sub(
    r'self\.CODE_GENERATION_MODEL = self\._get_secret_or_env\("CODE_GENERATION_MODEL", "[^"]+"\)',
    f'self.CODE_GENERATION_MODEL = self._get_secret_or_env("CODE_GENERATION_MODEL", "{CODE_GEN_MODEL}")',
    content
)
content = re.sub(
    r'return os\.getenv\("LLM_MODEL_NAME", "[^"]+"\)',
    f'return os.getenv("LLM_MODEL_NAME", "{INTENT_MODEL}")',
    content
)
content = re.sub(
    r'model = os\.getenv\("GEMINI_MODEL_NAME", "[^"]+"\)',
    f'model = os.getenv("GEMINI_MODEL_NAME", "{INTENT_MODEL}")',
    content
)

with open(path, "w", encoding="utf-8") as f:
    f.write(content)
files_updated.append(path)
print(f"    [OK]")

# 3. streamlit_settings.py
path = "core/config/streamlit_settings.py"
if os.path.exists(path):
    print(f"[3] Atualizando {path}...")
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()
    
    content = re.sub(
        r'return os\.getenv\("LLM_MODEL_NAME", "[^"]+"\)',
        f'return os.getenv("LLM_MODEL_NAME", "{INTENT_MODEL}")',
        content
    )
    
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    files_updated.append(path)
    print(f"    [OK]")

# 4. component_factory.py
path = "core/factory/component_factory.py"
print(f"[4] Atualizando {path}...")
with open(path, "r", encoding="utf-8") as f:
    content = f.read()

content = re.sub(
    r'model_name = config\.LLM_MODEL_NAME or "[^"]+"',
    f'model_name = config.LLM_MODEL_NAME or "{INTENT_MODEL}"',
    content
)

with open(path, "w", encoding="utf-8") as f:
    f.write(content)
files_updated.append(path)
print(f"    [OK]")

print()
print("=" * 70)
print("ATUALIZACAO CONCLUIDA")
print("=" * 70)
print("\n[INFO] Arquivos atualizados:")
for f in files_updated:
    print(f"  - {f}")

print("\n[INFO] Modelos configurados:")
print(f"  INTENT_CLASSIFICATION_MODEL = {INTENT_MODEL}")
print(f"  CODE_GENERATION_MODEL = {CODE_GEN_MODEL}")

print("\n[NEXT] Execute: python tests/test_simple.py")
