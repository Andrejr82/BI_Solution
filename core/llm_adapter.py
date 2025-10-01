import logging
from openai import OpenAI, RateLimitError
from core.utils.response_cache import ResponseCache
from core.factory.component_factory import ComponentFactory

logger = logging.getLogger(__name__)

class GeminiLLMAdapter:
    def __init__(self, api_key: str, model_name: str, enable_cache: bool = True):
        """
        Inicializa o cliente para um modelo compatível com a API OpenAI (como o Gemini via proxy/serviço compatível).
        """
        if not api_key:
            raise ValueError("A chave da API do Gemini não foi fornecida.")
        
        # A URL base pode precisar ser ajustada dependendo de como você acessa a API do Gemini
        # Exemplo para um proxy local ou serviço como litellm: "http://localhost:8000"
        # Para APIs que mimetizam a OpenAI, você pode precisar de uma base_url.
        # Se a biblioteca do Gemini for usada diretamente, a inicialização será diferente.
        # Por simplicidade, vamos assumir uma interface compatível com OpenAI.
        self.client = OpenAI(api_key=api_key) 
        self.model_name = model_name

        self.cache_enabled = enable_cache
        if enable_cache:
            self.cache = ResponseCache(ttl_hours=48)
            self.cache.clear_expired()
            logger.info("✅ Cache de respostas ativado para Gemini - ECONOMIA DE CRÉDITOS")
        else:
            self.cache = None

        logger.info("Adaptador do GeminiLLMAdapter inicializado com sucesso.")

    def get_completion(self, messages, model=None, temperature=0, max_tokens=1024, json_mode=False):
        try:
            if self.cache_enabled and self.cache:
                cached_response = self.cache.get(messages, model, temperature)
                if cached_response:
                    return cached_response

            # Usa o modelo da chamada ou o padrão da instância
            model_to_use = model or self.model_name

            params = {
                "model": model_to_use,
                "messages": messages,
                "temperature": temperature,
                "max_tokens": max_tokens,
            }
            if json_mode:
                params["response_format"] = {"type": "json_object"}

            logger.info(f"💰 Chamada API Gemini: {model_to_use} - tokens: {max_tokens}")
            response = self.client.chat.completions.create(**params)

            content = response.choices[0].message.content
            result = {"content": content}

            if self.cache_enabled and self.cache:
                self.cache.set(messages, model, temperature, result)

            return result

        except RateLimitError as e:
            logger.error(f"Limite de taxa da API Gemini atingido: {e}", exc_info=True)
            # ATIVA O FALLBACK!
            ComponentFactory.set_gemini_unavailable(True)
            return {"error": "Rate limit exceeded", "fallback_activated": True}
        except Exception as e:
            logger.error(f"Erro ao chamar a API do Gemini: {e}", exc_info=True)
            return {"error": str(e)}

    def get_cache_stats(self):
        if not self.cache_enabled or not self.cache:
            return {"cache_enabled": False}
        stats = self.cache.get_stats()
        stats["cache_enabled"] = True
        return stats

class DeepSeekLLMAdapter:
    def __init__(self, api_key: str, model_name: str, enable_cache: bool = True):
        """
        Inicializa o cliente para a API DeepSeek.
        """
        if not api_key:
            raise ValueError("A chave da API da DeepSeek não foi fornecida.")
        
        self.client = OpenAI(
            api_key=api_key,
            base_url="https://api.deepseek.com/v1"
        )
        self.model_name = model_name

        self.cache_enabled = enable_cache
        if enable_cache:
            self.cache = ResponseCache(ttl_hours=48)
            self.cache.clear_expired()
            logger.info("✅ Cache de respostas ativado para DeepSeek.")
        else:
            self.cache = None

        logger.info("Adaptador do DeepSeekLLMAdapter inicializado com sucesso.")

    def get_completion(self, messages, model=None, temperature=0, max_tokens=1024, json_mode=False):
        """
        Obtém uma conclusão do modelo DeepSeek.
        """
        try:
            if self.cache_enabled and self.cache:
                cached_response = self.cache.get(messages, model, temperature)
                if cached_response:
                    return cached_response

            # Usa o modelo da chamada ou o padrão da instância
            model_to_use = model or self.model_name

            params = {
                "model": model_to_use,
                "messages": messages,
                "temperature": temperature,
                "max_tokens": max_tokens,
            }
            if json_mode:
                params["response_format"] = {"type": "json_object"}

            logger.info(f"💰 Chamada API DeepSeek: {model_to_use} - tokens: {max_tokens}")
            response = self.client.chat.completions.create(**params)

            content = response.choices[0].message.content
            result = {"content": content}

            if self.cache_enabled and self.cache:
                self.cache.set(messages, model, temperature, result)

            return result

        except Exception as e:
            logger.error(f"Erro ao chamar a API da DeepSeek: {e}", exc_info=True)
            return {"error": str(e)}

    def get_cache_stats(self):
        if not self.cache_enabled or not self.cache:
            return {"cache_enabled": False}
        stats = self.cache.get_stats()
        stats["cache_enabled"] = True
        return stats

class OpenAILLMAdapter:
    def __init__(self, api_key: str, model_name: str, enable_cache: bool = True):
        """
        Inicializa o cliente para a API oficial da OpenAI.
        """
        if not api_key:
            raise ValueError("A chave da API da OpenAI não foi fornecida.")
        
        self.client = OpenAI(api_key=api_key)
        self.model_name = model_name

        self.cache_enabled = enable_cache
        if enable_cache:
            self.cache = ResponseCache(ttl_hours=48)
            self.cache.clear_expired()
            logger.info("✅ Cache de respostas ativado para OpenAI.")
        else:
            self.cache = None

        logger.info("Adaptador do OpenAILLMAdapter inicializado com sucesso.")

    def get_completion(self, messages, model=None, temperature=0, max_tokens=1024, json_mode=False):
        """
        Obtém uma conclusão do modelo OpenAI.
        """
        try:
            if self.cache_enabled and self.cache:
                cached_response = self.cache.get(messages, model, temperature)
                if cached_response:
                    return cached_response

            model_to_use = model or self.model_name

            params = {
                "model": model_to_use,
                "messages": messages,
                "temperature": temperature,
                "max_tokens": max_tokens,
            }
            if json_mode:
                params["response_format"] = {"type": "json_object"}

            logger.info(f"💰 Chamada API OpenAI: {model_to_use} - tokens: {max_tokens}")
            response = self.client.chat.completions.create(**params)

            content = response.choices[0].message.content
            result = {"content": content}

            if self.cache_enabled and self.cache:
                self.cache.set(messages, model, temperature, result)

            return result

        except Exception as e:
            logger.error(f"Erro ao chamar a API da OpenAI: {e}", exc_info=True)
            return {"error": str(e)}

    def get_cache_stats(self):
        if not self.cache_enabled or not self.cache:
            return {"cache_enabled": False}
        stats = self.cache.get_stats()
        stats["cache_enabled"] = True
        return stats
