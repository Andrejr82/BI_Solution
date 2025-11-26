"""
Factory para seleção automática de adaptadores LLM.
"""

import logging
from typing import Optional
from app.config.settings import settings
from app.core.llm_base import BaseLLMAdapter


class LLMFactory:
    """Factory pattern para criar adaptadores LLM."""

    _instance: Optional["LLMFactory"] = None
    _adapter: Optional[BaseLLMAdapter] = None
    _logger = logging.getLogger(__name__)

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    @classmethod
    def get_adapter(cls) -> BaseLLMAdapter:
        """
        Obtém o adaptador LLM configurado (apenas Gemini).

        Returns:
            BaseLLMAdapter: Adaptador LLM inicializado

        Raises:
            ValueError: Se o adaptador Gemini não puder ser inicializado
        """
        if cls._adapter is not None:
            return cls._adapter

        factory = cls()
        cls._logger.info("Inicializando adaptador Gemini.")
        cls._adapter = factory._get_gemini_adapter()

        if cls._adapter is None:
            raise ValueError(
                "Nenhum adaptador LLM pode ser inicializado. "
                "Verifique as configurações de GEMINI_API_KEY."
            )

        return cls._adapter

    @staticmethod
    def _get_gemini_adapter() -> Optional[BaseLLMAdapter]:
        """Tenta inicializar adaptador Gemini."""
        try:
            from app.core.llm_gemini_adapter import GeminiLLMAdapter

            if not settings.GEMINI_API_KEY:
                LLMFactory._logger.warning("GEMINI_API_KEY não configurada")
                return None

            adapter = GeminiLLMAdapter()
            LLMFactory._logger.info("Adaptador Gemini inicializado com sucesso")
            return adapter

        except Exception as e:
            LLMFactory._logger.error(f"Erro ao inicializar Gemini: {e}")
            return None

    @classmethod
    def reset(cls):
        """Reseta o adaptador cache (útil para testes)."""
        cls._adapter = None
        cls._logger.info("Adaptador LLM resetado")

    @classmethod
    def get_available_providers(cls) -> dict:
        """
        Verifica quais provedores estão disponíveis.

        Returns:
            dict: {'gemini': bool}
        """
        providers = {}
        try:
            providers["gemini"] = settings.GEMINI_API_KEY is not None
        except Exception:
            providers["gemini"] = False

        return providers
