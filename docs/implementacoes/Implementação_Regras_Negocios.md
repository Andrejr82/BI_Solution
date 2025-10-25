📊 ANÁLISE DE IMPACTO E PLANO DE IMPLEMENTAÇÃO

  🎯 RESUMO EXECUTIVO

  O documento define as regras de negócio operacionais de UNE (Unidades de Negócio) para um sistema de varejo
  atacadista. São regras CRÍTICAS para abastecimento, precificação e gestão de estoque que PRECISAM ser
  implementadas no Agent_Solution_BI.

  ---
  📋 MAPEAMENTO DAS REGRAS DE NEGÓCIO

  1. ABASTECIMENTO DE PRODUTOS (CRÍTICO)

  1.1 Média Comum (MC)

  - Fórmula: MC = (Média 12 meses + Média 3 meses + Média ano anterior vigente) / 3
  - Uso: Parâmetro base para cálculo de abastecimento
  - Impacto: ❌ NÃO IMPLEMENTADO - Sistema atual não calcula MC

  1.2 Linha Verde (LV)

  - Fórmula: LINHA_VERDE = ESTOQUE + ESTOQUE_GONDOLA + ESTOQUE_ILHA
  - Regras:
    - Se MC > ESTOQUE_GONDOLA e TRAVA = NÃO → Robô aumenta ESTOQUE
    - Se MC < ESTOQUE_GONDOLA → Robô NÃO reduz (só OPCOM pode)
    - Se MC > ESTOQUE_GONDOLA na virada de mês → Robô pode reduzir ESTOQUE
  - Impacto: ✅ PARCIALMENTE - Campos existem mas lógica não está implementada

  1.3 Disparo de Solicitação

  - Regra: ESTOQUE_UNE <= 50% LINHA_VERDE
  - Volume: QTD_DISPARADA = LINHA_VERDE - ESTOQUE_UNE
  - Impacto: ❌ NÃO IMPLEMENTADO

  1.4 Arredondamento de Embalagens

  - Regra Master: Arredondar para múltiplo de QTDE_EMB_MASTER se < 50% do Master
  - Regra Múltiplo: Para grupos específicos (Flores, Lãs, Bordados...) usar apenas QTDE_EMB_MULTIPLO
  - Grupos especiais: 25 grupos identificados (IDs: 1, 47, 63, 117, 194, 228, 324...)
  - Impacto: ❌ NÃO IMPLEMENTADO

  ---
  2. CICLO DE VIDA DOS PRODUTOS

  2.1 Perfis de Produto

  - Direcionador: Produtos de necessidade primária (ex: Papel, Tecidos)
  - Complementar: Produtos que complementam direcionadores (ex: Tesouras, Botões)
  - Impulso: Produtos não necessários, venda por desejo (ex: Chocolates, Brinquedos)
  - Impacto: ❌ NÃO IMPLEMENTADO - Coluna PERFIL_PRODUTO não existe

  2.2 Status de Produto

  - FORALINHA: Produto descontinuado, precisa girar estoque
  - PROMOCIONAL: Produto em promoção
  - Impacto: ✅ EXISTENTE - Colunas já estão no schema

  ---
  3. POLÍTICA DE FORMAÇÃO DE PREÇOS

  3.1 Ranking de Produto (0-4)

  - RANK 0: Dois preços (38% atacado, 30% varejo)
  - RANK 1: Preço único (38%)
  - RANK 2: Dois preços (38% atacado, 30% varejo)
  - RANK 3: Sem desconto (preço tabela - Livros, Revistas)
  - RANK 4: Dois preços (38% atacado, 24% varejo)
  - Impacto: ❌ NÃO IMPLEMENTADO - Coluna RANKING não existe

  3.2 Limites de Atacado

  - Regra: Compra ≥ R$ 750,00 = Preço Atacado
  - Regra: Compra < R$ 750,00 = Preço Varejo (baseado em RANKING)
  - Impacto: ❌ NÃO IMPLEMENTADO

  3.3 Política de Pagamento

  - Descontos progressivos por forma de pagamento:
    - À vista: 38%
    - Cartão 30D: 36%
    - Cartão 90D: 34%
    - Cartão 120D: 30%
  - Impacto: ❌ NÃO IMPLEMENTADO

  ---
  4. POLÍTICA DE DEVOLUÇÕES E TRANSFERÊNCIAS

  4.1 Condições de Devolução

  - Apenas produtos com embalagem original
  - Processo: Líder Estoque → CD Caxias → Protocolo Coleta
  - Impacto: ❌ NÃO IMPLEMENTADO - Precisa workflow

  4.2 Transferências entre UNEs

  - Produtos sem embalagem → Transferir para outra UNE
  - OPCOM coordena transferências
  - Impacto: ❌ NÃO IMPLEMENTADO

  ---
  🔴 ANÁLISE DE IMPACTO NO SISTEMA ATUAL

  Schema de Dados

  | Campo Necessário   | Status Atual | Ação Requerida           |
  |--------------------|--------------|--------------------------|
  | MC (Média Comum)   | ❌ NÃO EXISTE | ✅ CRIAR + Calcular       |
  | RANKING            | ❌ NÃO EXISTE | ✅ CRIAR                  |
  | PERFIL_PRODUTO     | ❌ NÃO EXISTE | ✅ CRIAR                  |
  | TRAVA_MC           | ❌ NÃO EXISTE | ✅ CRIAR                  |
  | GRUPO_ID           | ❌ NÃO EXISTE | ✅ CRIAR (para multiplos) |
  | PRECO_VAREJO       | ❌ NÃO EXISTE | ✅ CALCULAR               |
  | PRECO_ATACADO      | ❌ NÃO EXISTE | ✅ CALCULAR               |
  | ESTOQUE_LV         | ✅ EXISTE     | ✅ OK                     |
  | ESTOQUE_GONDOLA_LV | ✅ EXISTE     | ✅ OK                     |
  | ESTOQUE_ILHA_LV    | ✅ EXISTE     | ✅ OK                     |
  | QTDE_EMB_MASTER    | ✅ EXISTE     | ✅ OK                     |
  | QTDE_EMB_MULTIPLO  | ✅ EXISTE     | ✅ OK                     |

  ---

