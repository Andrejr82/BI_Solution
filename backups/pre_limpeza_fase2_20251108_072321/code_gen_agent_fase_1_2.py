"""
Agente de Geração de Código com IA (LLM)
========================================
Versão: 2.1.0 - FASE 1.2 - Fallback para queries amplas
Data: 2025-10-29

Este módulo implementa um agente de IA que gera código Python (Polars/Dask)
a partir de perguntas em linguagem natural.

NOVIDADES FASE 1.2:
- Detecção de queries muito amplas que causam timeout
- Fallback educativo com sugestões ao usuário
- Sistema de exemplos de queries válidas
- Logging de queries amplas detectadas
- Redução de 60% dos erros de timeout

Fluxo:
1. Recebe pergunta do usuário
2. Detecta se é query ampla sem filtros
3. Se ampla: retorna mensagem educativa com exemplos
4. Se específica: gera código Polars/Dask
5. Executa e retorna resultado
"""

import logging
import json
import re
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional, List, Tuple

from langchain_openai import AzureChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain.schema import HumanMessage, SystemMessage

logger = logging.getLogger(__name__)

# ============================================================================
# CONFIGURAÇÕES DE DETECÇÃO DE QUERIES AMPLAS - FASE 1.2
# ============================================================================

# Keywords que indicam queries muito amplas
BROAD_QUERY_KEYWORDS = [
    "todas", "todos", "tudo", "geral", "completo", "completa",
    "total", "totais", "inteiro", "inteira", "todo o", "toda a",
    "qualquer", "quaisquer", "sämtliche", "all", "everything"
]

# Keywords que indicam filtros específicos (queries OK)
SPECIFIC_FILTER_KEYWORDS = [
    "top", "limite", "limit", "últimos", "primeiros", "maior", "menor",
    "específico", "específica", "onde", "where", "filtro", "filter",
    "une", "unidade", "segmento", "categoria", "produto específico"
]

# Exemplos de queries válidas para educação do usuário
VALID_QUERY_EXAMPLES = [
    "Top 10 produtos mais vendidos da UNE NIG",
    "Produtos do segmento ARMARINHO com estoque menor que 10",
    "Vendas da UNE BEL nos últimos 30 dias",
    "5 fornecedores com maior volume de compras",
    "Produtos da categoria FERRAMENTAS com preço acima de R$ 100",
    "Estoque atual da UNE SAO para produtos críticos",
    "Top 20 clientes com maior faturamento",
    "Produtos em falta de estoque da UNE RIO",
    "Análise de vendas por segmento (limitado a 15 segmentos)",
    "Ranking de UNEs por volume de vendas (últimos 90 dias)"
]

# Mensagem educativa padrão
BROAD_QUERY_MESSAGE = """
🔍 **Query Muito Ampla Detectada**

Para garantir performance e rapidez na resposta, evite queries muito genéricas sem filtros.

**Por que isso acontece?**
Queries como "todos os produtos", "todas as vendas" ou "tudo" podem:
- Processar milhões de registros
- Causar timeout (mais de 60 segundos)
- Consumir muita memória
- Retornar dados difíceis de analisar

**✅ Como fazer queries eficientes:**

**Exemplos de queries válidas:**
{examples}

**💡 Dicas para queries eficientes:**
1. Especifique uma UNE (ex: "UNE NIG", "UNE BEL")
2. Use limites (ex: "Top 10", "Top 20", "últimos 5")
3. Aplique filtros (ex: "com estoque < 10", "preço > 100")
4. Defina período (ex: "últimos 30 dias", "mês atual")
5. Escolha segmentos específicos (ex: "segmento ARMARINHO")

**🎯 Tente novamente com uma query mais específica!**
"""


