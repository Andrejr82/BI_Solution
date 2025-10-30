"""
Script de reorganização da raiz do projeto.
Move arquivos para pastas apropriadas mantendo arquivos críticos.
"""

import os
import shutil
from pathlib import Path

BASE_DIR = Path(__file__).parent

# Arquivos CRÍTICOS que NÃO devem ser movidos (ficam na raiz)
MANTER_RAIZ = [
    # Entrada do sistema
    "streamlit_app.py",
    "api_server.py",
    "start_all.py",
    "start.bat",
    "start.sh",

    # Configuração
    ".env",
    ".env.example",
    ".gitignore",
    "requirements.txt",
    "requirements.in",
    "pytest.ini",

    # Documentação essencial
    "README.md",
    "START_AQUI.md",
    "GUIA_USO_COMPLETO.md",
    "RELATORIO_TESTES_COMPLETO.md",
    "LEIA_ME_PRIMEIRO.md",
    "CONSOLIDACAO_DOCUMENTACAO.md",

    # Este script
    "reorganizar_raiz.py",
    "consolidar_docs.py"
]

# Mapeamento: arquivo -> destino
MOVER = {
    # Scripts de teste
    "scripts/tests": [
        "test_integration.py",
        "test_simple.py",
        "test_launcher.py",
        "test_funcional_api.py",
        "test_frontend.py",
        "test_query_optimizer.py",
        "verificacao_final.py",
        "verificar_frontend.py",
        "validar_sistema.py"
    ],

    # Scripts utilitários
    "scripts/utils": [
        "kill_port_8080.py",
        "processar_logo_chat.py",
        "salvar_logo_nova.py"
    ],

    # Launchers alternativos
    "scripts/launchers": [
        "iniciar_sistema_completo.bat",
        "iniciar_streamlit.bat",
        "limpar_cache_streamlit.bat"
    ],

    # Launchers React obsoletos
    "scripts/launchers/deprecated": [
        "INICIAR_LIMPO.bat",
        "start_react_system.bat",
        "start_react_system_fixed.bat"
    ],

    # Arquivos TXT duplicados
    "docs/archive_txt": [
        "LEIA_ME_PRIMEIRO.txt",
        "FAZER_AGORA.txt",
        "COMECE_AQUI_STREAMLIT.txt",
        "CONFIRMACAO_FINAL.txt"
    ]
}

# Arquivos a deletar
DELETAR = [
    "nul"
]

def criar_estrutura():
    """Cria estrutura de pastas"""
    print("=" * 80)
    print("CRIANDO ESTRUTURA DE PASTAS")
    print("=" * 80)

    for pasta in MOVER.keys():
        destino = BASE_DIR / pasta
        destino.mkdir(parents=True, exist_ok=True)
        print(f"[OK] {pasta}/")

    print()

def mover_arquivos():
    """Move arquivos para pastas apropriadas"""
    print("=" * 80)
    print("MOVENDO ARQUIVOS")
    print("=" * 80)

    total_movidos = 0

    for pasta, arquivos in MOVER.items():
        destino_pasta = BASE_DIR / pasta

        for arquivo in arquivos:
            origem = BASE_DIR / arquivo
            destino = destino_pasta / arquivo

            if origem.exists():
                try:
                    shutil.move(str(origem), str(destino))
                    print(f"[MOVIDO] {arquivo}")
                    print(f"         -> {pasta}/")
                    total_movidos += 1
                except Exception as e:
                    print(f"[ERRO] {arquivo}: {e}")
            else:
                print(f"[SKIP] {arquivo} (nao encontrado)")

    print()
    print(f"Total movidos: {total_movidos} arquivos")
    print()

def deletar_arquivos():
    """Deleta arquivos temporários/vazios"""
    print("=" * 80)
    print("DELETANDO ARQUIVOS TEMPORARIOS")
    print("=" * 80)

    total_deletados = 0

    for arquivo in DELETAR:
        origem = BASE_DIR / arquivo

        if origem.exists():
            try:
                if origem.is_file():
                    origem.unlink()
                    print(f"[DELETADO] {arquivo}")
                    total_deletados += 1
                else:
                    print(f"[SKIP] {arquivo} (e um diretorio)")
            except Exception as e:
                print(f"[ERRO] {arquivo}: {e}")
        else:
            print(f"[SKIP] {arquivo} (nao encontrado)")

    print()
    print(f"Total deletados: {total_deletados} arquivos")
    print()

