"""
Módulo de Dashboard de Métricas - Pilar 4: Monitoramento e Aprimoramento Contínuo

Este módulo fornece análise e visualização de métricas de desempenho do sistema,
incluindo taxa de sucesso, tempo de resposta, cache hit rate e análise de queries.

Autor: Code Agent
Data: 2025-10-18
Versão: 1.0.0
"""

import json
import logging
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from collections import Counter, defaultdict

# Configuração de logging
logger = logging.getLogger(__name__)


class MetricsDashboard:
    """
    Dashboard de métricas para monitoramento do sistema de BI.

    Responsável por coletar, processar e apresentar métricas de:
    - Taxa de sucesso de queries
    - Tempo médio de resposta
    - Taxa de acerto de cache
    - Top queries mais executadas
    - Tendências de erros

    Attributes:
        learning_dir (Path): Diretório onde os arquivos de learning estão armazenados
    """

    def __init__(self, learning_dir: str = "data/learning"):
        """
        Inicializa o dashboard de métricas.

        Args:
            learning_dir (str): Caminho para o diretório de dados de aprendizado.
                              Padrão: "data/learning"
        """
        self.learning_dir = Path(learning_dir)
        logger.info(f"MetricsDashboard inicializado com diretório: {self.learning_dir}")

        # Cria diretório se não existir
        self.learning_dir.mkdir(parents=True, exist_ok=True)

    def get_metrics(self, days: int = 7) -> Dict[str, Any]:
        """
        Retorna todas as métricas consolidadas do período especificado.

        Args:
            days (int): Número de dias para análise retroativa. Padrão: 7

        Returns:
            Dict[str, Any]: Dicionário com métricas consolidadas:
                - success_rate (float): Taxa de sucesso (0.0 a 1.0)
                - avg_response_time (float): Tempo médio de resposta em segundos
                - cache_hit_rate (float): Taxa de acerto do cache (0.0 a 1.0)
                - total_queries (int): Total de queries processadas
                - top_queries (List[Dict]): Lista das top 10 queries
                - error_trend (Dict): Tendência de erros por dia

        Example:
            >>> dashboard = MetricsDashboard()
            >>> metrics = dashboard.get_metrics(days=7)
            >>> print(f"Taxa de sucesso: {metrics['success_rate']:.2%}")
        """
        logger.info(f"Coletando métricas dos últimos {days} dias")

        # Carrega dados de successful_queries e feedback
        successful_data = self._load_successful_queries(days)
        feedback_data = self._load_feedback(days)

        # Calcula métricas individuais
        success_rate = self.get_success_rate(successful_data, feedback_data)
        avg_response_time = self._calculate_avg_response_time(successful_data)
        cache_hit_rate = self._calculate_cache_hit_rate(successful_data)
        total_queries = len(successful_data) + len(feedback_data)
        top_queries = self.get_top_queries(successful_data, limit=10)
        error_trend = self._calculate_error_trend(feedback_data, days)

        metrics = {
            "success_rate": success_rate,
            "avg_response_time": avg_response_time,
            "cache_hit_rate": cache_hit_rate,
            "total_queries": total_queries,
            "top_queries": top_queries,
            "error_trend": error_trend
        }

        logger.info(
            f"Métricas coletadas: success_rate={success_rate:.2f}, "
            f"total_queries={total_queries}, cache_hit_rate={cache_hit_rate:.2f}"
        )

        return metrics

    def get_success_rate(
        self,
        successful_data: Optional[List[Dict]] = None,
        feedback_data: Optional[List[Dict]] = None
    ) -> float:
        """
        Calcula a taxa de sucesso das queries (positivo/total).

        Args:
            successful_data (Optional[List[Dict]]): Dados de queries bem-sucedidas.
                                                   Se None, carrega automaticamente.
            feedback_data (Optional[List[Dict]]): Dados de feedback.
                                                 Se None, carrega automaticamente.

        Returns:
            float: Taxa de sucesso entre 0.0 e 1.0

        Example:
            >>> dashboard = MetricsDashboard()
            >>> rate = dashboard.get_success_rate()
            >>> print(f"Taxa de sucesso: {rate:.2%}")
        """
        if successful_data is None:
            successful_data = self._load_successful_queries(days=7)

        if feedback_data is None:
            feedback_data = self._load_feedback(days=7)

        # Conta feedbacks positivos
        positive_feedback = sum(
            1 for item in feedback_data
            if item.get("feedback") == "positive"
        )

        # Total: queries bem-sucedidas + feedbacks
        total_successful = len(successful_data) + positive_feedback
        total_queries = len(successful_data) + len(feedback_data)

        if total_queries == 0:
            logger.warning("Nenhuma query encontrada para calcular taxa de sucesso")
            return 0.0

        success_rate = total_successful / total_queries
        logger.debug(f"Taxa de sucesso calculada: {success_rate:.2%} ({total_successful}/{total_queries})")

        return success_rate

    def get_top_queries(
        self,
        successful_data: Optional[List[Dict]] = None,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Retorna as top N queries mais executadas.

        Args:
            successful_data (Optional[List[Dict]]): Dados de queries bem-sucedidas.
                                                   Se None, carrega automaticamente.
            limit (int): Número máximo de queries a retornar. Padrão: 10

        Returns:
            List[Dict[str, Any]]: Lista de dicionários com:
                - query (str): Texto da query
                - count (int): Número de execuções
                - avg_time (float): Tempo médio de execução

        Example:
            >>> dashboard = MetricsDashboard()
            >>> top = dashboard.get_top_queries(limit=5)
            >>> for item in top:
            ...     print(f"{item['query']}: {item['count']} execuções")
        """
        if successful_data is None:
            successful_data = self._load_successful_queries(days=7)

        # Agrupa queries e coleta métricas
        query_stats = defaultdict(lambda: {"count": 0, "total_time": 0.0})

        for item in successful_data:
            query = item.get("query", "").strip().lower()
            if not query:
                continue

            query_stats[query]["count"] += 1

            # Tempo de resposta (se disponível)
            response_time = item.get("response_time", 0.0)
            query_stats[query]["total_time"] += response_time

        # Calcula média e ordena por contagem
        top_queries = []
        for query, stats in query_stats.items():
            avg_time = stats["total_time"] / stats["count"] if stats["count"] > 0 else 0.0
            top_queries.append({
                "query": query,
                "count": stats["count"],
                "avg_time": round(avg_time, 2)
            })

        # Ordena por count decrescente e limita
        top_queries.sort(key=lambda x: x["count"], reverse=True)
        top_queries = top_queries[:limit]

        logger.debug(f"Top {limit} queries calculadas: {len(top_queries)} queries únicas")

        return top_queries

    def _load_successful_queries(self, days: int) -> List[Dict[str, Any]]:
        """
        Carrega queries bem-sucedidas dos arquivos JSONL.

        Args:
            days (int): Número de dias retroativos para carregar

        Returns:
            List[Dict[str, Any]]: Lista de registros de queries bem-sucedidas
        """
        cutoff_date = datetime.now() - timedelta(days=days)
        data = []

        # Procura por arquivos successful_queries_*.jsonl
        pattern = "successful_queries_*.jsonl"
        for filepath in self.learning_dir.glob(pattern):
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    for line in f:
                        if line.strip():
                            record = json.loads(line)

                            # Filtra por data se disponível
                            timestamp_str = record.get("timestamp")
                            if timestamp_str:
                                record_date = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
                                if record_date >= cutoff_date:
                                    data.append(record)
                            else:
                                # Se não tem timestamp, inclui
                                data.append(record)

                logger.debug(f"Carregados {len(data)} registros de {filepath.name}")

            except Exception as e:
                logger.error(f"Erro ao carregar {filepath}: {e}")

        logger.info(f"Total de queries bem-sucedidas carregadas: {len(data)}")
        return data

    def _load_feedback(self, days: int) -> List[Dict[str, Any]]:
        """
        Carrega dados de feedback dos arquivos JSONL.

        Args:
            days (int): Número de dias retroativos para carregar

        Returns:
            List[Dict[str, Any]]: Lista de registros de feedback
        """
        cutoff_date = datetime.now() - timedelta(days=days)
        data = []

        # Procura por arquivos feedback_*.jsonl
        pattern = "feedback_*.jsonl"
        for filepath in self.learning_dir.glob(pattern):
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    for line in f:
                        if line.strip():
                            record = json.loads(line)

                            # Filtra por data se disponível
                            timestamp_str = record.get("timestamp")
                            if timestamp_str:
                                record_date = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
                                if record_date >= cutoff_date:
                                    data.append(record)
                            else:
                                # Se não tem timestamp, inclui
                                data.append(record)

                logger.debug(f"Carregados {len(data)} feedbacks de {filepath.name}")

            except Exception as e:
                logger.error(f"Erro ao carregar {filepath}: {e}")

        logger.info(f"Total de feedbacks carregados: {len(data)}")
        return data

    def _calculate_avg_response_time(self, successful_data: List[Dict]) -> float:
        """
        Calcula o tempo médio de resposta das queries.

        Args:
            successful_data (List[Dict]): Lista de queries bem-sucedidas

        Returns:
            float: Tempo médio de resposta em segundos
        """
        times = [
            item.get("response_time", 0.0)
            for item in successful_data
            if "response_time" in item
        ]

        if not times:
            logger.warning("Nenhum tempo de resposta encontrado")
            return 0.0

        avg_time = sum(times) / len(times)
        logger.debug(f"Tempo médio de resposta: {avg_time:.2f}s ({len(times)} amostras)")

        return round(avg_time, 2)

    def _calculate_cache_hit_rate(self, successful_data: List[Dict]) -> float:
        """
        Calcula a taxa de acerto do cache.

        Args:
            successful_data (List[Dict]): Lista de queries bem-sucedidas

        Returns:
            float: Taxa de cache hit entre 0.0 e 1.0
        """
        total = len(successful_data)
        if total == 0:
            logger.warning("Nenhuma query para calcular cache hit rate")
            return 0.0

        # Conta queries que vieram do cache
        cache_hits = sum(
            1 for item in successful_data
            if item.get("from_cache", False) or item.get("cached", False)
        )

        cache_hit_rate = cache_hits / total
        logger.debug(f"Cache hit rate: {cache_hit_rate:.2%} ({cache_hits}/{total})")

        return round(cache_hit_rate, 2)

    def _calculate_error_trend(self, feedback_data: List[Dict], days: int) -> Dict[str, int]:
        """
        Calcula a tendência de erros por dia.

        Args:
            feedback_data (List[Dict]): Lista de feedbacks
            days (int): Número de dias para análise

        Returns:
            Dict[str, int]: Mapa de data (YYYY-MM-DD) para contagem de erros
        """
        error_trend = defaultdict(int)

        for item in feedback_data:
            # Conta apenas feedbacks negativos como erros
            if item.get("feedback") == "negative":
                timestamp_str = item.get("timestamp")
                if timestamp_str:
                    try:
                        record_date = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
                        date_key = record_date.strftime("%Y-%m-%d")
                        error_trend[date_key] += 1
                    except Exception as e:
                        logger.warning(f"Erro ao processar timestamp: {e}")

        # Garante que todos os dias do período estejam presentes
        start_date = datetime.now() - timedelta(days=days)
        for i in range(days):
            date_key = (start_date + timedelta(days=i)).strftime("%Y-%m-%d")
            if date_key not in error_trend:
                error_trend[date_key] = 0

        # Converte para dict ordenado
        sorted_trend = dict(sorted(error_trend.items()))

        logger.debug(f"Tendência de erros calculada para {len(sorted_trend)} dias")

        return sorted_trend