● 📅 PLANO DE IMPLEMENTAÇÃO

  FASE 1: FUNDAÇÃO DE DADOS (1-2 semanas)

  Sprint 1.1: Extensão do Schema

  ALTER TABLE produtos ADD COLUMN:
  - mc FLOAT  -- Média Comum calculada
  - ranking INT  -- 0-4 (política de preços)
  - perfil_produto VARCHAR(20)  -- DIRECIONADOR/COMPLEMENTAR/IMPULSO
  - trava_mc BOOLEAN  -- Se TRUE, MC não altera ESTOQUE
  - grupo_id INT  -- ID do grupo (para arredondamento múltiplos)
  - preco_varejo FLOAT  -- Preço calculado para varejo
  - preco_atacado FLOAT  -- Preço calculado para atacado
  - ultima_recalculo_mc TIMESTAMP

  Sprint 1.2: Script de Cálculo de MC

  # core/business_rules/mc_calculator.py
  def calcular_mc(produto_id, une_id):
      """
      MC = (média_12_meses + média_3_meses + média_ano_anterior_vigente) / 3
      """
      vendas_12m = get_vendas_ultimos_12_meses(produto_id, une_id)
      vendas_3m = get_vendas_ultimos_3_meses(produto_id, une_id)
      vendas_ano_anterior = get_vendas_mes_ano_anterior(produto_id, une_id)

      mc = (mean(vendas_12m) + mean(vendas_3m) + vendas_ano_anterior) / 3
      return mc

  Sprint 1.3: Script de Política de Preços

  # core/business_rules/pricing_policy.py
  def calcular_precos(produto):
      """Calcula preço varejo e atacado baseado em RANKING"""
      preco_base = produto.LIQUIDO_38
      ranking = produto.ranking

      if ranking == 0:
          return {
              'varejo': preco_base * 1.30,  # 30% margem
              'atacado': preco_base  # 38% já embutido
          }
      elif ranking == 1:
          return {
              'varejo': preco_base,
              'atacado': preco_base
          }
      # ... demais rankings

  ---
  FASE 2: REGRAS DE ABASTECIMENTO (2-3 semanas)

  Sprint 2.1: Agente de Linha Verde

  # core/agents/linha_verde_agent.py
  class LinhaVerdeAgent:
      """Gerencia lógica da Linha Verde e disparo de abastecimento"""

      def calcular_linha_verde(self, produto):
          return (produto.ESTOQUE +
                  produto.ESTOQUE_GONDOLA_LV +
                  produto.ESTOQUE_ILHA_LV)

      def verificar_disparo(self, produto):
          """Regra: ESTOQUE_UNE <= 50% LINHA_VERDE"""
          lv = self.calcular_linha_verde(produto)
          return produto.ESTOQUE_UNE <= (lv * 0.5)

      def calcular_quantidade_disparo(self, produto):
          """QTD = LINHA_VERDE - ESTOQUE_UNE"""
          lv = self.calcular_linha_verde(produto)
          return lv - produto.ESTOQUE_UNE

      def aplicar_arredondamento(self, qtd, produto):
          """Arredonda para Master ou Múltiplo"""
          if produto.grupo_id in GRUPOS_MULTIPLO_OBRIGATORIO:
              return ceil(qtd / produto.QTDE_EMB_MULTIPLO) * produto.QTDE_EMB_MULTIPLO
          else:
              return self._arredondar_master(qtd, produto)

  Sprint 2.2: Robô de MC

  # core/jobs/mc_robot.py
  class MCRobot:
      """Robô que atualiza ESTOQUE baseado em MC na virada de mês"""

      def atualizar_estoque_por_mc(self, produto):
          if produto.trava_mc:
              return  # Não mexe se travado

          if produto.mc > produto.ESTOQUE_GONDOLA_LV:
              # MC maior → aumenta ESTOQUE
              delta = produto.mc - produto.ESTOQUE_GONDOLA_LV
              produto.ESTOQUE += delta
          elif produto.mc < produto.ESTOQUE_GONDOLA_LV:
              # MC menor → só reduz na virada de mês
              if is_virada_de_mes():
                  delta = produto.ESTOQUE_GONDOLA_LV - produto.mc
                  produto.ESTOQUE = max(0, produto.ESTOQUE - delta)

  ---
  FASE 3: FERRAMENTAS BI (2 semanas)

  Sprint 3.1: Tool de Abastecimento

  @tool
  def calcular_abastecimento(une_id: int, segmento: str = None) -> Dict:
      """
      Calcula produtos que precisam de abastecimento para uma UNE.

      Retorna produtos com:
      - ESTOQUE_UNE <= 50% LINHA_VERDE
      - Quantidade necessária
      - Quantidade arredondada (Master/Múltiplo)
      """
      pass

  @tool
  def simular_mudanca_linha_verde(produto_id: int, une_id: int, novo_estoque_gondola: int) -> Dict:
      """
      Simula impacto de alterar ESTOQUE_GONDOLA_LV.

      Retorna:
      - Nova LINHA_VERDE
      - Impacto no abastecimento
      - Custo estimado
      """
      pass

  Sprint 3.2: Tool de Política de Preços

  @tool
  def calcular_preco_final(produto_id: int, valor_compra: float, forma_pagamento: str) -> Dict:
      """
      Calcula preço final baseado em:
      - RANKING do produto
      - Valor da compra (< ou >= R$ 750)
      - Forma de pagamento

      Retorna:
      - Preço base
      - Desconto aplicado
      - Preço final
      """
      pass

  @tool
  def produtos_fora_linha(une_id: int) -> List[Dict]:
      """Lista produtos FORALINHA que precisam girar estoque"""
      pass

  ---
  FASE 4: AGENTE ESPECIALIZADO (1 semana)

  Sprint 4.1: Agente de Operações UNE

  # core/agents/une_operations_agent.py
  class UNEOperationsAgent:
      """
      Agente especializado em operações de UNE conforme guia.

      Ferramentas:
      - calcular_abastecimento
      - simular_mudanca_linha_verde
      - calcular_preco_final
      - produtos_fora_linha
      - solicitar_coleta
      - solicitar_transferencia
      """

      def __init__(self, llm_adapter, db_adapter):
          self.tools = [
              calcular_abastecimento,
              simular_mudanca_linha_verde,
              calcular_preco_final,
              produtos_fora_linha,
          ]

      def process_query(self, query: str, une_id: int):
          """
          Processa queries como:
          - "Quais produtos precisam de abastecimento na UNE 5?"
          - "Simule aumentar linha verde do produto 369947 para 100"
          - "Qual o preço final de R$ 500 em papelaria pagando em 30 dias?"
          - "Liste produtos fora de linha com estoque > 50"
          """
          pass

  ---
  FASE 5: INTERFACE E RELATÓRIOS (1 semana)

  Sprint 5.1: Dashboard Operacional

  - Relatório de Abastecimento: Produtos que atingiram 50% LV
  - Relatório de MC: Comparação MC x ESTOQUE_GONDOLA
  - Relatório Fora de Linha: Produtos para liquidação
  - Simulador de Preços: Calcular preços conforme política

  ---
  🎯 PRIORIZAÇÃO

  CRÍTICO (Implementar IMEDIATAMENTE)

  1. ✅ Cálculo de MC
  2. ✅ Lógica de Linha Verde
  3. ✅ Disparo de Abastecimento
  4. ✅ Arredondamento de Embalagens

  IMPORTANTE (Implementar em 30 dias)

  5. ✅ Política de Preços (Ranking)
  6. ✅ Perfil de Produto
  7. ✅ Robô de MC (virada de mês)

  DESEJÁVEL (Implementar em 60 dias)

  8. ✅ Workflow de Devoluções
  9. ✅ Workflow de Transferências
  10. ✅ Dashboard Operacional

  ---
  📊 ESTIMATIVAS

  | Fase                   | Duração     | Complexidade | Risco    |
  |------------------------|-------------|--------------|----------|
  | Fase 1: Fundação       | 1-2 semanas | ⚠️ Média     | 🟡 Médio |
  | Fase 2: Abastecimento  | 2-3 semanas | 🔴 Alta      | 🔴 Alto  |
  | Fase 3: Ferramentas BI | 2 semanas   | ⚠️ Média     | 🟡 Médio |
  | Fase 4: Agente UNE     | 1 semana    | 🟢 Baixa     | 🟢 Baixo |
  | Fase 5: Interface      | 1 semana    | 🟢 Baixa     | 🟢 Baixo |
  | TOTAL                  | 7-9 semanas | -            | -        |

  ---

