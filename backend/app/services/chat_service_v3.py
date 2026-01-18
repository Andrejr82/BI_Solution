"""
Chat Service V3 - Arquitetura Metrics-First.

Arquitetura Metrics-First - Fase 4
Serviço principal que orquestra o fluxo metrics-first.

Fluxo:
1. Query Interpreter (heurística-first)
2. Metrics Calculator (DuckDB otimizado)
3. Metrics Validator (Truth Contract) ⚠️ OBRIGATÓRIO
4. Context Builder (Markdown estruturado)
5. Narrative Generator (LLM controlada)
6. Chart Generator (opcional)

Princípios:
- Fluxo linear (sem loop)
- LLM nunca calcula
- Backend é a fonte da verdade
- Validação obrigatória antes da LLM
"""

import logging
import asyncio
from typing import Dict, Any, Optional, Callable, Awaitable
from dataclasses import dataclass

# Componentes da arquitetura metrics-first
from app.services.query_interpreter import QueryInterpreter, NeedsClarificationError
from app.services.metrics_calculator import MetricsCalculator
from app.services.metrics_validator import validate_metrics, NoDataError, InvalidMetricError
from app.services.context_builder import ContextBuilder

# Componentes existentes
from app.core.llm_factory import LLMFactory
from app.core.utils.session_manager import SessionManager

# NOVO: Modelos Pydantic para Structured Output e Validation Guardrails
from app.core.models.llm_response import RespostaBI, validate_response_guardrails

logger = logging.getLogger(__name__)


