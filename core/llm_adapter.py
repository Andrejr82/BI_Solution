"""
Módulo para core/llm_adapter.py. Define as classes: GeminiLLMAdapter, DeepSeekLLMAdapter, CustomLangChainLLM. Fornece funções utilitárias, incluindo 'get_completion' e outras.
"""

import logging
from typing import Any, List, Optional
from openai import OpenAI, RateLimitError
from core.utils.response_cache import ResponseCache
from langchain_core.language_models import BaseChatModel
from langchain_core.messages import BaseMessage, AIMessage
from langchain_core.outputs import ChatResult, ChatGeneration

logger = logging.getLogger(__name__)

class GeminiLLMAdapter:
    def __init__(self, api_key: str, model_name: str, enable_cache: bool = True):
        """
        Inicializa o cliente Gemini usando OpenAI SDK com base_url customizada.
        Gemini 2.5 Flash suporta interface compatível com OpenAI.
        """
        if not api_key:
            raise ValueError("A chave da API do Gemini não foi fornecida.")

        # ✅ FIX CRÍTICO: Usar base_url do Gemini, não da OpenAI
        # Gemini API endpoint compatível com OpenAI
        self.client = OpenAI(
            api_key=api_key,
            base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
        )
        self.model_name = model_name

        self.cache_enabled = enable_cache
        if enable_cache:
            self.cache = ResponseCache(ttl_hours=48)
            self.cache.clear_expired()
            logger.info("[OK] Cache de respostas ativado para Gemini - ECONOMIA DE CRÉDITOS")
        else:
            self.cache = None

        logger.info("Adaptador do GeminiLLMAdapter inicializado com sucesso.")

    def _stream_completion_generator(self, response_stream):
        for chunk in response_stream:
            content = chunk.choices[0].delta.content or ""
            yield content

    def get_completion(self, messages, model=None, temperature=0, max_tokens=4096, json_mode=False, stream=False):
        try:
            if not stream and self.cache_enabled and self.cache:
                cached_response = self.cache.get(messages, model, temperature)
                if cached_response:
                    return cached_response

            model_to_use = model or self.model_name

            params = {
                "model": model_to_use,
                "messages": messages,
                "temperature": temperature,
                "max_tokens": max_tokens,
                "stream": stream,
            }
            if json_mode:
                params["response_format"] = {"type": "json_object"}

            logger.info(f"[API] Chamada API Gemini: {model_to_use} - tokens: {max_tokens}")
            response = self.client.chat.completions.create(**params)

            if stream:
                return self._stream_completion_generator(response)

            # Extrair conteúdo com validação
            try:
                content = response.choices[0].message.content
                finish_reason = response.choices[0].finish_reason

                # Verificar se parou por limite de tokens sem gerar nada
                if finish_reason == 'length' and (content is None or not content):
                    completion_tokens = response.usage.completion_tokens if hasattr(response, 'usage') else 0
                    if completion_tokens == 0:
                        logger.error(f"[ERRO] max_tokens muito baixo! O modelo parou antes de gerar qualquer resposta. Tokens usados: {response.usage}")
                        # Mensagem amigável para o usuário
                        content = "Desculpe, não consegui processar sua solicitação no momento. Por favor, tente reformular sua pergunta de forma mais concisa ou entre em contato com o suporte."
                    else:
                        logger.warning(f"[AVISO] Resposta cortada por limite de tokens. Aumente max_tokens se necessário.")
                        # Mensagem parcial está OK, não precisa alterar
                elif content is None:
                    logger.warning(f"[AVISO] API retornou content=None. Response: {response}")
                    # Tentar pegar de outro lugar se disponível
                    if hasattr(response.choices[0].message, 'text'):
                        content = response.choices[0].message.text
                    elif hasattr(response.choices[0], 'text'):
                        content = response.choices[0].text
                    else:
                        content = ""
                        logger.error(f"[ERRO] Não foi possível extrair conteúdo. Response completo: {response.model_dump() if hasattr(response, 'model_dump') else response}")
            except (IndexError, AttributeError) as e:
                logger.error(f"[ERRO] Erro ao extrair conteúdo da resposta: {e}")
                content = ""

            result = {"content": content}

            if self.cache_enabled and self.cache:
                self.cache.set(messages, model, temperature, result)

            return result

        except RateLimitError as e:
            logger.error(f"[ALERTA] Rate limit Gemini 2.5 Flash-Lite atingido: {e}", exc_info=True)
            # ATIVA O FALLBACK AUTOMÁTICO PARA DEEPSEEK!
            try:
                from core.factory.component_factory import ComponentFactory
                ComponentFactory.set_gemini_unavailable(True)
                logger.warning("[FALLBACK] Fallback ativado: Gemini -> DeepSeek")
            except ImportError:
                pass
            return {"error": "Rate limit exceeded", "fallback_activated": True, "retry_with": "deepseek"}
        except Exception as e:
            error_msg = str(e).lower()
            # Detectar outros tipos de rate limit/quota exceeded
            if any(term in error_msg for term in ["quota", "limit", "429", "rate", "exceeded"]):
                logger.error(f"[ALERTA] Quota/Rate limit detectado no Gemini: {e}")
                try:
                    from core.factory.component_factory import ComponentFactory
                    ComponentFactory.set_gemini_unavailable(True)
                    logger.warning("[FALLBACK] Fallback ativado por quota: Gemini -> DeepSeek")
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
            logger.info("[OK] Cache de respostas ativado para DeepSeek.")
        else:
            self.cache = None

        logger.info("Adaptador do DeepSeekLLMAdapter inicializado com sucesso.")

    def get_completion(self, messages, model=None, temperature=0, max_tokens=4096, json_mode=False):
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

            logger.info(f"[API] Chamada API DeepSeek: {model_to_use} - tokens: {max_tokens}")
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



class CustomLangChainLLM(BaseChatModel):
    """
    Wrapper LangChain para os adaptadores Gemini/DeepSeek.
    Permite usar nossos adapters customizados com LangChain.
    """
    llm_adapter: Any

    def __init__(self, llm_adapter: Any):
        """
        Inicializa o wrapper com um adapter (GeminiLLMAdapter ou DeepSeekLLMAdapter).

        Args:
            llm_adapter: Instância de GeminiLLMAdapter ou DeepSeekLLMAdapter
        """
        super().__init__(llm_adapter=llm_adapter)

    def _generate(
        self,
        messages: List[BaseMessage],
        stop: Optional[List[str]] = None,
        **kwargs: Any,
    ) -> ChatResult:
        """
        Implementação obrigatória do BaseChatModel.
        Converte mensagens LangChain para formato OpenAI e chama o adapter.
        """
        # Converter mensagens LangChain para formato OpenAI
        openai_messages = []
        for msg in messages:
            if hasattr(msg, 'type') and hasattr(msg, 'content'):
                role = "user" if msg.type == "human" else msg.type
                openai_messages.append({"role": role, "content": msg.content})

        # Chamar o adapter
        response = self.llm_adapter.get_completion(
            messages=openai_messages,
            temperature=kwargs.get("temperature", 0),
            max_tokens=kwargs.get("max_tokens", 4096)
        )

        # Converter resposta para formato LangChain
        content = response.get("content", "")
        message = AIMessage(content=content)
        generation = ChatGeneration(message=message)

        return ChatResult(generations=[generation])

    @property
    def _llm_type(self) -> str:
        """Retorna o tipo do LLM para identificação."""
        return "custom_llm_adapter"
