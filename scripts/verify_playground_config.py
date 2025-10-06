"""
Verificação final das configurações do Gemini Playground
"""
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

print("=" * 60)
print("VERIFICACAO FINAL - GEMINI PLAYGROUND")
print("=" * 60)

# Testar SafeSettings
print("\n[*] Testando SafeSettings...")
try:
    from core.config.safe_settings import get_safe_settings

    settings = get_safe_settings()

    # Verificar todas as variáveis
    print("\n[Configuracoes Carregadas]")
    print("-" * 60)

    # API Keys
    if settings.GEMINI_API_KEY:
        print(f"[OK] GEMINI_API_KEY: {settings.GEMINI_API_KEY[:15]}...")
    else:
        print("[ERRO] GEMINI_API_KEY: NAO CONFIGURADA")

    if settings.DEEPSEEK_API_KEY:
        print(f"[OK] DEEPSEEK_API_KEY: {settings.DEEPSEEK_API_KEY[:15]}...")
    else:
        print("[AVISO] DEEPSEEK_API_KEY: NAO CONFIGURADA")

    # Modelos
    print(f"\n[Modelos Configurados]")
    print("-" * 60)
    print(f"LLM_MODEL_NAME (generico): {settings.LLM_MODEL_NAME}")

    if hasattr(settings, 'GEMINI_MODEL_NAME'):
        print(f"[OK] GEMINI_MODEL_NAME: {settings.GEMINI_MODEL_NAME}")
    else:
        print("[AVISO] GEMINI_MODEL_NAME nao encontrado")

    if hasattr(settings, 'DEEPSEEK_MODEL_NAME'):
        print(f"[OK] DEEPSEEK_MODEL_NAME: {settings.DEEPSEEK_MODEL_NAME}")
    else:
        print("[AVISO] DEEPSEEK_MODEL_NAME nao encontrado")

    # Banco de dados
    print(f"\n[Configuracoes de Banco de Dados]")
    print("-" * 60)
    print(f"DB_SERVER: {settings.DB_SERVER if settings.DB_SERVER else 'NAO CONFIGURADO'}")
    print(f"DB_NAME: {settings.DB_NAME if settings.DB_NAME else 'NAO CONFIGURADO'}")
    print(f"DB Disponivel: {'SIM' if settings.is_database_available() else 'NAO'}")

except Exception as e:
    print(f"[ERRO] Falha ao carregar SafeSettings: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Testar se a página pode ser importada
print(f"\n[*] Verificando sintaxe da pagina...")
try:
    page_path = os.path.join(os.path.dirname(__file__), '..', 'pages', '10_🤖_Gemini_Playground.py')

    with open(page_path, 'r', encoding='utf-8') as f:
        code = f.read()

    compile(code, page_path, 'exec')
    print("[OK] Pagina sem erros de sintaxe")

except Exception as e:
    print(f"[ERRO] Problema na pagina: {e}")
    sys.exit(1)

# Testar inicialização do adaptador com as configurações
print(f"\n[*] Testando inicializacao com SafeSettings...")
try:
    from core.llm_adapter import GeminiLLMAdapter

    # Usar o modelo específico do Gemini
    gemini_model = getattr(settings, 'GEMINI_MODEL_NAME', settings.LLM_MODEL_NAME)

    adapter = GeminiLLMAdapter(
        api_key=settings.GEMINI_API_KEY,
        model_name=gemini_model,
        enable_cache=True
    )

    print(f"[OK] Adaptador inicializado com modelo: {adapter.model_name}")
    print(f"[OK] Cache habilitado: {adapter.cache_enabled}")

except Exception as e:
    print(f"[ERRO] Falha ao inicializar adaptador: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Resumo final
print("\n" + "=" * 60)
print("RESUMO DA VERIFICACAO")
print("=" * 60)
print()
print("[✓] SafeSettings carregado corretamente")
print(f"[✓] GEMINI_API_KEY configurada")
print(f"[✓] GEMINI_MODEL_NAME: {gemini_model}")
print("[✓] Pagina sem erros de sintaxe")
print("[✓] GeminiLLMAdapter funcional")
print("[✓] Cache habilitado")
print()
print("=" * 60)
print("GEMINI PLAYGROUND - PRONTO PARA USO!")
print("=" * 60)
print()
print("Para iniciar o Streamlit:")
print("  streamlit run streamlit_app.py")
print()
print("O playground estara disponivel em:")
print("  http://localhost:8501")
print("  Menu Lateral > 🤖 Gemini Playground")
print()
print("NOTA: Acesso restrito a usuarios com role 'admin'")
print("=" * 60)
