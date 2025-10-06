"""
Rate Limiter para prevenir abuso de endpoints
"""
import time
from collections import defaultdict
from typing import Dict, List
import logging

logger = logging.getLogger(__name__)


class RateLimiter:
    """
    Implementa rate limiting baseado em tempo e tentativas

    Exemplo:
        limiter = RateLimiter(max_calls=5, period=300)  # 5 tentativas em 5 min
        if limiter.is_allowed("user@example.com"):
            # Permitir ação
        else:
            # Bloquear e avisar
    """

    def __init__(self, max_calls: int = 5, period: int = 60):
        """
        Args:
            max_calls: Número máximo de chamadas permitidas
            period: Período em segundos para resetar o contador
        """
        self.max_calls = max_calls
        self.period = period
        self.calls: Dict[str, List[float]] = defaultdict(list)

    def is_allowed(self, key: str) -> bool:
        """
        Verifica se uma chave (usuário/IP) pode fazer uma ação

        Args:
            key: Identificador único (username, IP, etc)

        Returns:
            True se permitido, False se bloqueado
        """
        now = time.time()

        # Limpar chamadas antigas (fora do período)
        self.calls[key] = [t for t in self.calls[key] if now - t < self.period]

        # Verificar limite
        if len(self.calls[key]) < self.max_calls:
            self.calls[key].append(now)
            return True

        # Bloqueado - log de segurança
        remaining = self.period - (now - self.calls[key][0])
        logger.warning(f"Rate limit excedido para {key}. Tente novamente em {remaining:.0f}s")
        return False

    def get_remaining_calls(self, key: str) -> int:
        """Retorna número de chamadas restantes"""
        now = time.time()
        self.calls[key] = [t for t in self.calls[key] if now - t < self.period]
        return max(0, self.max_calls - len(self.calls[key]))

    def get_reset_time(self, key: str) -> float:
        """Retorna tempo em segundos até o reset"""
        if not self.calls[key]:
            return 0

        now = time.time()
        oldest = self.calls[key][0]
        return max(0, self.period - (now - oldest))

    def reset(self, key: str):
        """Reseta o contador para uma chave específica"""
        if key in self.calls:
            del self.calls[key]
            logger.info(f"Rate limiter resetado para {key}")


# Instâncias globais para uso comum
login_limiter = RateLimiter(max_calls=5, period=300)  # 5 tentativas em 5 min
api_limiter = RateLimiter(max_calls=60, period=60)    # 60 chamadas por minuto
