#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para aplicar correções de logging automaticamente
Execute com: python APLICAR_CORRECOES.py
"""

import sys
import shutil
import os
from pathlib import Path
from datetime import datetime

def print_header(titulo):
    """Imprime header"""
    print("\n" + "="*80)
    print(f"  {titulo}")
    print("="*80 + "\n")

def print_status(status, mensagem):
    """Imprime status com emoji"""
    icons = {
        "OK": "[✓]",
        "ERRO": "[✗]",
        "INFO": "[i]",
        "AVISO": "[!]"
    }
    print(f"{icons.get(status, '[-]')} {mensagem}")

def aplicar_correcao_1():
    """Aplicar Correção 1: Copiar logging_config.py"""
    print_status("INFO", "Correção 1: Copiar LOGGING_CONFIG_NOVO.py para core/config/logging_config.py")

    try:
        src = Path("LOGGING_CONFIG_NOVO.py")
        dst = Path("core/config/logging_config.py")

        if not src.exists():
            print_status("ERRO", f"Arquivo {src} nao encontrado")
            return False

        # Fazer backup do original se existir
        if dst.exists():
            backup = dst.with_suffix(".py.backup")
            shutil.copy2(dst, backup)
            print_status("INFO", f"Backup criado: {backup}")

        # Copiar novo arquivo
        shutil.copy2(src, dst)
        print_status("OK", f"Arquivo copiado: {src} -> {dst}")

        # Verificar
        if dst.exists():
            print_status("OK", f"Verificacao OK: {dst} ({dst.stat().st_size} bytes)")
            return True
        else:
            print_status("ERRO", "Arquivo nao foi copiado")
            return False

    except Exception as e:
        print_status("ERRO", f"Erro ao copiar: {e}")
        return False

def aplicar_correcao_2():
    """Aplicar Correção 2: Adicionar setup_logging() em streamlit_app.py"""
    print_status("INFO", "Correção 2: Adicionar setup_logging() em streamlit_app.py")

    try:
        app_file = Path("streamlit_app.py")

        if not app_file.exists():
            print_status("ERRO", f"Arquivo {app_file} nao encontrado")
            return False

        with open(app_file, 'r', encoding='utf-8') as f:
            conteudo = f.read()

        # Verificar se ja tem setup_logging
        if "setup_logging()" in conteudo:
            print_status("AVISO", "setup_logging() ja presente no arquivo")
            return True

        # Procurar by def main() ou if __name__ == "__main__"
        if "def main():" in conteudo:
            linhas = conteudo.splitlines(keepends=True)

            # Encontrar linha de def main():
            for i, linha in enumerate(linhas):
                if "def main():" in linha:
                    # Adicionar setup_logging() na proxima linha (com indentacao)
                    import_line = 'from core.config.logging_config import setup_logging\n'
                    setup_line = '    setup_logging()\n'

                    # Verificar se import ja existe
                    if 'from core.config.logging_config import setup_logging' not in conteudo:
                        # Adicionar import no inicio
                        if "import" in conteudo.splitlines()[0] or "from" in conteudo.splitlines()[0]:
                            # Adicionar depois do primeiro bloco de imports
                            insert_pos = 0
                            for j, l in enumerate(linhas):
                                if "import" in l or "from" in l:
                                    insert_pos = j + 1
                            linhas.insert(insert_pos, import_line)
                        else:
                            linhas.insert(0, import_line)

                    # Adicionar setup_logging() logo apos def main():
                    linhas.insert(i + 1, setup_line + '\n')

                    # Escrever de volta
                    novo_conteudo = ''.join(linhas)

                    # Backup
                    backup = app_file.with_suffix(".py.backup")
                    shutil.copy2(app_file, backup)
                    print_status("INFO", f"Backup criado: {backup}")

                    # Escrever novo
                    with open(app_file, 'w', encoding='utf-8') as f:
                        f.write(novo_conteudo)

                    print_status("OK", "setup_logging() adicionado com sucesso")
                    return True

            print_status("AVISO", "def main(): nao encontrado no arquivo")
            return False
        else:
            print_status("AVISO", "Estrutura do arquivo nao é familiar")
            return False

    except Exception as e:
        print_status("ERRO", f"Erro ao modificar: {e}")
        return False

def validar_logs():
    """Validar que logs estao funcionando"""
    print_status("INFO", "Validando sistema de logs...")

    try:
        logs_dir = Path("logs")
        if logs_dir.exists():
            log_files = list(logs_dir.glob("*.log"))
            if log_files:
                print_status("OK", f"Diretorio logs/ existe com {len(log_files)} arquivo(s)")
                recent = sorted(log_files, key=lambda x: x.stat().st_mtime, reverse=True)[0]
                print_status("OK", f"Arquivo mais recente: {recent.name}")
                return True
            else:
                print_status("AVISO", "Diretorio logs/ existe mas vazio")
        else:
            print_status("AVISO", "Diretorio logs/ ainda nao foi criado (será criado na primeira execução)")

        return True

    except Exception as e:
        print_status("ERRO", f"Erro ao validar: {e}")
        return False

def main():
    """Executa todas as correcoes"""
    print_header("APLICADOR DE CORRECOES - SISTEMA DE LOGS")

    print_status("INFO", f"Data/Hora: {datetime.now().isoformat()}")
    print_status("INFO", f"Diretorio: {os.getcwd()}")

    # Verificar arquivos necessarios
    if not Path("LOGGING_CONFIG_NOVO.py").exists():
        print_status("ERRO", "LOGGING_CONFIG_NOVO.py nao encontrado!")
        return False

    print("\n" + "="*80)
    print("INICIANDO APLICACAO DE CORRECOES")
    print("="*80 + "\n")

    resultados = {}

    # Correcao 1
    print_status("INFO", "Aplicando Correcao 1...")
    resultados["correcao_1"] = aplicar_correcao_1()

    # Correcao 2
    print_status("INFO", "Aplicando Correcao 2...")
    resultados["correcao_2"] = aplicar_correcao_2()

    # Validar
    print_status("INFO", "Validando...")
    resultados["validacao"] = validar_logs()

    # Resumo
    print("\n" + "="*80)
    print("RESUMO")
    print("="*80 + "\n")

    print_status("INFO", "Resultados:")
    for k, v in resultados.items():
        status = "OK" if v else "ERRO"
        print_status(status, f"{k}: {v}")

    if all(resultados.values()):
        print_status("OK", "TODAS AS CORRECOES APLICADAS COM SUCESSO!")
        print_status("INFO", "Proximo passo: Testar com 'streamlit run streamlit_app.py'")
        return True
    else:
        print_status("ERRO", "Algumas correcoes falharam")
        return False

if __name__ == "__main__":
    sucesso = main()
    sys.exit(0 if sucesso else 1)
