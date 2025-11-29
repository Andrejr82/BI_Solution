#!/usr/bin/env python3
"""
Agent Solution BI - Unified Launcher
====================================

Inicializa toda a stack do sistema:
- Backend FastAPI (port 8000) - Prioridade Alta
- Frontend SolidJS (port 3000) - Prioridade Média

Uso:
    python run.py                    # Inicia tudo
    python run.py --backend-only     # Apenas backend
    python run.py --frontend-only    # Apenas frontend
    python run.py --dev              # Modo desenvolvimento (logs verbosos)

Teclas de Controle:
    Ctrl+C - Encerra todos os processos gracefully
"""

import os
import sys
import time
import signal
import subprocess
import platform
import webbrowser
from pathlib import Path
from typing import Optional, List
from datetime import datetime
import argparse

# Adiciona o diretório raiz ao PYTHONPATH
ROOT_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT_DIR))


class Colors:
    """ANSI color codes para output colorido"""
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

    @staticmethod
    def disable():
        """Desabilita cores no Windows antigo"""
        Colors.HEADER = ''
        Colors.OKBLUE = ''
        Colors.OKCYAN = ''
        Colors.OKGREEN = ''
        Colors.WARNING = ''
        Colors.FAIL = ''
        Colors.ENDC = ''
        Colors.BOLD = ''
        Colors.UNDERLINE = ''


# Desabilita cores se não suportado
if platform.system() == 'Windows':
    try:
        import colorama
        colorama.init()
    except ImportError:
        Colors.disable()


