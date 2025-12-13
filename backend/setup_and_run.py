#!/usr/bin/env python3
"""
Backend Setup and Run Script
Automatically configures virtual environment and starts the FastAPI server
"""
import os
import sys
import subprocess
import venv
from pathlib import Path

# Colors for Windows console
try:
    import colorama
    colorama.init()
    GREEN = '\033[92m'
    BLUE = '\033[94m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    RESET = '\033[0m'
except ImportError:
    GREEN = BLUE = YELLOW = RED = RESET = ''


def log(message, color=BLUE):
    """Print colored log message"""
    print(f"{color}[BACKEND]{RESET} {message}")


def check_python_version():
    """Verify Python version is 3.11+"""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 11):
        log(f"[ERRO] Python 3.11+ required. Current: {version.major}.{version.minor}", RED)
        sys.exit(1)
    log(f"[OK] Python {version.major}.{version.minor}.{version.micro} detected", GREEN)


def get_venv_path():
    """Get virtual environment path"""
    backend_dir = Path(__file__).parent
    return backend_dir / ".venv"


def get_venv_python():
    """Get Python executable from venv"""
    venv_path = get_venv_path()
    if sys.platform == "win32":
        return venv_path / "Scripts" / "python.exe"
    return venv_path / "bin" / "python"


def venv_is_valid():
    """Check if venv exists and is functional"""
    python_exe = get_venv_python()

    if not python_exe.exists():
        return False

    # Try to run python --version
    try:
        result = subprocess.run(
            [str(python_exe), "--version"],
            capture_output=True,
            timeout=5
        )
        return result.returncode == 0
    except Exception:
        return False


def create_venv():
    """Create virtual environment"""
    venv_path = get_venv_path()

    log("Creating virtual environment (this may take a minute)...", YELLOW)

    # Remove old venv if corrupted
    if venv_path.exists():
        log("Removing old/corrupted venv...", YELLOW)
        import shutil
        shutil.rmtree(venv_path, ignore_errors=True)

    # Create new venv using subprocess (more reliable than venv module)
    try:
        result = subprocess.run(
            [sys.executable, "-m", "venv", str(venv_path)],
            check=True,
            capture_output=True,
            text=True,
            timeout=120  # 2 minutes timeout
        )
        log("[OK] Virtual environment created successfully", GREEN)
        return True
    except subprocess.TimeoutExpired:
        log("[ERRO] Timeout creating virtual environment (took >2 minutes)", RED)
        return False
    except subprocess.CalledProcessError as e:
        log(f"[ERRO] Failed to create venv: {e}", RED)
        if e.stderr:
            log(f"Error details: {e.stderr}", RED)
        return False
    except Exception as e:
        log(f"[ERRO] Unexpected error creating venv: {e}", RED)
        return False


def install_dependencies():
    """Install Python dependencies from requirements.txt"""
    backend_dir = Path(__file__).parent
    requirements_file = backend_dir / "requirements.txt"

    if not requirements_file.exists():
        log("[AVISO] requirements.txt not found, skipping dependency installation", YELLOW)
        return True

    log("Installing dependencies (this may take a few minutes)...", YELLOW)

    python_exe = get_venv_python()

    try:
        # Upgrade pip first
        subprocess.run(
            [str(python_exe), "-m", "pip", "install", "--upgrade", "pip"],
            check=True,
            capture_output=True
        )

        # Install requirements
        result = subprocess.run(
            [str(python_exe), "-m", "pip", "install", "-r", str(requirements_file)],
            check=True,
            cwd=str(backend_dir)
        )

        log("[OK] Dependencies installed successfully", GREEN)
        return True

    except subprocess.CalledProcessError as e:
        log(f"[ERRO] Failed to install dependencies: {e}", RED)
        return False


def start_server():
    """Start the FastAPI server using uvicorn"""
    backend_dir = Path(__file__).parent
    python_exe = get_venv_python()

    log("=" * 60, BLUE)
    log("Starting FastAPI server...", GREEN)
    log("=" * 60, BLUE)
    log("", BLUE)
    log("Backend URL: http://localhost:8000", GREEN)
    log("API Docs:    http://localhost:8000/docs", GREEN)
    log("", BLUE)
    log("Press Ctrl+C to stop the server", YELLOW)
    log("=" * 60, BLUE)

    # Start uvicorn (reload disabled to fix Windows multiprocessing issues)
    try:
        subprocess.run(
            [
                str(python_exe),
                "-m",
                "uvicorn",
                "main:app",
                "--host",
                "0.0.0.0",
                "--port",
                "8000"
            ],
            cwd=str(backend_dir),
            check=True
        )
    except KeyboardInterrupt:
        log("\n[INFO] Server stopped by user", YELLOW)
    except subprocess.CalledProcessError as e:
        log(f"[ERRO] Server failed: {e}", RED)
        sys.exit(1)


def main():
    """Main entry point"""
    log("=" * 60, BLUE)
    log("BACKEND SETUP AND RUN", BLUE)
    log("=" * 60, BLUE)

    # Check Python version
    check_python_version()

    # Check/create venv
    if not venv_is_valid():
        log("Virtual environment not found or invalid", YELLOW)
        if not create_venv():
            log("Failed to create virtual environment", RED)
            sys.exit(1)

        # Install dependencies
        if not install_dependencies():
            log("Failed to install dependencies, but continuing...", YELLOW)
    else:
        log("[OK] Virtual environment is ready", GREEN)

    # Start server
    start_server()


if __name__ == "__main__":
    main()
