"""
Módulo de configuração de logging com structured logging (Context7).
Fornece: setup_logging
"""

import logging
import logging.config
import os
import sys
import json
from datetime import datetime
from pathlib import Path

# Tentar importar structlog
try:
    import structlog
    STRUCTLOG_AVAILABLE = True
except ImportError:
    STRUCTLOG_AVAILABLE = False
    structlog = None


def setup_logging(debug_mode: bool = False):
    """
    Configura logging estruturado usando structlog + stdlib.

    Features:
    - JSON output para produção
    - Console colorido para desenvolvimento
    - Thread/processo tracking
    - Contexto automático (func_name, lineno)
    - Rotação de arquivos
    - Performance otimizada

    Args:
        debug_mode: Ativa nível DEBUG (default: False = INFO)
    """
    # Caminhos
    project_root = Path(__file__).parent.parent.parent
    logs_dir = project_root / "logs"
    logs_dir.mkdir(exist_ok=True)

    # Subdiretorios
    activity_log_dir = logs_dir / "app_activity"
    error_log_dir = logs_dir / "errors"
    interaction_log_dir = logs_dir / "user_interactions"

    for d in [activity_log_dir, error_log_dir, interaction_log_dir]:
        d.mkdir(exist_ok=True)

    # Filenames com timestamp
    current_date = datetime.now().strftime("%Y-%m-%d")
    activity_log = activity_log_dir / f"activity_{current_date}.log"
    error_log = error_log_dir / f"error_{current_date}.log"
    interaction_log = interaction_log_dir / f"interactions_{current_date}.log"

    # Level baseado em modo
    log_level = logging.DEBUG if debug_mode else logging.INFO

    if STRUCTLOG_AVAILABLE:
        # ✅ STRUCTURED LOGGING (Context7)
        _setup_structlog(
            activity_log, error_log, interaction_log, log_level
        )
    else:
        # Fallback: logging padrão
        _setup_stdlib_logging(
            activity_log, error_log, interaction_log, log_level
        )


def _setup_structlog(activity_log, error_log, interaction_log, log_level):
    """Configura structlog com Context7 best practices."""

    # Detectar ambiente (terminal vs produção)
    is_terminal = sys.stderr.isatty()

    # Processors compartilhados
    shared_processors = [
        structlog.contextvars.merge_contextvars,
        structlog.stdlib.add_log_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso", utc=False),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        # Adicionar contexto de execução
        structlog.processors.CallsiteParameterAdder(
            [
                structlog.processors.CallsiteParameter.FUNC_NAME,
                structlog.processors.CallsiteParameter.LINENO,
                structlog.processors.CallsiteParameter.THREAD_NAME,
                structlog.processors.CallsiteParameter.PROCESS_NAME,
            ]
        ),
    ]

    # Renderer baseado em ambiente
    if is_terminal:
        # Dev: console colorido
        renderer = structlog.dev.ConsoleRenderer(colors=True)
    else:
        # Prod: JSON + traceback estruturado
        shared_processors.append(structlog.processors.dict_tracebacks)
        renderer = structlog.processors.JSONRenderer()

    # Configurar structlog
    structlog.configure(
        processors=shared_processors + [
            structlog.stdlib.ProcessorFormatter.wrap_for_formatter,
        ],
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )

    # Configurar stdlib handlers com ProcessorFormatter
    timestamper = structlog.processors.TimeStamper(fmt="%Y-%m-%d %H:%M:%S")
    pre_chain = [
        structlog.stdlib.add_log_level,
        structlog.stdlib.ExtraAdder(),
        timestamper,
    ]

    def extract_from_record(_, __, event_dict):
        """Extrai info do LogRecord para event_dict."""
        record = event_dict.get("_record")
        if record:
            event_dict["thread_name"] = record.threadName
            event_dict["process_name"] = record.processName
        return event_dict

    logging.config.dictConfig({
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "json": {
                "()": structlog.stdlib.ProcessorFormatter,
                "processors": [
                    extract_from_record,
                    structlog.stdlib.ProcessorFormatter.remove_processors_meta,
                    structlog.processors.JSONRenderer(),
                ],
                "foreign_pre_chain": pre_chain,
            },
            "colored": {
                "()": structlog.stdlib.ProcessorFormatter,
                "processors": [
                    extract_from_record,
                    structlog.stdlib.ProcessorFormatter.remove_processors_meta,
                    structlog.dev.ConsoleRenderer(colors=True),
                ],
                "foreign_pre_chain": pre_chain,
            },
        },
        "handlers": {
            "console": {
                "level": "DEBUG" if log_level == logging.DEBUG else "INFO",
                "class": "logging.StreamHandler",
                "formatter": "colored",
                "stream": "ext://sys.stdout",
            },
            "activity_file": {
                "level": "INFO",
                "class": "logging.handlers.RotatingFileHandler",
                "formatter": "json",
                "filename": str(activity_log),
                "maxBytes": 10485760,  # 10MB
                "backupCount": 5,
                "encoding": "utf-8",
            },
            "error_file": {
                "level": "ERROR",
                "class": "logging.handlers.RotatingFileHandler",
                "formatter": "json",
                "filename": str(error_log),
                "maxBytes": 10485760,
                "backupCount": 5,
                "encoding": "utf-8",
            },
            "interaction_file": {
                "level": "INFO",
                "class": "logging.handlers.RotatingFileHandler",
                "formatter": "json",
                "filename": str(interaction_log),
                "maxBytes": 10485760,
                "backupCount": 5,
                "encoding": "utf-8",
            },
        },
        "loggers": {
            "user_interaction": {
                "handlers": ["interaction_file"],
                "level": "INFO",
                "propagate": False,
            }
        },
        "root": {
            "handlers": ["console", "activity_file", "error_file"],
            "level": "DEBUG" if log_level == logging.DEBUG else "INFO",
        },
    })

    logging.info("Structured logging (structlog) configurado com sucesso")