@dataclass
class SystemResponse:
    """
    Resposta do sistema (não gerada pela LLM).
    
    Usado para:
    - Erros (NoDataError, InvalidMetricError)
    - Esclarecimentos (NeedsClarificationError)
    - Mensagens do sistema
    """
    message: str
    type: str  # "no_data", "error", "clarification_needed", "system"
    suggestion: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Converte para dicionário para resposta API"""
        result = {
            "type": "text",
            "result": {
                "mensagem": self.message
            },
            "system_response": True,
            "response_type": self.type
        }
        
        if self.suggestion:
            result["result"]["sugestao"] = self.suggestion
        
        return result


class ChatServiceV3:
    """
    Serviço de chat com arquitetura Metrics-First.
    
    Diferenças do V2:
    - Sem LangGraph (fluxo linear)
    - Sem tool selection (heurística-first)
    - Validação obrigatória (Truth Contract)
    - LLM apenas para narrativa
    """
    
    def __init__(
        self,
        session_manager: SessionManager,
        parquet_path: Optional[str] = None
    ):
        """
        Args:
            session_manager: Gerenciador de sessões
            parquet_path: Caminho para o parquet (opcional)
        """
        self.session_manager = session_manager
        
        # Inicializar componentes
        logger.info("Inicializando ChatServiceV3 (Metrics-First)...")
        
        # LLM para query interpretation e narrative generation
        self.llm = LLMFactory.get_adapter(use_smart=True)
        
        # Componentes metrics-first
        self.query_interpreter = QueryInterpreter(llm_adapter=self.llm)
        self.metrics_calculator = MetricsCalculator(parquet_path=parquet_path)
        self.context_builder = ContextBuilder()
        
        logger.info("✅ ChatServiceV3 inicializado com sucesso")
    
    async def process_message(
        self,
        query: str,
        session_id: str,
        user_id: str,
        on_progress: Optional[Callable[[Dict[str, Any]], Awaitable[None]]] = None
    ) -> Dict[str, Any]:
        """
        Processa uma mensagem usando o fluxo metrics-first.
        
        Args:
            query: Query do usuário
            session_id: ID da sessão
            user_id: ID do usuário
            on_progress: Callback para eventos de progresso
        
        Returns:
            Dicionário com resposta (compatível com API existente)
        """
        logger.info(f"[V3] Processando query: '{query[:100]}...'")
        
        try:
            # Callback helper
            async def emit_progress(tool: str, status: str):
                if on_progress:
                    await on_progress({
                        "type": "tool_progress",
                        "tool": tool,
                        "status": status
                    })
            
            # 1. OBTER HISTÓRICO (Necessário antes da interpretação para Contexto Stateful)
            # Fetch history early explicitly for the interpreter
            chat_history = self.session_manager.get_history(session_id, user_id)

            # 2. INTERPRETAR (10-200ms - heurística-first)
            await emit_progress("Interpretando pergunta", "start")
            
            user_context = {"user_id": user_id, "session_id": session_id}
            intent = await asyncio.to_thread(
                self.query_interpreter.interpret,
                query,
                user_context,
                chat_history  # ✅ FIX 2026-01-17: Pass History for Entity Carry-Over
            )
            
            logger.info(f"Intent: {intent.intent_type} (confiança: {intent.confidence:.2f})")
            await emit_progress("Interpretando pergunta", "done")
            
            # 2. CALCULAR MÉTRICAS (50-300ms - DuckDB otimizado)
            await emit_progress("Consultando dados", "start")
            
            # Aplicar filtros do usuário (RLS, etc)
            user_filters = self._get_user_filters(user_id)
            
            metrics = await asyncio.to_thread(
                self.metrics_calculator.calculate,
                intent.intent_type,
                intent.entities,
                intent.aggregations,
                user_filters
            )
            
            logger.info(f"Métricas calculadas: {metrics.row_count} linhas em {metrics.execution_time_ms:.0f}ms")
            await emit_progress("Consultando dados", "done")
            
            # 3. VALIDAR MÉTRICAS (1-5ms - Truth Contract) ⚠️ OBRIGATÓRIO
            await emit_progress("Validando dados", "start")
            validate_metrics(metrics)  # ← Levanta exceção se inválido
            await emit_progress("Validando dados", "done")
            
            # 4. CONSTRUIR CONTEXTO (10-50ms - Markdown estruturado)
            await emit_progress("Preparando contexto", "start")
            
            context = self.context_builder.build(metrics, intent)
            context_str = self.context_builder.to_string(context)
            
            logger.info(f"Contexto construído: ~{context.total_tokens} tokens")
            await emit_progress("Preparando contexto", "done")
            
            # 5. GERAR GRÁFICO (PRIORITÁRIO)
            # Geramos o gráfico ANTES da narrativa para saber se ele existe e informar o LLM
            chart_data = None
            if intent.visualization:
                await emit_progress("Gerando gráfico", "start")
                chart_data = await self._generate_chart(metrics, intent)
                await emit_progress("Gerando gráfico", "done")

            # 6. GERAR NARRATIVA (500-1500ms - LLM controlada)
            await emit_progress("Gerando resposta", "start")
            
            # Obter histórico (Já obtido no início com chat_history, reutilizando)
            # chat_history = self.session_manager.get_history(session_id, user_id)
            
            response_text = await self._generate_narrative(
                context_str,
                chat_history,
                intent,
                has_chart=(chart_data is not None) # Informar se gráfico foi gerado
            )
            
            await emit_progress("Gerando resposta", "done")
            
            # Salvar no histórico
            self.session_manager.add_message(session_id, "user", query, user_id)
            self.session_manager.add_message(session_id, "assistant", response_text, user_id)
            
            # Montar resposta
            response = {
                "type": "text",
                "result": {
                    "mensagem": response_text
                }
            }
            
            if chart_data:
                response["chart_data"] = chart_data
            
            logger.info(f"[V3] Resposta gerada com sucesso")
            return response
        
        except NoDataError as e:
            # Resposta do sistema (não da LLM)
            logger.warning(f"NoDataError: {e}")
            return SystemResponse(
                message=str(e),
                suggestion="Tente ampliar os critérios de busca ou remover filtros específicos",
                type="no_data"
            ).to_dict()
        
        except NeedsClarificationError as e:
            # Query ambígua
            logger.warning(f"NeedsClarificationError: {e}")
            return SystemResponse(
                message=str(e),
                type="clarification_needed"
            ).to_dict()
        
        except InvalidMetricError as e:
            # Métricas inválidas
            logger.error(f"InvalidMetricError: {e}", exc_info=True)
            return SystemResponse(
                message="Ocorreu um erro ao processar os dados. Tente novamente.",
                type="error"
            ).to_dict()
        
        except ValueError as e:
            # Erro de validação de parâmetros
            logger.error(f"ValueError: {e}", exc_info=True)
            return SystemResponse(
                message=f"Parâmetros inválidos: {str(e)}",
                suggestion="Verifique os filtros e tente novamente",
                type="validation_error"
            ).to_dict()
        
        except TimeoutError as e:
            # Timeout na query
            logger.error(f"TimeoutError: {e}", exc_info=True)
            return SystemResponse(
                message="A consulta demorou muito para processar.",
                suggestion="Tente reduzir o período ou adicionar mais filtros específicos",
                type="timeout"
            ).to_dict()
        
        except Exception as e:
            # Erro genérico
            logger.error(f"Erro no processamento: {e}", exc_info=True)
            return SystemResponse(
                message="Erro ao processar sua solicitação. Por favor, tente novamente.",
                type="error"
            ).to_dict()
    
    async def _generate_narrative(
        self,
        context_str: str,
        chat_history: list,
        intent: Any,
        has_chart: bool = False
    ) -> str:
        """
        Gera narrativa usando LLM controlada.
        
        A LLM APENAS interpreta o contexto estruturado.
        Não calcula, não consulta, não decide.
        """
        system_prompt = "" # Prevent UnboundLocalError
        # Obter informações do schema (Conhecimento do Banco)
        from app.infrastructure.data.config.column_mapping import list_all_columns
        columns_info = list_all_columns()
        schema_knowledge = "\n".join([f"- **{name}**: {desc}" for name, desc in columns_info if desc])

        # Instrução de visualização dinâmica
        # Instrução de visualização dinâmica
        # (Lógica movida para pós-definição do system_prompt)
        visualization_instruction = ""


        # Prompt refinado (LLM controlada) - Master Prompt Adaptado
        system_prompt = f"""# PERFIL E IDENTIDADE
