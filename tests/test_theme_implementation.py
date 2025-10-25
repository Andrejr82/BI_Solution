"""
Script de teste para validar implementação do tema ChatGPT
Data: 20/10/2025
"""

import os
import sys

def test_config_toml():
    """Testa se .streamlit/config.toml existe e tem as configurações corretas"""
    print("=" * 60)
    print("1. Testando .streamlit/config.toml...")
    print("=" * 60)

    config_path = os.path.join(os.getcwd(), ".streamlit", "config.toml")

    if not os.path.exists(config_path):
        print("❌ ERRO: .streamlit/config.toml não encontrado!")
        return False

    with open(config_path, 'r', encoding='utf-8') as f:
        content = f.read()

    required_settings = [
        'primaryColor = "#10a37f"',
        'backgroundColor = "#343541"',
        'secondaryBackgroundColor = "#444654"',
        'textColor = "#ececf1"'
    ]

    missing = []
    for setting in required_settings:
        if setting not in content:
            missing.append(setting)

    if missing:
        print(f"❌ ERRO: Configurações faltando:")
        for m in missing:
            print(f"   - {m}")
        return False

    print("✅ .streamlit/config.toml configurado corretamente!")
    return True

def test_streamlit_css():
    """Testa se streamlit_app.py tem o CSS customizado"""
    print("\n" + "=" * 60)
    print("2. Testando CSS customizado em streamlit_app.py...")
    print("=" * 60)

    streamlit_path = os.path.join(os.getcwd(), "streamlit_app.py")

    if not os.path.exists(streamlit_path):
        print("❌ ERRO: streamlit_app.py não encontrado!")
        return False

    with open(streamlit_path, 'r', encoding='utf-8') as f:
        content = f.read()

    required_css = [
        "CSS CUSTOMIZADO - TEMA CHATGPT",
        "--bg-primary: #343541",
        "--bg-sidebar: #202123",
        "--color-primary: #10a37f",
        "section[data-testid=\"stSidebar\"]",
        ".stChatMessage"
    ]

    missing = []
    for css in required_css:
        if css not in content:
            missing.append(css)

    if missing:
        print(f"❌ ERRO: CSS faltando:")
        for m in missing:
            print(f"   - {m}")
        return False

    print("✅ CSS customizado aplicado em streamlit_app.py!")
    return True

def test_plotly_theme():
    """Testa se code_gen_agent.py aplica tema escuro nos gráficos"""
    print("\n" + "=" * 60)
    print("3. Testando tema Plotly em code_gen_agent.py...")
    print("=" * 60)

    codegen_path = os.path.join(os.getcwd(), "core", "agents", "code_gen_agent.py")

    if not os.path.exists(codegen_path):
        print("❌ ERRO: code_gen_agent.py não encontrado!")
        return False

    with open(codegen_path, 'r', encoding='utf-8') as f:
        content = f.read()

    required_theme = [
        "APLICAR TEMA ESCURO CHATGPT",
        "plot_bgcolor='#2a2b32'",
        "paper_bgcolor='#2a2b32'",
        "font=dict(color='#ececf1'"
    ]

    missing = []
    for theme in required_theme:
        if theme not in content:
            missing.append(theme)

    if missing:
        print(f"❌ ERRO: Tema Plotly faltando:")
        for m in missing:
            print(f"   - {m}")
        return False

    print("✅ Tema Plotly aplicado em code_gen_agent.py!")
    return True

def test_page_12_theme():
    """Testa se página 12 tem tema Plotly"""
    print("\n" + "=" * 60)
    print("4. Testando tema Plotly em páginas...")
    print("=" * 60)

    page12_path = os.path.join(os.getcwd(), "pages", "12_📊_Sistema_Aprendizado.py")

    if not os.path.exists(page12_path):
        print("❌ ERRO: 12_📊_Sistema_Aprendizado.py não encontrado!")
        return False

    with open(page12_path, 'r', encoding='utf-8') as f:
        content = f.read()

    required_theme = [
        "Aplicar tema escuro ChatGPT",
        "plot_bgcolor='#2a2b32'",
        "paper_bgcolor='#2a2b32'"
    ]

    missing = []
    for theme in required_theme:
        if theme not in content:
            missing.append(theme)

    if missing:
        print(f"❌ ERRO: Tema Plotly faltando na página 12:")
        for m in missing:
            print(f"   - {m}")
        return False

    print("✅ Tema Plotly aplicado na página 12!")
    return True

def test_backup():
    """Testa se backup foi criado"""
    print("\n" + "=" * 60)
    print("5. Testando backup...")
    print("=" * 60)

    backup_path = os.path.join(os.getcwd(), "backup_before_ui_implementation")

    if not os.path.exists(backup_path):
        print("❌ AVISO: Diretório de backup não encontrado!")
        return False

    required_files = ["streamlit_app.py"]
    missing = []

    for file in required_files:
        if not os.path.exists(os.path.join(backup_path, file)):
            missing.append(file)

    if missing:
        print(f"⚠️ AVISO: Alguns backups faltando:")
        for m in missing:
            print(f"   - {m}")
    else:
        print("✅ Backup criado com sucesso!")

    return True

def main():
    """Executa todos os testes"""
    print("\n")
    print("TESTE DE IMPLEMENTACAO DO TEMA CHATGPT")
    print("Data: 20/10/2025")
    print("\n")

    results = []

    results.append(("Config TOML", test_config_toml()))
    results.append(("CSS Streamlit", test_streamlit_css()))
    results.append(("Tema Plotly (Core)", test_plotly_theme()))
    results.append(("Tema Plotly (Páginas)", test_page_12_theme()))
    results.append(("Backup", test_backup()))

    print("\n" + "=" * 60)
    print("RESUMO DOS TESTES")
    print("=" * 60)

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for name, result in results:
        status = "✅ PASSOU" if result else "❌ FALHOU"
        print(f"{name:30} {status}")

    print("\n" + "=" * 60)
    print(f"RESULTADO FINAL: {passed}/{total} testes passaram")
    print("=" * 60)

    if passed == total:
        print("\nSUCESSO! Todos os testes passaram!")
        print("\nProximos passos:")
        print("   1. Execute: streamlit run streamlit_app.py")
        print("   2. Navegue pelas 12 paginas")
        print("   3. Teste uma query com grafico")
        print("   4. Verifique as cores do tema escuro")
        return 0
    else:
        print("\nATENCAO! Alguns testes falharam!")
        print("\nVerifique os erros acima antes de continuar.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