class ProcessManager:
    """Gerenciador de processos do sistema"""

    def __init__(self, dev_mode: bool = False):
        self.processes: List[subprocess.Popen] = []
        self.dev_mode = dev_mode
        self.start_time = datetime.now()

        # Registra handler de sinais
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)

    def _signal_handler(self, sig, frame):
        """Handler para Ctrl+C e kill signals"""
        print(f"\n{Colors.WARNING}⚠️  Recebido sinal de encerramento...{Colors.ENDC}")
        self.shutdown()
        sys.exit(0)

    def log(self, message: str, level: str = "INFO"):
        """Log formatado com timestamp"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        colors = {
            "INFO": Colors.OKBLUE,
            "SUCCESS": Colors.OKGREEN,
            "WARNING": Colors.WARNING,
            "ERROR": Colors.FAIL,
            "HEADER": Colors.HEADER
        }
        color = colors.get(level, "")
        print(f"{color}[{timestamp}] {message}{Colors.ENDC}")

    def check_port(self, port: int) -> bool:
        """Verifica se uma porta está livre"""
        import socket
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            return s.connect_ex(('localhost', port)) != 0

    def kill_process_on_port(self, port: int):
        """Mata o processo que está usando a porta especificada"""
        try:
            if platform.system() == 'Windows':
                # Encontra o PID usando netstat
                cmd = f'netstat -ano | findstr :{port}'
                result = subprocess.check_output(cmd, shell=True).decode()
                
                if result:
                    # Pega o último elemento da linha que é o PID
                    for line in result.splitlines():
                        if "LISTENING" in line:
                            parts = line.strip().split()
                            pid = parts[-1]
                            if pid != "0":
                                self.log(f"Liberando porta {port} (Matando PID {pid})...", "WARNING")
                                subprocess.run(f'taskkill /F /PID {pid}', shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            else:
                # Linux/Mac (lsof)
                cmd = f"lsof -t -i:{port}"
                try:
                    pid = subprocess.check_output(cmd, shell=True).decode().strip()
                    if pid:
                        self.log(f"Liberando porta {port} (Matando PID {pid})...", "WARNING")
                        subprocess.run(f"kill -9 {pid}", shell=True)
                except:
                    pass
                    
            # Aguarda 1 segundo para o SO liberar a porta
            time.sleep(1)

            # Verifica se a porta foi liberada (mas não falha se não foi)
            if self.check_port(port):
                self.log(f"Porta {port} liberada com sucesso", "SUCCESS")
            else:
                self.log(f"Porta {port} pode estar ocupada (ignorando...)", "INFO")
            
        except Exception as e:
            self.log(f"Erro ao liberar porta {port}: {e}", "WARNING")


    def wait_for_port(self, port: int, timeout: int = 30, service: str = "Service") -> bool:
        """Espera até que uma porta esteja respondendo"""
        import socket
        self.log(f"Aguardando {service} iniciar na porta {port}...", "INFO")

        start = time.time()
        while time.time() - start < timeout:
            try:
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                    s.settimeout(1)
                    if s.connect_ex(('localhost', port)) == 0:
                        self.log(f"{service} está respondendo na porta {port}", "SUCCESS")
                        return True
            except:
                pass
            time.sleep(0.5)

        self.log(f"Timeout esperando {service} na porta {port}", "ERROR")
        return False

    def _stream_output(self, process: subprocess.Popen, prefix: str):
        """Streams output from a process to stdout in a separate thread"""
        def reader():
            for line in iter(process.stdout.readline, ''):
                if line:
                    print(f"[{prefix}] {line.strip()}")
            process.stdout.close()

        import threading
        t = threading.Thread(target=reader, daemon=True)
        t.start()

    def start_backend(self) -> Optional[subprocess.Popen]:
        """Inicia o backend FastAPI"""
        self.log("=" * 60, "HEADER")
        self.log("INICIANDO BACKEND FASTAPI (Prioridade Alta)", "HEADER")
        self.log("=" * 60, "HEADER")

        backend_dir = ROOT_DIR / "backend"

        if not backend_dir.exists():
            self.log(f"Diretório backend não encontrado: {backend_dir}", "ERROR")
            return None

        # Tenta liberar porta 8000 se estiver ocupada
        if not self.check_port(8000):
            self.log("Porta 8000 ocupada, tentando liberar...", "WARNING")
            self.kill_process_on_port(8000)
            # Continua mesmo se não conseguir liberar (uvicorn pode forçar)

        # Comando para iniciar backend usando Python do venv Poetry
        backend_venv = backend_dir / ".venv"
        if platform.system() == 'Windows':
            venv_python = backend_venv / "Scripts" / "python.exe"
        else:
            venv_python = backend_venv / "bin" / "python"

        if venv_python.exists():
            # Removido --reload para evitar problemas com subprocess em alguns ambientes, 
            # ou manter se for essencial. Manteremos --reload mas capturando output.
            cmd = [str(venv_python), '-m', 'uvicorn', 'main:app', '--reload', '--host', '127.0.0.1', '--port', '8000']
        else:
            # Fallback para python global (não recomendado)
            self.log("AVISO: venv não encontrado, usando Python global", "WARNING")
            if platform.system() == 'Windows':
                cmd = ['python', '-m', 'uvicorn', 'main:app', '--reload']
            else:
                cmd = ['python3', '-m', 'uvicorn', 'main:app', '--reload']

        self.log(f"Executando: {' '.join(cmd)}", "INFO")
        self.log(f"Diretório: {backend_dir}", "INFO")

        try:
            process = subprocess.Popen(
                cmd,
                cwd=backend_dir,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT, # Redirect stderr to stdout
                text=True,
                bufsize=1,
                universal_newlines=True
            )

            self.processes.append(process)
            self.log(f"Backend iniciado (PID: {process.pid})", "SUCCESS")

            # Inicia streaming de logs
            self._stream_output(process, "BACKEND")

            # Aguarda backend estar pronto
            if self.wait_for_port(8000, timeout=30, service="Backend FastAPI"):
                self.log("Backend URL: http://localhost:8000", "SUCCESS")
                self.log("API Docs: http://localhost:8000/docs", "SUCCESS")
                return process
            else:
                self.log("Backend não respondeu a tempo", "ERROR")
                process.kill()
                return None

        except Exception as e:
            self.log(f"Erro ao iniciar backend: {e}", "ERROR")
            return None

    def start_frontend(self) -> Optional[subprocess.Popen]:
        """Inicia o frontend React"""
        self.log("=" * 60, "HEADER")
        self.log("INICIANDO FRONTEND SOLIDJS (Prioridade Média)", "HEADER")
        self.log("=" * 60, "HEADER")

        # Verifica se Node.js está instalado
        if not self._check_node_installed():
            self.log("Node.js não encontrado no sistema!", "ERROR")
            self.log("Instale Node.js 20+ em: https://nodejs.org/", "ERROR")
            return None

        # Verifica se npm ou pnpm está disponível
        has_npm = self._check_npm_installed()
        has_pnpm = self._has_pnpm()

        if not has_npm and not has_pnpm:
            self.log("npm/pnpm não encontrado no sistema!", "ERROR")
            self.log("Reinstale Node.js ou execute: npm install -g pnpm", "ERROR")
            return None

        frontend_dir = ROOT_DIR / "frontend-solid"

        if not frontend_dir.exists():
            self.log(f"Diretório frontend-solid não encontrado: {frontend_dir}", "ERROR")
            return None

        # Verifica se node_modules existe
        node_modules = frontend_dir / "node_modules"
        if not node_modules.exists():
            self.log("node_modules não encontrado. Executando npm install...", "WARNING")
            install_cmd = ['pnpm', 'install'] if has_pnpm else ['npm', 'install']

            try:
                subprocess.run(install_cmd, cwd=frontend_dir, check=True, shell=True)
                self.log("Dependências instaladas com sucesso", "SUCCESS")
            except subprocess.CalledProcessError:
                self.log("Erro ao instalar dependências do frontend", "ERROR")
                return None

        # Verifica se porta 3000 está livre
        if not self.check_port(3000):
            self.log("Porta 3000 já está em uso!", "ERROR")
            return None

        # Comando para iniciar frontend
        cmd = ['pnpm', 'dev'] if has_pnpm else ['npm', 'run', 'dev']

        self.log(f"Executando: {' '.join(cmd)}", "INFO")
        self.log(f"Diretório: {frontend_dir}", "INFO")

        try:
            # Define variável de ambiente para o frontend usar a URL correta
            env = os.environ.copy()
            env['NEXT_PUBLIC_API_URL'] = 'http://127.0.0.1:8000'
            process = subprocess.Popen(
                cmd,
                cwd=frontend_dir,
                env=env,
                stdout=subprocess.PIPE if not self.dev_mode else None,
                stderr=subprocess.PIPE if not self.dev_mode else None,
                text=True,
                bufsize=1,
                universal_newlines=True,
                shell=True  # Necessário no Windows para encontrar npm/pnpm no PATH
            )

            self.processes.append(process)
            self.log(f"Frontend iniciado (PID: {process.pid})", "SUCCESS")

            # Aguarda frontend estar pronto (Next.js demora mais)
            if self.wait_for_port(3000, timeout=60, service="Frontend SolidJS"):
                self.log("Frontend URL: http://localhost:3000", "SUCCESS")

                # Abre automaticamente o navegador
                try:
                    time.sleep(2)  # Aguarda 2s para garantir que está estável
                    self.log("Abrindo navegador automaticamente...", "INFO")

                    # Limpa localStorage antes de abrir o navegador
                    # A função já abre o navegador com um HTML temporário
                    self._clear_browser_storage()

                    self.log("Navegador aberto em http://localhost:3000", "SUCCESS")
                except Exception as e:
                    self.log(f"Erro ao abrir navegador: {e}", "WARNING")
                    self.log("Acesse manualmente: http://localhost:3000", "INFO")

                return process
            else:
                self.log("Frontend não respondeu a tempo", "WARNING")
                self.log("Pode estar ainda compilando. Aguarde mais alguns segundos.", "INFO")
                return process

        except Exception as e:
            self.log(f"Erro ao iniciar frontend: {e}", "ERROR")
            return None

    def _has_pnpm(self) -> bool:
        """Verifica se pnpm está disponível"""
        try:
            subprocess.run(['pnpm', '--version'],
                         stdout=subprocess.DEVNULL,
                         stderr=subprocess.DEVNULL,
                         check=True,
                         shell=True)
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            return False

    def _check_node_installed(self) -> bool:
        """Verifica se Node.js está instalado"""
        try:
            subprocess.run(['node', '--version'],
                         stdout=subprocess.DEVNULL,
                         stderr=subprocess.DEVNULL,
                         check=True,
                         shell=True)
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            return False

    def _check_npm_installed(self) -> bool:
        """Verifica se npm está instalado"""
        try:
            subprocess.run(['npm', '--version'],
                         stdout=subprocess.DEVNULL,
                         stderr=subprocess.DEVNULL,
                         check=True,
                         shell=True)
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            return False

    def _clear_browser_storage(self):
        """
        Cria um arquivo HTML temporário que limpa o localStorage
        antes de redirecionar para a aplicação
        """
        try:
            import tempfile

            # HTML que limpa localStorage e redireciona
            html_content = """<!DOCTYPE html>