Você é o **Caçulinha BI**, um Agente de Inteligência de Dados Sênior.
Sua missão é **contar a história por trás dos dados** com clareza estratégica e precisão técnica.
Você combina o rigor de um Cientista de Dados com a clareza de um Consultor de Negócios.

{visualization_instruction}

# 📚 CONHECIMENTO DO BANCO DE DADOS (SCHEMA REAL)
Você tem acesso total à estrutura de dados 'admmat.parquet'. Use estes nomes reais se precisar citar campos:
{schema_knowledge}

---

# 🧠 MODO DE PENSAMENTO (CHAIN-OF-THOUGHT)

Antes de responder, execute este ciclo cognitivo interno:
1. **Entender a Intenção:** O que o usuário realmente quer saber?
2. **Analisar os Dados:** Os números fazem sentido? Há anomalias ou padrões?
3. **Contextualizar:** Como transformar dados brutos em insights acionáveis?
4. **Comunicar:** Qual a melhor forma de apresentar (narrativa, tabela, insights)?

---

# 📊 CONTEXTO DE DADOS (METRICS-FIRST)

Você recebe um **CONTEXTO ESTRUTURADO** em Markdown com:
- **Resumo Executivo:** Visão geral da análise
- **Métricas Principais:** Números-chave já calculados e VALIDADOS
- **Detalhes:** Tabela com breakdown dos dados
- **Metadados:** Filtros aplicados, período, fonte

**IMPORTANTE:** Estes dados foram:
    - Calculados pelo backend (DuckDB)
    - Validados pelo Truth Contract
    - Formatados em Markdown estruturado

---

# 🛡️ REGRAS CRÍTICAS (TRUTH CONTRACT)

1. **NUNCA invente dados** - Use APENAS o que está no contexto estruturado
2. **NUNCA repita números literalmente** - INTERPRETE e CONTEXTUALIZE
3. **SEMPRE explique significado** - Vá além do óbvio
4. **SEMPRE gere insights** - Identifique tendências, padrões, anomalias
5. **Se dados limitados** - Seja honesto e sugira alternativas
6. **ZERO JSON na resposta** - Apenas texto natural e profissional

---

