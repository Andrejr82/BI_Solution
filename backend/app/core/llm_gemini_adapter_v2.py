"""
GeminiLLMAdapter V2 - Usando objetos nativos do SDK
SOLUÇÃO PARA THOUGHT SIGNATURES - Usar Content/Part nativos em vez de dicionários
"""

from typing import List, Dict, Any, Optional
import logging
import json
import os
import google.generativeai as genai
from google.generativeai.protos import Content, Part, FunctionCall, FunctionResponse
from app.core.llm_base import BaseLLMAdapter
from app.config.settings import settings

logger = logging.getLogger(__name__)


def _convert_to_serializable(obj):
    """
    Converte recursivamente objetos Protobuf (MapComposite, RepeatedComposite) 
    para tipos Python nativos (dict, list).
    
    CRÍTICO: Esta função resolve o erro "Object of type MapComposite is not JSON serializable"
    que ocorre quando a API Gemini retorna objetos especiais em function_call.args.
    """
    # MapComposite (dict-like do Protobuf)
    if hasattr(obj, 'keys') and callable(getattr(obj, 'keys')):
        return {k: _convert_to_serializable(v) for k, v in obj.items()}
    
    # RepeatedComposite (list-like do Protobuf)
    elif hasattr(obj, '__iter__') and not isinstance(obj, (str, bytes)):
        try:
            return [_convert_to_serializable(item) for item in obj]
        except TypeError:
            # Não é iterável de fato
            pass
    
    # Tipos primitivos - retornar como está
    if isinstance(obj, (str, int, float, bool, type(None))):
        return obj
    
    # Fallback: tentar converter para string
    return str(obj)


