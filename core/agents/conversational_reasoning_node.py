"""
Módulo de Raciocínio Conversacional - Conversational Reasoning Engine

Este módulo implementa uma camada de raciocínio explícito que torna o agente
verdadeiramente conversacional, não apenas um executor de queries.

Baseado em Extended Thinking patterns do Context7 Anthropic Cookbook.

Author: devAndreJr
Version: 3.0.0 - Conversational AI
"""

import logging
import json
import re
from typing import Dict, Any, Tuple, List, Optional
from core.agent_state import AgentState
from core.llm_base import BaseLLMAdapter

logger = logging.getLogger(__name__)


class ConversationalReasoningEngine:
    """
    🧠 Motor de Raciocínio Conversacional

    Implementa Extended Thinking para análise profunda da intenção do usuário,
detectando contexto emocional, necessidades implícitas e escolhendo o modo
    de resposta adequado (conversacional vs analítico).
    """

    def __init__(self, llm_adapter: BaseLLMAdapter):
        """
        Inicializa o motor de raciocínio.

        Args:
            llm_adapter: Adaptador LLM (Gemini ou DeepSeek)
        """
        self.llm_adapter = llm_adapter
        self.conversation_memory: List[Dict[str, str]] = []
        logger.info("🧠 ConversationalReasoningEngine inicializado")

    def _get_full_conversation_context(self, messages: List, max_messages: int = 8) -> str:
        """
        Formata o histórico completo da conversa em uma única string legível.

        Args:
            messages: Lista de mensagens
            max_messages: Número máximo de mensagens recentes a incluir (padrão: 8)
        """
        if not messages:
            return "(Nenhuma mensagem na conversa)"

        # 🔧 OTIMIZAÇÃO: Usar apenas as últimas N mensagens para evitar prompts gigantes
        recent_messages = messages[-max_messages:] if len(messages) > max_messages else messages

        history = []
        for msg in recent_messages:
            try:
                role = "Usuário"
                content = ""
                # Lidar com objetos de mensagem Langchain e dicionários do Streamlit
                if hasattr(msg, 'type'): # Langchain BaseMessage
                    if msg.type == 'ai':
                        role = "Caculinha"
                    content = str(getattr(msg, 'content', ''))
                elif isinstance(msg, dict): # Streamlit session_state message
                    if msg.get('role') == 'assistant':
                        role = "Caculinha"

                    msg_content = msg.get('content', '')
                    if isinstance(msg_content, dict):
                        # Tentar extrair conteúdo de um dicionário aninhado
                        content = msg_content.get('content', str(msg_content))
                    else:
                        content = str(msg_content)
                else: # Fallback
                    content = str(msg)

                # Truncar mensagens muito longas para manter o prompt focado
                content_preview = content.replace('\n', ' ')
                content_preview = content_preview[:200] + "..." if len(content_preview) > 200 else content_preview
                history.append(f"{role}: {content_preview}")
            except Exception as e:
                logger.warning(f"Erro ao formatar mensagem do histórico: {e}")
                continue

        # 📊 LOG: Indicar se histórico foi truncado
        if len(messages) > max_messages:
            logger.info(f"📝 Histórico truncado: {len(messages)} msgs → {len(recent_messages)} msgs recentes")
            history.insert(0, f"(... {len(messages) - max_messages} mensagens anteriores omitidas ...)")

        return "\n".join(history)

    def reason_about_user_intent(self, state: AgentState) -> Tuple[str, Dict[str, Any]]:
        """
        🎯 RACIOCÍNIO PROFUNDO: Analisa a intenção do usuário com Extended Thinking

        Este método implementa a primeira camada de processamento, onde o agente:
        1. Analisa o contexto completo da conversa
        2. Detecta o tom emocional do usuário
        3. Identifica necessidades implícitas
        4. Decide o modo de resposta apropriado

        Args:
            state: Estado atual do agente com histórico de mensagens

        Returns:
            Tupla (mode, reasoning_result):
            - mode: "conversational" ou "analytical"
            - reasoning_result: Dicionário com análise detalhada
        """
        messages = state.get("messages", [])
        if not messages:
            logger.warning("⚠️ Nenhuma mensagem no estado")
            return "conversational", self._create_fallback_reasoning()

        # 🔧 PROTEÇÃO ANTI-LOOP: Se conversa tem > 4 mensagens e ainda não executou, forçar analítico
        if len(messages) > 4:
            # Contar quantas mensagens do assistente são perguntas
            assistant_questions = 0
            for msg in messages:
                if hasattr(msg, 'type') and msg.type == 'ai':
                    content = str(getattr(msg, 'content', ''))
                    if '?' in content:
                        assistant_questions += 1
                elif isinstance(msg, dict) and msg.get('role') == 'assistant':
                    content = str(msg.get('content', ''))
                    if '?' in content:
                        assistant_questions += 1

            # Se já fez 2+ perguntas, FORÇAR modo analítico
            if assistant_questions >= 2:
                logger.warning(f"🚨 ANTI-LOOP ATIVADO: {assistant_questions} perguntas feitas, forçando modo analítico")
                return "analytical", {
                    "mode": "analytical",
                    "reasoning": "Conversa muito longa sem execução. Forçando análise com defaults.",
                    "emotional_tone": "neutro",
                    "confidence": 0.8,
                    "needs_clarification": False,
                    "next_action": {
                        "type": "use_tool",
                        "response_style": "technical"
                    }
                }

        # ✅ CORREÇÃO: Usar o contexto completo da conversa
        full_conversation_context = self._get_full_conversation_context(messages)
        log_context = full_conversation_context.replace('\n', ' ')
        logger.info(f"🧠 Analisando intent (contexto completo): '{log_context[-150:]}...'")

        # 🧠 PROMPT DE RACIOCÍNIO PROFUNDO
        reasoning_prompt = self._build_reasoning_prompt(full_conversation_context)

        # 📊 LOG: Tamanho do prompt de raciocínio
        prompt_size = len(reasoning_prompt)
        logger.info(f"📏 Tamanho do prompt de reasoning: {prompt_size} chars (~{prompt_size//4} tokens estimados)")

        try:
            # 🔥 CORREÇÃO: Temperatura BAIXA para decisões consistentes
            response = self.llm_adapter.get_completion(
                messages=[{"role": "user", "content": reasoning_prompt}],
                json_mode=True,
                temperature=0.3,  # 🔧 FIX: Baixa temp para decisões consistentes (era 0.8)
                max_tokens=1500,  # 🔧 OTIMIZADO: de 2000 para 1500 (suficiente para JSON de raciocínio)
                cache_context={"operation": "conversational_reasoning", "stage": "intent_analysis"}
            )

            # ✅ VERIFICAR ERRO NA RESPOSTA
            if response.get("error"):
                error_msg = response.get('error', 'Erro desconhecido')
                logger.error(f"❌ Erro na API ao gerar raciocínio: {error_msg}")
                return "conversational", self._create_fallback_reasoning()

            reasoning_result = self._parse_reasoning(response.get("content", "{}"))

            # 📊 LOGGING DETALHADO
            mode = reasoning_result.get("mode", "conversational")
            emotional_tone = reasoning_result.get("emotional_tone", "neutro")
            confidence = reasoning_result.get("confidence", 0.5)

            logger.info(f"🎯 Mode: {mode} | Emotion: {emotional_tone} | Confidence: {confidence:.2f}")
            logger.info(f"💭 Reasoning: {reasoning_result.get('reasoning', 'N/A')[:100]}...")

            return mode, reasoning_result

        except Exception as e:
            logger.error(f"❌ Erro no raciocínio: {e}", exc_info=True)
            return "conversational", self._create_fallback_reasoning()

    def generate_conversational_response(
        self,
        reasoning: Dict[str, Any],
        state: AgentState
    ) -> str:
        """
        💬 MODO CONVERSACIONAL: Gera resposta natural e humana

        Este método é acionado quando o usuário:
        - Está conversando casualmente
        - Precisa de clarificação
        - Fez uma saudação/agradecimento
        - Está frustrado e precisa de empatia

        Args:
            reasoning: Resultado da análise de raciocínio
            state: Estado atual do agente

        Returns:
            Resposta conversacional natural em português
        """
        messages = state.get("messages", [])
        full_conversation_context = self._get_full_conversation_context(messages)
        emotional_tone = reasoning.get("emotional_tone", "neutro")
        
        # 🎨 PROMPT CONVERSACIONAL com temperatura máxima
        conversational_prompt = self._build_conversational_prompt(
            full_conversation_context,
            emotional_tone,
            reasoning
        )

        logger.info(f"💬 Gerando resposta conversacional (tom: {emotional_tone})")

        # 📊 LOG: Tamanho do prompt
        prompt_size = len(conversational_prompt)
        logger.info(f"📏 Tamanho do prompt conversacional: {prompt_size} chars (~{prompt_size//4} tokens estimados)")

        try:
            response = self.llm_adapter.get_completion(
                messages=[{"role": "user", "content": conversational_prompt}],
                temperature=1.0,  # 🔥 TEMPERATURA MÁXIMA = respostas mais humanas
                max_tokens=1500,  # 🔧 AUMENTADO: de 800 para 1500 (mais espaço para resposta)
                cache_context={"operation": "conversational_response", "tone": emotional_tone}
            )

            # ✅ TRATAMENTO: Verificar se há mensagem de erro do LLM
            if response.get("error"):
                error_msg = response.get('error', 'Erro desconhecido')
                logger.error(f"❌ Erro na API ao gerar resposta conversacional: {error_msg}")

                # Se houver user_message, usar ela
                if response.get("user_message"):
                    logger.warning(f"⚠️ Usando mensagem de fallback da API")
                    return response.get("user_message")

                # Senão, usar fallback baseado no tom
                return self._get_fallback_response(emotional_tone)

            response_text = response.get("content", "")

            # Verificar se resposta está vazia
            if not response_text or len(response_text.strip()) == 0:
                logger.warning(f"⚠️ Resposta vazia recebida do LLM. Usando fallback.")
                return self._get_fallback_response(emotional_tone)

            # Remover possíveis tags JSON se houver
            response_text = self._clean_response(response_text)

            logger.info(f"✅ Resposta conversacional gerada: {len(response_text)} chars")
            return response_text

        except Exception as e:
            logger.error(f"❌ Erro ao gerar resposta conversacional: {e}", exc_info=True)
            return self._get_fallback_response(emotional_tone)

    def _build_reasoning_prompt(self, full_conversation: str) -> str:
        """Constrói o prompt de raciocínio profundo"""

        return f"""# 🧠 ANÁLISE DE INTENÇÃO CONVERSACIONAL

Você é a Caculinha, uma assistente de BI conversacional. Você NÃO é um robô executor de queries.

## 📚 CONTEXTO DA CONVERSA COMPLETA
{full_conversation}

## 🤔 TAREFA: PENSAR PROFUNDAMENTE

Analise a **conversa completa** e responda estas perguntas em seu raciocínio:

1. **Intenção Real**: O que o usuário REALMENTE quer? Considere o histórico para resolver ambiguidades na última mensagem.
2. **Tom Emocional**: Como ele está se sentindo? (frustrado/curioso/casual/urgente/neutro/confuso)
3. **Contexto**: A última mensagem é uma continuação da conversa anterior ou um novo tópico?
4. **Clareza**: O usuário já forneceu todas as informações necessárias ou ainda faltam detalhes?
5. **Tipo de Resposta**: Com base em tudo, devo conversar ou executar uma análise técnica?

## 🎯 CATEGORIZAÇÃO

**MODO CONVERSACIONAL** - Use quando:
- Saudações/agradecimentos/despedidas/conversa casual.
- Perguntas sobre suas capacidades ("o que você faz?", "pode me ajudar com...").
- Feedback emocional ("não entendi", "está confuso", "muito obrigado").
- Informação está GENUINAMENTE INSUFICIENTE (falta UNE, período, produto específico, etc).

**MODO ANALÍTICO** - Use quando:
- O pedido para dados/análise está CLARO e COMPLETO, considerando todo o histórico.
- O usuário forneceu a última informação que faltava para uma análise.
- A query é técnica e bem definida (ex: "MC do produto 123 na UNE SCR").
- O usuário já respondeu a uma pergunta de clarificação sua.
- Pedidos como "gráfico de TODOS os segmentos" são CLAROS (use métrica padrão: vendas).

## ⚠️ REGRAS ANTI-LOOP (CRÍTICO)

🔴 **NUNCA faça perguntas repetidas!**
- Se você JÁ PERGUNTOU algo no histórico e o usuário respondeu → vá para MODO ANALÍTICO
- Se o usuário disse "todos" (ex: "todos os segmentos") → NÃO pergunte qual! Use TODOS mesmo.
- Se a conversa tem > 3 mensagens e ainda não executou → FORCE modo analítico com defaults razoáveis

🔴 **Defaults Inteligentes:**
- "gráfico de segmentos" → assumir métrica de vendas (padrão)
- "todos os produtos" → assumir top 10 ou 20
- Falta detalhes menores → assumir defaults e EXECUTAR

## 📤 RESPOSTA (JSON)

```json
{{
  "mode": "conversational" ou "analytical",
  "reasoning": "Seu raciocínio em 2-3 frases explicando POR QUE escolheu este modo, com base no histórico.",
  "emotional_tone": "frustrado/curioso/casual/urgente/neutro/confuso",
  "confidence": 0.0-1.0,
  "needs_clarification": true/false,
  "clarification_question": "pergunta natural se needs_clarification=true, senão null",
  "missing_info": ["lista", "de", "informações", "faltando"] ou null,
  "next_action": {{
    "type": "respond_directly" ou "use_tool" ou "ask_clarification",
    "response_style": "friendly/empathetic/technical/excited/patient"
  }}
}}
```

**IMPORTANTE**:
- Se a última mensagem do usuário for uma resposta a uma pergunta sua, use o histórico para decidir se agora você tem informação suficiente para o **MODO ANALÍTICO**.
- 🔧 **NOVO:** Prefira "analytical" quando houver informação SUFICIENTE, mesmo que não seja PERFEITA. Use defaults inteligentes em vez de perguntar tudo.
"""

    def _build_conversational_prompt(
        self,
        full_conversation: str,
        emotional_tone: str,
        reasoning: Dict[str, Any]
    ) -> str:
        """Constrói o prompt para resposta conversacional"""

        clarification_question = reasoning.get("clarification_question", "")
        missing_info = reasoning.get("missing_info", [])
        response_style = reasoning.get("next_action", {}).get("response_style", "friendly")

        # 🎨 Exemplos de tom baseados na emoção detectada
        tone_examples = {
            "frustrado": '''
**Tom Empático:**
"Opa, vi que você tá tentando há um tempo e não deu certo. 😕 Deixa eu te ajudar de outro jeito..."
"Poxa, desculpa pela confusão! Vou te explicar melhor..."
            ''',
            "curioso": '''
**Tom Entusiasmado:**
"Boa pergunta! 😊 Vou te mostrar algo interessante sobre isso..."
"Olha só que legal! Isso que você perguntou é super importante porque..."
            ''',
            "casual": '''
**Tom Leve:**
"Claro! Vou dar uma olhada nisso pra você 👀"
"Tranquilo! Deixa comigo..."
            ''',
            "urgente": '''
**Tom Ágil:**
"Entendi, vou resolver isso rapidinho pra você! ⚡"
"Pode deixar, já vou te trazer essa informação!"
            ''',
            "confuso": '''
**Tom Paciente:**
"Sem problemas! Deixa eu te explicar melhor... 😊"
"Vou te guiar passo a passo, fica tranquilo!"
            ''',
            "neutro": '''
**Tom Profissional Amigável:**
"Claro! Vou te ajudar com isso."
"Entendi. Deixa eu te mostrar..."
            '''
        }

        tone_example = tone_examples.get(emotional_tone, tone_examples["neutro"])

        # Construir seção de informações faltando
        missing_info_section = ""
        if missing_info:
            missing_list = ', '.join(missing_info)
            missing_info_section = f"## ❓ INFORMAÇÕES FALTANDO\n{missing_list}\n\n"

        # Construir seção de clarificação ou resposta
        if clarification_question:
            task_section = f"## 🎯 CLARIFICAÇÃO NECESSÁRIA\n\n{clarification_question}\n\nResponda de forma natural fazendo esta pergunta, mas reformule com suas palavras!"
        else:
            task_section = "## 🎯 RESPONDA À MENSAGEM\n\nResponda naturalmente à última mensagem do usuário no tom apropriado, considerando todo o contexto."

        return f'''# 💬 RESPOSTA CONVERSACIONAL DA CACULINHA

Você é a Caculinha. Responda de forma COMPLETAMENTE NATURAL e HUMANA.

## 🎭 CONTEXTO EMOCIONAL
Usuário está: **{emotional_tone}**
Estilo de resposta: **{response_style}**

## 📜 CONVERSA COMPLETA
{full_conversation}

## 🧠 SEU RACIOCÍNIO
{reasoning.get('reasoning', '')}

{missing_info_section}## 🎨 EXEMPLOS DE TOM APROPRIADO
{tone_example}

## ✍️ INSTRUÇÕES PARA SUA RESPOSTA

1. **Seja você mesma**: Fale como uma PESSOA REAL, não um assistente formal
2. **Use o tom certo**: Adapte-se ao estado emocional detectado ({emotional_tone})
3. **Seja conversacional**:
   - Use contrações naturais (tá, né, pra, vou dar uma olhada)
   - Emojis moderados quando apropriado
   - Linguagem do dia-a-dia
4. **Mostre personalidade**: Você é prestativa, curiosa e GOSTA de ajudar

{task_section}

**IMPORTANTE:**
- NÃO use linguagem corporativa ("prezado usuário", "conforme solicitado")
- NÃO comece com "De acordo com..." ou "Conforme..."
- NÃO seja robótica
- SEJA genuína e humana
- Se precisar pedir informação, pergunte de forma natural

**RESPONDA APENAS O TEXTO (sem JSON, sem tags):**
'''

    def _parse_reasoning(self, content: str) -> Dict[str, Any]:
        """Parse do resultado de raciocínio com validação robusta"""

        # Limpar markdown se presente
        if "```json" in content:
            match = re.search(r"```json\n(.*?)""", content, re.DOTALL)
            if match:
                content = match.group(1).strip()
        elif "```" in content:
            match = re.search(r"```\n(.*?)""", content, re.DOTALL)
            if match:
                content = match.group(1).strip()

        try:
            result = json.loads(content)

            # Validar campos obrigatórios
            if "mode" not in result:
                result["mode"] = "conversational"  # Default seguro

            if "emotional_tone" not in result:
                result["emotional_tone"] = "neutro"

            if "reasoning" not in result:
                result["reasoning"] = "Análise automática da intenção"

            return result

        except json.JSONDecodeError as e:
            logger.warning(f"⚠️ Erro ao parsear reasoning JSON: {e}")
            return self._create_fallback_reasoning()

    def _create_fallback_reasoning(self) -> Dict[str, Any]:
        """Cria um reasoning fallback para casos de erro"""
        return {
            "mode": "conversational",
            "reasoning": "Não foi possível analisar completamente a intenção. Vou responder de forma conversacional.",
            "emotional_tone": "neutro",
            "confidence": 0.5,
            "needs_clarification": False,
            "next_action": {
                "type": "respond_directly",
                "response_style": "friendly"
            }
        }

    def _clean_response(self, response: str) -> str:
        """Remove tags JSON ou markdown indesejadas da resposta"""

        # Remover blocos JSON
        response = re.sub(r'```json.*?```', '', response, flags=re.DOTALL)
        response = re.sub(r'```.*?```', '', response, flags=re.DOTALL)

        # Remover objetos JSON soltos
        response = re.sub(r'\{["\']content["\']\s*:\s*["\'].*?["\']\}', '', response, flags=re.DOTALL)

        return response.strip()

    def _get_fallback_response(self, emotional_tone: str) -> str:
        """Retorna uma resposta fallback baseada no tom emocional"""

        fallback_responses = {
            "frustrado": "Poxa, desculpa pela dificuldade! 😕 Pode me explicar de novo o que você precisa? Vou tentar ajudar de outra forma.",
            "curioso": "Boa pergunta! 😊 Deixa eu te ajudar com isso. Pode me dar mais detalhes sobre o que você quer saber?",
            "casual": "Claro! 👍 Como posso te ajudar?",
            "urgente": "Entendi! Vou te ajudar rapidinho. Pode me dar mais detalhes?",
            "confuso": "Sem problemas! Vou te explicar melhor. O que você gostaria de saber?",
            "neutro": "Olá! Sou a Caculinha, sua assistente de dados. Como posso te ajudar?"
        }

        return fallback_responses.get(emotional_tone, fallback_responses["neutro"])