def listar_raiz():
    """Lista arquivos restantes na raiz"""
    print("=" * 80)
    print("ARQUIVOS RESTANTES NA RAIZ")
    print("=" * 80)

    arquivos = []
    pastas = []

    for item in sorted(BASE_DIR.iterdir()):
        if item.name.startswith('.'):
            continue
        if item.is_file():
            arquivos.append(item.name)
        elif item.is_dir():
            pastas.append(item.name + "/")

    print("\nARQUIVOS:")
    for arquivo in arquivos:
        critico = "[CRITICO]" if arquivo in MANTER_RAIZ else "[OUTRO]"
        print(f"  {critico} {arquivo}")

    print(f"\nTotal arquivos: {len(arquivos)}")
    print(f"  - Criticos: {sum(1 for a in arquivos if a in MANTER_RAIZ)}")
    print(f"  - Outros: {sum(1 for a in arquivos if a not in MANTER_RAIZ)}")

    print("\nPASTAS:")
    for pasta in pastas[:10]:  # Primeiras 10
        print(f"  {pasta}")
    if len(pastas) > 10:
        print(f"  ... e mais {len(pastas)-10} pastas")

    print()

def criar_relatorio():
    """Cria relatório da reorganização"""
    print("=" * 80)
    print("CRIANDO RELATORIO")
    print("=" * 80)

    relatorio = BASE_DIR / "REORGANIZACAO_RAIZ.md"

    with open(relatorio, "w", encoding="utf-8") as f:
        f.write("# Reorganização da Raiz do Projeto\n\n")
        f.write("**Data:** 2025-10-26\n\n")
        f.write("## Arquivos Movidos\n\n")

        for pasta, arquivos in MOVER.items():
            f.write(f"### {pasta}/\n")
            for arquivo in arquivos:
                origem = BASE_DIR / arquivo
                if not origem.exists():
                    f.write(f"- {arquivo} ✅\n")
            f.write("\n")

        f.write("## Arquivos Mantidos na Raiz\n\n")
        f.write("### Críticos (Entrada do Sistema)\n")
        f.write("- streamlit_app.py ⭐\n")
        f.write("- api_server.py ⭐\n")
        f.write("- start_all.py ⭐\n")
        f.write("- start.bat / start.sh\n\n")

        f.write("### Configuração\n")
        f.write("- .env, .env.example\n")
        f.write("- requirements.txt, requirements.in\n")
        f.write("- .gitignore, pytest.ini\n\n")

        f.write("### Documentação\n")
        f.write("- README.md\n")
        f.write("- START_AQUI.md\n")
        f.write("- GUIA_USO_COMPLETO.md\n")
        f.write("- RELATORIO_TESTES_COMPLETO.md\n")
        f.write("- LEIA_ME_PRIMEIRO.md\n\n")

        f.write("## Nova Estrutura\n\n")
        f.write("```\n")
        f.write("raiz/\n")
        f.write("├── streamlit_app.py (ENTRADA)\n")
        f.write("├── api_server.py (ENTRADA)\n")
        f.write("├── start_all.py (ENTRADA)\n")
        f.write("├── scripts/\n")
        f.write("│   ├── tests/\n")
        f.write("│   ├── utils/\n")
        f.write("│   └── launchers/\n")
        f.write("└── docs/\n")
        f.write("    └── archive_txt/\n")
        f.write("```\n")

    print(f"[OK] REORGANIZACAO_RAIZ.md criado")
    print()

def main():
    """Executa reorganização completa"""
    print("\n")
    print("=" * 80)
    print("REORGANIZACAO DA RAIZ DO PROJETO")
    print("=" * 80)
    print()
    print("ATENCAO: Arquivos de entrada do sistema serao MANTIDOS na raiz:")
    print("  - streamlit_app.py")
    print("  - api_server.py")
    print("  - start_all.py")
    print("  - start.bat / start.sh")
    print()

    # 1. Criar estrutura
    criar_estrutura()

    # 2. Mover arquivos
    mover_arquivos()

    # 3. Deletar temporários
    deletar_arquivos()

    # 4. Listar raiz
    listar_raiz()

    # 5. Criar relatório
    criar_relatorio()

    print("=" * 80)
    print("[CONCLUIDO] REORGANIZACAO FINALIZADA")
    print("=" * 80)
    print()
    print("Proximos passos:")
    print("1. Verificar que sistema ainda funciona")
    print("2. Testar: streamlit run streamlit_app.py")
    print("3. Testar: python start_all.py")
    print("4. Ler REORGANIZACAO_RAIZ.md")

if __name__ == "__main__":
    main()
