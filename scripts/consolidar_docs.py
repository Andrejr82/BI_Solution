"""
Script de consolidação de documentação.
Move arquivos .md obsoletos para archive com segurança.
"""

import os
import shutil
from pathlib import Path

# Diretório base
BASE_DIR = Path(__file__).parent

# Estrutura de destino
ARCHIVE_BASE = BASE_DIR / "docs" / "archive_2025-10-26"

# Arquivos a manter na raiz
MANTER = [
    "README.md",
    "START_AQUI.md",
    "GUIA_USO_COMPLETO.md",
    "RELATORIO_TESTES_COMPLETO.md",
    "LEIA_ME_PRIMEIRO.md",
    "CONSOLIDACAO_DOCUMENTACAO.md"  # Este relatório
]

# Mapeamento: arquivo -> pasta destino
MOVER = {
    # READMEs antigos
    "readme": [
        "README_OLD.md",
        "README_PROJETO_COMPLETO.md",
        "README_REACT_INTEGRATION.md",
        "README_NOVO.md"  # Já foi renomeado para README.md
    ],

    # Quick Starts duplicados
    "quickstart": [
        "QUICK_START.md",
        "QUICK_START_ATUALIZADO.md",
        "COMECE_AQUI.md",
        "INICIAR_AQUI.md",
        "ABRIR_AGORA.md"
    ],

    # Implementações antigas
    "implementation": [
        "SUMARIO_IMPLEMENTACAO_FASTAPI.md",
        "INTEGRACAO_CLAUDE_SHARE_BUDDY.md",
        "ARQUITETURA_MULTI_INTERFACE.md",
        "INSTALACAO_COMPLETA.md"
    ],

    # Fixes já aplicados
    "fixes": [
        "FIX_AUTENTICACAO.md",
        "FIX_FINAL_BCRYPT.md",
        "FIX_DUAS_INTERFACES.md",
        "FIX_INTERFACE_CORES.md",
        "FIX_MENSAGEM_LOGIN.md",
        "SOLUCAO_CACHE.md",
        "SOLUCAO_ERRO_MEMORIA.md",
        "PROBLEMA_RESOLVIDO.md"
    ],

    # Guias obsoletos
    "guides": [
        "GUIA_REACT_COMPLETO.md",
        "SOLUCOES_IMPLEMENTADAS.md",
        "DOCUMENTACAO_LAUNCHER.md",
        "COMO_USAR.md",
        "RESUMO_FINAL_COMPLETO.md",
        "RESUMO_FINAL_REACT.md",
        "RESULTADOS_TESTES.md"
    ],

    # Melhorias recentes (já documentadas)
    "melhorias": [
        "CORRECOES_LLM_METRICAS_LOGO.md",
        "INSTRUCOES_LOGO_NOVA.md",
        "LOGO_CHAT_ATUALIZADA.md",
        "SOLUCAO_SATURACAO_BUFFER.md",
        "RESTAURADO_STREAMLIT.md",
        "INTERFACE_RESTAURADA.md",
        "INTERFACE_LOGIN_CORRETA.md",
        "INTEGRACAO_AUTH_STREAMLIT.md",
        "MELHORIAS_FINAIS.md"
    ]
}

# Arquivos a deletar (obsoletos)
DELETAR = [
    "PROXIMOS_PASSOS.md"
]

def criar_estrutura():
    """Cria estrutura de pastas archive"""
    print("=" * 80)
    print("CRIANDO ESTRUTURA DE PASTAS")
    print("=" * 80)

    for pasta in MOVER.keys():
        destino = ARCHIVE_BASE / pasta
        destino.mkdir(parents=True, exist_ok=True)
        print(f"[OK] Pasta criada: {destino.name}/")

    print()

def mover_arquivos():
    """Move arquivos para archive"""
    print("=" * 80)
    print("MOVENDO ARQUIVOS")
    print("=" * 80)

    total_movidos = 0

    for pasta, arquivos in MOVER.items():
        destino_pasta = ARCHIVE_BASE / pasta

        for arquivo in arquivos:
            origem = BASE_DIR / arquivo
            destino = destino_pasta / arquivo

            if origem.exists():
                try:
                    shutil.move(str(origem), str(destino))
                    print(f"[MOVIDO] {arquivo} -> archive_2025-10-26/{pasta}/")
                    total_movidos += 1
                except Exception as e:
                    print(f"[ERRO] {arquivo}: {e}")
            else:
                print(f"[SKIP] {arquivo} (nao encontrado)")

    print()
    print(f"Total movidos: {total_movidos} arquivos")
    print()

def deletar_arquivos():
    """Deleta arquivos obsoletos"""
    print("=" * 80)
    print("DELETANDO ARQUIVOS OBSOLETOS")
    print("=" * 80)

    total_deletados = 0

    for arquivo in DELETAR:
        origem = BASE_DIR / arquivo

        if origem.exists():
            try:
                origem.unlink()
                print(f"[DELETADO] {arquivo}")
                total_deletados += 1
            except Exception as e:
                print(f"[ERRO] {arquivo}: {e}")
        else:
            print(f"[SKIP] {arquivo} (nao encontrado)")

    print()
    print(f"Total deletados: {total_deletados} arquivos")
    print()

def renomear_readme():
    """Renomeia README_NOVO.md para README.md"""
    print("=" * 80)
    print("RENOMEANDO README PRINCIPAL")
    print("=" * 80)

    origem = BASE_DIR / "README_NOVO.md"
    destino = BASE_DIR / "README.md"

    if origem.exists():
        # Fazer backup do README.md atual se existir
        if destino.exists():
            backup = BASE_DIR / "docs" / "archive_2025-10-26" / "readme" / "README_OLD_BACKUP.md"
            shutil.copy(str(destino), str(backup))
            print(f"[BACKUP] README.md -> {backup.name}")

        # Renomear
        shutil.move(str(origem), str(destino))
        print(f"[OK] README_NOVO.md -> README.md")
    else:
        print(f"[SKIP] README_NOVO.md nao encontrado")

    print()

def listar_restantes():
    """Lista arquivos .md restantes na raiz"""
    print("=" * 80)
    print("ARQUIVOS .MD RESTANTES NA RAIZ")
    print("=" * 80)

    arquivos_md = sorted(BASE_DIR.glob("*.md"))

    if arquivos_md:
        for arquivo in arquivos_md:
            print(f"  - {arquivo.name}")
        print()
        print(f"Total: {len(arquivos_md)} arquivos")
    else:
        print("Nenhum arquivo .md encontrado")

    print()

def main():
    """Executa consolidação completa"""
    print("\n")
    print("=" * 80)
    print("CONSOLIDACAO DE DOCUMENTACAO")
    print("=" * 80)
    print()

    # 1. Criar estrutura
    criar_estrutura()

    # 2. Renomear README
    renomear_readme()

    # 3. Mover arquivos
    mover_arquivos()

    # 4. Deletar obsoletos
    deletar_arquivos()

    # 5. Listar restantes
    listar_restantes()

    print("=" * 80)
    print("[CONCLUIDO] CONSOLIDACAO FINALIZADA COM SUCESSO")
    print("=" * 80)
    print()
    print("Proximos passos:")
    print("1. Verificar pasta docs/archive_2025-10-26/")
    print("2. Confirmar que apenas arquivos essenciais estao na raiz")
    print("3. Ler CONSOLIDACAO_DOCUMENTACAO.md para detalhes")

if __name__ == "__main__":
    main()
