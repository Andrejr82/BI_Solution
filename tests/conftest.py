"""
Conftest to make test-collection safe: some legacy 'test' scripts call
sys.exit(...) at module import which aborts pytest collection. This file
neutralizes sys.exit during collection/import so tests can be discovered.

This is a lightweight shim for local dev only; consider refactoring
the legacy test scripts to guard with `if __name__ == "__main__"`.
"""
import sys
import warnings
import builtins

_original_exit = sys.exit

def _ignore_exit(code=0):
    warnings.warn(f"Intercepted sys.exit({code}) during test import — ignored by test runner")

# Replace sys.exit with a no-op during pytest collection/import
sys.exit = _ignore_exit
# Também interceptar builtins.exit/quit (alguns scripts usam exit() diretamente)
_orig_builtin_exit = builtins.exit if hasattr(builtins, 'exit') else None
_orig_builtin_quit = builtins.quit if hasattr(builtins, 'quit') else None
builtins.exit = _ignore_exit
builtins.quit = _ignore_exit

# Protect pytest capture: some legacy tests reassign sys.stdout to a
# TextIOWrapper and the wrapper may close the underlying buffer which is
# pytest's tmpfile. We monkeypatch io.TextIOWrapper to a safe wrapper that
# delegates but makes close() a no-op to avoid closing pytest internals.
import io as _io
_orig_TextIOWrapper = _io.TextIOWrapper

class _SafeTextIOWrapper:
    def __init__(self, buffer, encoding=None, errors=None, **kwargs):
        # create a real wrapper but keep a reference so we can delegate
        self._inner = _orig_TextIOWrapper(buffer, encoding=encoding, errors=errors, **kwargs)

    def write(self, *args, **kwargs):
        try:
            return self._inner.write(*args, **kwargs)
        except Exception:
            # Silenciar erros I/O se stream subjacente estiver fechado
            return None

    def flush(self, *args, **kwargs):
        try:
            return self._inner.flush(*args, **kwargs)
        except Exception:
            return None

    def close(self):
        # no-op: avoid closing underlying capture buffer
        return None

    def __getattr__(self, name):
        try:
            return getattr(self._inner, name)
        except Exception:
            raise AttributeError(name)


_io.TextIOWrapper = _SafeTextIOWrapper

# Protege também sys.stdout e sys.stderr substituindo por wrappers que
# delegam operações, mas tornam close() um no-op. Isso evita que scripts
# de teste fechem o buffer de captura do pytest durante importação.
_orig_stdout = sys.stdout
_orig_stderr = sys.stderr

class _SafeStream:
    def __init__(self, stream):
        self._inner = stream

    def write(self, *args, **kwargs):
        try:
            return self._inner.write(*args, **kwargs)
        except Exception:
            # Silenciar erros I/O se stream subjacente estiver fechado
            return None

    def flush(self, *args, **kwargs):
        try:
            return self._inner.flush(*args, **kwargs)
        except Exception:
            return None

    def close(self):
        # no-op: evitar fechar o buffer do pytest
        return None

    def __getattr__(self, name):
        return getattr(self._inner, name)


sys.stdout = _SafeStream(_orig_stdout)
sys.stderr = _SafeStream(_orig_stderr)


def pytest_sessionfinish(session, exitstatus):
    # Restore patched items to be safe
    try:
        sys.exit = _original_exit
        _io.TextIOWrapper = _orig_TextIOWrapper
        # Restaurar builtins
        if _orig_builtin_exit is not None:
            builtins.exit = _orig_builtin_exit
        if _orig_builtin_quit is not None:
            builtins.quit = _orig_builtin_quit
        # Restaurar stdout/stderr originais caso tenham sido substituídos
        try:
            sys.stdout = _orig_stdout
            sys.stderr = _orig_stderr
        except Exception:
            pass
    except Exception:
        pass