def _setup_stdlib_logging(activity_log, error_log, interaction_log, log_level):
    """Fallback: logging padrão sem structlog."""

    LOGGING_CONFIG = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "default": {
                "format": (
                    "%(asctime)s - %(name)s - %(levelname)s - "
                    "%(funcName)s:%(lineno)d - %(message)s"
                ),
                "datefmt": "%Y-%m-%d %H:%M:%S",
            },
            "interaction": {
                "format": "%(asctime)s - %(message)s",
                "datefmt": "%Y-%m-%d %H:%M:%S",
            }
        },
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "formatter": "default",
                "level": "DEBUG" if log_level == logging.DEBUG else "INFO",
            },
            "activity_file": {
                "class": "logging.handlers.RotatingFileHandler",
                "formatter": "default",
                "filename": str(activity_log),
                "maxBytes": 10485760,
                "backupCount": 5,
                "level": "INFO",
                "encoding": "utf-8",
            },
            "error_file": {
                "class": "logging.handlers.RotatingFileHandler",
                "formatter": "default",
                "filename": str(error_log),
                "maxBytes": 10485760,
                "backupCount": 5,
                "level": "ERROR",
                "encoding": "utf-8",
            },
            "interaction_file": {
                "class": "logging.handlers.RotatingFileHandler",
                "formatter": "interaction",
                "filename": str(interaction_log),
                "maxBytes": 10485760,
                "backupCount": 5,
                "level": "INFO",
                "encoding": "utf-8",
            },
        },
        "loggers": {
            "user_interaction": {
                "handlers": ["interaction_file"],
                "level": "INFO",
                "propagate": False,
            }
        },
        "root": {
            "handlers": ["console", "activity_file", "error_file"],
            "level": "DEBUG" if log_level == logging.DEBUG else "INFO",
        },
    }

    logging.config.dictConfig(LOGGING_CONFIG)
    logging.info("Logging padrão configurado (structlog não disponível)")


class _StdlibStructLogAdapter:
    """Adaptador leve que torna um logger stdlib compatível com chamadas
    no estilo `structlog.get_logger().info("msg", key=value)`.

    Em vez de passar kwargs para Logger._log (que pode gerar TypeError),
    formatamos os kwargs como JSON e anexamos à mensagem.
    """

    def __init__(self, base_logger: logging.Logger):
        self._base = base_logger

    def _fmt(self, msg: str, kwargs: dict) -> str:
        if not kwargs:
            return msg
        try:
            meta = json.dumps(kwargs, default=str, ensure_ascii=False)
            return f"{msg} | {meta}"
        except Exception:
            return f"{msg} | {kwargs}"

    def info(self, msg: str, *args, **kwargs) -> None:
        self._base.info(self._fmt(msg, kwargs), *args)

    def warning(self, msg: str, *args, **kwargs) -> None:
        self._base.warning(self._fmt(msg, kwargs), *args)

    def error(self, msg: str, *args, **kwargs) -> None:
        exc = kwargs.pop("exc_info", None)
        self._base.error(self._fmt(msg, kwargs), *args, exc_info=exc)

    def debug(self, msg: str, *args, **kwargs) -> None:
        self._base.debug(self._fmt(msg, kwargs), *args)

    def exception(self, msg: str, *args, **kwargs) -> None:
        self._base.exception(self._fmt(msg, kwargs), *args)


def get_logger(name: str):
    """Retorna um logger compatível com chamadas structlog-style.

    Se `structlog` estiver disponível e a configuração já tiver sido
    aplicada, retorna `structlog.get_logger(name)`. Caso contrário,
    retorna um adaptador leve que evita passar kwargs ao stdlib logger.
    """
    if STRUCTLOG_AVAILABLE and structlog is not None:
        try:
            return structlog.get_logger(name)
        except Exception:
            # Falha segura: fallback para stdlib
            pass

    base = logging.getLogger(name)
    return _StdlibStructLogAdapter(base)
