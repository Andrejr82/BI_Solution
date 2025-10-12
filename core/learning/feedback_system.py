"""
Sistema de coleta e análise de feedback do usuário.
"""

import json
import os
import logging
from datetime import datetime
from typing import Dict, Any, Optional


class FeedbackSystem:
    """
    Sistema para coletar, armazenar e analisar feedback do usuário
    sobre queries e respostas do sistema.
    """

    def __init__(self, feedback_dir: str = None):
        """
        Inicializa o sistema de feedback.

        Args:
            feedback_dir: Diretório para armazenar feedback (opcional)
        """
        self.logger = logging.getLogger(__name__)

        if feedback_dir is None:
            feedback_dir = os.path.join(os.getcwd(), "data", "feedback")

        self.feedback_dir = feedback_dir
        os.makedirs(self.feedback_dir, exist_ok=True)

        self.logger.info(f"✅ FeedbackSystem inicializado em {self.feedback_dir}")

    def record_feedback(
        self,
        query: str,
        code: str,
        feedback_type: str,
        user_comment: Optional[str] = None,
        result_rows: int = 0,
        session_id: Optional[str] = None,
        user_id: Optional[str] = None
    ) -> bool:
        """
        Registra feedback do usuário sobre uma query.

        Args:
            query: Query original do usuário
            code: Código gerado
            feedback_type: 'positive', 'negative', ou 'partial'
            user_comment: Comentário adicional do usuário (opcional)
            result_rows: Número de linhas retornadas
            session_id: ID da sessão (opcional)
            user_id: ID do usuário (opcional)

        Returns:
            True se salvou com sucesso
        """
        try:
            feedback_entry = {
                'timestamp': datetime.now().isoformat(),
                'query': query,
                'code': code,
                'feedback_type': feedback_type,
                'user_comment': user_comment,
                'result_rows': result_rows,
                'session_id': session_id,
                'user_id': user_id
            }

            # Salvar em arquivo diário
            date_str = datetime.now().strftime('%Y%m%d')
            feedback_file = os.path.join(self.feedback_dir, f'feedback_{date_str}.jsonl')

            with open(feedback_file, 'a', encoding='utf-8') as f:
                f.write(json.dumps(feedback_entry, ensure_ascii=False) + '\n')

            self.logger.info(f"✅ Feedback '{feedback_type}' registrado")
            return True

        except Exception as e:
            self.logger.error(f"❌ Erro ao registrar feedback: {e}")
            return False

    def get_feedback_stats(self, days: int = 7) -> Dict[str, Any]:
        """
        Calcula estatísticas de feedback dos últimos N dias.

        Args:
            days: Número de dias para analisar

        Returns:
            Dicionário com estatísticas
        """
        from datetime import timedelta

        stats = {
            'total': 0,
            'positive': 0,
            'negative': 0,
            'partial': 0,
            'success_rate': 0.0,
            'common_issues': []
        }

        try:
            # Ler arquivos dos últimos N dias
            today = datetime.now()
            feedback_entries = []

            for i in range(days):
                date = today - timedelta(days=i)
                date_str = date.strftime('%Y%m%d')
                feedback_file = os.path.join(self.feedback_dir, f'feedback_{date_str}.jsonl')

                if os.path.exists(feedback_file):
                    with open(feedback_file, 'r', encoding='utf-8') as f:
                        for line in f:
                            try:
                                feedback_entries.append(json.loads(line.strip()))
                            except json.JSONDecodeError:
                                continue

            # Calcular estatísticas
            stats['total'] = len(feedback_entries)

            if stats['total'] > 0:
                for entry in feedback_entries:
                    feedback_type = entry.get('feedback_type', '')
                    if feedback_type == 'positive':
                        stats['positive'] += 1
                    elif feedback_type == 'negative':
                        stats['negative'] += 1
                    elif feedback_type == 'partial':
                        stats['partial'] += 1

                # Taxa de sucesso = (positivo + parcial/2) / total
                stats['success_rate'] = (
                    (stats['positive'] + stats['partial'] * 0.5) / stats['total'] * 100
                )

                # Coletar problemas comuns (comentários negativos)
                issues = [
                    entry.get('user_comment', '')
                    for entry in feedback_entries
                    if entry.get('feedback_type') == 'negative' and entry.get('user_comment')
                ]
                stats['common_issues'] = issues[:10]  # Top 10

            self.logger.info(f"📊 Stats: {stats['total']} feedbacks, {stats['success_rate']:.1f}% sucesso")

        except Exception as e:
            self.logger.error(f"❌ Erro ao calcular estatísticas: {e}")

        return stats

    def get_problematic_queries(self, limit: int = 10) -> list:
        """
        Retorna queries que receberam mais feedback negativo.

        Args:
            limit: Número máximo de queries a retornar

        Returns:
            Lista de queries problemáticas
        """
        try:
            from collections import Counter

            negative_queries = []

            # Ler todos os arquivos de feedback
            for filename in os.listdir(self.feedback_dir):
                if filename.startswith('feedback_') and filename.endswith('.jsonl'):
                    feedback_file = os.path.join(self.feedback_dir, filename)

                    with open(feedback_file, 'r', encoding='utf-8') as f:
                        for line in f:
                            try:
                                entry = json.loads(line.strip())
                                if entry.get('feedback_type') == 'negative':
                                    negative_queries.append(entry.get('query', ''))
                            except json.JSONDecodeError:
                                continue

            # Contar queries mais problemáticas
            query_counts = Counter(negative_queries)
            most_common = query_counts.most_common(limit)

            return [
                {
                    'query': query,
                    'negative_count': count
                }
                for query, count in most_common
            ]

        except Exception as e:
            self.logger.error(f"❌ Erro ao buscar queries problemáticas: {e}")
            return []

    def export_feedback_for_training(self, output_file: str = None) -> bool:
        """
        Exporta feedback positivo para treinar o sistema (RAG/few-shot).

        Args:
            output_file: Arquivo de saída (opcional)

        Returns:
            True se exportou com sucesso
        """
        if output_file is None:
            output_file = os.path.join(self.feedback_dir, 'positive_examples.json')

        try:
            positive_examples = []

            # Ler todos os arquivos de feedback
            for filename in os.listdir(self.feedback_dir):
                if filename.startswith('feedback_') and filename.endswith('.jsonl'):
                    feedback_file = os.path.join(self.feedback_dir, filename)

                    with open(feedback_file, 'r', encoding='utf-8') as f:
                        for line in f:
                            try:
                                entry = json.loads(line.strip())
                                if entry.get('feedback_type') == 'positive':
                                    positive_examples.append({
                                        'query': entry.get('query'),
                                        'code': entry.get('code'),
                                        'result_rows': entry.get('result_rows'),
                                        'timestamp': entry.get('timestamp')
                                    })
                            except json.JSONDecodeError:
                                continue

            # Salvar exemplos positivos
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(positive_examples, f, indent=2, ensure_ascii=False)

            self.logger.info(f"✅ {len(positive_examples)} exemplos positivos exportados para {output_file}")
            return True

        except Exception as e:
            self.logger.error(f"❌ Erro ao exportar feedback: {e}")
            return False
