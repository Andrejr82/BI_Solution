"""
FeedbackCollector - Coletor de Feedback do Usuário

Módulo responsável por coletar e armazenar feedback sobre respostas geradas,
permitindo aprendizado contínuo do sistema.

Autor: Code Agent
Data: 2025-10-18
Versão: 1.0.0
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)


class FeedbackCollector:
    """
    Coleta e armazena feedback do usuário sobre respostas geradas.

    Attributes:
        feedback_dir (Path): Diretório para armazenar feedbacks
    """

    def __init__(self, feedback_dir: str = "data/feedback"):
        """
        Inicializa o coletor de feedback

        Args:
            feedback_dir: Diretório onde serão salvos os feedbacks
        """
        self.feedback_dir = Path(feedback_dir)
        self.feedback_dir.mkdir(parents=True, exist_ok=True)

        logger.info(f"FeedbackCollector inicializado - Dir: {self.feedback_dir}")

    def save_feedback(
        self,
        query: str,
        response: str,
        rating: int,
        comment: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Salva feedback do usuário

        Args:
            query: Query original do usuário
            response: Resposta gerada pelo sistema
            rating: Avaliação (1-5)
            comment: Comentário adicional (opcional)
            metadata: Metadados adicionais (opcional)

        Returns:
            True se salvou com sucesso
        """
        try:
            feedback = {
                "timestamp": datetime.now().isoformat(),
                "query": query,
                "response": response,
                "rating": rating,
                "comment": comment,
                "metadata": metadata or {}
            }

            # Arquivo com data atual
            today = datetime.now().strftime("%Y%m%d")
            filepath = self.feedback_dir / f"feedback_{today}.jsonl"

            # Append ao arquivo JSONL
            with open(filepath, 'a', encoding='utf-8') as f:
                f.write(json.dumps(feedback, ensure_ascii=False) + '\n')

            logger.info(f"Feedback salvo: rating={rating}, query='{query[:50]}...'")
            return True

        except Exception as e:
            logger.error(f"Erro ao salvar feedback: {e}")
            return False


if __name__ == "__main__":
    # Teste rápido
    logging.basicConfig(level=logging.INFO)
    collector = FeedbackCollector()
    collector.save_feedback(
        query="Teste de feedback",
        response="Resposta teste",
        rating=5,
        comment="Funcionou perfeitamente!"
    )
    print("Feedback de teste salvo com sucesso!")
