"""
Script auxiliar para rodar o teste de 80 perguntas com 100% LLM
"""

import sys
from pathlib import Path

# Adicionar o diretório raiz ao path
root_dir = Path(__file__).parent.parent
sys.path.insert(0, str(root_dir))

def main():
    """Executa o teste de 80 perguntas com 100% LLM"""
    print("=" * 80)
    print("SCRIPT AUXILIAR - TESTE DE 80 PERGUNTAS COM 100% LLM")
    print("=" * 80)
    print(f"\nDiretório raiz: {root_dir}")
    print(f"Python: {sys.version}")

    # Carregar .env
    print("\nCarregando variáveis de ambiente...")
    import os
    from pathlib import Path

    # Tentar carregar dotenv se disponível
    try:
        from dotenv import load_dotenv
        env_file = root_dir / '.env'
        if env_file.exists():
            load_dotenv(env_file)
            print(f"[OK] Arquivo .env carregado de {env_file}")
        else:
            print(f"[WARN] Arquivo .env não encontrado em {env_file}")
    except ImportError:
        print("[WARN] python-dotenv não instalado, tentando usar variáveis do sistema...")

    # Verificar variáveis de ambiente
    print("\nVerificando configuração...")

    # Verificar chaves de API
    gemini_key = os.getenv('GEMINI_API_KEY')
    deepseek_key = os.getenv('DEEPSEEK_API_KEY')

    if gemini_key:
        print("[OK] GEMINI_API_KEY configurada")
    else:
        print("[WARN] GEMINI_API_KEY não encontrada")

    if deepseek_key:
        print("[OK] DEEPSEEK_API_KEY configurada")
    else:
        print("[WARN] DEEPSEEK_API_KEY não encontrada")

    if not gemini_key and not deepseek_key:
        print("\n[ERRO] Nenhuma API key encontrada!")
        print("Configure pelo menos uma das seguintes variáveis de ambiente:")
        print("  - GEMINI_API_KEY")
        print("  - DEEPSEEK_API_KEY")
        return 1

    # Importar e executar o teste
    print("\nImportando módulo de teste...")
    try:
        from test_80_perguntas_llm import executar_teste
        print("[OK] Módulo importado com sucesso")
    except ImportError as e:
        print(f"[ERRO] Falha ao importar módulo de teste: {e}")
        import traceback
        traceback.print_exc()
        return 1

    # Executar teste
    print("\n" + "=" * 80)
    print("INICIANDO TESTE COM 100% LLM")
    print("=" * 80)
    print("\n[AVISO] Este teste vai consumir tokens da API!")
    print("[AVISO] Estimativa: ~5000-10000 tokens para 80 perguntas")
    print("\nPressione Ctrl+C para cancelar nos próximos 5 segundos...")

    try:
        import time
        for i in range(5, 0, -1):
            print(f"Iniciando em {i}...", end='\r')
            time.sleep(1)
        print("\nIniciando teste!                    \n")
    except KeyboardInterrupt:
        print("\n\n[CANCELADO] Teste cancelado pelo usuário")
        return 0

    try:
        relatorio = executar_teste()

        if relatorio:
            print("\n" + "=" * 80)
            print("TESTE CONCLUÍDO COM SUCESSO!")
            print("=" * 80)

            # Mostrar resumo de tokens
            total_tokens = relatorio['estatisticas'].get('total_tokens_estimados', 0)
            media_tokens = relatorio['estatisticas'].get('media_tokens_pergunta', 0)

            print(f"\n[RESUMO DE CUSTOS]")
            print(f"Total de tokens estimados: {total_tokens:,}")
            print(f"Média por pergunta: {media_tokens:.1f} tokens")

            # Estimativa de custo (valores aproximados)
            # Gemini: ~$0.001 / 1K tokens
            # DeepSeek: ~$0.0001 / 1K tokens
            custo_gemini = (total_tokens / 1000) * 0.001
            custo_deepseek = (total_tokens / 1000) * 0.0001

            print(f"\nEstimativa de custo:")
            print(f"  Gemini: ~${custo_gemini:.4f}")
            print(f"  DeepSeek: ~${custo_deepseek:.4f}")

            return 0
        else:
            print("\n" + "=" * 80)
            print("TESTE FALHOU - Verifique os logs acima")
            print("=" * 80)
            return 1

    except KeyboardInterrupt:
        print("\n\n[CANCELADO] Teste interrompido pelo usuário")
        return 0
    except Exception as e:
        print(f"\n[ERRO CRÍTICO] Exceção durante execução: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
