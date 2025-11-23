"""
Módulo de Segurança: Mascaramento de PII (Informações Pessoais Identificáveis)
Fornece funções para identificar e mascarar dados sensíveis antes de enviar ao LLM.
"""

import re
import logging
from typing import Dict, List, Tuple

logger = logging.getLogger("data_masking")

# Padrões de regex para identificar PII
PII_PATTERNS = {
    "email": r"[\w\.-]+@[\w\.-]+\.\w+",
    "cpf": r"\d{3}\.\d{3}\.\d{3}-\d{2}",
    "telefone": r"\(\d{2}\)\s?\d{4,5}-\d{4}",
    "cartao_credito": r"\d{4}[\s-]?\d{4}[\s-]?\d{4}[\s-]?\d{4}",
    "nome_proprio": r"\b[A-Z][a-z]+\s[A-Z][a-z]+\b",  # Heurístico básico
}

# Mapeamento de padrão para token de mascaramento
PII_MASKS = {
    "email": "[EMAIL_MASKED]",
    "cpf": "[CPF_MASKED]",
    "telefone": "[TELEFONE_MASKED]",
    "cartao_credito": "[CARTAO_MASKED]",
    "nome_proprio": "[NOME_MASKED]",
}


class PIIMasker:
    """
    Classe responsável por mascarar dados sensíveis em textos.
    """
    
    def __init__(self, patterns: Dict[str, str] = None, masks: Dict[str, str] = None):
        """
        Inicializa o mascarador de PII.
        
        Args:
            patterns (Dict[str, str]): Dicionário de padrões regex customizados
            masks (Dict[str, str]): Dicionário de máscaras customizadas
        """
        self.patterns = patterns or PII_PATTERNS
        self.masks = masks or PII_MASKS
        self.masked_items: List[Tuple[str, str]] = []  # Histórico de mascaramentos
    
    def mask_text(self, text: str) -> str:
        """
        Mascara todos os padrões de PII em um texto.
        
        Args:
            text (str): Texto a ser mascarado
            
        Returns:
            str: Texto com PII mascarado
        """
        if not text:
            return text
        
        masked_text = text
        self.masked_items = []
        
        for pii_type, pattern in self.patterns.items():
            mask = self.masks.get(pii_type, "[MASKED]")
            
            # Encontra todas as ocorrências do padrão
            matches = re.finditer(pattern, masked_text)
            
            for match in matches:
                original_value = match.group(0)
                # Registra o mascaramento
                self.masked_items.append((pii_type, original_value))
                logger.debug(f"PII detectado ({pii_type}): {original_value[:10]}...")
            
            # Substitui todas as ocorrências
            masked_text = re.sub(pattern, mask, masked_text)
        
        logger.info(f"Mascaramento concluído: {len(self.masked_items)} itens de PII mascarados")
        return masked_text
    
    def mask_dict(self, data: Dict) -> Dict:
        """
        Mascara valores de PII em um dicionário.
        
        Args:
            data (Dict): Dicionário com dados potencialmente sensíveis
            
        Returns:
            Dict: Dicionário com PII mascarado
        """
        masked_data = {}
        
        for key, value in data.items():
            if isinstance(value, str):
                masked_data[key] = self.mask_text(value)
            elif isinstance(value, dict):
                masked_data[key] = self.mask_dict(value)
            elif isinstance(value, list):
                masked_data[key] = [
                    self.mask_text(item) if isinstance(item, str) else item
                    for item in value
                ]
            else:
                masked_data[key] = value
        
        return masked_data
    
    def get_masked_items_summary(self) -> Dict:
        """
        Retorna um resumo dos itens mascarados.
        
        Returns:
            Dict: Resumo com contagem por tipo de PII
        """
        summary = {}
        for pii_type, _ in self.masked_items:
            summary[pii_type] = summary.get(pii_type, 0) + 1
        
        return summary


# Instância global do mascarador
_global_masker = PIIMasker()


def mask_pii(text: str) -> str:
    """
    Função utilitária para mascarar PII em um texto.
    
    Args:
        text (str): Texto a ser mascarado
        
    Returns:
        str: Texto com PII mascarado
    """
    return _global_masker.mask_text(text)


def mask_pii_dict(data: Dict) -> Dict:
    """
    Função utilitária para mascarar PII em um dicionário.
    
    Args:
        data (Dict): Dicionário com dados potencialmente sensíveis
        
    Returns:
        Dict: Dicionário com PII mascarado
    """
    return _global_masker.mask_dict(data)


def get_pii_summary() -> Dict:
    """
    Retorna um resumo dos itens mascarados na sessão atual.
    
    Returns:
        Dict: Resumo com contagem por tipo de PII
    """
    return _global_masker.get_masked_items_summary()
