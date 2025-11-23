import os

env_path = ".env"
new_lines = []
keys_updated = set()

updates = {
    "INTENT_CLASSIFICATION_MODEL": "models/gemini-2.5-flash",
    "CODE_GENERATION_MODEL": "models/gemini-3-pro"
}

if os.path.exists(env_path):
    with open(env_path, "r", encoding="utf-8") as f:
        lines = f.readlines()
    
    for line in lines:
        line = line.strip()
        if not line or line.startswith("#"):
            new_lines.append(line)
            continue
        
        if "=" in line:
            key, val = line.split("=", 1)
            key = key.strip()
            if key in updates:
                new_lines.append(f"{key}={updates[key]}")
                keys_updated.add(key)
            else:
                new_lines.append(line)
        else:
            new_lines.append(line)

for key, val in updates.items():
    if key not in keys_updated:
        new_lines.append(f"{key}={val}")

with open(env_path, "w", encoding="utf-8") as f:
    f.write("\n".join(new_lines) + "\n")

print("Updated .env")
