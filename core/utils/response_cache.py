"""
Sistema de cache inteligente para respostas LLM (Gemini/DeepSeek)
Economiza créditos evitando chamadas repetidas à API

✅ CORREÇÃO v2.1.4 (02/11/2025):
- Adicionado versionamento para invalidar cache após mudanças de código
- Reduzido TTL padrão de 24h para 1h (evita cache obsoleto)
- Hash inclui contexto adicional para evitar mistura de respostas
- Limpeza automática de cache expirado no init
"""
import hashlib
import json
import os
import time
import logging
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

# 🔥 VERSÃO DO CÓDIGO - Incremente quando mudar lógica de formatação/respostas
CACHE_VERSION = "v2.1.4"

class ResponseCache:
    """Cache inteligente para respostas LLM (Gemini/DeepSeek)"""

    def __init__(self, cache_dir: str = "data/cache", ttl_hours: int = 1):
        """
        Inicializa cache com TTL reduzido e limpeza automática

        Args:
            cache_dir: Diretório para armazenar cache
            ttl_hours: Tempo de vida do cache em horas (padrão: 1h, antes era 24h)
        """
        self.cache_dir = cache_dir
        self.ttl_seconds = ttl_hours * 3600
        os.makedirs(cache_dir, exist_ok=True)

        # 🚀 Limpeza automática no init
        self.clear_expired()

        logger.info(f"✅ Cache inicializado: {cache_dir}, TTL: {ttl_hours}h, Versão: {CACHE_VERSION}")

    def _generate_key(self, messages: list, model: str, temperature: float, context: Optional[Dict] = None) -> str:
        """
        Gera chave única para a consulta incluindo versionamento e contexto

        Args:
            messages: Lista de mensagens da conversa
            model: Nome do modelo LLM
            temperature: Temperatura da geração
            context: Contexto adicional (intent, tipo de resposta, etc.)
        """
        # 🔥 NOVO: Incluir versão do código e contexto adicional
        query_data = {
            "version": CACHE_VERSION,  # Invalida cache quando código muda
            "messages": messages,
            "model": model,
            "temperature": temperature,
            "context": context or {}  # Intent, tipo de resposta, etc.
        }
        query_str = json.dumps(query_data, sort_keys=True)
        return hashlib.md5(query_str.encode()).hexdigest()

    def get(self, messages: list, model: str, temperature: float, context: Optional[Dict] = None) -> Optional[Dict[str, Any]]:
        """
        Recupera resposta do cache se disponível e válida

        Args:
            messages: Lista de mensagens
            model: Nome do modelo
            temperature: Temperatura
            context: Contexto adicional (intent, tipo, etc.)
        """
        cache_key = self._generate_key(messages, model, temperature, context)
        cache_file = os.path.join(self.cache_dir, f"{cache_key}.json")

        try:
            if not os.path.exists(cache_file):
                return None

            with open(cache_file, 'r', encoding='utf-8') as f:
                cached_data = json.load(f)

            # 🔥 NOVO: Verificar versão do cache
            cached_version = cached_data.get('metadata', {}).get('version', 'v0.0.0')
            if cached_version != CACHE_VERSION:
                os.remove(cache_file)  # Remove cache de versão antiga
                logger.info(f"Cache de versão antiga removido: {cache_key[:8]} ({cached_version} -> {CACHE_VERSION})")
                return None

            # Verificar se ainda está válido (TTL)
            cache_time = cached_data.get('timestamp', 0)
            if time.time() - cache_time > self.ttl_seconds:
                os.remove(cache_file)  # Remove cache expirado
                logger.info(f"Cache expirado removido: {cache_key[:8]}")
                return None

            logger.info(f"✅ Cache HIT - Economia de tokens: {cache_key[:8]}")
            return cached_data.get('response')

        except Exception as e:
            logger.error(f"Erro ao ler cache: {e}")
            return None

    def set(self, messages: list, model: str, temperature: float, response: Dict[str, Any], context: Optional[Dict] = None):
        """
        Armazena resposta no cache

        Args:
            messages: Lista de mensagens
            model: Nome do modelo
            temperature: Temperatura
            response: Resposta a ser cacheada
            context: Contexto adicional (intent, tipo, etc.)
        """
        cache_key = self._generate_key(messages, model, temperature, context)
        cache_file = os.path.join(self.cache_dir, f"{cache_key}.json")

        try:
            cache_data = {
                'timestamp': time.time(),
                'response': response,
                'metadata': {
                    'version': CACHE_VERSION,  # 🔥 NOVO: Armazenar versão
                    'model': model,
                    'temperature': temperature,
                    'query_hash': cache_key,
                    'context': context or {}  # 🔥 NOVO: Armazenar contexto
                }
            }

            with open(cache_file, 'w', encoding='utf-8') as f:
                json.dump(cache_data, f, ensure_ascii=False, indent=2)

            logger.info(f"💾 Resposta cacheada: {cache_key[:8]} (v{CACHE_VERSION})")

        except Exception as e:
            logger.error(f"Erro ao salvar cache: {e}")

    def clear_expired(self):
        """Remove todos os caches expirados"""
        if not os.path.exists(self.cache_dir):
            return

        removed_count = 0
        for filename in os.listdir(self.cache_dir):
            if filename.endswith('.json'):
                cache_file = os.path.join(self.cache_dir, filename)
                try:
                    with open(cache_file, 'r', encoding='utf-8') as f:
                        cached_data = json.load(f)

                    cache_time = cached_data.get('timestamp', 0)
                    if time.time() - cache_time > self.ttl_seconds:
                        os.remove(cache_file)
                        removed_count += 1

                except Exception:
                    # Remove arquivos corrompidos
                    os.remove(cache_file)
                    removed_count += 1

        if removed_count > 0:
            logger.info(f"[INFO] Limpeza: {removed_count} caches expirados removidos")

    def get_stats(self) -> Dict[str, Any]:
        """Retorna estatísticas do cache"""
        if not os.path.exists(self.cache_dir):
            return {"total_files": 0, "total_size_mb": 0}

        total_files = len([f for f in os.listdir(self.cache_dir) if f.endswith('.json')])
        total_size = sum(
            os.path.getsize(os.path.join(self.cache_dir, f))
            for f in os.listdir(self.cache_dir)
            if f.endswith('.json')
        )

        return {
            "total_files": total_files,
            "total_size_mb": round(total_size / (1024 * 1024), 2),
            "ttl_hours": self.ttl_seconds / 3600
        }