<html>
<head>
    <title>Limpando cache...</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            display: flex;
            justify-content: center;
            align-items: center;
            height: 100vh;
            margin: 0;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
        }
        .container {
            text-align: center;
        }
        .spinner {
            border: 4px solid rgba(255, 255, 255, 0.3);
            border-top: 4px solid white;
            border-radius: 50%;
            width: 40px;
            height: 40px;
            animation: spin 1s linear infinite;
            margin: 20px auto;
        }
        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
    </style>
</head>
<body>
    <div class="container">
        <h2>Agent Solution BI</h2>
        <div class="spinner"></div>
        <p>Limpando cache e iniciando...</p>
    </div>
    <script>
        // Limpa localStorage
        localStorage.clear();
        sessionStorage.clear();

        // Aguarda 1 segundo e redireciona
        setTimeout(() => {
            window.location.href = 'http://localhost:3000';
        }, 1000);
    </script>
</body>
</html>"""

            # Cria arquivo temporário
            with tempfile.NamedTemporaryFile(mode='w', suffix='.html', delete=False, encoding='utf-8') as f:
                f.write(html_content)
                temp_file = f.name

            self.log("Cache do navegador será limpo automaticamente", "INFO")

            # Abre o arquivo temporário ao invés da URL direta
            webbrowser.open(f'file:///{temp_file.replace(os.sep, "/")}')

            # Agenda limpeza do arquivo temporário após 10 segundos
            def cleanup_temp_file():
                time.sleep(10)
                try:
                    os.unlink(temp_file)
                except:
                    pass

            import threading
            cleanup_thread = threading.Thread(target=cleanup_temp_file, daemon=True)
            cleanup_thread.start()

        except Exception as e:
            self.log(f"Aviso: Não foi possível limpar cache automaticamente: {e}", "WARNING")

    def monitor_processes(self):
        """Monitora processos em execução"""
        self.log("=" * 60, "HEADER")
        self.log("SISTEMA INICIADO COM SUCESSO!", "SUCCESS")
        self.log("=" * 60, "HEADER")

        uptime = (datetime.now() - self.start_time).total_seconds()
        self.log(f"Tempo de inicialização: {uptime:.2f}s", "INFO")
        self.log("", "INFO")
        self.log("Pressione Ctrl+C para encerrar todos os processos", "WARNING")
        self.log("", "INFO")

        try:
            while True:
                time.sleep(1)

                # Verifica se algum processo morreu
                for i, proc in enumerate(self.processes):
                    if proc.poll() is not None:
                        self.log(f"Processo {i} (PID {proc.pid}) encerrou inesperadamente!", "ERROR")
                        self.shutdown()
                        sys.exit(1)

        except KeyboardInterrupt:
            pass

    def shutdown(self):
        """Encerra todos os processos gracefully"""
        self.log("=" * 60, "WARNING")
        self.log("ENCERRANDO SISTEMA...", "WARNING")
        self.log("=" * 60, "WARNING")

        for i, proc in enumerate(self.processes):
            try:
                self.log(f"Encerrando processo {i} (PID {proc.pid})...", "INFO")
                proc.terminate()

                # Aguarda até 5 segundos para encerramento graceful
                try:
                    proc.wait(timeout=5)
                    self.log(f"Processo {i} encerrado gracefully", "SUCCESS")
                except subprocess.TimeoutExpired:
                    self.log(f"Processo {i} não respondeu, forçando encerramento...", "WARNING")
                    proc.kill()
                    proc.wait()
                    self.log(f"Processo {i} forçadamente encerrado", "WARNING")

            except Exception as e:
                self.log(f"Erro ao encerrar processo {i}: {e}", "ERROR")

        uptime = (datetime.now() - self.start_time).total_seconds()
        self.log(f"Sistema rodou por {uptime:.2f}s", "INFO")
        self.log("Sistema encerrado", "SUCCESS")


def print_banner():
    """Imprime banner do sistema"""
    banner = f"""
{Colors.OKBLUE}================================================================

            {Colors.BOLD}AGENT SOLUTION BI - UNIFIED LAUNCHER{Colors.ENDC}{Colors.OKBLUE}

  Arquitetura: SolidJS (Frontend) + FastAPI (Backend) + Core
  LLM: Gemini 2.5 Flash | Data: Parquet + SQL Server

