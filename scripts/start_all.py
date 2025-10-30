"""
Agent Solution BI - Launcher Único
Inicia todas as interfaces do sistema
Data: 2025-10-25
"""

import subprocess
import sys
import os
import time
import webbrowser
from pathlib import Path

# Configurar encoding UTF-8 para Windows
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

# Cores para terminal
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    MAGENTA = '\033[95m'
    END = '\033[0m'
    BOLD = '\033[1m'

def print_header():
    """Imprime cabeçalho"""
    print(f"\n{Colors.CYAN}{'='*70}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.MAGENTA}🤖 Agent Solution BI - Launcher{Colors.END}")
    print(f"{Colors.CYAN}{'='*70}{Colors.END}\n")

def print_success(msg):
    """Mensagem de sucesso"""
    print(f"{Colors.GREEN}✓ {msg}{Colors.END}")

def print_error(msg):
    """Mensagem de erro"""
    print(f"{Colors.RED}✗ {msg}{Colors.END}")

def print_info(msg):
    """Mensagem de informação"""
    print(f"{Colors.BLUE}ℹ {msg}{Colors.END}")

def print_warning(msg):
    """Mensagem de aviso"""
    print(f"{Colors.YELLOW}⚠ {msg}{Colors.END}")

def check_dependencies():
    """Verifica dependências necessárias"""
    print(f"\n{Colors.BOLD}[1/3] Verificando dependências...{Colors.END}")

    deps = {
        'fastapi': 'FastAPI',
        'uvicorn': 'Uvicorn',
        'streamlit': 'Streamlit'
    }

    missing = []
    for module, name in deps.items():
        try:
            __import__(module)
            print_success(f"{name} instalado")
        except ImportError:
            print_error(f"{name} NÃO instalado")
            missing.append(module)

    if missing:
        print_error(f"\nFaltam dependências: {', '.join(missing)}")
        print_info("Execute: pip install -r requirements.txt")
        return False

    return True

def check_env():
    """Verifica variáveis de ambiente"""
    print(f"\n{Colors.BOLD}[2/3] Verificando configuração...{Colors.END}")

    from dotenv import load_dotenv
    load_dotenv()

    has_key = False
    if os.getenv("GEMINI_API_KEY"):
        print_success("GEMINI_API_KEY configurada")
        has_key = True
    elif os.getenv("DEEPSEEK_API_KEY"):
        print_success("DEEPSEEK_API_KEY configurada")
        has_key = True
    else:
        print_error("Nenhuma API KEY configurada!")
        print_info("Crie arquivo .env com: GEMINI_API_KEY=sua_chave")
        return False

    return True

def show_menu():
    """Mostra menu de opções"""
    print(f"\n{Colors.BOLD}[3/3] Escolha a interface:{Colors.END}\n")

    options = [
        ("1", "🎨 React Frontend", "Interface moderna e profissional (14 páginas)"),
        ("2", "⚡ Streamlit", "Interface rápida para prototipagem"),
        ("3", "🔌 API FastAPI", "Apenas API REST com documentação"),
        ("4", "🚀 TODAS (React + Streamlit + API)", "Inicia as 3 interfaces simultaneamente"),
        ("5", "❌ Sair", "")
    ]

    for num, title, desc in options:
        print(f"{Colors.CYAN}{num}.{Colors.END} {Colors.BOLD}{title}{Colors.END}")
        if desc:
            print(f"   {Colors.YELLOW}{desc}{Colors.END}")
        print()

    choice = input(f"{Colors.BOLD}Escolha (1-5): {Colors.END}").strip()
    return choice

