"""
LangGraph Multi-Step Agent - Workflow cíclico para raciocínio avançado
Implementa: Planner → Executor → Validator → (loop se necessário)
"""

import logging
from typing import Dict, Any, List, Optional, TypedDict, Annotated
from dataclasses import dataclass
import operator

logger = logging.getLogger(__name__)

# Tentar importar LangGraph - fallback se não disponível
try:
    from langgraph.graph import StateGraph, END
    LANGGRAPH_AVAILABLE = True
except ImportError:
    LANGGRAPH_AVAILABLE = False
    logger.warning("LangGraph não disponível - usando implementação simplificada")


class AgentState(TypedDict):
    """Estado do agente durante execução do workflow."""
    query: str                          # Pergunta original
    plan: Optional[str]                 # Plano gerado
    tool_calls: List[Dict[str, Any]]    # Chamadas de ferramentas
    results: List[Dict[str, Any]]       # Resultados das ferramentas
    response: Optional[str]             # Resposta final
    validation: Optional[Dict[str, Any]]  # Resultado da validação
    iteration: int                      # Número da iteração
    should_retry: bool                  # Se deve tentar novamente
    error: Optional[str]                # Mensagem de erro


class MultiStepAgent:
    """
    Agente multi-step com workflow cíclico.
    
    Workflow:
    1. Planner: Analisa query e define estratégia
    2. Executor: Executa ferramentas necessárias
    3. Validator: Valida resultado e decide se precisa retry
    4. (Loop): Se necessário, refina e tenta novamente
    """
    
    MAX_ITERATIONS = 3
    
    def __init__(self, agent, validator=None):
        """
        Args:
            agent: Agente base (CaculinhaBIAgent)
            validator: Validador de respostas (opcional)
        """
        self.agent = agent
        self.validator = validator
        self.execution_count = 0
        
        # Construir grafo se LangGraph disponível
        if LANGGRAPH_AVAILABLE:
            self.graph = self._build_graph()
        else:
            self.graph = None
    
    def _build_graph(self):
        """Constrói o grafo de estados do workflow."""
        workflow = StateGraph(AgentState)
        
        # Adicionar nodes
        workflow.add_node("planner", self._planner_node)
        workflow.add_node("executor", self._executor_node)
        workflow.add_node("validator", self._validator_node)
        
        # Definir edges
        workflow.set_entry_point("planner")
        workflow.add_edge("planner", "executor")
        workflow.add_edge("executor", "validator")
        
        # Conditional edge: retry ou finalizar
        workflow.add_conditional_edges(
            "validator",
            self._should_retry,
            {
                "retry": "planner",
                "end": END
            }
        )
        
        return workflow.compile()
    
    def _planner_node(self, state: AgentState) -> AgentState:
        """Node de planejamento: analisa query e define estratégia."""
        logger.info(f"📝 Planner: Analisando query (iter={state['iteration']})")
        
        # Criar plano baseado na query e iteração anterior
        plan = f"Analisar: {state['query'][:100]}"
        
        if state['iteration'] > 0 and state.get('error'):
            plan = f"Retry devido a: {state['error'][:50]}. " + plan
        
        return {**state, "plan": plan}
    
    def _executor_node(self, state: AgentState) -> AgentState:
        """Node de execução: chama o agente base."""
        logger.info(f"⚙️ Executor: Executando plano")
        
        try:
            # Chamar agente base
            result = self.agent.run(state['query'])
            
            return {
                **state,
                "results": [result],
                "response": result.get("result", ""),
                "error": None
            }
        except Exception as e:
            logger.error(f"Erro no Executor: {e}")
            return {
                **state,
                "error": str(e),
                "response": None
            }
    
    def _validator_node(self, state: AgentState) -> AgentState:
        """Node de validação: verifica qualidade da resposta."""
        logger.info(f"✅ Validator: Validando resposta")
        
        # Se houve erro, marcar para retry
        if state.get('error'):
            return {
                **state,
                "should_retry": state['iteration'] < self.MAX_ITERATIONS,
                "iteration": state['iteration'] + 1
            }
        
        # Usar validador se disponível
        if self.validator:
            validation = self.validator.validate(
                {"result": state.get('response', '')},
                state['query']
            )
            
            should_retry = (
                not validation.is_valid and 
                validation.confidence < 0.5 and
                state['iteration'] < self.MAX_ITERATIONS
            )
            
            return {
                **state,
                "validation": {
                    "is_valid": validation.is_valid,
                    "confidence": validation.confidence,
                    "issues": validation.issues
                },
                "should_retry": should_retry,
                "iteration": state['iteration'] + 1
            }
        
        # Sem validador, aceitar resposta
        return {
            **state,
            "validation": {"is_valid": True, "confidence": 1.0},
            "should_retry": False,
            "iteration": state['iteration'] + 1
        }
    
    def _should_retry(self, state: AgentState) -> str:
        """Decide se deve fazer retry ou finalizar."""
        if state.get('should_retry', False):
            logger.info(f"🔄 Retry: iteration={state['iteration']}")
            return "retry"
        return "end"
    
    def run(self, query: str, chat_history: List[Dict] = None) -> Dict[str, Any]:
        """
        Executa workflow multi-step.
        
        Args:
            query: Pergunta do usuário
            chat_history: Histórico de chat (opcional)
            
        Returns:
            Resultado do agente
        """
        self.execution_count += 1
        logger.info(f"🚀 MultiStepAgent: Iniciando workflow para: {query[:50]}...")
        
        # Estado inicial
        initial_state: AgentState = {
            "query": query,
            "plan": None,
            "tool_calls": [],
            "results": [],
            "response": None,
            "validation": None,
            "iteration": 0,
            "should_retry": False,
            "error": None
        }
        
        # Usar LangGraph se disponível
        if self.graph and LANGGRAPH_AVAILABLE:
            try:
                final_state = self.graph.invoke(initial_state)
                
                return {
                    "type": "text",
                    "result": final_state.get("response", ""),
                    "validation": final_state.get("validation"),
                    "iterations": final_state.get("iteration", 1)
                }
            except Exception as e:
                logger.error(f"Erro no LangGraph: {e}")
                # Fallback para implementação simples
        
        # Implementação simplificada (fallback)
        return self._run_simple(query, chat_history)
    
    def _run_simple(self, query: str, chat_history: List[Dict] = None) -> Dict[str, Any]:
        """Implementação simplificada sem LangGraph."""
        logger.info("📝 Usando implementação simplificada (sem LangGraph)")
        
        for iteration in range(self.MAX_ITERATIONS):
            try:
                # Executar agente
                result = self.agent.run(query, chat_history)
                
                # Validar se possível
                if self.validator:
                    validation = self.validator.validate(result, query)
                    
                    if validation.is_valid or validation.confidence >= 0.5:
                        return {
                            **result,
                            "validation": {
                                "confidence": validation.confidence,
                                "issues": validation.issues
                            },
                            "iterations": iteration + 1
                        }
                    
                    logger.warning(f"Validação falhou (iter={iteration}): {validation.issues}")
                else:
                    return {**result, "iterations": iteration + 1}
                    
            except Exception as e:
                logger.error(f"Erro na iteração {iteration}: {e}")
                if iteration == self.MAX_ITERATIONS - 1:
                    return {
                        "type": "text",
                        "result": f"Erro após {self.MAX_ITERATIONS} tentativas: {str(e)}",
                        "iterations": iteration + 1
                    }
        
        return {
            "type": "text",
            "result": "Não foi possível obter uma resposta válida.",
            "iterations": self.MAX_ITERATIONS
        }
    
    def get_stats(self) -> Dict[str, Any]:
        """Retorna estatísticas do agente."""
        return {
            "execution_count": self.execution_count,
            "max_iterations": self.MAX_ITERATIONS,
            "langgraph_available": LANGGRAPH_AVAILABLE
        }


# Factory function
def create_multi_step_agent(base_agent, validator=None) -> MultiStepAgent:
    """Cria instância do MultiStepAgent."""
    return MultiStepAgent(agent=base_agent, validator=validator)
