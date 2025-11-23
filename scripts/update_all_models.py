import os
import re

NEW_MODEL = "gemini-2.0-flash-exp"

print(f"Atualizando para o modelo: {NEW_MODEL}\n")

# 1. Atualizar .env
env_path = ".env"
print("1. Atualizando .env...")
with open(env_path, "r", encoding="utf-8") as f:
    content = f.read()

content = re.sub(
    r'INTENT_CLASSIFICATION_MODEL=.*',
    f'INTENT_CLASSIFICATION_MODEL={NEW_MODEL}',
    content
)
content = re.sub(
    r'CODE_GENERATION_MODEL=.*',
    f'CODE_GENERATION_MODEL={NEW_MODEL}',
    content
)

with open(env_path, "w", encoding="utf-8") as f:
    f.write(content)
print("   ✅ .env atualizado\n")

# 2. Atualizar safe_settings.py
safe_settings_path = "core/config/safe_settings.py"
print("2. Atualizando safe_settings.py...")
with open(safe_settings_path, "r", encoding="utf-8") as f:
    content = f.read()

# Atualizar linha 44
content = re.sub(
    r'self\.INTENT_CLASSIFICATION_MODEL = self\._get_secret_or_env\("INTENT_CLASSIFICATION_MODEL", ".*?"\)',
    f'self.INTENT_CLASSIFICATION_MODEL = self._get_secret_or_env("INTENT_CLASSIFICATION_MODEL", "{NEW_MODEL}")',
    content
)

# Atualizar linha 45
content = re.sub(
    r'self\.CODE_GENERATION_MODEL = self\._get_secret_or_env\("CODE_GENERATION_MODEL", ".*?"\)',
    f'self.CODE_GENERATION_MODEL = self._get_secret_or_env("CODE_GENERATION_MODEL", "{NEW_MODEL}")',
    content
)

# Atualizar linha 86 (LLM_MODEL_NAME fallback)
content = re.sub(
    r'return os\.getenv\("LLM_MODEL_NAME", "gemini-.*?"\)',
    f'return os.getenv("LLM_MODEL_NAME", "{NEW_MODEL}")',
    content
)

# Atualizar linha 97 (GEMINI_MODEL_NAME fallback)
content = re.sub(
    r'model = os\.getenv\("GEMINI_MODEL_NAME", "gemini-.*?"\)',
    f'model = os.getenv("GEMINI_MODEL_NAME", "{NEW_MODEL}")',
    content
)

with open(safe_settings_path, "w", encoding="utf-8") as f:
    f.write(content)
print("   ✅ safe_settings.py atualizado\n")

# 3. Atualizar streamlit_settings.py
streamlit_settings_path = "core/config/streamlit_settings.py"
print("3. Atualizando streamlit_settings.py...")
with open(streamlit_settings_path, "r", encoding="utf-8") as f:
    content = f.read()

content = re.sub(
    r'return os\.getenv\("LLM_MODEL_NAME", "gemini-.*?"\)',
    f'return os.getenv("LLM_MODEL_NAME", "{NEW_MODEL}")',
    content
)

with open(streamlit_settings_path, "w", encoding="utf-8") as f:
    f.write(content)
print("   ✅ streamlit_settings.py atualizado\n")

# 4. Atualizar component_factory.py
factory_path = "core/factory/component_factory.py"
print("4. Atualizando component_factory.py...")
with open(factory_path, "r", encoding="utf-8") as f:
    content = f.read()

content = re.sub(
    r'model_name = config\.LLM_MODEL_NAME or "gemini-.*?"',
    f'model_name = config.LLM_MODEL_NAME or "{NEW_MODEL}"',
    content
)

with open(factory_path, "w", encoding="utf-8") as f:
    f.write(content)
print("   ✅ component_factory.py atualizado\n")

print(f"✅ Todos os arquivos atualizados para {NEW_MODEL}!")
print(f"\nExecute: python tests/test_simple.py")
