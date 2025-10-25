"""
Configuração de Logging Estruturado
- Logs estruturados em logs/activity_YYYY-MM-DD.log
- Logs de aprendizado em data/learning/ (gerenciados separadamente)
- Suporte a Plano A com tracking de filtros e performance

Inicialização: Chamada automática via importação + manual em entry points
"""

import logging
import logging.handlers
from pathlib import Path
from datetime import datetime
import json
import sys


def setup_logging(log_level=logging.DEBUG):
    """
    Inicializa o sistema de logging estruturado.

    Args:
        log_level: Nível de logging (padrão: DEBUG)

    Returns:
        logger configurado

    Cria:
        - logs/activity_YYYY-MM-DD.log (logs estruturados)
        - logs/activity_YYYY-MM-DD.log.1, .2, etc (backup)
    """

    try:
        # Criar diretórios
        logs_dir = Path("logs")
        logs_dir.mkdir(exist_ok=True, parents=True)

        data_dir = Path("data")
        data_dir.mkdir(exist_ok=True, parents=True)

        learning_dir = data_dir / "learning"
        learning_dir.mkdir(exist_ok=True, parents=True)

    except Exception as e:
        print(f"[LOGGING] Erro ao criar diretórios: {e}", file=sys.stderr)
        return logging.getLogger()

    # Obter logger raiz
    logger = logging.getLogger()

    # Limpar handlers existentes para evitar duplicação
    for handler in logger.handlers[:]:
        handler.close()
        logger.removeHandler(handler)

    logger.setLevel(log_level)

    # Formato padrão
    formatter = logging.Formatter(
        '%(asctime)s | %(levelname)-8s | %(name)-20s | %(funcName)s:%(lineno)d | %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    try:
        # Handler para arquivo com rotação
        today = datetime.now().strftime("%Y-%m-%d")
        log_file = logs_dir / f"activity_{today}.log"

        file_handler = logging.handlers.RotatingFileHandler(
            str(log_file),
            maxBytes=10 * 1024 * 1024,  # 10 MB
            backupCount=5,
            encoding='utf-8'
        )
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    except Exception as e:
        print(f"[LOGGING] Erro ao criar file handler: {e}", file=sys.stderr)

    try:
        # Handler para console
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

    except Exception as e:
        print(f"[LOGGING] Erro ao criar console handler: {e}", file=sys.stderr)

    # Log inicial
    logger.info("=" * 80)
    logger.info("SISTEMA DE LOGGING INICIALIZADO")
    logger.info(f"Timestamp: {datetime.now().isoformat()}")
    logger.info(f"Log file: {logs_dir / f'activity_{today}.log'}")
    logger.info("=" * 80)

    return logger


def get_logger(name, level=logging.DEBUG):
    """
    Retorna logger com nome específico.

    Args:
        name: Nome do logger (ex: '__name__')
        level: Nível de logging

    Returns:
        logger configurado
    """
    logger = logging.getLogger(name)
    logger.setLevel(level)
    return logger


def log_plano_a_load_data(filters, source="unknown"):
    """
    Log estruturado para load_data com filtros (Plano A)

    Args:
        filters: dict com filtros aplicados
        source: origem da requisição
    """
    logger = get_logger("plano_a.load_data")
    logger.info(f"LOAD_DATA_INICIADO | source={source} | filtros={len(filters)} | detalhes={json.dumps(filters, default=str)}")


def log_plano_a_performance(duration_ms, rows_loaded, query_type="unknown"):
    """
    Log de performance do Plano A

    Args:
        duration_ms: duração em milissegundos
        rows_loaded: quantidade de linhas carregadas
        query_type: tipo de query
    """
    logger = get_logger("plano_a.performance")
    logger.info(f"PERFORMANCE | query_type={query_type} | duration_ms={duration_ms} | rows={rows_loaded}")


def log_plano_a_fallback(reason, original_filter=None):
    """
    Log quando Plano A faz fallback

    Args:
        reason: razão do fallback
        original_filter: filtro original que falhou
    """
    logger = get_logger("plano_a.fallback")
    logger.warning(f"FALLBACK_ACIONADO | reason={reason} | original_filter={original_filter}")


# Auto-inicializar se importado
_initialized = False
if not _initialized:
    try:
        if not logging.root.handlers:
            setup_logging()
            _initialized = True
    except Exception as e:
        print(f"[LOGGING] Erro na inicialização automática: {e}", file=sys.stderr)
