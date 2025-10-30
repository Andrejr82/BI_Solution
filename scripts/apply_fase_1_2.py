"""
Script de Integração - FASE 1.2
================================
Data: 2025-10-29

Aplica a FASE 1.2 (Fallback para queries amplas) no sistema principal.

Tarefas:
1. Backup do arquivo atual
2. Aplicar nova versão
3. Executar testes
4. Validar integração
"""

import os
import shutil
from pathlib import Path
from datetime import datetime
import subprocess
import sys


def print_header(title):
    """Imprime cabeçalho formatado."""
    print("\n" + "=" * 80)
    print(f"  {title}")
    print("=" * 80 + "\n")


def backup_current_file():
    """Faz backup do arquivo atual."""
    print_header("PASSO 1: Backup do Arquivo Atual")

    current_file = Path("core/agents/code_gen_agent.py")

    if not current_file.exists():
        print("⚠️  Arquivo code_gen_agent.py não encontrado. Criando novo...")
        return False

    # Criar diretório de backups se não existir
    backup_dir = Path("backups/code_gen_agent")
    backup_dir.mkdir(parents=True, exist_ok=True)

    # Nome do backup com timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_file = backup_dir / f"code_gen_agent_before_fase_1_2_{timestamp}.py"

    try:
        shutil.copy2(current_file, backup_file)
        print(f"✅ Backup criado: {backup_file}")
        return True
    except Exception as e:
        print(f"❌ Erro ao criar backup: {e}")
        return False


def apply_new_version():
    """Aplica a nova versão com FASE 1.2."""
    print_header("PASSO 2: Aplicar Nova Versão")

    source_file = Path("core/agents/code_gen_agent_fase_1_2.py")
    target_file = Path("core/agents/code_gen_agent.py")

    if not source_file.exists():
        print(f"❌ Arquivo fonte não encontrado: {source_file}")
        return False

    try:
        shutil.copy2(source_file, target_file)
        print(f"✅ Nova versão aplicada: {target_file}")
        print("   Versão: 2.1.0 - FASE 1.2 - Fallback para queries amplas")
        return True
    except Exception as e:
        print(f"❌ Erro ao aplicar nova versão: {e}")
        return False


def run_tests():
    """Executa os testes da FASE 1.2."""
    print_header("PASSO 3: Executar Testes")

    test_script = Path("scripts/test_broad_query_detection.py")

    if not test_script.exists():
        print(f"❌ Script de teste não encontrado: {test_script}")
        return False

    try:
        print("🧪 Executando bateria de testes...\n")
        result = subprocess.run(
            [sys.executable, str(test_script)],
            capture_output=True,
            text=True,
            timeout=30
        )

        print(result.stdout)

        if result.stderr:
            print("⚠️  Erros/avisos durante os testes:")
            print(result.stderr)

        if result.returncode == 0:
            print("\n✅ Todos os testes passaram!")
            return True
        else:
            print(f"\n❌ Testes falharam com código: {result.returncode}")
            return False

    except subprocess.TimeoutExpired:
        print("❌ Timeout ao executar testes (> 30s)")
        return False
    except Exception as e:
        print(f"❌ Erro ao executar testes: {e}")
        return False


def validate_integration():
    """Valida se a integração foi bem-sucedida."""
    print_header("PASSO 4: Validar Integração")

    target_file = Path("core/agents/code_gen_agent.py")

    if not target_file.exists():
        print("❌ Arquivo code_gen_agent.py não encontrado")
        return False

    # Verificar se contém código da FASE 1.2
    try:
        with open(target_file, "r", encoding="utf-8") as f:
            content = f.read()

        # Verificações de conteúdo
        checks = [
            ("FASE 1.2", "Marcador de versão"),
            ("detect_broad_query", "Método de detecção"),
            ("BROAD_QUERY_KEYWORDS", "Constante de keywords"),
            ("log_broad_query", "Método de logging"),
            ("get_educational_message", "Método de mensagem educativa"),
        ]

        all_ok = True
        for keyword, description in checks:
            if keyword in content:
                print(f"✅ {description}: OK")
            else:
                print(f"❌ {description}: NÃO ENCONTRADO")
                all_ok = False

        if all_ok:
            print("\n✅ Integração validada com sucesso!")
            return True
        else:
            print("\n❌ Integração incompleta. Verifique o arquivo.")
            return False

    except Exception as e:
        print(f"❌ Erro ao validar integração: {e}")
        return False


def show_next_steps():
    """Mostra os próximos passos."""
    print_header("PRÓXIMOS PASSOS")

    print("""
📋 Checklist Pós-Integração:

1. ✅ Testar via Streamlit UI
   - Executar: streamlit run streamlit_app.py
   - Testar query ampla: "Mostre todos os produtos"
   - Verificar mensagem educativa

2. ✅ Monitorar log de detecções
   - Arquivo: data/learning/broad_queries_detected.jsonl
   - Verificar estatísticas após algumas queries

3. ✅ Validar redução de timeouts
   - Comparar erros antes/depois (1 semana)
   - Meta: 60% de redução

4. ✅ Ajustar se necessário
   - Revisar falsos positivos/negativos
   - Ajustar keywords se necessário

📊 Monitoramento Sugerido:

- Executar diariamente por 1 semana
- Coletar estatísticas com: agent.get_broad_query_statistics()
- Revisar queries bloqueadas
- Ajustar thresholds se taxa de falsos positivos > 10%

📚 Documentação:

- Relatório completo: docs/RELATORIO_FASE_1_2_FALLBACK_QUERIES_AMPLAS.md
- Código fonte: core/agents/code_gen_agent.py
- Testes: scripts/test_broad_query_detection.py
""")


def main():
    """Função principal de integração."""
    print("""
╔═══════════════════════════════════════════════════════════════════════════╗
║                                                                           ║
║   INTEGRAÇÃO DA FASE 1.2 - FALLBACK PARA QUERIES AMPLAS                 ║
║                                                                           ║
║   Objetivo: Reduzir 60% dos erros de timeout através de detecção        ║
║            proativa e educação do usuário                                ║
║                                                                           ║
╚═══════════════════════════════════════════════════════════════════════════╝
""")

    # Executar passos
    steps = [
        ("Backup", backup_current_file),
        ("Aplicar Nova Versão", apply_new_version),
        ("Executar Testes", run_tests),
        ("Validar Integração", validate_integration),
    ]

    results = []
    for step_name, step_func in steps:
        try:
            result = step_func()
            results.append((step_name, result))

            if not result:
                print(f"\n⚠️  Passo '{step_name}' falhou. Abortando integração.")
                print("\nVerifique os erros acima e tente novamente.")
                return False

        except Exception as e:
            print(f"\n❌ Erro inesperado no passo '{step_name}': {e}")
            return False

    # Resumo final
    print_header("RESUMO DA INTEGRAÇÃO")

    all_ok = all(result for _, result in results)

    for step_name, result in results:
        status = "✅ OK" if result else "❌ FALHOU"
        print(f"{status} - {step_name}")

    if all_ok:
        print("\n" + "=" * 80)
        print("🎉 FASE 1.2 INTEGRADA COM SUCESSO!")
        print("=" * 80)
        show_next_steps()
        return True
    else:
        print("\n" + "=" * 80)
        print("❌ INTEGRAÇÃO FALHOU")
        print("=" * 80)
        print("\nVerifique os erros acima e consulte a documentação.")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