class GeminiLLMAdapterV2(BaseLLMAdapter):
    """
    Adapter usando OBJETOS NATIVOS do SDK para preservar thought_signatures automaticamente
    """

    def __init__(self, model_name: Optional[str] = None, gemini_api_key: Optional[str] = None, system_instruction: Optional[str] = None):
        self.logger = logging.getLogger(__name__)

        api_key = gemini_api_key or settings.GEMINI_API_KEY
        if not api_key:
            raise ValueError("GEMINI_API_KEY não configurada")

        genai.configure(api_key=api_key)
        self.model_name = model_name or settings.LLM_MODEL_NAME or "gemini-3-flash-preview"
        self.system_instruction = system_instruction
        self.max_retries = 3

        self.logger.info(f"[OK] GeminiLLMAdapterV2 inicializado: {self.model_name}")

    def get_completion(
        self,
        messages: List[Dict[str, str]],
        tools: Optional[Dict[str, List[Dict[str, Any]]]] = None,
    ) -> Dict[str, Any]:
        """
        Obtém completion usando objetos NATIVOS do SDK (Content/Part)
        Isso garante que thought_signatures sejam preservados automaticamente
        """
        try:
            # Converter ferramentas para formato Gemini
            gemini_tools = []
            if tools:
                gemini_tools = self._convert_tools(tools)

            # Configuração de geração
            generation_config = genai.GenerationConfig(
                temperature=0.1,
                top_p=0.9,
                top_k=20,
                max_output_tokens=4096,
            )

            tool_config = None
            if gemini_tools:
                tool_config = {
                    "function_calling_config": {
                        "mode": "AUTO"
                    }
                }

            # Criar modelo
            model = genai.GenerativeModel(
                model_name=self.model_name,
                tools=gemini_tools if gemini_tools else None,
                tool_config=tool_config,
                generation_config=generation_config,
                system_instruction=self.system_instruction
            )

            # [OK] CRITICAL: Converter mensagens para objetos NATIVOS Content/Part
            contents = self._messages_to_contents(messages)

            self.logger.info(f"[SEND] Enviando {len(contents)} contents para Gemini")
            for i, content in enumerate(contents):
                self.logger.info(f"  Content {i}: role={content.role}, parts={len(content.parts)}")

            # Chamar generate_content com objetos nativos
            response = model.generate_content(
                contents=contents,
                request_options={"timeout": 15}
            )

            self.logger.info("[RCV] Resposta recebida do Gemini")

            # Processar resposta
            tool_calls = []
            content = ""

            if response.candidates:
                candidate = response.candidates[0]
                if candidate.content and candidate.content.parts:
                    for part in candidate.content.parts:
                        if part.function_call:
                            # [OK] Armazenar o Part INTEIRO (inclui thought_signature automaticamente)
                            tool_calls.append({
                                "id": f"call_{part.function_call.name}",
                                "function": {
                                    "name": part.function_call.name,
                                    # CRÍTICO: Usar _convert_to_serializable para evitar erro "MapComposite is not JSON serializable"
                                    "arguments": json.dumps(_convert_to_serializable(part.function_call.args)),
                                },
                                "type": "function",
                                "_native_part": part  # [OK] Guardar Part nativo
                            })
                            self.logger.info(f"[CALL] Function call: {part.function_call.name}")
                            if hasattr(part, 'thought_signature') and part.thought_signature:
                                self.logger.info(f"[THOUGHT] Thought signature presente ({len(part.thought_signature)} bytes)")
                        elif part.text:
                            content = part.text

            result = {"content": content}
            if tool_calls:
                result["tool_calls"] = tool_calls

            return result

        except Exception as e:
            self.logger.error(f"[ERR] Erro ao chamar Gemini: {e}", exc_info=True)
            return {"error": str(e)}

    def _messages_to_contents(self, messages: List[Dict[str, str]]) -> List[Content]:
        """
        Converte mensagens do formato OpenAI-like para objetos NATIVOS Content/Part do Gemini.
        Lida com a persistência de histórico: se um tool call antigo não tiver _native_part
        (porque veio do banco de dados/JSON), ele deve ser removido para evitar Erro 400 (missing thought_signature).
        """
        contents = []
        last_content_was_tool_call = False

        for msg in messages:
            role = msg.get("role", "user")
            content_text = msg.get("content", "")
            tool_calls = msg.get("tool_calls")
            function_call_meta = msg.get("function_call")

            # Mapear role
            gemini_role = "model" if role in ["assistant", "model"] else "user"

            # 1. Se tiver tool_calls (modelo chamando função)
            if tool_calls:
                parts = []
                has_native = False
                for tc in tool_calls:
                    # [OK] CRITICAL: Usar Part nativo se disponível
                    if "_native_part" in tc:
                        parts.append(tc["_native_part"])
                        self.logger.info(f"[OK] Reusando Part nativo com thought_signature")
                        has_native = True
                    else:
                        # Se não tem native part (veio do histórico JSON), NÃO podemos usar.
                        # Gemini 3.0+ exige thought_signature. Sem ele = Erro 400.
                        # Melhor dropar esse turno do histórico do que falhar.
                        pass

                if has_native:
                    contents.append(Content(role="model", parts=parts))
                    last_content_was_tool_call = True
                else:
                    self.logger.warning(f"[WARN] Dropando tool call do historico sem assinatura (evita Erro 400)")
                    last_content_was_tool_call = False # Marcamos que pulamos, para pular a resposta também

            # 2. Se tiver function response (usuário respondendo com resultado da função)
            elif function_call_meta:
                # Só adicionamos a resposta se a chamada anterior foi mantida.
                # Gemini exige par Call -> Response.
                if last_content_was_tool_call:
                    func_name = function_call_meta.get("name")
                    
                    # ✅ FIX CRÍTICO: Garantir que o conteúdo do function_response nunca seja vazio
                    final_content = content_text if content_text and content_text.strip() else "."
                    
                    parts = [
                        Part(function_response=FunctionResponse(
                            name=func_name,
                            response={"content": final_content}
                        ))
                    ]
                    contents.append(Content(role="user", parts=parts))
                    last_content_was_tool_call = False # Reset para próximo ciclo
                else:
                    self.logger.warning(f"[WARN] Dropando resposta de funcao orfa do historico (evita confusao do modelo)")
                    last_content_was_tool_call = False

            # 3. Mensagem de texto normal
            elif role != "system":  # Filtrar system
                # Ensure content is not empty to avoid API error
                final_text = content_text
                if not final_text or not final_text.strip():
                    self.logger.warning(f"[WARN] Empty content detected for role {role}. Using placeholder.")
                    final_text = "." # Placeholder to satisfy API requirements

                parts = [Part(text=final_text)]
                contents.append(Content(role=gemini_role, parts=parts))
                last_content_was_tool_call = False

        return contents

    def _convert_tools(self, tools_wrapper: Dict[str, List[Dict[str, Any]]]) -> List:
        """Converte ferramentas para formato Gemini"""
        from google.generativeai.types import FunctionDeclaration, Tool

        function_declarations = tools_wrapper.get("function_declarations", [])
        gemini_tools = []

        for tool_declaration in function_declarations:
            gemini_tool = FunctionDeclaration(
                name=tool_declaration.get("name", ""),
                description=tool_declaration.get("description", ""),
                parameters=tool_declaration.get("parameters", {}),
            )
            gemini_tools.append(gemini_tool)

        return [Tool(function_declarations=gemini_tools)]

    def get_llm(self):
        """Retorna self para compatibilidade"""
        return self

    def invoke(self, input: Any, config: Optional[Dict] = None) -> Any:
        """Implementation of LangChain Runnable protocol"""
        from langchain_core.messages import AIMessage, HumanMessage

        if isinstance(input, str):
            messages = [{"role": "user", "content": input}]
        elif isinstance(input, list):
            # Converter LangChain messages
            messages = []
            for msg in input:
                if hasattr(msg, 'content'):
                    role = "user" if isinstance(msg, HumanMessage) else "model"
                    messages.append({"role": role, "content": msg.content})
        else:
            messages = [{"role": "user", "content": str(input)}]

        result = self.get_completion(messages)

        if "error" in result:
            raise ValueError(result["error"])

        return AIMessage(content=result.get("content", ""))

    async def generate_response(self, prompt: str) -> str:
        """Wrapper para compatibilidade"""
        messages = [{"role": "user", "content": prompt}]
        result = self.get_completion(messages)

        if "error" in result:
            raise Exception(result["error"])

        return result.get("content", "")