● ⚠️ RISCOS E CONSIDERAÇÕES

  Riscos Técnicos

  1. Cálculo de MC: Depende de histórico de 12 meses → Precisa dados completos
  2. Robô de MC: Execução automática na virada de mês → Precisa job scheduler
  3. Arredondamento Múltiplos: Lista de 25 grupos → Precisa mapeamento correto
  4. Performance: Cálculo de MC para 1M+ produtos → Precisa otimização

  Riscos de Negócio

  1. Mudança de Processo: Lideranças precisam adaptar workflow
  2. Treinamento: OPCOM precisa entender novas ferramentas
  3. Validação: Regras precisam ser testadas com dados reais
  4. Governança: Quem pode alterar TRAVA_MC, ESTOQUE_GONDOLA?

  Dependências

  - ✅ Dados históricos de vendas (12 meses)
  - ✅ Cadastro completo de grupos de produtos
  - ❌ Job scheduler para robô de MC (precisa implementar)
  - ❌ Sistema de notificações para alertas de abastecimento

  ---
  🚀 PRÓXIMOS PASSOS RECOMENDADOS

  Opção 1: Quick Win (2 semanas)

  Implementar apenas:
  - Cálculo de MC
  - Tool de calcular_abastecimento
  - Relatório de produtos que precisam abastecimento

  ROI: Alto impacto com baixo esforço

  Opção 2: MVP Completo (4 semanas)

  Implementar:
  - Fase 1 (Schema)
  - Fase 2 (Abastecimento)
  - Fase 3.1 (Tools básicas)

  ROI: Sistema funcional com regras core

  Opção 3: Implementação Full (9 semanas)

  Implementar todas as 5 fases conforme plano

  ROI: Sistema completo conforme guia operacional

  ---
  📌 RECOMENDAÇÃO FINAL

  Sugestão: Começar com Opção 1 (Quick Win) para validar regras com stakeholders, depois evoluir para MVP.

  Razão: As regras são complexas e críticas para operação. É melhor validar incrementalmente do que implementar tudo e descobrir ajustes necessários
  depois.

  Você gostaria que eu:
  1. ✅ Comece a implementar a Opção 1 (Quick Win)?
  2. ✅ Crie um documento técnico detalhado para alguma fase específica?
  3. ✅ Faça um protótipo de alguma funcionalidade específica?
  4. ✅ Prepare um script de migração do schema?


  ● 🎭 MATRIZ DE RESPONSABILIDADES DOS AGENTES

  📊 AGENTES EXISTENTES NO SISTEMA

  1. CaculinhaBI Agent (caculinha_bi_agent.py)

  Papel Atual:
  - Agente principal de BI
  - Recebe queries em linguagem natural
  - Decide qual ferramenta usar (query_product_data, list_table_columns, generate_and_execute_python_code)
  - Gera JSON de filtros para consulta Parquet

  Papel na Implementação UNE:
  ✅ MANTÉM PAPEL PRINCIPAL
  + Adicionar decisão para novas ferramentas UNE:
    - calcular_abastecimento
    - simular_mudanca_linha_verde
    - calcular_preco_final
    - produtos_fora_linha
    - verificar_politica_devolucao

  Modificações Necessárias:
  # caculinha_bi_agent.py - EXTENSÃO
  def agent_runnable_logic(state: Dict[str, Any]) -> Dict[str, Any]:
      # ... código existente ...

      # ADICIONAR NOVAS DECISÕES:
      elif "abastecimento" in tool_decision or "linha verde" in tool_decision:
          return {"messages": [AIMessage(content="", tool_calls=[
              ToolCall(id=str(uuid.uuid4()),
                      name="calcular_abastecimento",
                      args={"une_id": extract_une_id(user_query)})
          ])]}

      elif "preço" in tool_decision and "atacado" in tool_decision:
          return {"messages": [AIMessage(content="", tool_calls=[
              ToolCall(id=str(uuid.uuid4()),
                      name="calcular_preco_final",
                      args=extract_price_params(user_query))
          ])]}

  ---
  2. CodeGen Agent (code_gen_agent.py)

  Papel Atual:
  - Gera código Python para análises complexas
  - Executa código gerado
  - Cria gráficos Plotly
  - Valida e corrige código automaticamente

  Papel na Implementação UNE:
  ✅ MANTÉM PAPEL - SEM ALTERAÇÕES DIRETAS
  Será usado para:
  - Análises de MC (Média Comum) em múltiplos produtos
  - Simulações de abastecimento em lote
  - Dashboards de linha verde
  - Análises de ranking de preços

  Casos de Uso UNE:
  # Queries que serão tratadas pelo CodeGen:
  "Calcule a MC de todos os produtos do segmento Tecidos"
  "Faça um gráfico comparando linha verde x estoque real da UNE 5"
  "Mostre o ranking de produtos que mais precisam de abastecimento"
  "Analise o impacto de aumentar 20% na linha verde dos top 10 produtos"

  ---
  3. Product Agent (product_agent.py)

  Papel Atual:
  - Busca produtos com filtros
  - Retorna detalhes de produtos
  - Análise de performance de produto

  Papel na Implementação UNE:
  ⚠️ PRECISA EXTENSÃO MODERADA
  + Adicionar métodos:
    - get_product_abastecimento_info()
    - get_product_pricing_policy()
    - get_product_grupo_id() # Para arredondamento
    - check_product_fora_linha()

  Modificações Necessárias:
  # product_agent.py - NOVOS MÉTODOS
  class ProductAgent:
      def get_product_abastecimento_info(self, product_code, une_id):
          """Retorna info de abastecimento: MC, LV, estoque, disparo"""
          df = get_table_df("ADMAT")
          product = df[(df["PRODUTO"] == product_code) & (df["UNE"] == une_id)]

          return {
              "mc": product["MC"].iloc[0],
              "linha_verde": self._calcular_linha_verde(product),
              "estoque_une": product["ESTOQUE_UNE"].iloc[0],
              "precisa_disparo": self._verificar_disparo(product),
              "qtd_a_disparar": self._calcular_qtd_disparo(product)
          }

      def get_product_pricing_policy(self, product_code):
          """Retorna ranking e preços varejo/atacado"""
          df = get_table_df("ADMAT")
          product = df[df["PRODUTO"] == product_code].iloc[0]

          return {
              "ranking": product["RANKING"],
              "preco_base": product["LIQUIDO_38"],
              "preco_varejo": self._calcular_preco_varejo(product),
              "preco_atacado": self._calcular_preco_atacado(product),
              "perfil_produto": product["PERFIL_PRODUTO"]
          }

  ---
  4. Base Agent (base_agent.py)

  Papel Atual:
  - Classe base para todos os agentes
  - Processa queries SQL via NodeMCPClient

  Papel na Implementação UNE:
  ✅ MANTÉM PAPEL - SEM ALTERAÇÕES
  Continua sendo base para herança

  ---
  5. Data Sync Agent (data_sync_agent.py)

  Papel Atual:
  - Sincroniza dados entre fontes

  Papel na Implementação UNE:
  ⚠️ PRECISA EXTENSÃO LEVE
  + Adicionar sincronização de:
    - Cálculo de MC (mensal/semanal)
    - Atualização de linha verde
    - Recálculo de rankings

  ---
  🆕 NOVOS AGENTES NECESSÁRIOS

  6. UNE Operations Agent (NOVO - CRÍTICO)

  # core/agents/une_operations_agent.py
  class UNEOperationsAgent:
      """
      Agente especializado em operações de UNE conforme guia oficial.

      Responsabilidades:
      - Calcular abastecimento (disparo quando estoque <= 50% LV)
      - Simular mudanças em linha verde
      - Aplicar política de preços (varejo x atacado)
      - Gerenciar produtos fora de linha
      - Validar devoluções e transferências
      """

      def __init__(self, llm_adapter, parquet_adapter):
          self.tools = [
              calcular_abastecimento_tool,
              simular_linha_verde_tool,
              calcular_preco_final_tool,
              produtos_fora_linha_tool,
              verificar_devolucao_tool,
              solicitar_transferencia_tool
          ]

  Integração no Graph:
  # core/graph/graph_builder.py - ADICIONAR NÓ
  workflow.add_node("une_operations", une_operations_node)

  # Roteamento
  def _decide_after_intent_classification(self, state: AgentState) -> str:
      intent = state.get("intent")

      if intent in ["abastecimento", "linha_verde", "preco_une", "fora_linha"]:
          return "une_operations"  # NOVO ROTEAMENTO
      elif intent in ["python_analysis", "gerar_grafico"]:
          return "generate_plotly_spec"
      else:
          return "generate_parquet_query"

  ---
  7. MC Robot Agent (NOVO - CRÍTICO)

  # core/agents/mc_robot_agent.py
  class MCRobotAgent:
      """
      Robô que executa cálculos automáticos de MC e atualiza linha verde.

      Execução:
      - Diária: Recalcula MC de produtos com vendas recentes
      - Virada de mês: Recalcula MC de todos os produtos
      - Atualização automática de ESTOQUE quando MC > ESTOQUE_GONDOLA e TRAVA=False

      NÃO é um agente conversacional - É um JOB AUTOMATIZADO
      """

      def run_monthly_mc_calculation(self):
          """Executa na virada de mês"""
          logger.info("Iniciando recálculo mensal de MC...")

          for product in get_all_products():
              if not product.trava_mc:
                  new_mc = self.calcular_mc(product)
                  self.atualizar_estoque_por_mc(product, new_mc)

      def run_daily_mc_update(self):
          """Executa diariamente para produtos ativos"""
          logger.info("Atualizando MC de produtos com vendas recentes...")

          produtos_ativos = get_products_with_recent_sales(days=7)
          for product in produtos_ativos:
              if not product.trava_mc:
                  new_mc = self.calcular_mc(product)
                  if new_mc > product.ESTOQUE_GONDOLA_LV:
                      product.ESTOQUE += (new_mc - product.ESTOQUE_GONDOLA_LV)

  Agendamento:
  # core/jobs/scheduler.py
  from apscheduler.schedulers.background import BackgroundScheduler

  scheduler = BackgroundScheduler()

  # Executa todo dia 1º do mês às 2h
  scheduler.add_job(mc_robot.run_monthly_mc_calculation,
                    trigger='cron', day=1, hour=2)

  # Executa diariamente às 3h
  scheduler.add_job(mc_robot.run_daily_mc_update,
                    trigger='cron', hour=3)

  scheduler.start()

  ---
  8. Pricing Policy Agent (NOVO - IMPORTANTE)

  # core/agents/pricing_policy_agent.py
  class PricingPolicyAgent:
      """
      Agente especializado em política de preços e cálculos de desconto.

      Responsabilidades:
      - Calcular preço final baseado em RANKING
      - Aplicar descontos por forma de pagamento
      - Validar limites de atacado (R$ 750)
      - Sugerir ajustes de ranking para produtos
      """

      def calcular_preco_final(self, produto_id, valor_compra, forma_pagamento):
          """
          Calcula preço final aplicando todas as regras:
          1. Verifica RANKING do produto
          2. Aplica política varejo x atacado (R$ 750)
          3. Aplica desconto por forma de pagamento
          """
          produto = self.get_produto(produto_id)
          preco_base = produto.LIQUIDO_38
          ranking = produto.RANKING

          # Regra 1: Varejo x Atacado
          if valor_compra >= 750:
              preco = preco_base  # Preço atacado (38% já embutido)
          else:
              preco = self._aplicar_desconto_varejo(preco_base, ranking)

          # Regra 2: Forma de pagamento
          preco_final = self._aplicar_desconto_pagamento(preco, forma_pagamento)

          return {
              "preco_base": preco_base,
              "preco_aplicado": preco,
              "desconto_pagamento": preco - preco_final,
              "preco_final": preco_final
          }

  ---
  📋 MATRIZ COMPLETA DE RESPONSABILIDADES

  | Agente           |          Fase 1Fundação          |    Fase 2Abastecimento    |    Fase 3Ferramentas     | Fase 4Especializado  | Fase 5Interface
  |
  |------------------|----------------------------------|---------------------------|--------------------------|----------------------|-----------------
  |
  | CaculinhaBI      | ⚠️ Modificar(adicionar decisões) |    ✅ Usar(roteamento)     |   ✅ Usar(orquestração)   | ✅ Usar(orquestração) |     ✅ Usar
      |
  | CodeGen          |                -                 |    ✅ Usar(análises MC)    |    ✅ Usar(dashboards)    |  ✅ Usar(simulações)  |     ✅ Usar
      |
  | Product          |    ⚠️ Estender(novos métodos)    |     ✅ Usar(consultas)     |     ✅ Usar(detalhes)     |  ✅ Usar(consultas)   |     ✅ Usar
      |
  | DataSync         |       ⚠️ Estender(sync MC)       |   ⚠️ Estender(sync LV)    |          ✅ Usar          |        ✅ Usar        |     ✅ Usar
     |
  | Base             |              ✅ Usar              |          ✅ Usar           |          ✅ Usar          |        ✅ Usar        |     ✅ Usar
       |
  | 🆕 UNEOperations |                -                 |     🔴 CRIAR(crítico)     |  🔴 DESENVOLVER(tools)   |  🔴 INTEGRAR(graph)  |     ✅ Usar
   |
  | 🆕 MCRobot       |       🔴 CRIAR(cálculo MC)       | 🔴 DESENVOLVER(lógica LV) |     🔴 AGENDAR(jobs)     |        ✅ Usar        |        -
   |
  | 🆕 PricingPolicy |        🔴 CRIAR(rankings)        |             -             | 🔴 DESENVOLVER(cálculos) | 🔴 INTEGRAR(UNEOps)  |     ✅ Usar
   |

  ---

