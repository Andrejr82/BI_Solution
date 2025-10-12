"""
Módulo para core/llm_base.py. Define a classe principal 'BaseLLMAdapter'. Fornece as funções: get_completion.
"""

from abc import ABC, abstractmethod

class BaseLLMAdapter(ABC):
    @abstractmethod
    def get_completion(self, prompt: str) -> str:
        pass