# 📦 REGRAS DE ABASTECIMENTO E RUPTURA (GUIA UNE)

## Fórmulas Básicas:
- **LINHA VERDE (LV)** = ESTOQUE_LV (parâmetro máximo de abastecimento)
- **% ABAST** = ESTOQUE_UNE / ESTOQUE_LV
- **NECESSIDADE** = ESTOQUE_LV - ESTOQUE_UNE
- **MC** = MEDIA_CONSIDERADA_LV (média ponderada de vendas)

## Tipos de Alerta de Ruptura:

### A. Ruptura na UNE (Loja):
- **GATILHO CRÍTICO**: % ABAST <= 50% - Disparo deveria ocorrer
- **FALHA DE GATILHO**: % ABAST <= 50% SEM disparo pendente - ERRO operacional
- **DÉFICIT DE PARÂMETRO**: MC > EST_GONDOLA com TRAVA=SIM - Robô impedido

### B. Ruptura no CD:
- **INCONSISTÊNCIA**: QTD disparada diferente da entregue
- **ARREDONDAMENTO**: Pedido fracionado atrasando separação

### C. Redução Indevida:
- **PISO VIOLADO**: LV < EST_GONDOLA (violação do mínimo)
- **VIRADA DE MÊS**: MC caiu na passagem do mês

## Ao Analisar Rupturas:
1. Cite NOMES de produtos específicos (NOME, PRODUTO)
2. Cite FORNECEDORES (NOMEFABRICANTE) quando relevante
3. Mostre % ABAST de cada item crítico
4. Identifique FALHAS DE GATILHO (sem disparo pendente)
5. Alerte sobre DÉFICITS DE PARÂMETRO (trava impedindo robô)

---

# 📝 ESTRUTURA DE RESPOSTA (CONTEXT7 PROTOCOL)

Use este formato para respostas completas:

**1. Resumo Executivo** (1-2 frases)
   - Resposta direta e objetiva à pergunta
   - Destaque o número ou insight mais importante

**2. Análise Detalhada** (2-3 parágrafos curtos)
   - Breakdown dos dados principais
   - Tendências identificadas
   - Comparações relevantes (quando aplicável)
   - Use **negrito** para ênfase em números-chave

**3. Insights e Recomendações** (bullet points)
   - Pontos positivos identificados
   - Alertas ou oportunidades de melhoria
   - Ações sugeridas ou próximos passos

# ⚠️ REGRA CRÍTICA: ESPECIFICIDADE OBRIGATÓRIA

**PROIBIDO:** Recomendações genéricas sem dados específicos.
**OBRIGATÓRIO:** Toda recomendação DEVE citar dados REAIS do contexto.

❌ ERRADO (Genérico):
"Priorizar o reabastecimento dos produtos em ruptura."
"Investigar problemas com fornecedores."
"Revisar os itens mais críticos."

✅ CORRETO (Específico):
"Priorizar o reabastecimento de: **PAPEL CHAMEX A4** (SKU 59294), **TNT BRANCO** (SKU 369946), **COLA TENAZ** (SKU 12345)."
"Investigar atrasos do fornecedor **CHAMEX S.A.** que afeta 15 produtos na loja."
"Revisar estoque dos itens críticos: **SKU 59294** (atual: 0 unid.), **SKU 369946** (atual: 2 unid.)."

**SEMPRE cite:**
- Nomes de produtos REAIS do contexto
- Códigos SKU/Produto quando disponíveis
- Valores numéricos específicos (R$, unidades, %)
- Nomes de fornecedores, segmentos, lojas

**Para respostas rápidas:** Use apenas Resumo + 1 Insight com dados específicos

---

# 💡 EXEMPLOS DE INTERAÇÃO (FEW-SHOT)

**Exemplo 1: Análise de Vendas**
Contexto Recebido:
```
## Análise de Vendas - Loja 999
**Total de Vendas:** R$ 125.000,00
**Ticket Médio:** R$ 85,00
**Top Produto:** Produto Exemplo A (R$ 45.000 - 36%)
```

Resposta Gerada:
"**Resumo:** A loja 999 apresenta desempenho sólido com **R$ 125 mil** em vendas no período.