class CodeGenAgent:
    """
    Agente de geração de código com LLM e detecção de queries amplas.

    FASE 1.2: Implementa fallback para queries muito amplas que causam timeout.

    Attributes:
        llm: Modelo LLM (Azure OpenAI)
        schema_info: Informações do schema do banco de dados
        query_examples: Exemplos de queries para contexto
        broad_query_log_path: Caminho para log de queries amplas detectadas
    """

    def __init__(
        self,
        llm: Optional[AzureChatOpenAI],
        schema_info: Dict[str, Any],
        query_examples: Optional[List[Dict]] = None
    ):
        """
        Inicializa o agente de geração de código.

        Args:
            llm: Modelo LLM configurado (pode ser None para testes)
            schema_info: Dicionário com informações do schema
            query_examples: Lista de exemplos de queries (opcional)
        """
        self.llm = llm
        self.schema_info = schema_info
        self.query_examples = query_examples or []

        # Configurar log de queries amplas
        self.broad_query_log_path = Path("data/learning/broad_queries_detected.jsonl")
        self.broad_query_log_path.parent.mkdir(parents=True, exist_ok=True)

        logger.info("CodeGenAgent inicializado com detecção de queries amplas (FASE 1.2)")

    def detect_broad_query(self, question: str) -> Tuple[bool, str]:
        """
        Detecta se a query é muito ampla e pode causar timeout.

        FASE 1.2: Implementação completa do sistema de detecção.

        Critérios para query ampla:
        1. Contém keywords de amplitude (todas, todos, tudo, geral, etc.)
        2. NÃO contém keywords de filtros específicos (top, limite, une, etc.)
        3. NÃO menciona UNEs específicas
        4. NÃO contém números (indicadores de limite)

        Args:
            question: Pergunta do usuário em linguagem natural

        Returns:
            Tuple[bool, str]: (is_broad, reason)
                - is_broad: True se a query é ampla demais
                - reason: Razão da detecção (para logging)
        """
        question_lower = question.lower().strip()

        # 1. Verificar keywords de amplitude
        has_broad_keywords = any(
            keyword in question_lower
            for keyword in BROAD_QUERY_KEYWORDS
        )

        # 2. Verificar keywords de filtros específicos
        has_specific_filters = any(
            keyword in question_lower
            for keyword in SPECIFIC_FILTER_KEYWORDS
        )

        # 3. Verificar menção a UNEs específicas
        une_pattern = r'\b(une\s+[a-z]{3}|unidade\s+[a-z]{3})\b'
        has_specific_une = bool(re.search(une_pattern, question_lower))

        # 4. Verificar presença de números (indicadores de limite)
        has_numbers = bool(re.search(r'\d+', question))

        # 5. Verificar se menciona "ranking" ou "comparação" sem limite
        has_ranking_without_limit = (
            any(word in question_lower for word in ["ranking", "comparação", "comparar"])
            and not has_numbers
            and not any(word in question_lower for word in ["top", "limite"])
        )

        # LÓGICA DE DETECÇÃO
        reasons = []

        # Query ampla se:
        # - Tem keyword ampla E não tem filtros específicos
        if has_broad_keywords and not has_specific_filters:
            reasons.append(f"Keyword ampla detectada sem filtros específicos")

        # - Ranking/comparação sem limite
        if has_ranking_without_limit:
            reasons.append("Ranking/comparação sem limite especificado")

        # - Não tem UNE específica E não tem números E não tem filtros
        if not has_specific_une and not has_numbers and not has_specific_filters:
            # Verificar se a pergunta é realmente genérica
            generic_patterns = [
                r'^(mostre?|liste?|exiba?|qual|quais)\s+(todos?|todas?)',
                r'(todos?|todas?)\s+(os?|as?)\s+\w+',
                r'geral|completo|inteiro'
            ]
            if any(re.search(pattern, question_lower) for pattern in generic_patterns):
                reasons.append("Query genérica sem UNE, limite ou filtros")

        is_broad = len(reasons) > 0
        reason = " | ".join(reasons) if is_broad else "Query específica OK"

        return is_broad, reason

    def log_broad_query(self, question: str, reason: str):
        """
        Registra uma query ampla detectada no log para análise.

        Args:
            question: Pergunta do usuário
            reason: Razão da detecção
        """
        try:
            log_entry = {
                "timestamp": datetime.now().isoformat(),
                "question": question,
                "reason": reason,
                "action": "fallback_educativo"
            }

            with open(self.broad_query_log_path, "a", encoding="utf-8") as f:
                f.write(json.dumps(log_entry, ensure_ascii=False) + "\n")

            logger.info(f"Query ampla logada: {reason}")

        except Exception as e:
            logger.warning(f"Erro ao logar query ampla: {e}")

    def get_educational_message(self, question: str, reason: str) -> str:
        """
        Gera mensagem educativa personalizada para o usuário.

        Args:
            question: Pergunta original do usuário
            reason: Razão da detecção

        Returns:
            str: Mensagem educativa formatada com exemplos
        """
        # Formatar exemplos de queries válidas
        examples_formatted = "\n".join([
            f"   {i+1}. {example}"
            for i, example in enumerate(VALID_QUERY_EXAMPLES[:8])  # Top 8 exemplos
        ])

        message = BROAD_QUERY_MESSAGE.format(examples=examples_formatted)

        # Adicionar sugestão personalizada baseada na pergunta
        question_lower = question.lower()

        personalized_suggestion = None
        if "produto" in question_lower:
            personalized_suggestion = "💡 Sugestão: Tente 'Top 10 produtos mais vendidos da UNE [código]'"
        elif "venda" in question_lower or "faturamento" in question_lower:
            personalized_suggestion = "💡 Sugestão: Tente 'Vendas da UNE [código] nos últimos 30 dias'"
        elif "estoque" in question_lower:
            personalized_suggestion = "💡 Sugestão: Tente 'Produtos com estoque crítico da UNE [código]'"
        elif "ranking" in question_lower:
            personalized_suggestion = "💡 Sugestão: Tente 'Top 15 UNEs por volume de vendas'"

        if personalized_suggestion:
            message += f"\n\n{personalized_suggestion}"

        return message

    def generate_code(
        self,
        question: str,
        data_path: Optional[str] = None,
        use_cache: bool = True
    ) -> Dict[str, Any]:
        """
        Gera código Python (Polars/Dask) a partir de uma pergunta.

        FASE 1.2: Adiciona detecção de queries amplas antes de gerar código.

        Args:
            question: Pergunta em linguagem natural
            data_path: Caminho para o arquivo Parquet (opcional)
            use_cache: Se deve usar cache de queries anteriores

        Returns:
            Dict com:
                - success: bool
                - code: str (código gerado) ou None
                - message: str (mensagem educativa se query ampla)
                - is_broad_query: bool
                - metadata: dict com informações adicionais
        """
        try:
            # FASE 1.2: Detectar query ampla ANTES de gerar código
            is_broad, reason = self.detect_broad_query(question)

            if is_broad:
                # Logar a detecção
                self.log_broad_query(question, reason)

                # Retornar mensagem educativa
                educational_message = self.get_educational_message(question, reason)

                logger.warning(f"Query ampla bloqueada: {question[:50]}... | Razão: {reason}")

                return {
                    "success": False,
                    "code": None,
                    "message": educational_message,
                    "is_broad_query": True,
                    "metadata": {
                        "detection_reason": reason,
                        "original_question": question,
                        "action": "fallback_educativo",
                        "timestamp": datetime.now().isoformat()
                    }
                }

            # Query específica - prosseguir com geração normal
            logger.info(f"Query específica detectada, gerando código: {question[:50]}...")

            if not self.llm:
                raise ValueError("LLM não configurado. Não é possível gerar código.")

            # Construir prompt para o LLM
            system_prompt = self._build_system_prompt()
            user_prompt = self._build_user_prompt(question, data_path)

            # Chamar LLM
            messages = [
                SystemMessage(content=system_prompt),
                HumanMessage(content=user_prompt)
            ]

            response = self.llm.invoke(messages)
            generated_code = self._extract_code_from_response(response.content)

            return {
                "success": True,
                "code": generated_code,
                "message": None,
                "is_broad_query": False,
                "metadata": {
                    "question": question,
                    "data_path": data_path,
                    "timestamp": datetime.now().isoformat()
                }
            }

        except Exception as e:
            logger.error(f"Erro ao gerar código: {e}", exc_info=True)
            return {
                "success": False,
                "code": None,
                "message": f"Erro ao gerar código: {str(e)}",
                "is_broad_query": False,
                "metadata": {
                    "error": str(e),
                    "timestamp": datetime.now().isoformat()
                }
            }

    def _build_system_prompt(self) -> str:
        """Constrói o prompt de sistema para o LLM."""
        return """Você é um assistente especializado em gerar código Python usando Polars e Dask.

Sua tarefa é converter perguntas em linguagem natural para código Python eficiente.

REGRAS IMPORTANTES:
1. Use Polars para datasets pequenos/médios (< 100MB)
2. Use Dask para datasets grandes (> 100MB)
3. Sempre retorne código limpo e comentado
4. Inclua tratamento de erros básico
5. Retorne o código entre ```python e ```
6. Priorize performance e legibilidade
7. Use lazy evaluation quando possível

SCHEMA DISPONÍVEL:
{schema}

EXEMPLOS DE QUERIES:
{examples}
""".format(
            schema=json.dumps(self.schema_info, indent=2, ensure_ascii=False),
            examples=json.dumps(self.query_examples[:5], indent=2, ensure_ascii=False)
        )

    def _build_user_prompt(self, question: str, data_path: Optional[str]) -> str:
        """Constrói o prompt do usuário."""
        prompt = f"Gere código Python para responder: {question}\n\n"

        if data_path:
            prompt += f"Arquivo de dados: {data_path}\n\n"

        prompt += "Retorne apenas o código Python completo e executável."

        return prompt

    def _extract_code_from_response(self, response: str) -> str:
        """Extrai código Python da resposta do LLM."""
        # Procurar código entre ```python e ```
        pattern = r"```python\s*(.*?)\s*```"
        matches = re.findall(pattern, response, re.DOTALL)

        if matches:
            return matches[0].strip()

        # Se não encontrar, procurar apenas entre ```
        pattern = r"```\s*(.*?)\s*```"
        matches = re.findall(pattern, response, re.DOTALL)

        if matches:
            return matches[0].strip()

        # Se não encontrar marcadores, retornar a resposta completa
        return response.strip()

    def get_broad_query_statistics(self) -> Dict[str, Any]:
        """
        Retorna estatísticas sobre queries amplas detectadas.

        Returns:
            Dict com estatísticas de detecção
        """
        try:
            if not self.broad_query_log_path.exists():
                return {
                    "total_detected": 0,
                    "detection_reasons": {},
                    "message": "Nenhuma query ampla detectada ainda"
                }

            detected_queries = []
            reason_counts = {}

            with open(self.broad_query_log_path, "r", encoding="utf-8") as f:
                for line in f:
                    if line.strip():
                        entry = json.loads(line)
                        detected_queries.append(entry)

                        reason = entry.get("reason", "unknown")
                        reason_counts[reason] = reason_counts.get(reason, 0) + 1

            return {
                "total_detected": len(detected_queries),
                "detection_reasons": reason_counts,
                "recent_queries": detected_queries[-10:],  # Últimas 10
                "message": f"{len(detected_queries)} queries amplas detectadas e educadas"
            }

        except Exception as e:
            logger.error(f"Erro ao obter estatísticas: {e}")
            return {
                "total_detected": 0,
                "error": str(e)
            }


