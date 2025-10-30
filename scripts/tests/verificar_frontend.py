"""
Script para verificar se o frontend está servindo o projeto correto
"""
import urllib.request
import time

def verificar_frontend():
    """Verifica se frontend está servindo Caçulinha"""
    print("="*60)
    print("VERIFICACAO DO FRONTEND")
    print("="*60)

    url = "http://localhost:8080"

    print(f"\n[1/2] Tentando acessar {url}...")

    try:
        # Aguardar um pouco para garantir que o servidor está pronto
        time.sleep(2)

        # Fazer requisição
        response = urllib.request.urlopen(url, timeout=5)
        html = response.read().decode('utf-8')

        print("[OK] Frontend respondendo!")

        print(f"\n[2/2] Verificando conteudo...")

        # Verificar se é o projeto correto (Caçulinha)
        checks = {
            "Agent BI - Lojas Caçula": "Agent BI - Lojas Caçula" in html,
            "Caçulinha": "Caçulinha" in html or "Ca\u00e7ulinha" in html,
            "Business Intelligence": "Business Intelligence" in html,
            "NOT Lovable Badge": "lovable-badge" not in html,  # Não deve ter badge do Lovable
        }

        print("\nResultados:")
        print("-" * 60)

        all_ok = True
        for check_name, result in checks.items():
            status = "[OK]" if result else "[FALHOU]"
            print(f"{status} {check_name}")
            if not result and "NOT" not in check_name:
                all_ok = False
            elif not result and "NOT" in check_name:
                all_ok = False

        print("-" * 60)

        if all_ok:
            print("\n[SUCESSO] Frontend esta servindo o projeto CORRETO (Caçulinha)!")
            print(f"\nAcesse: {url}")
            print("\nO que voce deve ver:")
            print("  - Titulo: Agent BI - Lojas Caçula")
            print("  - Chat com Caçulinha")
            print("  - Metricas de vendas")
            print("  - Sidebar com menu de navegacao")
            return True
        else:
            print("\n[ERRO] Frontend pode estar servindo projeto ERRADO!")
            print("\nVerifique:")
            print("  1. Limpe o cache do navegador (Ctrl+Shift+Del)")
            print("  2. Tente acessar em aba anonima")
            print("  3. Verifique se nao ha outro processo na porta 8080")
            return False

    except urllib.error.URLError as e:
        print(f"[ERRO] Nao foi possivel acessar o frontend: {e}")
        print("\nVerifique se o servidor está rodando:")
        print("  cd frontend")
        print("  npm run dev")
        return False
    except Exception as e:
        print(f"[ERRO] Erro inesperado: {e}")
        return False

if __name__ == "__main__":
    verificar_frontend()
