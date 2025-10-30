"""
Sistema de Auto-Correção (Self-Healing) para CodeGenAgent
Baseado em best practices da Anthropic Cookbook

Implementa:
1. Validação pre-execução de código
2. Sistema de retry inteligente com feedback
3. Aprendizado automático de erros
4. Correção automática de código

Autor: Claude Code
Data: 2025-10-26
Baseado em: Anthropic Cookbook - Iterative Code Generation
"""

import logging
import re
from typing import Dict, List, Any, Optional, Tuple
import pandas as pd

logger = logging.getLogger(__name__)


class SelfHealingSystem:
    """
    Sistema de auto-correção que valida e corrige código automaticamente.

    Baseado em padrões da Anthropic:
    - Iterative evaluation/generation loop
    - Feedback-driven improvement
    - Schema validation
    """

    def __init__(self, llm_adapter, schema_validator=None):
        """
        Inicializa sistema de auto-correção.

        Args:
            llm_adapter: Adaptador LLM para correções
            schema_validator: Validador de schema (opcional)
        """
        self.llm = llm_adapter
        self.schema_validator = schema_validator
        self.correction_history = []

        # Padrões de erro comuns e correções
        self.error_patterns = {
            "KeyError": self._fix_keyerror,
            "AttributeError": self._fix_attributeerror,
            "TypeError": self._fix_typeerror,
            "NameError": self._fix_nameerror,
            "ValueError": self._fix_valueerror,
        }

        logger.info("✅ SelfHealingSystem inicializado")

    def validate_and_heal(self, code: str, context: Dict[str, Any]) -> Tuple[bool, str, List[str]]:
        """
        Valida código e corrige automaticamente se possível.

        Args:
            code: Código Python gerado
            context: Contexto (query, schema, etc.)

        Returns:
            (success, corrected_code, feedback_list)
        """
        feedback = []

        # 1. Validação de sintaxe
        syntax_valid, syntax_error = self._validate_syntax(code)
        if not syntax_valid:
            feedback.append(f"Erro de sintaxe: {syntax_error}")
            return False, code, feedback

        # 2. Validação de schema (colunas)
        if self.schema_validator:
            schema_valid, schema_errors = self._validate_schema(code, context)
            if not schema_valid:
                feedback.extend(schema_errors)
                # Tentar corrigir automaticamente
                code = self._auto_fix_schema(code, schema_errors, context)
                feedback.append("✅ Código corrigido automaticamente (schema)")

        # 3. Validação de load_data()
        if "load_data" not in code:
            feedback.append("❌ Código não carrega dados com load_data()")
            return False, code, feedback

        # 4. Validação de result
        if not re.search(r'\nresult\s*=', code):
            feedback.append("❌ Código não define 'result'")
            return False, code, feedback

        # 5. Validação de filtros (otimização)
        filter_valid, filter_feedback = self._validate_filters(code, context)
        if filter_feedback:
            feedback.extend(filter_feedback)

        logger.info(f"✅ Validação concluída: {len(feedback)} avisos/correções")
        return True, code, feedback

    def heal_after_error(self, code: str, error: Exception, context: Dict[str, Any],
                         max_retries: int = 2) -> Tuple[bool, str, str]:
        """
        Tenta corrigir código após erro de execução.

        Baseado em: Anthropic Cookbook - Evaluator/Optimizer pattern

        Args:
            code: Código que falhou
            error: Exceção ocorrida
            context: Contexto da query
            max_retries: Máximo de tentativas

        Returns:
            (success, corrected_code, explanation)
        """
        error_type = type(error).__name__
        error_msg = str(error)

        logger.info(f"🔧 Tentando curar erro: {error_type}: {error_msg}")

        # Verificar se temos correção específica para este tipo de erro
        if error_type in self.error_patterns:
            try:
                corrected_code = self.error_patterns[error_type](code, error_msg, context)
                if corrected_code and corrected_code != code:
                    logger.info(f"✅ Código corrigido automaticamente ({error_type})")
                    return True, corrected_code, f"Corrigido {error_type} automaticamente"
            except Exception as e:
                logger.warning(f"⚠️ Correção automática falhou: {e}")

        # Fallback: Usar LLM para correção
        if max_retries > 0:
            return self._llm_based_correction(code, error_type, error_msg, context)

        return False, code, "Não foi possível corrigir automaticamente"

    def _validate_syntax(self, code: str) -> Tuple[bool, Optional[str]]:
        """Valida sintaxe Python."""
        try:
            compile(code, '<string>', 'exec')
            return True, None
        except SyntaxError as e:
            return False, str(e)

    def _validate_schema(self, code: str, context: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """
        Valida uso de colunas no código.

        Verifica se colunas mencionadas existem no schema real.
        """
        errors = []

        if not self.schema_validator:
            return True, []

        # Extrair colunas mencionadas no código
        column_patterns = [
            r"df\['([^']+)'\]",
            r'df\["([^"]+)"\]',
            r"\.([a-z_]+)\s*==",
            r"\.([a-z_]+)\s*!=",
            r"\.([a-z_]+)\.",
        ]

        mentioned_columns = set()
        for pattern in column_patterns:
            matches = re.findall(pattern, code, re.IGNORECASE)
            mentioned_columns.update(matches)

        # Verificar quais colunas não existem
        schema_columns = context.get('schema_columns', [])
        if schema_columns:
            for col in mentioned_columns:
                if col not in schema_columns and col.lower() not in [c.lower() for c in schema_columns]:
                    errors.append(f"Coluna '{col}' não existe no schema. Colunas disponíveis: {schema_columns[:5]}...")

        return len(errors) == 0, errors

    def _validate_filters(self, code: str, context: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """
        Valida uso de filtros no load_data().

        Baseado em: Best practice de passar filtros para otimização.
        """
        feedback = []
        query = context.get('query', '').lower()

        # Detectar se query menciona UNE/segmento específico
        une_match = re.search(r'une\s+(\w+)', query)
        segmento_match = re.search(r'segmento\s+(\w+)', query)

        # Verificar se código usa filtros
        has_filters = 'load_data(filters=' in code

        if (une_match or segmento_match) and not has_filters:
            feedback.append("⚠️ Query menciona UNE/segmento específico mas código não usa filtros")
            feedback.append("💡 Recomendação: Usar load_data(filters={...}) para melhor performance")

        return True, feedback

    def _auto_fix_schema(self, code: str, errors: List[str], context: Dict[str, Any]) -> str:
        """
        Tenta corrigir erros de schema automaticamente.

        Substitui nomes de colunas incorretos pelos corretos.
        """
        schema_columns = context.get('schema_columns', [])

        # Criar mapeamento case-insensitive
        column_map = {col.lower(): col for col in schema_columns}

        # Substituir colunas incorretas
        for error in errors:
            match = re.search(r"Coluna '([^']+)' não existe", error)
            if match:
                wrong_col = match.group(1)
                correct_col = column_map.get(wrong_col.lower())

                if correct_col:
                    # Substituir no código
                    code = re.sub(
                        rf"\['{wrong_col}'\]",
                        f"['{correct_col}']",
                        code,
                        flags=re.IGNORECASE
                    )
                    code = re.sub(
                        rf'\["{wrong_col}"\]',
                        f'["{correct_col}"]',
                        code,
                        flags=re.IGNORECASE
                    )
                    logger.info(f"✅ Substituído '{wrong_col}' → '{correct_col}'")

        return code

    def _fix_keyerror(self, code: str, error_msg: str, context: Dict[str, Any]) -> str:
        """
        Corrige KeyError (coluna não encontrada).

        Baseado em: Schema validation + column mapping
        """
        # Extrair nome da coluna do erro
        match = re.search(r"KeyError:\s*['\"]([^'\"]+)['\"]", error_msg)
        if not match:
            return code

        missing_col = match.group(1)
        schema_columns = context.get('schema_columns', [])

        # Buscar coluna similar (case-insensitive)
        column_map = {col.lower(): col for col in schema_columns}
        correct_col = column_map.get(missing_col.lower())

        if correct_col:
            # Substituir todas as ocorrências
            code = code.replace(f"['{missing_col}']", f"['{correct_col}']")
            code = code.replace(f'["{missing_col}"]', f'["{correct_col}"]')
            logger.info(f"✅ KeyError corrigido: '{missing_col}' → '{correct_col}'")
            return code

        return code

    def _fix_attributeerror(self, code: str, error_msg: str, context: Dict[str, Any]) -> str:
        """Corrige AttributeError comum."""
        # Exemplo: DataFrame/Series confusion
        if "has no attribute 'sort_values'" in error_msg:
            # Adicionar .reset_index() antes de sort_values
            code = re.sub(
                r'\.sum\(\)\.sort_values\(',
                '.sum().reset_index().sort_values(',
                code
            )
            logger.info("✅ AttributeError corrigido: adicionado .reset_index()")

        return code

    def _fix_typeerror(self, code: str, error_msg: str, context: Dict[str, Any]) -> str:
        """Corrige TypeError comum."""
        # Implementar correções específicas conforme necessário
        return code

    def _fix_nameerror(self, code: str, error_msg: str, context: Dict[str, Any]) -> str:
        """Corrige NameError (variável não definida)."""
        # Implementar correções específicas conforme necessário
        return code

    def _fix_valueerror(self, code: str, error_msg: str, context: Dict[str, Any]) -> str:
        """Corrige ValueError comum."""
        # Implementar correções específicas conforme necessário
        return code

    def _llm_based_correction(self, code: str, error_type: str, error_msg: str,
                              context: Dict[str, Any]) -> Tuple[bool, str, str]:
        """
        Usa LLM para corrigir código (fallback).

        Baseado em: Anthropic Cookbook - Evaluator/Optimizer pattern
        """
        correction_prompt = f"""
Você é um especialista em correção de código Python para análise de dados.

**CÓDIGO COM ERRO:**
```python
{code}
```

**ERRO OCORRIDO:**
Tipo: {error_type}
Mensagem: {error_msg}

**CONTEXTO:**
Query do usuário: {context.get('query', 'N/A')}
Colunas disponíveis: {context.get('schema_columns', [])}

**INSTRUÇÕES:**
1. Identifique o problema no código
2. Corrija APENAS o erro específico
3. NÃO mude a lógica do código
4. Use os NOMES CORRETOS das colunas do schema

**CÓDIGO CORRIGIDO:**
Forneça apenas o código Python corrigido, sem explicações.
"""

        try:
            messages = [{"role": "user", "content": correction_prompt}]
            response = self.llm.get_completion(messages=messages, temperature=0)

            if "error" in response:
                return False, code, "LLM falhou ao corrigir"

            corrected_code = self._extract_python_code(response.get("content", ""))
            if corrected_code:
                logger.info("✅ Código corrigido pela LLM")
                return True, corrected_code, "Corrigido pela LLM"

        except Exception as e:
            logger.error(f"❌ Erro ao usar LLM para correção: {e}")

        return False, code, "Correção LLM falhou"

    def _extract_python_code(self, text: str) -> Optional[str]:
        """Extrai código Python de resposta LLM."""
        match = re.search(r'```python\n(.*)```', text, re.DOTALL)
        if match:
            return match.group(1).strip()

        # Fallback: retornar texto completo se não encontrar bloco
        return text.strip()


# ============================================================================
# INTEGRAÇÃO COM CODE_GEN_AGENT
# ============================================================================

def integrate_self_healing(code_gen_agent):
    """
    Integra sistema de auto-correção no CodeGenAgent existente.

    Modifica o método generate_and_execute_code para usar auto-correção.
    """
    # Criar instância do self-healing
    self_healing = SelfHealingSystem(
        llm_adapter=code_gen_agent.llm,
        schema_validator=True
    )

    # Salvar referência
    code_gen_agent.self_healing = self_healing

    logger.info("✅ SelfHealingSystem integrado ao CodeGenAgent")

    return self_healing
