<<<<<<< HEAD
"""
Adaptadores LLM para Gemini e DeepSeek usando SDK OpenAI.

Ambos os LLMs suportam a API compatível com OpenAI:
- Gemini: Via Google AI Studio (https://ai.google.dev/gemini-api/docs/openai)
- DeepSeek: Via API nativa compatível (https://api.deepseek.com)
"""
import logging
from openai import OpenAI, RateLimitError
from core.utils.response_cache import ResponseCache

logger = logging.getLogger(__name__)

class GeminiLLMAdapter:
    def __init__(self, api_key: str, model_name: str, enable_cache: bool = True):
        """
        Inicializa o cliente para o Google Gemini usando SDK OpenAI para compatibilidade.
        O Gemini suporta a API compatível com OpenAI via Google AI Studio.
        """
        if not api_key:
            raise ValueError("A chave da API do Gemini não foi fornecida.")

        # Gemini API via OpenAI-compatible endpoint (Google AI Studio)
        # https://ai.google.dev/gemini-api/docs/openai
        self.client = OpenAI(
            api_key=api_key,
            base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
        ) 
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
=======
import logging
from openai import OpenAI
# CORREÇÃO: A importação de 'Config' foi removida, pois era da arquitetura antiga.
# A classe agora receberá a chave da API diretamente no seu construtor.

logger = logging.getLogger(__name__)

class OpenAILLMAdapter:
    def __init__(self, api_key: str):
        """
        Inicializa o cliente da OpenAI com a chave da API fornecida.
        """
        if not api_key:
            raise ValueError("A chave da API da OpenAI não foi fornecida.")
        self.client = OpenAI(api_key=api_key)
        logger.info("Adaptador da OpenAI inicializado com sucesso.")

    def get_completion(self, messages, model="gpt-4-turbo", temperature=0, max_tokens=2048, json_mode=False):
        """
        Obtém uma conclusão do modelo da OpenAI.
        """
        try:
            params = {
                "model": model,
>>>>>>> 946e2ce9d874562f3c9e0f0d54e9c41c50cb3399
                "messages": messages,
                "temperature": temperature,
                "max_tokens": max_tokens,
            }
            if json_mode:
                params["response_format"] = {"type": "json_object"}

<<<<<<< HEAD
            logger.info(f"💰 Chamada API Gemini: {model_to_use} - tokens: {max_tokens}")
            response = self.client.chat.completions.create(**params)

            content = response.choices[0].message.content
            result = {"content": content}

            if self.cache_enabled and self.cache:
                self.cache.set(messages, model, temperature, result)

            return result

        except RateLimitError as e:
            logger.error(f"🚨 Rate limit Gemini 2.5 Flash-Lite atingido: {e}", exc_info=True)
            # ATIVA O FALLBACK AUTOMÁTICO PARA DEEPSEEK!
            try:
                from core.factory.component_factory import ComponentFactory
                ComponentFactory.set_gemini_unavailable(True)
                logger.warning("🔄 Fallback ativado: Gemini → DeepSeek")
            except ImportError:
                pass
            return {"error": "Rate limit exceeded", "fallback_activated": True, "retry_with": "deepseek"}
        except Exception as e:
            error_msg = str(e).lower()
            # Detectar outros tipos de rate limit/quota exceeded
            if any(term in error_msg for term in ["quota", "limit", "429", "rate", "exceeded"]):
                logger.error(f"🚨 Quota/Rate limit detectado no Gemini: {e}")
                try:
                    from core.factory.component_factory import ComponentFactory
                    ComponentFactory.set_gemini_unavailable(True)
                    logger.warning("🔄 Fallback ativado por quota: Gemini → DeepSeek")
                except ImportError:
                    pass
                return {"error": "Quota exceeded", "fallback_activated": True, "retry_with": "deepseek"}

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


=======
            response = self.client.chat.completions.create(**params)
            
            content = response.choices[0].message.content
            return {"content": content}
        except Exception as e:
            logger.error(f"Erro ao chamar a API da OpenAI: {e}", exc_info=True)
            return {"error": str(e)}
>>>>>>> 946e2ce9d874562f3c9e0f0d54e9c41c50cb3399