def start_api():
    """Inicia API FastAPI"""
    print_info("Iniciando API FastAPI na porta 5000...")
    print_info("  (Isso pode levar ate 40 segundos...)")

    process = subprocess.Popen(
        [sys.executable, "api_server.py"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )

    # Aguardar inicialização e verificar se API está respondendo
    max_wait = 90  # 90 segundos no máximo (API demora ~30s)
    start_time = time.time()
    api_ready = False
    attempt = 0

    while (time.time() - start_time) < max_wait:
        attempt += 1
        elapsed = int(time.time() - start_time)

        if process.poll() is not None:
            print_error("Processo da API encerrou inesperadamente!")
            return None

        # Tentar conectar na API
        try:
            import urllib.request
            response = urllib.request.urlopen("http://localhost:5000/api/health", timeout=3)
            if response.status == 200:
                api_ready = True
                break
        except Exception as e:
            # Mostrar progresso a cada 10 segundos
            if elapsed > 0 and elapsed % 10 == 0 and attempt % 5 == 1:
                print_info(f"  Aguardando... ({elapsed}s/90s)")
            pass

        time.sleep(2)

    if api_ready:
        elapsed = int(time.time() - start_time)
        print_success(f"API FastAPI iniciada em {elapsed}s!")
        print_info("  → http://localhost:5000")
        print_info("  → http://localhost:5000/docs (Swagger)")
        return process
    else:
        print_error("Timeout aguardando API iniciar!")
        process.terminate()
        return None

def start_streamlit():
    """Inicia Streamlit"""
    print_info("Iniciando Streamlit na porta 8501...")

    process = subprocess.Popen(
        [sys.executable, "-m", "streamlit", "run", "streamlit_app.py"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )

    # Aguardar inicialização
    time.sleep(5)

    if process.poll() is None:
        print_success("Streamlit iniciado!")
        print_info("  → http://localhost:8501")
        return process
    else:
        print_error("Erro ao iniciar Streamlit!")
        return None

def start_react():
    """Inicia React Frontend"""
    print_info("Verificando Node.js...")

    # Determinar comando npm (Windows usa .cmd)
    npm_cmd = "npm.cmd" if os.name == 'nt' else "npm"

    # Verificar se npm está disponível
    try:
        result = subprocess.run(
            [npm_cmd, "--version"],
            capture_output=True,
            text=True,
            timeout=5,
            shell=True  # Necessário no Windows
        )
        if result.returncode != 0:
            print_error("npm não encontrado! Instale Node.js primeiro.")
            return None
    except Exception as e:
        print_error(f"Erro ao verificar npm: {e}")
        return None

    frontend_path = Path("frontend")

    # Verificar se node_modules existe
    if not (frontend_path / "node_modules").exists():
        print_warning("Dependências do frontend não instaladas!")
        print_info("Instalando dependências (isso pode demorar)...")

        result = subprocess.run(
            [npm_cmd, "install"],
            shell=True,
            cwd=str(frontend_path),
            capture_output=True,
            text=True
        )

        if result.returncode != 0:
            print_error("Erro ao instalar dependências!")
            print(result.stderr)
            return None

        print_success("Dependências instaladas!")

    print_info("Iniciando React Frontend na porta 8080...")

    process = subprocess.Popen(
        [npm_cmd, "run", "dev"],
        cwd=str(frontend_path),
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        shell=True  # Necessário no Windows
    )

    # Aguardar inicialização
    time.sleep(5)

    if process.poll() is None:
        print_success("React Frontend iniciado!")
        print_info("  → http://localhost:8080")
        return process
    else:
        print_error("Erro ao iniciar React!")
        return None

def open_browser(url):
    """Abre navegador"""
    try:
        webbrowser.open(url)
    except:
        pass

def main():
    """Função principal"""
    print_header()

    # Verificações
    if not check_dependencies():
        sys.exit(1)

    if not check_env():
        sys.exit(1)

    # Menu
    choice = show_menu()

    processes = []

    try:
        if choice == "1":
            # React + API
            print(f"\n{Colors.BOLD}Iniciando React + API...{Colors.END}\n")

            api_proc = start_api()
            if api_proc:
                processes.append(api_proc)
                time.sleep(2)

            react_proc = start_react()
            if react_proc:
                processes.append(react_proc)
                time.sleep(3)
                open_browser("http://localhost:8080")

        elif choice == "2":
            # Streamlit
            print(f"\n{Colors.BOLD}Iniciando Streamlit...{Colors.END}\n")

            streamlit_proc = start_streamlit()
            if streamlit_proc:
                processes.append(streamlit_proc)
                time.sleep(3)
                open_browser("http://localhost:8501")

        elif choice == "3":
            # API apenas
            print(f"\n{Colors.BOLD}Iniciando API...{Colors.END}\n")

            api_proc = start_api()
            if api_proc:
                processes.append(api_proc)
                time.sleep(3)
                open_browser("http://localhost:5000/docs")

        elif choice == "4":
            # TODAS
            print(f"\n{Colors.BOLD}Iniciando TODAS as interfaces...{Colors.END}\n")

            # 1. API
            api_proc = start_api()
            if api_proc:
                processes.append(api_proc)
                time.sleep(2)

            # 2. Streamlit
            streamlit_proc = start_streamlit()
            if streamlit_proc:
                processes.append(streamlit_proc)
                time.sleep(2)

            # 3. React
            react_proc = start_react()
            if react_proc:
                processes.append(react_proc)
                time.sleep(3)

            # Abrir navegador no React
            open_browser("http://localhost:8080")

        elif choice == "5":
            print_info("Saindo...")
            sys.exit(0)

        else:
            print_error("Opção inválida!")
            sys.exit(1)

        # Se chegou aqui, algo foi iniciado
        if processes:
            print(f"\n{Colors.GREEN}{'='*70}{Colors.END}")
            print(f"{Colors.BOLD}{Colors.GREEN}✓ Sistema iniciado com sucesso!{Colors.END}")
            print(f"{Colors.GREEN}{'='*70}{Colors.END}\n")

            print(f"{Colors.BOLD}Interfaces disponíveis:{Colors.END}")
            if any("api_server.py" in str(p.args) for p in processes):
                print(f"  • API FastAPI: {Colors.CYAN}http://localhost:5000{Colors.END}")
                print(f"    Docs: {Colors.CYAN}http://localhost:5000/docs{Colors.END}")

            if any("streamlit" in str(p.args) for p in processes):
                print(f"  • Streamlit: {Colors.CYAN}http://localhost:8501{Colors.END}")

            if any("npm" in str(p.args) for p in processes):
                print(f"  • React: {Colors.CYAN}http://localhost:8080{Colors.END}")

            print(f"\n{Colors.YELLOW}Pressione Ctrl+C para encerrar todos os serviços{Colors.END}\n")

            # Manter vivo
            try:
                while True:
                    time.sleep(1)
                    # Verificar se algum processo morreu
                    for proc in processes:
                        if proc.poll() is not None:
                            print_error(f"Um processo foi encerrado inesperadamente!")
            except KeyboardInterrupt:
                print(f"\n\n{Colors.YELLOW}Encerrando serviços...{Colors.END}")

    except KeyboardInterrupt:
        print(f"\n\n{Colors.YELLOW}Encerrando serviços...{Colors.END}")

    finally:
        # Encerrar todos os processos
        for proc in processes:
            try:
                proc.terminate()
                proc.wait(timeout=5)
            except:
                proc.kill()

        print_success("Todos os serviços foram encerrados.")
        print(f"\n{Colors.CYAN}{'='*70}{Colors.END}")
        print(f"{Colors.BOLD}Obrigado por usar Agent Solution BI!{Colors.END}")
        print(f"{Colors.CYAN}{'='*70}{Colors.END}\n")

if __name__ == "__main__":
    main()
