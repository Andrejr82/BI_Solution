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

        user_query = self._extract_user_message(messages[-1])
        conversation_history = self._format_conversation_history(messages)

        # 🧠 PROMPT DE RACIOCÍNIO PROFUNDO
        reasoning_prompt = self._build_reasoning_prompt(user_query, conversation_history)

        logger.info(f"🧠 Analisando intent: '{user_query[:80]}...'")

        try:
            # 🔥 CHAMADA COM TEMPERATURA ALTA para raciocínio criativo
            response = self.llm_adapter.get_completion(
                messages=[{"role": "user", "content": reasoning_prompt}],
                json_mode=True,
                temperature=0.8,  # Alta criatividade no raciocínio
                max_tokens=2000,
                cache_context={"operation": "conversational_reasoning", "stage": "intent_analysis"}
            )

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
        user_query = self._extract_user_message(messages[-1])
        emotional_tone = reasoning.get("emotional_tone", "neutro")
        needs_clarification = reasoning.get("needs_clarification", False)

        # 🎨 PROMPT CONVERSACIONAL com temperatura máxima
        conversational_prompt = self._build_conversational_prompt(
            user_query,
            emotional_tone,
            reasoning,
            self._format_conversation_history(messages[-5:])  # Últimas 5 mensagens
        )

        logger.info(f"💬 Gerando resposta conversacional (tom: {emotional_tone})")

        try:
            response = self.llm_adapter.get_completion(
                messages=[{"role": "user", "content": conversational_prompt}],
                temperature=1.0,  # 🔥 TEMPERATURA MÁXIMA = respostas mais humanas
                max_tokens=800,
                cache_context={"operation": "conversational_response", "tone": emotional_tone}
            )

            response_text = response.get("content", "")

            # Remover possíveis tags JSON se houver
            response_text = self._clean_response(response_text)

            logger.info(f"✅ Resposta conversacional gerada: {len(response_text)} chars")
            return response_text

        except Exception as e:
            logger.error(f"❌ Erro ao gerar resposta conversacional: {e}", exc_info=True)
            return self._get_fallback_response(emotional_tone)

    def _build_reasoning_prompt(self, user_query: str, conversation_history: str) -> str:
        """Constrói o prompt de raciocínio profundo"""

        return f"""# 🧠 ANÁLISE DE INTENÇÃO CONVERSACIONAL

Você é a Caculinha, uma assistente de BI conversacional. Você NÃO é um robô executor de queries.

## 📚 CONTEXTO DA CONVERSA

Histórico recente:
{conversation_history}

**Mensagem atual:** "{user_query}"

## 🤔 TAREFA: PENSAR PROFUNDAMENTE

Analise a mensagem e responda estas perguntas em seu raciocínio:

1. **Intenção Real**: O que o usuário REALMENTE quer? (além das palavras literais)
2. **Tom Emocional**: Como ele está se sentindo? (frustrado/curioso/casual/urgente/neutro/confuso)
3. **Contexto**: É continuação da conversa anterior ou novo tópico?
4. **Clareza**: Ele tem informação suficiente ou está confuso sobre algo?
5. **Tipo de Resposta**: Preciso conversar ou executar análise técnica?

## 🎯 CATEGORIZAÇÃO

**MODO CONVERSACIONAL** - Use quando:
- Saudações/agradecimentos/despedidas
- Perguntas sobre capacidades ("o que você faz?", "pode me ajudar com...")
- Feedback emocional ("não entendi", "está confuso", "muito obrigado")
- Informação INSUFICIENTE (falta UNE, produto, período, etc.)
- Tom frustrado (precisa de empatia)
- Pedidos vagos sem detalhes técnicos

**MODO ANALÍTICO** - Use quando:
- Pedido CLARO de dados/análise com todas informações
- Query técnica bem definida (ex: "MC do produto 123 na UNE SCR")
- Solicitação de gráfico/relatório com contexto completo

## 📤 RESPOSTA (JSON)

```json
{{
  "mode": "conversational" ou "analytical",
  "reasoning": "Seu raciocínio em 2-3 frases explicando POR QUE escolheu este modo",
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
- Seja genuíno e humano no raciocínio
- Se FALTAR informação (UNE, produto, etc.), escolha "conversational" e peça clarificação
- Prefira "conversational" na dúvida - melhor conversar do que errar a query
"""

    def _build_conversational_prompt(
        self,
        user_query: str,
        emotional_tone: str,
        reasoning: Dict[str, Any],
        conversation_history: str
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
            task_section = "## 🎯 RESPONDA À MENSAGEM\n\nResponda naturalmente à mensagem do usuário no tom apropriado."

        return f'''# 💬 RESPOSTA CONVERSACIONAL DA CACULINHA

Você é a Caculinha. Responda de forma COMPLETAMENTE NATURAL e HUMANA.

## 🎭 CONTEXTO EMOCIONAL
Usuário está: **{emotional_tone}**
Estilo de resposta: **{response_style}**

## 📜 CONVERSA RECENTE
{conversation_history}

## 💬 MENSAGEM ATUAL
"{user_query}"

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

    def _extract_user_message(self, message: Any) -> str:
        """Extrai conteúdo da mensagem do usuário"""
        if hasattr(message, 'content'):
            return str(message.content)
        elif isinstance(message, dict):
            return str(message.get('content', ''))
        return str(message)

    def _format_conversation_history(self, messages: List) -> str:
        """Formata histórico de conversa de forma legível"""
        if not messages or len(messages) <= 1:
            return "(Primeira mensagem da conversa)"

        history = []
        for msg in messages[:-1]:  # Todas exceto a última
            try:
                role = "Usuário" if (hasattr(msg, 'type') and msg.type == 'human') or \
                                    (hasattr(msg, 'role') and msg.role == 'user') else "Caculinha"
                content = self._extract_user_message(msg)
                # Truncar mensagens muito longas
                content_preview = content[:150] + "..." if len(content) > 150 else content
                history.append(f"{role}: {content_preview}")
            except Exception as e:
                logger.warning(f"Erro ao formatar mensagem do histórico: {e}")
                continue

        return "\n".join(history[-5:]) if history else "(Sem histórico)"  # Últimas 5

    def _parse_reasoning(self, content: str) -> Dict[str, Any]:
        """Parse do resultado de raciocínio com validação robusta"""

        # Limpar markdown se presente
        if "```json" in content:
            match = re.search(r"```json\n(.*?)```", content, re.DOTALL)
            if match:
                content = match.group(1).strip()
        elif "```" in content:
            match = re.search(r"```\n(.*?)```", content, re.DOTALL)
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
