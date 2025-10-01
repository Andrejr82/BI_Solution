import logging
import os

<<<<<<< HEAD
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
=======
from langchain.chat_models import ChatOpenAI

"""
Utilitários para integração com LangChain
"""


def get_langchain_model(model_name=None, temperature=None):
    """
    Retorna um modelo LangChain configurado

    Args:
        model_name (str): Nome do modelo a ser usado
        temperature (float): Temperatura para geração

    Returns:
        ChatOpenAI: Modelo LangChain configurado
    """
    try:
        # Configura a chave da API OpenAI
        api_key = os.getenv("OPENAI_API_KEY")

        if not api_key:
            logging.error("Chave da API OpenAI não configurada")
            return None

        # Usa os valores padrão se não fornecidos
        if not model_name:
            model_name = os.getenv("LLM_MODEL", "gpt-4")

        if not temperature:
            temperature = float(os.getenv("LLM_TEMPERATURE", "0"))

        # Inicializa o modelo LangChain
        # Não inclui o parâmetro "proxies" que estava causando o erro
        chat = ChatOpenAI(
            model_name=model_name,
            temperature=temperature,
            openai_api_key=api_key,
            verbose=True,
        )

        return chat

    except Exception as e:
        logging.error(f"Erro ao criar modelo LangChain: {e}")
        return None
>>>>>>> 946e2ce9d874562f3c9e0f0d54e9c41c50cb3399


if __name__ == "__main__":
    print("Rodando como script...")
    # TODO: Adicionar chamada a uma função principal se necessário