================================================================{Colors.ENDC}
"""
    print(banner)


def main():
    """Função principal"""
    parser = argparse.ArgumentParser(
        description="Agent Solution BI - Unified Launcher",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemplos de uso:
  python run.py                    # Inicia backend + frontend
  python run.py --backend-only     # Apenas backend
  python run.py --frontend-only    # Apenas frontend
  python run.py --dev              # Modo desenvolvimento (logs verbosos)
        """
    )

    parser.add_argument('--backend-only', action='store_true',
                       help='Inicia apenas o backend FastAPI')
    parser.add_argument('--frontend-only', action='store_true',
                       help='Inicia apenas o frontend SolidJS')
    parser.add_argument('--dev', action='store_true',
                       help='Modo desenvolvimento (logs verbosos)')

    args = parser.parse_args()

    # Validação
    if args.backend_only and args.frontend_only:
        print(f"{Colors.FAIL}Erro: Não é possível usar --backend-only e --frontend-only juntos{Colors.ENDC}")
        sys.exit(1)

    print_banner()

    # Inicializa gerenciador
    manager = ProcessManager(dev_mode=args.dev)

    # Limpeza preventiva de portas
    manager.log("Verificando portas...", "INFO")
    if not args.frontend_only:
        manager.kill_process_on_port(8000)
    if not args.backend_only:
        manager.kill_process_on_port(3000)

    # Inicia serviços
    if not args.frontend_only:
        backend = manager.start_backend()
        if not backend and not args.backend_only:
            manager.log("Falha ao iniciar backend, abortando...", "ERROR")
            manager.shutdown()
            sys.exit(1)

    if not args.backend_only:
        frontend = manager.start_frontend()
        # Frontend pode falhar em iniciar mas continuar rodando
        if not frontend:
            manager.log("Frontend não iniciou, mas backend está rodando", "WARNING")

    # Monitora processos
    manager.monitor_processes()

    # Encerra gracefully
    manager.shutdown()


if __name__ == "__main__":
    main()
