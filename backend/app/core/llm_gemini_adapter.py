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

try:
    import google.generativeai as genai
    from google.api_core.exceptions import RetryError, InternalServerError
    # from google.generativeai.types import ToolCode # Removido
    from google.generativeai.types import FunctionDeclaration
    GEMINI_AVAILABLE = True
except ImportError as e:
    print(f"Erro de importação do Gemini: {e}")


class GeminiLLMAdapter(BaseLLMAdapter):
    """
    Adaptador para Google Gemini API.
    Implementa padrão similar ao OpenAI com retry automático e tratamento de erros.
    """

    def __init__(self):
        self.logger = logging.getLogger(__name__)

        if not GEMINI_AVAILABLE:
            raise ImportError(
                "google-generativeai não está instalado. "
                "Execute: pip install google-generativeai"
            )

        if not settings.GEMINI_API_KEY:
            raise ValueError("GEMINI_API_KEY não configurada no arquivo .env")

        genai.configure(api_key=settings.GEMINI_API_KEY)

        # Prioriza LLM_MODEL_NAME, fallback para GEMINI_MODEL_NAME, default para gemini-2.5-flash
        self.model_name = os.getenv("LLM_MODEL_NAME", os.getenv("GEMINI_MODEL_NAME", "models/gemini-2.5-flash"))
        self.max_retries = 3
        self.retry_delay = 2

        self.logger.info(f"Gemini adapter inicializado com modelo: {self.model_name}")

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

                        model = genai.GenerativeModel(
                            model_name=self.model_name,
                            tools=gemini_tools if gemini_tools else None,
                        )

                        chat_session = model.start_chat(history=gemini_messages[:-1])

                        self.logger.info(
                            f"Chamada Gemini (tentativa {attempt + 1}/"
                            f"{self.max_retries})"
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
                thread.join(timeout=90.0)

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

    def _convert_tools(self, tools_wrapper: Dict[str, List[Dict[str, Any]]]) -> List[FunctionDeclaration]:
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