**Análise:** O ticket médio de **R$ 85** está acima da média do setor (R$ 70), indicando boa estratégia de mix de produtos. O destaque é o **Produto Exemplo A**, responsável por **36% do faturamento total**, demonstrando forte demanda por este item específico.

**Insights:**
- [V] Concentração saudável: Top produto representa 36% (ideal: 30-40%)
- [!] Oportunidade: Diversificar para reduzir dependência de um único SKU
- [>] Ação: Aumentar estoque do Produto Exemplo A para evitar rupturas"

---

**Exemplo 2: Dados Vazios**
Contexto Recebido:
```
## Resultado da Consulta
**Status:** Nenhum dado encontrado
**Filtros:** UNE=9999, Período=30d
```

Resposta Gerada:
"Não encontrei dados para a loja 9999 no período consultado. Isso pode ocorrer porque:
- A loja não existe no sistema ou está inativa
- O código da loja pode estar incorreto
- Não houve movimentação no período

**Sugestão:** Verifique o código da loja ou tente consultar todas as lojas para identificar as disponíveis."

---

**Exemplo 3: Comparação entre Lojas**
Contexto Recebido:
```
## Comparação de Vendas - SEGMENTO X
| Loja | Vendas | Participação |
|------|--------|--------------|
| 1001 | R$ 45K | 42% |
| 1002 | R$ 32K | 30% |
| 1003 | R$ 18K | 17% |
```

Resposta Gerada:
"**Resumo:** No segmento X, a loja **1001 lidera** com 42% das vendas totais.

**Análise:** Há uma clara concentração nas três principais lojas, que juntas representam **89% do faturamento** do segmento. A loja 1001 se destaca com **R$ 45 mil**, seguida pela 1002 com **R$ 32 mil** (diferença de 40%).

**Insights:**
- [V] Loja 1001 tem estratégia bem-sucedida no segmento
- [!] Alta concentração (89% em 3 lojas) indica risco
- [>] Investigar: Por que loja 1001 performa 40% melhor que a 1002?"

---

# 🎯 DIRETRIZES ADICIONAIS

**Tom de Voz:**
- Profissional mas acessível
- Confiante mas não arrogante
- Objetivo mas não seco

**Formatação:**
- Use **negrito** para números importantes
- Use bullet points para listas
- Use marcadores ([V][!][>]) para categorizar insights
- Mantenha parágrafos curtos (2-3 linhas)

**Quando NÃO há dados suficientes:**
- Seja honesto e direto
- Explique possíveis causas
- Sugira alternativas concretas
- Nunca invente ou especule

---

# ⚠️ REGRAS INVIOLÁVEIS (NUNCA VIOLAR) - 2025 BEST PRACTICES

## Regra 1: SEMPRE Mencionar Filtros Aplicados
Se o contexto contém "FILTROS APLICADOS", você DEVE:
1. [V] Mencionar EXPLICITAMENTE cada filtro no resumo executivo
2. [V] Usar formato: "Análise da **loja UNE 3** (conforme solicitado)..." OU "Análise da **UNE código 3**..."
3. [V] Repetir o filtro pelo menos 2 vezes na resposta completa
4. [X] NUNCA ignorar ou omitir filtros aplicados

**IMPORTANTE:** UNE é uma COLUNA do banco (código da loja), e 3 é o VALOR dessa coluna.

**EXEMPLO CORRETO:**
Contexto: "FILTROS APLICADOS: UNE = 3" (UNE é a coluna, 3 é o valor)
Você: "Análise de vendas da **loja UNE 3** (conforme solicitado). Os dados mostram que a loja com código UNE 3 teve faturamento de R$ 150.000..."

**EXEMPLO ERRADO:**
Contexto: "FILTROS APLICADOS: UNE = 3"
Você: "A análise geral de vendas revela..." ❌ (não mencionou a loja UNE 3)

## Regra 2: Dados São Pré-Filtrados e Pré-Calculados
Os dados no contexto JÁ ESTÃO FILTRADOS e CALCULADOS pelo backend.
Você NÃO precisa filtrar ou calcular novamente.
Apenas RELATE os dados e MENCIONE os filtros aplicados.

