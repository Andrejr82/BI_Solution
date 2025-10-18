"""
Dynamic Prompt Module - Pilar 4: Prompt Engineering

Este módulo implementa prompts dinâmicos que evoluem baseados em erros históricos.
Adiciona avisos contextuais ao prompt base para prevenir erros recorrentes.

Autor: Code Agent
Data: 2025-10-18
"""

import logging
from typing import Dict, List, Optional

from core.learning.error_analyzer import ErrorAnalyzer

logger = logging.getLogger(__name__)


class DynamicPrompt:
    """
    Gerencia prompts dinâmicos que incorporam aprendizado de erros.

    Combina um prompt base com avisos gerados pela análise de erros históricos,
    criando prompts contextuais que ajudam a prevenir erros recorrentes.

    Attributes:
        base_prompt (str): Prompt base fundamental para geração de código
        error_analyzer (ErrorAnalyzer): Analisador de erros históricos
        _current_warnings (List[str]): Avisos ativos baseados em erros recentes
    """

    def __init__(self, base_prompt: Optional[str] = None) -> None:
        """
        Inicializa o sistema de prompts dinâmicos.

        Args:
            base_prompt: Prompt base customizado. Se None, usa prompt padrão.
        """
        self.base_prompt = base_prompt or self._get_default_prompt()
        self.error_analyzer = ErrorAnalyzer()
        self._current_warnings: List[str] = []

        logger.info("DynamicPrompt inicializado com base_prompt de %d caracteres",
                   len(self.base_prompt))

    def _get_default_prompt(self) -> str:
        """
        Retorna o prompt base padrão para geração de código.

        Returns:
            str: Prompt base padrão
        """
        return """Você é um assistente especializado em gerar consultas SQL e código Python para análise de dados.

REGRAS FUNDAMENTAIS:
1. Sempre valide os valores fornecidos pelo usuário contra os dados reais
2. Use aliases claros e descritivos em queries SQL
3. Sempre adicione tratamento de erros no código Python
4. Retorne DataFrames pandas quando apropriado
5. Use f-strings para formatação de strings em Python

BOAS PRÁTICAS:
- Prefira JOIN explícito ao invés de subconsultas quando possível
- Use LIMIT/head() para operações "top N"
- Valide tipos de dados antes de operações
- Adicione comentários explicativos no código gerado
"""

    def get_enhanced_prompt(self) -> str:
        """
        Retorna o prompt completo com avisos de erros comuns.

        Combina o prompt base com avisos contextuais gerados pela análise
        de erros históricos, criando um prompt enriquecido.

        Returns:
            str: Prompt completo com base + avisos contextuais
        """
        # Atualiza avisos baseados em análise recente
        self.update_prompt()

        # Monta prompt completo
        enhanced = self.base_prompt

        if self._current_warnings:
            enhanced += "\n\n⚠️ AVISOS (baseados em erros recentes):\n"
            for warning in self._current_warnings:
                enhanced += f"- {warning}\n"

        logger.debug("Prompt enriquecido gerado com %d avisos",
                    len(self._current_warnings))

        return enhanced

    def update_prompt(self) -> bool:
        """
        Atualiza o prompt baseado em análise de erros recentes.

        Analisa padrões de erros históricos e gera avisos contextuais
        para prevenir recorrências.

        Returns:
            bool: True se avisos foram atualizados, False caso contrário
        """
        try:
            # Obtém análise de erros recentes
            error_analysis = self.error_analyzer.analyze_recent_errors()

            if not error_analysis:
                logger.debug("Nenhuma análise de erro disponível")
                self._current_warnings = []
                return False

            # Gera avisos baseados nos padrões identificados
            new_warnings = self._generate_warnings(error_analysis)

            # Verifica se houve mudança
            warnings_changed = new_warnings != self._current_warnings

            if warnings_changed:
                self._current_warnings = new_warnings
                logger.info("Avisos do prompt atualizados: %d avisos ativos",
                           len(self._current_warnings))

            return warnings_changed

        except Exception as e:
            logger.error("Erro ao atualizar prompt: %s", str(e))
            return False

    def _generate_warnings(self, error_analysis: Dict) -> List[str]:
        """
        Gera avisos baseados na análise de erros.

        Args:
            error_analysis: Dicionário com análise de erros do ErrorAnalyzer

        Returns:
            List[str]: Lista de avisos contextuais
        """
        warnings = []

        # Extrai padrões da análise
        patterns = error_analysis.get('common_patterns', [])

        for pattern in patterns:
            pattern_type = pattern.get('type', '')
            pattern_count = pattern.get('count', 0)

            # Gera avisos específicos por tipo de padrão
            if pattern_type == 'column_not_found' and pattern_count >= 2:
                column_name = pattern.get('details', {}).get('column', 'desconhecida')
                warnings.append(
                    f"Valide se a coluna '{column_name}' existe antes de usar"
                )

            elif pattern_type == 'invalid_value' and pattern_count >= 2:
                warnings.append(
                    "Use valores EXATOS de segmentos/categorias conforme dados reais"
                )

            elif pattern_type == 'top_n_missing_head' and pattern_count >= 2:
                warnings.append(
                    "Se usuário pedir 'top N', SEMPRE use .head(N) ou LIMIT N"
                )

            elif pattern_type == 'missing_join' and pattern_count >= 2:
                warnings.append(
                    "Verifique se todas as tabelas necessárias estão com JOIN correto"
                )

            elif pattern_type == 'type_mismatch' and pattern_count >= 2:
                warnings.append(
                    "Valide tipos de dados antes de comparações e operações"
                )

        logger.debug("Gerados %d avisos a partir de %d padrões",
                    len(warnings), len(patterns))

        return warnings


# TODO: [in_progress] Implementar DynamicPrompt
# TODO: [completed] Classe DynamicPrompt com __init__, get_enhanced_prompt e update_prompt
# TODO: [completed] Integração com ErrorAnalyzer
# TODO: [completed] Geração de avisos contextuais baseados em padrões de erro
# TODO: [completed] Docstrings completas e type hints
# TODO: [completed] Sistema de logging
