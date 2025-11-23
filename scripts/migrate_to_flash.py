"""
Script para atualizar CODE_GENERATION_MODEL no .env
Migração: gemini-2.5-pro → gemini-2.5-flash
"""

import os
import re

def update_env_file():
    """Atualiza o arquivo .env com o novo modelo"""
    env_path = ".env"
    
    if not os.path.exists(env_path):
        print(f"❌ Arquivo {env_path} não encontrado")
        return False
    
    # Ler conteúdo atual
    with open(env_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Backup do conteúdo original
    original_content = content
    
    # Atualizar CODE_GENERATION_MODEL
    pattern = r'CODE_GENERATION_MODEL\s*=\s*["\']?models/gemini-2\.5-pro["\']?'
    replacement = 'CODE_GENERATION_MODEL="models/gemini-2.5-flash"'
    
    new_content, count = re.subn(pattern, replacement, content)
    
    if count == 0:
        print("⚠️  Padrão CODE_GENERATION_MODEL não encontrado ou já está atualizado")
        # Verificar se já está com Flash
        if 'CODE_GENERATION_MODEL="models/gemini-2.5-flash"' in content:
            print("✅ Configuração já está usando gemini-2.5-flash")
            return True
        return False
    
    # Salvar novo conteúdo
    with open(env_path, 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    print("✅ Arquivo .env atualizado com sucesso!")
    print(f"   Mudanças: {count} linha(s) modificada(s)")
    print(f"   De: models/gemini-2.5-pro")
    print(f"   Para: models/gemini-2.5-flash")
    
    return True

if __name__ == "__main__":
    print("="*60)
    print("🔄 Atualizando CODE_GENERATION_MODEL")
    print("="*60)
    
    success = update_env_file()
    
    if success:
        print("\n✅ Migração concluída!")
        print("\n📝 Próximos passos:")
        print("   1. Reiniciar a aplicação Streamlit")
        print("   2. Executar testes de validação")
    else:
        print("\n❌ Migração falhou!")
        print("   Verifique o arquivo .env manualmente")