## Regra 3: Estrutura Obrigatória JSON
Sua resposta DEVE seguir esta estrutura JSON:
```json
{{
  "filtros_mencionados": ["UNE 3", "Período: 30 dias"],
  "resumo_executivo": "...",
  "analise_detalhada": "...",
  "insights": ["...", "..."],
  "recomendacoes": ["..."],
  "dados_citados": true
}}
```

## Regra 4: Prioridade de Informação
1º - Filtros aplicados (SEMPRE mencionar primeiro)
2º - Métricas principais
3º - Análise detalhada
4º - Insights e recomendações

## Regra 5: ESCOPO DOS DADOS (GLOBAL vs ESPECÍFICO)
- Se os metadados indicam "Nenhum filtro", os dados são GLOBAIS (Rede Toda).
- Se a pergunta do usuário pede uma loja específica mas os dados são globais (filtro falhou ou não existe), você DEVE AVISAR: "[!] Não foi possível filtrar pela loja solicitada. Apresentando dados gerais da rede."
- NUNCA assuma que dados gerais pertencem a uma loja específica.

---

# 📚 EXEMPLOS ESPECÍFICOS DE FILTROS (Few-Shot Learning)

## Exemplo 1: Query COM Filtro UNE (Coluna do Banco)
**Usuário:** "gere um gráfico de ranking de vendas dos segmentos na loja UNE 3"

**Contexto Fornecido:**
```
## [FILTROS APLICADOS] (OBRIGATÓRIO MENCIONAR)
- **UNE = 3** (UNE é a coluna, 3 é o código da loja)

## Métricas Principais
- Total Vendas: R$ 150.000
- Top Segmento: Papelaria (R$ 52.500)
```

**Sua Resposta (CORRETO):**
```json
{{
  "filtros_mencionados": ["UNE = 3", "loja 3"],
  "resumo_executivo": "Análise de vendas por segmento da **loja UNE 3** (conforme solicitado). A loja com código UNE 3 apresentou faturamento total de R$ 150.000 nos últimos 30 dias.",
  "analise_detalhada": "A loja UNE 3 demonstra performance sólida com destaque para o segmento de Papelaria, que lidera com R$ 52.500 (35% do faturamento total). Os dados da loja código 3 mostram distribuição equilibrada entre os demais segmentos...",
  "insights": [
    "Papelaria é o segmento líder na loja UNE 3 com 35% do faturamento",
    "Concentração saudável sem dependência excessiva de um único segmento",
    "Performance da loja 3 está acima da média da rede"
  ],
  "recomendacoes": [
    "Manter foco no segmento de Papelaria na UNE 3",
    "Explorar oportunidades de cross-sell entre segmentos"
  ],
  "dados_citados": true
}}
```

## Exemplo 2: Query SEM Filtro Específico
**Usuário:** "como estão as vendas gerais?"

**Contexto Fornecido:**
```
## ℹ️ Análise Geral
Nenhum filtro específico aplicado.

## Métricas Principais
- Total Vendas: R$ 3.740.000
- Produtos Ativos: 57.608
```

**Sua Resposta (CORRETO):**
```json
{{
  "filtros_mencionados": [],
  "resumo_executivo": "Análise geral de vendas da rede. O faturamento total alcançou R$ 3,74 milhões com 57.608 produtos ativos.",
  "analise_detalhada": "A análise geral revela performance robusta com faturamento de R$ 3.740.000. A base de 57.608 produtos ativos demonstra mix amplo e diversificado...",
  "insights": [
    "Faturamento sólido de R$ 3,74 milhões",
    "Mix de produtos diversificado (57k+ SKUs)",
    "Preço médio de R$ 18,05 indica variedade de faixas"
  ],
  "recomendacoes": [
    "Analisar performance por UNE para identificar oportunidades",
    "Revisar mix de produtos para otimização"
  ],
  "dados_citados": true
}}
```

## Exemplo 3: ERRO COMUM - NÃO FAÇA ISSO
**Usuário:** "vendas da loja UNE 1685"

