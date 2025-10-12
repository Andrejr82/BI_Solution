"""
Verificar TODAS as API Keys configuradas no sistema
Identifica conflitos entre .env, secrets.toml e variaveis de ambiente
"""

import os
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from dotenv import load_dotenv
load_dotenv(override=True)

print("=" * 80)
print("  DIAGNOSTICO: API KEYS NO SISTEMA")
print("=" * 80)

chaves_encontradas = []

# 1. Verificar .env
print("\n[1/4] Arquivo .env:")
gemini_env = os.getenv("GEMINI_API_KEY")
if gemini_env:
    print(f"   [OK] GEMINI_API_KEY encontrada")
    print(f"   Valor: {gemini_env[:15]}...{gemini_env[-8:]}")
    chaves_encontradas.append(("arquivo .env", gemini_env))
else:
    print("   [X] GEMINI_API_KEY NAO encontrada")

# 2. Verificar secrets.toml (projeto)
print("\n[2/4] Streamlit Secrets (projeto):")
secrets_file = Path(".streamlit/secrets.toml")
if secrets_file.exists():
    print(f"   [!] Arquivo EXISTE: {secrets_file}")
    try:
        with open(secrets_file, 'r', encoding='utf-8') as f:
            content = f.read()
            if 'GEMINI_API_KEY' in content:
                # Extrair valor
                for line in content.split('\n'):
                    if 'GEMINI_API_KEY' in line and '=' in line:
                        value = line.split('=')[1].strip().strip('"').strip("'")
                        print(f"   [!] GEMINI_API_KEY encontrada")
                        print(f"   Valor: {value[:15]}...{value[-8:]}")
                        chaves_encontradas.append(("secrets.toml (projeto)", value))
            else:
                print("   [OK] GEMINI_API_KEY nao encontrada no arquivo")
    except Exception as e:
        print(f"   [X] Erro ao ler arquivo: {e}")
else:
    print(f"   [OK] Arquivo NAO existe (bom - usa .env)")

# 3. Verificar secrets.toml (global do usuario)
print("\n[3/4] Streamlit Secrets (global - usuario):")
home = Path.home()
global_secrets = home / ".streamlit" / "secrets.toml"
if global_secrets.exists():
    print(f"   [!] Arquivo EXISTE: {global_secrets}")
    try:
        with open(global_secrets, 'r', encoding='utf-8') as f:
            content = f.read()
            if 'GEMINI_API_KEY' in content:
                for line in content.split('\n'):
                    if 'GEMINI_API_KEY' in line and '=' in line:
                        value = line.split('=')[1].strip().strip('"').strip("'")
                        print(f"   [!] GEMINI_API_KEY encontrada")
                        print(f"   Valor: {value[:15]}...{value[-8:]}")
                        chaves_encontradas.append(("secrets.toml (global)", value))
            else:
                print("   [OK] GEMINI_API_KEY nao encontrada no arquivo")
    except Exception as e:
        print(f"   [X] Erro ao ler arquivo: {e}")
else:
    print(f"   [OK] Arquivo NAO existe (bom - usa .env)")

# 4. Verificar cache do Streamlit
print("\n[4/4] Cache do Streamlit:")
cache_dir = home / ".streamlit" / "cache"
if cache_dir.exists():
    cache_files = list(cache_dir.glob("**/*"))
    if cache_files:
        print(f"   [!] Cache EXISTE com {len(cache_files)} arquivos")
        print(f"   Localizacao: {cache_dir}")
        print(f"   [ACAO] Recomendado limpar cache!")
    else:
        print(f"   [OK] Cache vazio")
else:
    print(f"   [OK] Cache nao existe")

# Analise final
print("\n" + "=" * 80)
print("  ANALISE E RECOMENDACOES")
print("=" * 80)

if len(chaves_encontradas) == 0:
    print("\n[ERRO CRITICO] Nenhuma API Key encontrada!")
    print("Acao: Adicionar GEMINI_API_KEY no arquivo .env")

elif len(chaves_encontradas) == 1:
    fonte, chave = chaves_encontradas[0]
    print(f"\n[OK] Apenas 1 chave encontrada em: {fonte}")
    print(f"Chave: {chave[:15]}...{chave[-8:]}")

    if fonte == "arquivo .env":
        print("\n[OTIMO] Configuracao ideal - usando apenas .env")
        print("Se Streamlit nao funciona:")
        print("  1. Limpar cache do Streamlit")
        print("  2. Reiniciar aplicacao")
    else:
        print(f"\n[AVISO] Usando secrets.toml em vez de .env")
        print("Recomendacao:")
        print(f"  1. Deletar arquivo: {fonte}")
        print(f"  2. Adicionar chave no .env")
        print(f"  3. Reiniciar aplicacao")

else:
    print(f"\n[PROBLEMA] {len(chaves_encontradas)} chaves encontradas em locais diferentes!")
    print("\nChaves encontradas:")
    for i, (fonte, chave) in enumerate(chaves_encontradas, 1):
        print(f"  {i}. {fonte}: {chave[:15]}...{chave[-8:]}")

    # Verificar se sao iguais
    chaves_unicas = set(chave for _, chave in chaves_encontradas)

    if len(chaves_unicas) == 1:
        print("\n[OK] Todas as chaves sao IGUAIS (nao ha conflito)")
        print("Recomendacao: Usar apenas .env e deletar secrets.toml")
    else:
        print("\n[ERRO CRITICO] Chaves sao DIFERENTES!")
        print("Streamlit vai usar a chave de secrets.toml (prioridade alta)")
        print("e IGNORAR a chave do .env")
        print("\nACAO URGENTE:")
        print("  1. Deletar TODOS os arquivos secrets.toml")
        print("  2. Manter apenas .env com a chave correta")
        print("  3. Limpar cache do Streamlit")
        print("  4. Reiniciar aplicacao")

# Comandos rapidos
print("\n" + "=" * 80)
print("  COMANDOS RAPIDOS PARA CORRIGIR")
print("=" * 80)

print("\n1. Limpar cache do Streamlit:")
print('   rmdir /s /q "%USERPROFILE%\\.streamlit\\cache"')

if Path(".streamlit/secrets.toml").exists():
    print("\n2. Deletar secrets.toml do projeto:")
    print("   del .streamlit\\secrets.toml")

if (home / ".streamlit" / "secrets.toml").exists():
    print("\n3. Deletar secrets.toml global:")
    print(f"   del {home}\\.streamlit\\secrets.toml")

print("\n4. Reiniciar Streamlit:")
print("   streamlit run streamlit_app.py")

print("\n" + "=" * 80)
print("  TESTE RAPIDO")
print("=" * 80)

if gemini_env:
    print("\nTestando conexao com a chave do .env...")
    try:
        from openai import OpenAI

        client = OpenAI(
            api_key=gemini_env,
            base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
        )

        response = client.chat.completions.create(
            model="gemini-2.0-flash-exp",
            messages=[{"role": "user", "content": "Responda apenas: OK"}],
            max_tokens=10
        )

        print("[OK] Chave do .env FUNCIONA!")
        print(f"Resposta: {response.choices[0].message.content}")
    except Exception as e:
        erro = str(e)
        if "expired" in erro.lower():
            print("[ERRO] Chave do .env EXPIROU!")
            print("Acao: Gerar nova chave em https://aistudio.google.com/app/apikey")
        else:
            print(f"[ERRO] Chave do .env FALHOU: {erro[:100]}")

print("\n" + "=" * 80)
