import logging
import os

from core.factory.component_factory import ComponentFactory

"""
Utilitários para integração com adaptadores LLM (Gemini/DeepSeek)
"""


def get_llm_adapter(adapter_type="gemini"):
    """
    Retorna um adaptador LLM configurado

    Args:
        adapter_type (str): Tipo do adaptador ("gemini" ou "deepseek")

    Returns:
        LLMAdapter: Adaptador LLM configurado
    """
    try:
        # Usa o ComponentFactory para obter o adaptador
        adapter = ComponentFactory.get_llm_adapter(adapter_type)

        if not adapter:
            logging.error(f"Não foi possível obter adaptador LLM do tipo: {adapter_type}")
            return None

        logging.info(f"Adaptador LLM '{adapter_type}' configurado com sucesso")
        return adapter

    except Exception as e:
        logging.error(f"Erro ao criar adaptador LLM: {e}")
        return None


def get_langchain_model(model_name=None, temperature=None):
    """
    Função legacy - agora redireciona para get_llm_adapter
    Mantida para compatibilidade com código existente
    """
    logging.warning("get_langchain_model() é deprecated. Use get_llm_adapter() instead.")
    return get_llm_adapter("gemini")


if __name__ == "__main__":
    print("Rodando como script...")
    # TODO: Adicionar chamada a uma função principal se necessário
