from typing import List, Dict, Any, Optional
import logging
import threading
import time
from queue import Queue
import json # Adicionado para json.dumps
import os
from app.core.llm_base import BaseLLMAdapter
from app.config.settings import settings

GEMINI_AVAILABLE = False # Assume false until all imports succeed
LANGCHAIN_GEMINI_AVAILABLE = False

try:
    import google.generativeai as genai
    from google.api_core.exceptions import RetryError, InternalServerError
    # from google.generativeai.types import ToolCode # Removido
    from google.generativeai.types import FunctionDeclaration
    GEMINI_AVAILABLE = True
except ImportError as e:
    print(f"Erro de importação do Gemini: {e}")
    FunctionDeclaration = Any # Fallback to avoid NameError

# Disable langchain-google-genai to avoid version conflicts
# Using native google.generativeai adapter instead
LANGCHAIN_GEMINI_AVAILABLE = False


class GeminiLLMAdapter(BaseLLMAdapter):
    """
    Adaptador para Google Gemini API.
    Implementa padrão similar ao OpenAI com retry automático e tratamento de erros.
    """

    def __init__(self, model_name: Optional[str] = None, gemini_api_key: Optional[str] = None):
        self.logger = logging.getLogger(__name__)

        if not GEMINI_AVAILABLE:
            raise ImportError(
                "google-generativeai não está instalado. "
                "Execute: pip install google-generativeai"
            )

        # Use provided API key or fall back to settings
        api_key = gemini_api_key or settings.GEMINI_API_KEY
        if not api_key:
            raise ValueError("GEMINI_API_KEY não configurada no arquivo .env")

        genai.configure(api_key=api_key)
        self.gemini_api_key = api_key

        # Use provided model name or fall back to settings (which loads from .env)
        self.model_name = model_name or settings.LLM_MODEL_NAME or "gemini-1.5-flash"
        self.max_retries = 3  # ✅ Increased to 3 attempts
        self.retry_delay = 0.5  # ✅ 500ms entre tentativas

        self.logger.info(f"Gemini adapter inicializado com modelo: {self.model_name}")

    def get_llm(self):
        """
        Returns a LangChain-compatible ChatGoogleGenerativeAI instance.
        This method is required by chat.py endpoint for agent initialization.
        Falls back to self if langchain-google-genai is not available.
        """
        if not LANGCHAIN_GEMINI_AVAILABLE:
            self.logger.info("LangChain Google GenAI nao disponivel - usando adapter nativo")
            # Return self as fallback - the adapter itself can be used as an LLM
            return self

        try:
            return ChatGoogleGenerativeAI(
                model=self.model_name,
                google_api_key=self.gemini_api_key,
                temperature=0.0,
                max_retries=self.max_retries
            )
        except Exception as e:
            self.logger.error(f"Erro ao criar ChatGoogleGenerativeAI: {e}")
            self.logger.info(f"Erro ao criar ChatGoogleGenerativeAI: {e} - usando adapter nativo")
            return self

    def invoke(self, input: Any, config: Optional[Dict] = None) -> Any:
        """
        Implementation of the LangChain Runnable invoke protocol.
        Allows the adapter to be used directly in LangChain sequences.
        """
        from langchain_core.messages import AIMessage, HumanMessage, SystemMessage, BaseMessage
        from langchain_core.prompt_values import ChatPromptValue

        messages = []
        if isinstance(input, ChatPromptValue):
            messages = input.to_messages()
        elif isinstance(input, list):
            messages = input
        elif isinstance(input, str):
            messages = [HumanMessage(content=input)]
        
        # Convert LangChain messages to the dict format expected by _convert_messages
        adapter_messages = []
        for msg in messages:
            role = "user"
            if isinstance(msg, AIMessage):
                role = "model"
            elif isinstance(msg, SystemMessage):
                role = "user" 
            elif isinstance(msg, HumanMessage):
                role = "user"
            
            content = msg.content if hasattr(msg, "content") else str(msg)
            adapter_messages.append({"role": role, "content": content})

        # Call get_completion
        result = self.get_completion(adapter_messages)
        
        if "error" in result:
             # Log the error but try to return it as text if possible, or raise
             self.logger.error(f"Error in invoke: {result['error']}")
             raise ValueError(result["error"])
             
        return AIMessage(content=result.get("content", ""))

    def get_completion(
        self,
        messages: List[Dict[str, str]],
        tools: Optional[Dict[str, List[Dict[str, Any]]]] = None, # Alterado aqui
    ) -> Dict[str, Any]:
        """
        Obtém completion da API Gemini com retry automático.

        Args:
            messages: Lista de mensagens no formato OpenAI-like
            tools: Dicionário opcional de ferramentas no formato Gemini (com 'function_declarations')

        Returns:
            Dicionário com resultado ou erro
        """
        for attempt in range(self.max_retries):
            try:
                q = Queue()

                def worker():
                    try:
                        gemini_messages = self._convert_messages(messages)
                        
                        if tools:
                            gemini_tools = self._convert_tools(tools)
                        else:
                            gemini_tools = []

                        # ✅ NOVO: Configuração de geração avançada com Thinking Mode
                        generation_config = genai.GenerationConfig(
                            temperature=0.7,  # Balanceado para criatividade e precisão
                            top_p=0.95,
                            top_k=40,
                            max_output_tokens=8192,  # Aumentado para respostas detalhadas
                        )

                        model = genai.GenerativeModel(
                            model_name=self.model_name,
                            tools=gemini_tools if gemini_tools else None,
                            generation_config=generation_config,
                            # Sistema de instruções para melhor raciocínio
                            system_instruction="""Você é um assistente de BI altamente preciso.
Antes de responder, analise a pergunta cuidadosamente.
Para perguntas sobre dados:
1. Primeiro identifique qual ferramenta usar
2. Execute a consulta com os parâmetros corretos
3. Analise os resultados antes de responder
4. Formate a resposta de forma clara e organizada
5. Se não encontrar dados, explique o motivo"""
                        )

                        chat_session = model.start_chat(history=gemini_messages[:-1])

                        self.logger.info(
                            f"Chamada Gemini (tentativa {attempt + 1}/"
                            f"{self.max_retries}) - Thinking Mode ativo"
                        )

                        response = chat_session.send_message(gemini_messages[-1]["parts"])

                        self.logger.info("Chamada Gemini concluída.")

                        tool_calls = []
                        content = ""
                        
                        if response.candidates:
                            candidate = response.candidates[0]
                            if candidate.content and candidate.content.parts:
                                for part in candidate.content.parts:
                                    if part.function_call:
                                        function_call = part.function_call
                                        tool_calls.append({
                                            "id": f"call_{function_call.name}", # Gemini doesn't provide an ID, so we generate one
                                            "function": {
                                                "arguments": json.dumps(dict(function_call.args)),
                                                "name": function_call.name,
                                            },
                                            "type": "function",
                                        })
                                        # Se há tool_call, o conteúdo textual deve ser vazio
                                        content = "" 
                                        break # Only handle the first function call for now
                                    elif part.text:
                                        content = part.text
                                        break # Only handle the first text part for now
                        
                        result = {"content": content}
                        if tool_calls:
                            result["tool_calls"] = tool_calls
                        
                        q.put(result)

                    except Exception as e:
                        error_msg = str(e).lower()

                        retentable = any(
                            [
                                "quota" in error_msg,
                                "rate" in error_msg,
                                "timeout" in error_msg,
                                "500" in error_msg,
                                "503" in error_msg,
                                "429" in error_msg,
                            ]
                        )

                        self.logger.warning(
                            f"Erro Gemini na tentativa {attempt + 1}: {e} "
                            f"(retentável: {retentable})"
                        )

                        q.put({"error": f"Erro: {e}", "retry": retentable})

                thread = threading.Thread(target=worker)
                thread.start()
                thread.join(timeout=30.0)  # ✅ Increased to 30s

                if thread.is_alive():
                    self.logger.warning(f"Thread timeout tentativa {attempt + 1}")
                    continue

                result = q.get()

                if "error" not in result:
                    return result

                if result.get("retry") and (attempt < self.max_retries - 1):
                    delay = self.retry_delay * (2**attempt)
                    self.logger.info(
                        f"Aguardando {delay}s antes da próxima tentativa..."
                    )
                    time.sleep(delay)
                    continue

                return result

            except Exception as e:
                self.logger.error(
                    f"Erro externo tentativa {attempt + 1}: {e}", exc_info=True
                )
                if attempt < self.max_retries - 1:
                    delay = self.retry_delay * (2**attempt)
                    time.sleep(delay)
                    continue
                return {"error": f"Erro após {self.max_retries} tentativas: {e}"}

        return {"error": f"Falha após {self.max_retries} tentativas"}

    def _convert_messages(self, messages: List[Dict[str, str]]) -> List[Dict[str, Any]]:
        """
        Converte mensagens do formato OpenAI-like para formato Gemini.

        Formato OpenAI-like: [{"role": "user", "content": "..."}]
        Formato Gemini: [{"role": "user", "parts": [{"text": "..."}]}]
        """
        gemini_messages = []

        for msg in messages:
            role = msg.get("role", "user")
            content = msg.get("content", "")
            tool_calls = msg.get("tool_calls")
            function_call = msg.get("function_call")

            # Determine Gemini role based on actual content and OpenAI-like role
            # IMPORTANT: Check for tool_calls and function_call FIRST, before checking role
            if tool_calls:
                # Model's turn: calls a tool
                gemini_msg = {
                    "role": "model",
                    "parts": [
                        {"function_call": {"name": tc["function"]["name"], "args": json.loads(tc["function"]["arguments"])}}
                        for tc in tool_calls
                    ]
                }
            elif function_call:
                # User's turn: provides tool response
                # This handles both explicit "function"/"tool" roles AND cases where
                # LangChain sends "user" role with function_call metadata
                gemini_msg = {
                    "role": "user",
                    "parts": [
                        {
                            "function_response": {
                                "name": function_call["name"],
                                "response": {"content": content}
                            }
                        }
                    ]
                }
            elif role == "user":
                gemini_msg = {"role": "user", "parts": [{"text": content}]}
            elif role == "assistant" or role == "model":
                gemini_msg = {"role": "model", "parts": [{"text": content}]}
            else: # Fallback for unexpected roles, treat as user to avoid errors
                self.logger.warning(f"Unexpected role encountered: {role}. Treating as 'user'.")
                gemini_msg = {"role": "user", "parts": [{"text": content}]}

            gemini_messages.append(gemini_msg)

        return gemini_messages

    def _convert_tools(self, tools_wrapper: Dict[str, List[Dict[str, Any]]]) -> List['FunctionDeclaration']:
        """
        Converte ferramentas do formato OpenAI-like (agora encapsulado em 'function_declarations')
        para Gemini Tool Format.
        """
        gemini_tools = []

        # Extract the list of function declarations from the wrapper dictionary
        function_declarations = tools_wrapper.get("function_declarations", [])

        for tool_declaration in function_declarations:
            # Each tool_declaration is already in the format expected by FunctionDeclaration
            # e.g., {"name": "tool_name", "description": "...", "parameters": {...}}
            gemini_tool = FunctionDeclaration(
                name=tool_declaration.get("name", ""),
                description=tool_declaration.get("description", ""),
                parameters=tool_declaration.get("parameters", {}),
            )
            gemini_tools.append(gemini_tool)

        return gemini_tools
