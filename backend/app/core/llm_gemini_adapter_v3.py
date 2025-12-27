"""
GeminiLLMAdapter V3 - Usando o NOVO SDK google-genai (Oficial 2025)
Suporte nativo para Thinking (Reasoning) e Function Calling simplificado.
"""

from typing import List, Dict, Any, Optional
import logging
import json
import os
from google import genai
from google.genai import types
from app.core.llm_base import BaseLLMAdapter
from app.config.settings import settings

logger = logging.getLogger(__name__)

class GeminiLLMAdapterV3(BaseLLMAdapter):
    """
    Adapter moderno usando o SDK google-genai (v1.0.0+)
    Suporta nativamente o 'thinking' do Gemini 3.0+.
    """

    def __init__(
        self, 
        model_name: Optional[str] = None, 
        gemini_api_key: Optional[str] = None, 
        system_instruction: Optional[str] = None
    ):
        self.logger = logging.getLogger(__name__)
        
        api_key = gemini_api_key or settings.GEMINI_API_KEY
        if not api_key:
            raise ValueError("GEMINI_API_KEY não configurada")

        # Inicializar o novo cliente
        self.client = genai.Client(api_key=api_key)
        
        self.model_name = model_name or settings.LLM_MODEL_NAME or "gemini-3-flash-preview"
        self.system_instruction = system_instruction
        
        self.logger.info(f"[OK] GeminiLLMAdapterV3 inicializado: {self.model_name}")

    def get_completion(
        self,
        messages: List[Dict[str, str]],
        tools: Optional[Dict[str, List[Dict[str, Any]]]] = None,
    ) -> Dict[str, Any]:
        """
        Obtém completion usando o novo SDK.
        Inclui o 'thought process' (thinking) na resposta se disponível.
        """
        try:
            # 1. Converter mensagens para formato SDK v3
            contents = self._convert_messages(messages)
            
            # 2. Configurar Ferramentas
            sdk_tools = []
            if tools:
                sdk_tools = self._convert_tools_to_sdk(tools)

            # 3. Configuração de Geração (incluindo Thinking)
            config = types.GenerateContentConfig(
                system_instruction=self.system_instruction,
                temperature=0.1,
                top_p=0.9,
                max_output_tokens=4096,
                tools=sdk_tools if sdk_tools else None,
                # Ativar Thinking para modelos 3.0+
                thinking_config=types.ThinkingConfig(
                    include_thoughts=True,
                    thinking_budget=1024 # Ajustável conforme necessidade
                ) if "gemini-3" in self.model_name.lower() else None
            )

            self.logger.info(f"[SEND] Enviando requisição para {self.model_name}")
            
            # 4. Chamar API
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=contents,
                config=config
            )

            self.logger.info("[RCV] Resposta recebida")

            # 5. Processar Resposta
            content_text = ""
            thought_text = ""
            tool_calls = []

            # Extrair pensamento (thought) e texto
            if response.candidates:
                candidate = response.candidates[0]
                if candidate.content and candidate.content.parts:
                    for part in candidate.content.parts:
                        # No novo SDK (v1.0.0+), o pensamento vem em part.thought (se habilitado)
                        # ou pode vir em campos específicos dependendo da versão do modelo
                        if hasattr(part, 'thought') and part.thought:
                            # Se for booleano True (apenas indicando que pensou), não concatenamos. 
                            # Se for string, adicionamos.
                            if isinstance(part.thought, str):
                                thought_text += part.thought
                            elif hasattr(part, 'text') and part.text and not content_text:
                                # Em algumas versões preview, o thought pode estar no part.text 
                                # se for a primeira parte
                                pass
                        
                        if part.text:
                            content_text += part.text
                        
                        if part.function_call:
                            tool_calls.append({
                                "id": f"call_{part.function_call.name}",
                                "function": {
                                    "name": part.function_call.name,
                                    "arguments": json.dumps(part.function_call.args)
                                },
                                "type": "function",
                                "_native_part": part # Mantemos para histórico se necessário
                            })

            result = {
                "content": content_text,
                "thought": thought_text if thought_text else None
            }
            
            if tool_calls:
                result["tool_calls"] = tool_calls
                
            return result

        except Exception as e:
            self.logger.error(f"[ERR] Erro no Gemini V3: {e}", exc_info=True)
            return {"error": str(e)}

    def _convert_messages(self, messages: List[Dict[str, str]]) -> List[types.Content]:
        """Converte o histórico para o formato do novo SDK"""
        sdk_messages = []
        for msg in messages:
            role = msg.get("role", "user")
            # Mapear roles: assistant -> model
            sdk_role = "model" if role == "assistant" else role
            
            content = msg.get("content", "")
            tool_calls = msg.get("tool_calls")
            
            parts = []
            
            # Se tiver tool calls no histórico
            if tool_calls:
                for tc in tool_calls:
                    if "_native_part" in tc:
                        parts.append(tc["_native_part"])
                    else:
                        # Reconstrução manual se não tiver nativo (pode falhar no Gemini 3.0)
                        parts.append(types.Part.from_function_call(
                            name=tc["function"]["name"],
                            args=json.loads(tc["function"]["arguments"])
                        ))
            
            # Se for resposta de ferramenta
            elif msg.get("function_call"): # Marcador de resposta de função
                func_name = msg["function_call"].get("name")
                parts.append(types.Part.from_function_response(
                    name=func_name,
                    response={"result": content}
                ))
            
            # Texto normal
            else:
                if content:
                    parts.append(types.Part.from_text(text=content))
                else:
                    parts.append(types.Part.from_text(text=".")) # Evitar vazio

            if parts:
                sdk_messages.append(types.Content(role=sdk_role, parts=parts))
        
        return sdk_messages

    def _convert_tools_to_sdk(self, tools_wrapper: Dict[str, Any]) -> List[types.Tool]:
        """Converte declarações de funções para o novo formato de Tools"""
        decls = tools_wrapper.get("function_declarations", [])
        functions = []
        for d in decls:
            functions.append(types.FunctionDeclaration(
                name=d["name"],
                description=d["description"],
                parameters=d["parameters"]
            ))
        
        if functions:
            return [types.Tool(function_declarations=functions)]
        return []

    # Compatibilidade com padrões existentes
    def get_llm(self): return self
    
    async def generate_response(self, prompt: str) -> str:
        res = self.get_completion([{"role": "user", "content": prompt}])
        if "error" in res: raise Exception(res["error"])
        return res["content"]