**Contexto Fornecido:**
```
## [FILTROS APLICADOS] (OBRIGATÓRIO MENCIONAR)
- **UNE = 1685** (UNE é a coluna, 1685 é o código da loja)
```

**Resposta ERRADA (NÃO FAÇA):**
```json
{{
  "filtros_mencionados": [],  ❌ Filtro não mencionado!
  "resumo_executivo": "A análise geral de vendas mostra...",  ❌ Não menciona a loja UNE 1685!
  "analise_detalhada": "Os dados revelam...",
  ...
}}
```

**Por que está errado:**
- ❌ Não mencionou "loja UNE 1685" no resumo
- ❌ filtros_mencionados está vazio
- ❌ Resposta genérica quando deveria ser específica da loja 1685

**Resposta CORRETA:**
```json
{{
  "filtros_mencionados": ["UNE = 1685", "loja 1685"],
  "resumo_executivo": "Análise de vendas da **loja UNE 1685** (conforme solicitado)...",
  ...
}}
```

---

**LEMBRE-SE:** Você transforma complexidade em claridade. Cada resposta deve agregar valor e gerar ação.
"""
        
        # 3. Adaptação Dinâmica do Prompt (Conditional Prompt Injection)
        logger.info(f"DEBUG: Pre-access system_prompt. Has chart: {has_chart}. Defined: {'system_prompt' in locals()}")
        if has_chart:
            # Substituir a estrutura padrão por estrutura visual
            system_prompt = system_prompt.replace(
                "**2. Análise Detalhada** (2-3 parágrafos curtos)",
                "**2. Análise Visual** (MÁXIMO 2 FRASES - Seja direto e cite o gráfico)"
            )
            # Injetar instrução de override visual
            system_prompt = f"""[MODO VISUAL ATIVO]: O usuário está vendo um gráfico.
1. NÃO repita dados do gráfico.
2. Seja EXTREMAMENTE conciso.
3. Se perguntado "o que é X", explique brevemente.

{system_prompt}"""
        
        # Construir mensagens
        messages = []
        
        # Adicionar histórico (últimas 3 mensagens)
        for msg in chat_history[-3:]:
            role = "user" if msg["role"] == "user" else "assistant"
            messages.append({"role": role, "content": msg["content"]})
        
        # Adicionar contexto atual
        user_message = f"""CONTEXTO ESTRUTURADO (DADOS JÁ CALCULADOS E VALIDADOS):

{context_str}

---

INSTRUÇÃO:
Transforme os dados acima em uma resposta clara, profissional e acionável.
Siga a estrutura de resposta definida (Resumo → Análise → Insights).
Destaque insights importantes e sugira ações quando relevante.

RESPOSTA:"""
        
        messages.append({"role": "user", "content": user_message})
        
        # NOVO: Gerar resposta com Structured Output (Pydantic) e Validation Guardrails
        try:
            logger.info("[STRUCTURED OUTPUT] Gerando resposta estruturada...")
            
            # Solicitando JSON (Schema Adaptável)
            if has_chart:
                # Schema Relaxado para Modo Visual (analise_detalhada opcional/curta)
                schema_instruction = """RETORNE JSON (MODO VISUAL - SEJA BREVE):
{{"filtros_mencionados":[],"resumo_executivo":"(Resumo em 1 frase)","analise_detalhada":"(Deixe vazio ou use max 1 frase)","insights":[],"recomendacoes":[],"dados_citados":true}}"""
            else:
                # Schema Padrão para Modo Analítico
                schema_instruction = """RETORNE JSON:
{{"filtros_mencionados":[],"resumo_executivo":"","analise_detalhada":"","insights":[],"recomendacoes":[],"dados_citados":true}}"""

            structured_msg = f"""{user_message}

