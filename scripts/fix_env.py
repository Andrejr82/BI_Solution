import os
import re

env_path = ".env"
new_env_path = ".env.new"

# Default structure
config = {
    "MSSQL_SERVER": "",
    "MSSQL_DATABASE": "",
    "MSSQL_USER": "",
    "MSSQL_PASSWORD": "",
    "DB_DRIVER": "ODBC Driver 17 for SQL Server",
    "GEMINI_API_KEY": "",
    "DEEPSEEK_API_KEY": "",
    "INTENT_CLASSIFICATION_MODEL": "models/gemini-2.5-flash",
    "CODE_GENERATION_MODEL": "models/gemini-3-pro",
    "CACHE_AUTO_CLEAN": "false",
    "USE_QUERY_CACHE": "true"
}

if os.path.exists(env_path):
    try:
        with open(env_path, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read()
        
        # Try to find values using regex to handle messy files
        for key in config.keys():
            # Look for KEY=VALUE, handling potential garbage around it
            # We assume value ends at newline or some garbage
            match = re.search(f"{key}=([^\r\n]+)", content)
            if match:
                val = match.group(1).strip()
                # Clean up quotes if present
                val = val.strip('"').strip("'")
                # If value looks like it has garbage appended (e.g. from file corruption), try to clean it
                # Heuristic: API keys are long, alphanumeric. SQL settings are specific.
                
                if key.endswith("_KEY"):
                    # Take first word if spaces present? No, keys don't have spaces.
                    val = val.split()[0]
                    # Remove trailing garbage chars if obvious
                    val = re.sub(r"[^a-zA-Z0-9_\-\.]+$", "", val)
                
                if val:
                    config[key] = val
                    print(f"Found {key}: {val[:5]}...")

    except Exception as e:
        print(f"Error reading .env: {e}")

# Write new file
with open(env_path, "w", encoding="utf-8") as f:
    f.write("# Configurações do SQL Server\n")
    f.write(f"MSSQL_SERVER={config['MSSQL_SERVER']}\n")
    f.write(f"MSSQL_DATABASE={config['MSSQL_DATABASE']}\n")
    f.write(f"MSSQL_USER={config['MSSQL_USER']}\n")
    f.write(f"MSSQL_PASSWORD={config['MSSQL_PASSWORD']}\n\n")
    
    f.write("# Driver ODBC\n")
    f.write(f"DB_DRIVER={config['DB_DRIVER']}\n\n")
    
    f.write("# API Keys\n")
    f.write(f"GEMINI_API_KEY={config['GEMINI_API_KEY']}\n")
    f.write(f"DEEPSEEK_API_KEY={config['DEEPSEEK_API_KEY']}\n\n")
    
    f.write("# Modelos Híbridos (Gemini 2.5 Flash + Gemini 3 Pro)\n")
    f.write(f"INTENT_CLASSIFICATION_MODEL={config['INTENT_CLASSIFICATION_MODEL']}\n")
    f.write(f"CODE_GENERATION_MODEL={config['CODE_GENERATION_MODEL']}\n\n")
    
    f.write("# Cache\n")
    f.write(f"CACHE_AUTO_CLEAN={config['CACHE_AUTO_CLEAN']}\n")
    f.write(f"USE_QUERY_CACHE={config['USE_QUERY_CACHE']}\n")

print("Successfully rewrote .env")
