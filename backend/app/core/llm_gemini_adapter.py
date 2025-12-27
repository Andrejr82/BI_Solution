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
    from google.generativeai.types import FunctionDeclaration, Tool
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

    def __init__(self, model_name: Optional[str] = None, gemini_api_key: Optional[str] = None, system_instruction: Optional[str] = None):
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
        self.model_name = model_name or settings.LLM_MODEL_NAME or "gemini-3-flash-preview"
        self.max_retries = 3  # ✅ Increased to 3 attempts
        self.retry_delay = 0.5  # ✅ 500ms entre tentativas

        # Store configurable system instruction (default None)
        self.system_instruction = system_instruction

        self.logger.info(f"Gemini adapter inicializado com modelo: {self.model_name}")

    async def generate_response(self, prompt: str) -> str:
        """
        Gera uma resposta de texto simples para um prompt dado.
        Wrapper para get_completion para compatibilidade com insights.py.
        """
        messages = [{"role": "user", "content": prompt}]
        result = self.get_completion(messages)
        
        if "error" in result:
            raise Exception(result["error"])
            
        return result.get("content", "")

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
        
        MODIFICAÇÃO (Gemini 3 + REST):
        Se o modelo for 'gemini-3-flash-preview', usa a implementação REST direta (_generate_via_rest)
        para garantir suporte a 'thought_signature', que é filtrado pela biblioteca 'google-generativeai' (depreciada).
        """
        # Se for Gemini 3 Flash Preview, usar REST Bypass
        # SDK atual não suporta thought_signature
        if "gemini-3" in self.model_name or "thinking" in self.model_name:
            return self._generate_via_rest(messages, tools)

        # Implementação original via SDK (para modelos compatíveis como gemini-1.5, gemini-2.0)
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

                        # ✅ Configuração otimizada para Gemini 3 Flash + BI (precisão máxima)
                        # Ref: https://georgian.io/reduce-llm-costs-and-latency-guide/
                        generation_config = genai.GenerationConfig(
                            temperature=0.1,  # Baixo para precisão em BI (function calling determinístico)
                            top_p=0.9,       # Reduzido para respostas mais determinísticas
                            top_k=20,        # Reduzido para menos variabilidade
                            max_output_tokens=4096,  # Reduzido (gráficos retornam JSON pequeno)
                        )

                        # ✅ FIX CRÍTICO: Configurar tool_config com mode condicional
                        # Se detectar keywords de gráfico/visualização, FORÇAR uso de ferramentas (mode: ANY)
                        # Caso contrário, usar AUTO para dar flexibilidade ao LLM
                        tool_config = None
                        if gemini_tools:
                            # Detectar se mensagens contêm keywords de gráfico
                            all_content = " ".join([
                                m.get("parts", [{}])[0].get("text", "") if isinstance(m.get("parts"), list)
                                else str(m.get("content", ""))
                                for m in gemini_messages
                            ]).lower()

                            graph_keywords = [
                                "gráfico", "grafico", "chart", "gere", "mostre", "crie",
                                "visualização", "visualizacao", "plote", "ranking visual", "dashboard"
                            ]
                            force_tool_use = any(kw in all_content for kw in graph_keywords)

                            mode = "ANY" if force_tool_use else "AUTO"
                            if force_tool_use:
                                self.logger.warning(f"🎯 MODE: ANY - Forçando uso de ferramentas (keyword de gráfico detectada)")

                            tool_config = {
                                "function_calling_config": {
                                    "mode": mode
                                }
                            }

                        model = genai.GenerativeModel(
                            model_name=self.model_name,
                            tools=gemini_tools if gemini_tools else None,
                            tool_config=tool_config,
                            generation_config=generation_config,
                            # Use configurable system instruction (set during __init__)
                            system_instruction=self.system_instruction,
                            # SPEED OPTIMIZATION: Set thinking_level=low for latency-sensitive apps (Gemini 3+)
                            # Reduces response time by limiting model's thinking depth
                            # Ref: https://ai.google.dev/gemini-api/docs/models
                            thinking_level="low"
                        )

                        # ✅ FIX CRÍTICO: Usar generate_content com contents completos
                        # Em vez de start_chat, para preservar thought_signatures corretamente
                        # Ref: https://ai.google.dev/gemini-api/docs/thought-signatures
                        # O SDK gerencia thought_signatures automaticamente quando usamos generate_content
                        self.logger.info(
                            f"Chamada Gemini SDK (tentativa {attempt + 1}/"
                            f"{self.max_retries})"
                        )

                        response = model.generate_content(
                            contents=gemini_messages,
                            request_options={"timeout": 15}
                        )

                        self.logger.info("Chamada Gemini concluída.")

                        tool_calls = []
                        content = ""
                        
                        if response.candidates:
                            candidate = response.candidates[0]
                            if candidate.content and candidate.content.parts:
                                for part in candidate.content.parts:
                                    if part.function_call:
                                        function_call = part.function_call
                                        tool_call = {
                                            "id": f"call_{function_call.name}", # Gemini doesn't provide an ID, so we generate one
                                            "function": {
                                                "arguments": json.dumps(dict(function_call.args)),
                                                "name": function_call.name,
                                            },
                                            "type": "function",
                                        }

                                        # CRÍTICO: Capturar thought_signature do Gemini 3
                                        # Thought signatures são OBRIGATÓRIAS no Gemini 3 para function calling
                                        # Ref: https://ai.google.dev/gemini-api/docs/thought-signatures
                                        if hasattr(part, 'thought_signature') and part.thought_signature:
                                            tool_call["thought_signature"] = part.thought_signature
                                            self.logger.info(f"✅ Thought signature capturado para {function_call.name}")

                                        tool_calls.append(tool_call)
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
                thread.join(timeout=15.0)  # ✅ Gemini 3 Flash é 2x mais rápido que 1.5

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

    def _generate_via_rest(
        self,
        messages: List[Dict[str, str]],
        tools: Optional[Dict[str, List[Dict[str, Any]]]] = None,
    ) -> Dict[str, Any]:
        """
        Fallback implementation using direct REST API calls to support Gemini 3 thought_signatures.
        Bypasses the deprecated google-generativeai library limitations.
        """
        import requests
        
        self.logger.info(f"Usando REST API Bypass para modelo {self.model_name}")
        
        # Security: Send API Key in headers, not URL
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{self.model_name}:generateContent"
        headers = {
            "x-goog-api-key": self.gemini_api_key,
            "Content-Type": "application/json"
        }
        
        # 1. Converter mensagens para formato REST JSON
        gemini_messages = self._convert_messages_rest(messages)
        
        # 2. Preparar payload
        payload = {
            "contents": gemini_messages,
            "generationConfig": {
                "temperature": 0.1,
                "topP": 0.9,
                "topK": 20,
                "maxOutputTokens": 4096
            }
        }
        
        if self.system_instruction:
            payload["systemInstruction"] = {
                 "parts": [{"text": self.system_instruction}]
            }
            
        if tools:
            # Converter tools também
            # Formato tools REST: {"function_declarations": [...]}
            # Importante: O método _convert_tools retorna Objects 'Tool', precisamos extrair schemas
            # Mas aqui vamos assumir que o input 'tools' já vem no formato function_declarations wrapper
            # Simplificação: Converter manualmente o dicionário de entrada para o formato REST
            raw_functions = tools.get("function_declarations", [])
            payload["tools"] = [{
                "function_declarations": raw_functions
            }]

            # ✅ FIX: Mode condicional também no REST
            all_content_rest = " ".join([
                str(m.get("parts", [{}])[0].get("text", ""))
                for m in gemini_messages
            ]).lower()

            graph_keywords_rest = [
                "gráfico", "grafico", "chart", "gere", "mostre", "crie",
                "visualização", "visualizacao", "plote", "ranking visual"
            ]
            force_tool_use_rest = any(kw in all_content_rest for kw in graph_keywords_rest)
            mode_rest = "ANY" if force_tool_use_rest else "AUTO"

            if force_tool_use_rest:
                self.logger.warning(f"🎯 REST MODE: ANY - Forçando ferramentas")

            payload["toolConfig"] = {
                "function_calling_config": {"mode": mode_rest}
            }

        # 3. Executar com retry
        for attempt in range(self.max_retries):
            try:
                response = requests.post(url, json=payload, headers=headers, timeout=20)
                
                if response.status_code != 200:
                    error_msg = response.text
                    self.logger.warning(f"REST Error {response.status_code}: {error_msg}")
                    # Lógica de retry simples para erros 5xx/429
                    if response.status_code in [429, 500, 503] and attempt < self.max_retries - 1:
                        time.sleep(1 * (attempt + 1))
                        continue
                    return {"error": f"REST Error {response.status_code}: {error_msg}"}
                
                data = response.json()
                
                # 4. Processar resposta
                content = ""
                tool_calls = []
                
                candidates = data.get('candidates', [])
                if candidates:
                    candidate = candidates[0]
                    parts = candidate.get('content', {}).get('parts', [])
                    
                    for part in parts:
                        if 'functionCall' in part:
                            # Capturar function call E thought signature
                            fc = part['functionCall']
                            tc = {
                                "id": f"call_{fc['name']}",
                                "type": "function",
                                "function": {
                                    "name": fc['name'],
                                    # Args podem vir como objeto ou string vazia
                                    "arguments": json.dumps(fc.get('args', {}))
                                }
                            }
                            
                            # A MÁGICA: Capturar thoughtSignature
                            if 'thoughtSignature' in part:
                                tc["thought_signature"] = part['thoughtSignature']
                                self.logger.info(f"✅ REST: thought_signature capturado: {part['thoughtSignature'][:15]}...")
                            elif 'thought_signature' in part:
                                tc["thought_signature"] = part['thought_signature']
                            
                            tool_calls.append(tc)
                            content = "" # Se tem tool call, zerar content
                            break # Assume 1 tool call por vez por simplicidade
                        
                        elif 'text' in part:
                            content += part['text']
                
                result = {"content": content}
                if tool_calls:
                    result["tool_calls"] = tool_calls
                    
                return result

            except Exception as e:
                self.logger.error(f"REST Exception: {e}", exc_info=True)
                if attempt < self.max_retries - 1:
                    time.sleep(1)
                    continue
                return {"error": str(e)}
                
        return {"error": "Max retries exceeded via REST"}

    def _convert_messages_rest(self, messages: List[Dict[str, str]]) -> List[Dict[str, Any]]:
        """
        Converte mensagens para formato REST JSON puro (sem objetos SDK).
        """
        rest_messages = []
        for msg in messages:
            # Reutiliza lógica de _convert_messages mas retorna dicts puros compatíveis com JSON
            # _convert_messages do adapter já retorna dicts, mas precisamos garantir
            # que thought_signature (se existir) seja passado corretamente.
            
            # Chama o método existente pois ele já retorna Dicts
            # Mas precisamos validar se ele trata response function/tool_call corretamente
            # O método _convert_messages atual usa a lib SDK só para tipos? Não, retorna lista de dicts.
            # O problema é que _convert_messages gera estrutura que a lib SDK consome.
            # Para REST, a estrutura é a mesma (role, parts).
            
             # Precisamos apenas garantir compatibilidade de chaves snake_case vs camelCase?
             # A API Google aceita JSON, geralmente snake_case funciona ou camelCase.
             # Vamos reutilizar _convert_messages e ajustar keys se necessário.
             
             # Nota: _convert_messages retorna {"role": ..., "parts": [...]}
             # A API aceita isso.
             # O PULO DO GATO: Se tiver thought_signature no input msg (tool_calls),
             # _convert_messages JA coloca no output.
             # Vamos apenas chamar e transformar keys se precisar (SDK aceita snake, REST prefere camel?)
             # O endpoint v1beta aceita snake_case em muitas coisas. Vamos testar.
             # Se falhar, converter para camelCase (function_call -> functionCall)
             
            converted_msgs = self._convert_messages([msg]) # Processar 1 por 1
            for cvt_msg in converted_msgs:
                # Ajuste fino para REST se necessário
                # Part keys: function_call -> functionCall, thought_signature -> thoughtSignature
                # Mas API geralmente aceita snake_case se enviado via JSON.
                # Vamos converter para camelCase para garantir.
                
                new_parts = []
                for part in cvt_msg.get("parts", []):
                    new_part = {}
                    if "text" in part:
                        new_part["text"] = part["text"]
                    if "function_call" in part:
                        new_part["functionCall"] = part["function_call"]
                    if "function_response" in part:
                        new_part["functionResponse"] = part["function_response"]
                    
                    # CRÍTICO: Injetar thought_signature
                    # O REST API v1beta espera 'thought_signature' no snake_case ou camelCase?
                    # Testes anteriores indicam que o erro reclama de "missing thought_signature".
                    # Vamos enviar AMBOS se possível, ou tentar focar no que funcionou no curl.
                    # Mas "thought_signature" não é um campo padrão de 'Part' na definição proto.
                    # Ele é um campo irmão de functionCall? Não, é um campo dentro de Part?
                    # A doc diz: Part { text, data, functionCall, functionResponse }
                    # MAS para Gemini 3, existe um campo oculto.
                    # Vamos tentar passar como atributo direto e também dentro de functionCall se a API permitir (improvável).
                    
                    if "thought_signature" in part:
                         # Tentar camelCase que é padrão JSON do Google
                         new_part["thoughtSignature"] = part["thought_signature"]
                         # Fallback snake_case just in case
                         new_part["thought_signature"] = part["thought_signature"] 
                         self.logger.info("REST: Injetando thoughtSignature no request")
                         
                    new_parts.append(new_part)
                
                rest_messages.append({
                    "role": cvt_msg["role"],
                    "parts": new_parts
                })
                
        return rest_messages

    def _convert_messages(self, messages: List[Dict[str, str]]) -> List[Dict[str, Any]]:
        """
        Converte mensagens do formato OpenAI-like para formato Gemini.
        MANTER MÉTODO ORIGINAL para compatibilidade
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
                parts = []
                for tc in tool_calls:
                    part = {
                        "function_call": {
                            "name": tc["function"]["name"],
                            "args": json.loads(tc["function"]["arguments"])
                        }
                    }

                    # CRÍTICO: Preservar thought_signature (obrigatório no Gemini 3)
                    if "thought_signature" in tc and tc["thought_signature"]:
                        part["thought_signature"] = tc["thought_signature"]
                        pass  # Removed verbose logging for performance

                    parts.append(part)

                gemini_msg = {
                    "role": "model",
                    "parts": parts
                }
            elif function_call:
                # User's turn: provides tool response
                final_content = content if content and content.strip() else "."
                
                gemini_msg = {
                    "role": "user",
                    "parts": [
                        {
                            "function_response": {
                                "name": function_call["name"],
                                "response": {"content": final_content}
                            }
                        }
                    ]
                }
            elif role == "user":
                final_content = content if content and content.strip() else "."
                gemini_msg = {"role": "user", "parts": [{"text": final_content}]}
            elif role == "assistant" or role == "model":
                final_content = content if content and content.strip() else "."
                gemini_msg = {"role": "model", "parts": [{"text": final_content}]}
            else: 
                self.logger.warning(f"Unexpected role encountered: {role}. Treating as 'user'.")
                final_content = content if content and content.strip() else "."
                gemini_msg = {"role": "user", "parts": [{"text": final_content}]}

            gemini_messages.append(gemini_msg)

        return gemini_messages

    def _convert_tools(self, tools_wrapper: Dict[str, List[Dict[str, Any]]]) -> List['Tool']:
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

        return [Tool(function_declarations=gemini_tools)]