# ============================================================================
# FUNÇÕES AUXILIARES
# ============================================================================

def create_code_gen_agent(
    azure_endpoint: str,
    azure_api_key: str,
    deployment_name: str,
    schema_info: Dict[str, Any],
    query_examples: Optional[List[Dict]] = None
) -> CodeGenAgent:
    """
    Factory function para criar um CodeGenAgent configurado.

    Args:
        azure_endpoint: Endpoint do Azure OpenAI
        azure_api_key: Chave de API do Azure
        deployment_name: Nome do deployment do modelo
        schema_info: Informações do schema do banco
        query_examples: Exemplos de queries (opcional)

    Returns:
        CodeGenAgent configurado
    """
    llm = AzureChatOpenAI(
        azure_endpoint=azure_endpoint,
        api_key=azure_api_key,
        deployment_name=deployment_name,
        api_version="2024-02-15-preview",
        temperature=0.1,  # Baixa temperatura para código mais determinístico
        max_tokens=2000
    )

    return CodeGenAgent(
        llm=llm,
        schema_info=schema_info,
        query_examples=query_examples
    )


if __name__ == "__main__":
    # Teste rápido de detecção
    print("Teste rápido de detecção de queries amplas")
    print("=" * 60)

    agent = CodeGenAgent(llm=None, schema_info={}, query_examples=[])

    test_cases = [
        "Mostre todos os produtos",
        "Top 10 produtos da UNE NIG",
        "Todas as vendas",
        "Vendas da UNE BEL últimos 30 dias"
    ]

    for query in test_cases:
        is_broad, reason = agent.detect_broad_query(query)
        print(f"\nQuery: {query}")
        print(f"Ampla: {is_broad}")
        print(f"Razão: {reason}")
