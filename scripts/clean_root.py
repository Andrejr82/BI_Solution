import os
import shutil

# Arquivos e diretórios a MANTER na raiz
keep_files = {
    # Configuração essencial
    ".env",
    ".gitignore",
    "README.md",
    "requirements.txt",
    "requirements.in",
    "pytest.ini",
    
    # Scripts de execução
    "streamlit_app.py",
    "INICIAR_STREAMLIT.bat",
    "RUN.bat",
    "RUN_REDE_LOCAL.bat",
    
    # Diretórios essenciais
    ".git",
    ".github",
    ".streamlit",
    ".venv_new",
    "core",
    "config",
    "data",
    "logs",
    "pages",
    "reports",
    "scripts",
    "tests",
    "ui",
    ".mypy_cache"  # Cache do mypy, pode ser útil
}

# Arquivos a REMOVER (documentação temporária e testes na raiz)
to_remove = []

root_dir = "."
for item in os.listdir(root_dir):
    if item not in keep_files:
        to_remove.append(item)

print("Arquivos/diretórios que serão REMOVIDOS da raiz:\n")
for item in sorted(to_remove):
    path = os.path.join(root_dir, item)
    if os.path.isdir(path):
        print(f"  [DIR]  {item}")
    else:
        print(f"  [FILE] {item}")

print(f"\nTotal: {len(to_remove)} itens")

# Criar diretório de backup para documentação
docs_backup = "docs_backup"
if not os.path.exists(docs_backup):
    os.makedirs(docs_backup)
    print(f"\n✅ Criado diretório: {docs_backup}")

# Mover arquivos .md para docs_backup
md_files_moved = 0
for item in to_remove[:]:  # Cópia da lista para modificar durante iteração
    if item.endswith('.md'):
        src = os.path.join(root_dir, item)
        dst = os.path.join(docs_backup, item)
        try:
            shutil.move(src, dst)
            print(f"  Movido: {item} -> {docs_backup}/")
            to_remove.remove(item)
            md_files_moved += 1
        except Exception as e:
            print(f"  Erro ao mover {item}: {e}")

print(f"\n✅ {md_files_moved} arquivos .md movidos para {docs_backup}/")

# Remover arquivos restantes
print("\nRemovendo arquivos restantes...")
removed_count = 0
for item in to_remove:
    path = os.path.join(root_dir, item)
    try:
        if os.path.isdir(path):
            # Não remover diretórios por segurança
            print(f"  ⚠️  Pulado (diretório): {item}")
        else:
            os.remove(path)
            print(f"  ✅ Removido: {item}")
            removed_count += 1
    except Exception as e:
        print(f"  ❌ Erro ao remover {item}: {e}")

print(f"\n✅ Limpeza concluída!")
print(f"   - {md_files_moved} arquivos .md movidos para {docs_backup}/")
print(f"   - {removed_count} arquivos removidos")
print(f"\nA raiz do projeto agora contém apenas arquivos essenciais.")