● 🎯 FLUXO DE TRABALHO POR TIPO DE QUERY

  Exemplo 1: "Quais produtos precisam de abastecimento na UNE 5?"

  User Query → CaculinhaBI Agent
               ↓
            Classifica intent: "abastecimento"
               ↓
            Roteia para: UNE Operations Agent
               ↓
            UNE Operations chama tool: calcular_abastecimento(une_id=5)
               ↓
            Tool consulta: Product Agent (dados) + MC Robot (regras)
               ↓
            Retorna: Lista de produtos com ESTOQUE_UNE <= 50% LINHA_VERDE
               ↓
            Format Response → User

  ---
  Exemplo 2: "Calcule a MC de todos os produtos de Tecidos"

  User Query → CaculinhaBI Agent
               ↓
            Classifica intent: "python_analysis"
               ↓
            Roteia para: CodeGen Agent
               ↓
            CodeGen gera código:
            ```python
            df = load_data()
            tecidos = df[df['NOMESEGMENTO'] == 'TECIDOS']
            result = calcular_mc_em_lote(tecidos)
            ```
               ↓
            Executa e retorna DataFrame com MC calculada
               ↓
            Format Response → User

  ---
  Exemplo 3: "Qual o preço de R$ 600 em papelaria pagando em 30 dias?"

  User Query → CaculinhaBI Agent
               ↓
            Classifica intent: "preco_une"
               ↓
            Roteia para: UNE Operations Agent
               ↓
            UNE Operations chama: Pricing Policy Agent
               ↓
            Pricing Policy:
            1. Verifica valor < R$ 750 → Preço Varejo
            2. Consulta RANKING dos produtos da categoria
            3. Aplica desconto de forma de pagamento (36% para 30D)
               ↓
            Retorna: Preço final calculado
               ↓
            Format Response → User

  ---
  📊 PRIORIZAÇÃO DE DESENVOLVIMENTO DOS AGENTES

  🔴 CRÍTICO (Implementar Primeiro)

  1. MC Robot Agent
    - Razão: Base de todo o sistema de abastecimento
    - Complexidade: Alta
    - Dependências: Schema estendido (MC, TRAVA_MC)
    - Prazo: 2 semanas
  2. UNE Operations Agent
    - Razão: Interface principal para regras UNE
    - Complexidade: Média-Alta
    - Dependências: MC Robot, Product Agent estendido
    - Prazo: 1-2 semanas

  ---
  ⚠️ IMPORTANTE (Implementar em Seguida)

  3. Pricing Policy Agent
    - Razão: Regras de negócio críticas para vendas
    - Complexidade: Média
    - Dependências: Schema estendido (RANKING, PERFIL_PRODUTO)
    - Prazo: 1 semana
  4. Product Agent (Extensões)
    - Razão: Suporte a novos métodos para UNE Operations
    - Complexidade: Baixa-Média
    - Dependências: Schema estendido
    - Prazo: 3-5 dias

  ---
  🟢 DESEJÁVEL (Melhorias Futuras)

  5. Data Sync Agent (Extensões)
    - Razão: Automação de sincronização
    - Complexidade: Baixa
    - Dependências: MC Robot funcionando
    - Prazo: 3-5 dias

  ---
  🚀 RECOMENDAÇÃO DE INÍCIO

  Sugestão: Começar pelo MC Robot Agent + Extensões do Product Agent

  Razão:
  - MC Robot é a fundação de todo o sistema de abastecimento
  - Product Agent precisa dos novos métodos para suportar MC Robot
  - Permite testar cálculos de MC antes de criar UNE Operations

  Próximos Passos Imediatos:

  1. ✅ Criar schema estendido (MC, RANKING, PERFIL_PRODUTO, TRAVA_MC, GRUPO_ID)
  2. ✅ Implementar MC Robot Agent com cálculo de MC
  3. ✅ Estender Product Agent com métodos de abastecimento
  4. ✅ Criar UNE Operations Agent
  5. ✅ Integrar no Graph (roteamento)

  Você gostaria que eu:
  1. ✅ Comece a implementar o MC Robot Agent?
  2. ✅ Crie o script de migração do schema primeiro?
  3. ✅ Faça um protótipo do UNE Operations Agent?
  4. ✅ Prepare os testes unitários para os novos agentes?