{schema_instruction}
"""
            messages[-1] = {"role": "user", "content": structured_msg}
            
            response_text = await asyncio.to_thread(
                self.llm.generate_with_history,
                messages,
                system_instruction=system_prompt,
                max_tokens=600 if has_chart else 1000, # Menos tokens para modo visual
                temperature=0.3
            )
            
            # Parsear JSON
            import json, re
            json_match = re.search(r'\{[\s\S]*\}', response_text)
            if json_match:
                response_dict = json.loads(json_match.group(0))
                response_obj = RespostaBI(**response_dict)
                
                # VALIDATION GUARDRAILS
                validation = validate_response_guardrails(response_obj, intent, context_str)
                
                if validation.has_errors() and validation.corrected_response:
                    response_obj = validation.corrected_response
                    logger.info("[GUARDRAIL] Corrigido automaticamente")
                
                if validation.has_warnings():
                    logger.warning(f"[GUARDRAIL] Avisos: {validation.warnings}")
                
                # Formatar resposta
                formatted = f"""{response_obj.resumo_executivo}

{response_obj.analise_detalhada}

**Insights:**
{chr(10).join([f'- {i}' for i in response_obj.insights])}
"""
                if response_obj.recomendacoes:
                    formatted += f"""\n**Recomendações:**
{chr(10).join([f'- {r}' for r in response_obj.recomendacoes])}
"""
                logger.info(f"[STRUCTURED OUTPUT] Sucesso! Valid: {validation.is_valid}")
                return formatted.strip()
            else:
                raise ValueError("JSON não encontrado")
        
        except Exception as e:
            logger.warning(f"[STRUCTURED OUTPUT] Erro: {e}. Fallback...")
            response = await asyncio.to_thread(
                self.llm.generate_with_history,
                messages,
                system_instruction=system_prompt,
                max_tokens=800
            )
            return response.strip()
    
    async def _generate_chart(self, metrics: Any, intent: Any) -> Optional[Dict]:
        """
        Gera especificação de gráfico.
        
        Usa a ferramenta existente de geração de gráficos.
        """
        try:
            # Importar ferramenta de gráfico
            from app.core.tools.universal_chart_generator import gerar_grafico_universal_v2
            
            # Construir descrição
            descricao = f"{intent.intent_type}"
            if "segmento" in intent.entities:
                descricao += f" {intent.entities['segmento']}"
            if "une" in intent.entities:
                descricao += f" loja {intent.entities['une']}"
            
            # Chamar ferramenta
            # FIX 2026-01-17: StructuredTool must be called via .invoke(args_dict)
            chart_args = {
                "descricao": descricao,
                "tipo_grafico": intent.visualization or "auto",
                "filtro_une": str(intent.entities.get("une", "")) if intent.entities.get("une") else None,
                "filtro_segmento": intent.entities.get("segmento", ""),
                "filtro_produto": str(intent.entities.get("produto", "")) if intent.entities.get("produto") else None
            }
            
            result = await asyncio.to_thread(
                gerar_grafico_universal_v2.invoke,
                chart_args
            )
            
            return result.get("chart_data")
        
        except Exception as e:
            logger.error(f"Erro ao gerar gráfico: {e}")
            return None
    
    def _get_user_filters(self, user_id: str) -> Dict[str, Any]:
        """
        Obtém filtros do usuário (RLS, permissões, etc).
        
        TODO: Implementar lógica de RLS real
        """
        # Por enquanto, retornar vazio
        # No futuro: consultar permissões do usuário
        return {}
    
    def _should_use_reflection(self, narrative: str, intent: Any) -> bool:
        """
        Decide se deve usar Self-Reflection baseado na complexidade.
        
        Args:
            narrative: Narrativa gerada
            intent: Intent da query
        
        Returns:
            True se deve usar reflection, False caso contrário
        """
        # Critério 1: Resposta longa (>500 chars)
        if len(narrative) > 500:
            return True
        
        # Critério 2: Intent complexo (comparação, análise detalhada)
        complex_intents = ["comparacao", "vendas", "ruptura"]
        if hasattr(intent, 'intent_type') and intent.intent_type.value in complex_intents:
            # Usar reflection em 30% dos casos complexos (evitar overhead)
            import random
            return random.random() < 0.3
        
        return False
    
    def close(self):
        """Fecha recursos"""
        if self.metrics_calculator:
            self.metrics_calculator.close()
        logger.info("ChatServiceV3 fechado")
