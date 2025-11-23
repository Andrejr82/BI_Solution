"""
Módulo de Serviço LLM: Encapsula a lógica de chamada ao Large Language Model
Fornece suporte a streaming e tratamento de erros.
"""

import logging
import json
from typing import Generator, Optional, Dict, Any
from core.agents.prompt_loader import PromptLoader
from core.llm_adapter import GeminiLLMAdapter
from core.security import mask_pii

logger = logging.getLogger("llm_service")


class LLMService:
    """
    Serviço centralizado para chamadas ao LLM com suporte a streaming.
    """
    
    def __init__(self, llm_adapter: GeminiLLMAdapter = None):
        """
        Inicializa o serviço LLM.
        
        Args:
            llm_adapter: Instância de GeminiLLMAdapter (opcional)
        """
        self.llm_adapter = llm_adapter
        self.prompt_loader = PromptLoader()
    
    def get_response(
        self, 
        prompt: str, 
        context: Optional[Dict[str, Any]] = None,
        mask_pii_data: bool = True
    ) -> str:
        """
        Obtém uma resposta completa do LLM (não-streaming).
        
        Args:
            prompt (str): Prompt ou template de prompt
            context (Dict): Contexto para injeção dinâmica (opcional)
            mask_pii_data (bool): Se True, mascara PII no input/output
            
        Returns:
            str: Resposta completa do LLM
        """
        try:
            # Se o prompt é um template, carregar e injetar contexto
            if context:
                full_prompt = self.prompt_loader.inject_context_into_template(prompt, context)
            else:
                full_prompt = prompt
            
            # Mascarar PII se habilitado
            if mask_pii_data:
                full_prompt = mask_pii(full_prompt)
                logger.info("PII mascarado no input do LLM")
            
            # Preparar mensagens no formato esperado pelo adapter
            messages = [{"role": "user", "content": full_prompt}]
            
            # Chamada ao LLM usando o adapter
            response = self.llm_adapter.get_completion(
                messages=messages,
                stream=False
            )
            
            # Mascarar PII na resposta se habilitado
            if mask_pii_data:
                response = mask_pii(response)
                logger.info("PII mascarado no output do LLM")
            
            logger.info("Resposta do LLM obtida com sucesso (não-streaming)")
            return response
            
        except Exception as e:
            logger.error(f"Erro ao obter resposta do LLM: {e}")
            return f"Erro ao processar sua pergunta: {str(e)}"
    
    def get_response_stream(
        self, 
        prompt: str, 
        context: Optional[Dict[str, Any]] = None,
        mask_pii_data: bool = True
    ) -> Generator[str, None, None]:
        """
        Obtém uma resposta do LLM em modo streaming (chunks).
        
        Args:
            prompt (str): Prompt ou template de prompt
            context (Dict): Contexto para injeção dinâmica (opcional)
            mask_pii_data (bool): Se True, mascara PII no input/output
            
        Yields:
            str: Chunks de texto da resposta
        """
        try:
            # Se o prompt é um template, carregar e injetar contexto
            if context:
                full_prompt = self.prompt_loader.inject_context_into_template(prompt, context)
            else:
                full_prompt = prompt
            
            # Mascarar PII se habilitado
            if mask_pii_data:
                full_prompt = mask_pii(full_prompt)
                logger.info("PII mascarado no input do LLM (streaming)")
            
            # Preparar mensagens no formato esperado pelo adapter
            messages = [{"role": "user", "content": full_prompt}]
            
            # Chamada ao LLM com streaming usando o adapter
            stream_response = self.llm_adapter.get_completion(
                messages=messages,
                stream=True
            )
            
            logger.info("Streaming de resposta do LLM iniciado")
            
            # Acumular resposta completa para mascaramento final
            full_response = ""
            
            # Iterar sobre os chunks
            for chunk in stream_response:
                if chunk:
                    full_response += chunk
                    # Yield do chunk original (mascaramento será feito no final)
                    yield chunk
            
            # Mascarar PII na resposta completa se habilitado
            if mask_pii_data and full_response:
                # Verificar se há PII na resposta completa
                masked_full = mask_pii(full_response)
                if masked_full != full_response:
                    logger.warning("PII detectado na resposta do LLM (streaming)")
            
            logger.info("Streaming de resposta do LLM concluído")
            
        except Exception as e:
            logger.error(f"Erro ao fazer streaming da resposta do LLM: {e}")
            yield f"Erro ao processar sua pergunta: {str(e)}"
    
    def parse_json_response(self, response: str) -> Optional[Dict[str, Any]]:
        """
        Tenta fazer parse de uma resposta JSON do LLM.
        
        Args:
            response (str): Resposta do LLM (esperado ser JSON)
            
        Returns:
            Dict: Objeto JSON parseado ou None se falhar
        """
        try:
            # Remove markdown code blocks se presentes
            cleaned_response = response.strip()
            if cleaned_response.startswith("```json"):
                cleaned_response = cleaned_response[7:]
            if cleaned_response.startswith("```"):
                cleaned_response = cleaned_response[3:]
            if cleaned_response.endswith("```"):
                cleaned_response = cleaned_response[:-3]
            
            # Parse JSON
            parsed = json.loads(cleaned_response.strip())
            logger.info("Resposta JSON parseada com sucesso")
            return parsed
            
        except json.JSONDecodeError as e:
            logger.error(f"Erro ao fazer parse de JSON: {e}")
            logger.debug(f"Resposta recebida: {response[:200]}...")
            return None
        except Exception as e:
            logger.error(f"Erro inesperado ao processar resposta JSON: {e}")
            return None
    
    def load_and_inject_prompt(self, prompt_name: str, context: Dict[str, Any]) -> str:
        """
        Carrega um template de prompt e injeta contexto.
        
        Args:
            prompt_name (str): Nome do arquivo de prompt (sem extensão)
            context (Dict): Contexto para injeção
            
        Returns:
            str: Prompt completo com contexto injetado
        """
        # Carregar template
        template = self.prompt_loader.load_prompt_template(prompt_name)
        
        if not template:
            logger.error(f"Falha ao carregar template: {prompt_name}")
            return ""
        
        # Injetar contexto
        full_prompt = self.prompt_loader.inject_context_into_template(template, context)
        logger.info(f"Prompt '{prompt_name}' carregado e contexto injetado")
        
        return full_prompt


# Função utilitária para criar instância do serviço
def create_llm_service(llm_adapter: GeminiLLMAdapter = None) -> LLMService:
    """
    Cria uma instância do LLMService.
    
    Args:
        llm_adapter: Instância de GeminiLLMAdapter (opcional)
        
    Returns:
        LLMService: Instância configurada do serviço
    """
    return LLMService(llm_adapter=llm_adapter)

# Alias para compatibilidade
get_llm_service = create_llm_service
