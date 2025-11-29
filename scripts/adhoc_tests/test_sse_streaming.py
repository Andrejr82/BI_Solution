#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para testar SSE Streaming do ChatBI com Agente Real
"""
import requests
import json
import time
import sys
import io

# Fix Windows console encoding
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# Configurações
API_URL = "http://127.0.0.1:8000"
TEST_CREDENTIALS = {
    "username": "admin",
    "password": "Admin@2024"
}

def login():
    """Fazer login e obter token JWT"""
    print("🔐 Fazendo login...")
    try:
        response = requests.post(
            f"{API_URL}/api/v1/auth/login",
            data=TEST_CREDENTIALS
        )
        response.raise_for_status()
        data = response.json()
        token = data.get("access_token")
        print(f"✅ Login bem-sucedido! Token: {token[:20]}...")
        return token
    except Exception as e:
        print(f"❌ Erro no login: {e}")
        sys.exit(1)

def test_sse_streaming(token, query):
    """Testar SSE streaming com o agente real"""
    print(f"\n{'='*80}")
    print(f"📨 Enviando query: '{query}'")
    print(f"{'='*80}\n")

    url = f"{API_URL}/api/v1/chat/stream"
    params = {
        "q": query,
        "token": token
    }

    print("🔄 Conectando ao SSE stream...")
    start_time = time.time()

    try:
        response = requests.get(url, params=params, stream=True, timeout=60)
        response.raise_for_status()

        print("✅ Conexão SSE estabelecida!\n")
        print("📡 Recebendo eventos:\n")
        print("-" * 80)

        event_count = 0
        full_text = ""
        first_chunk_time = None

        for line in response.iter_lines():
            if not line:
                continue

            line = line.decode('utf-8')

            # Parse SSE format
            if line.startswith("id:"):
                event_id = line[3:].strip()
            elif line.startswith("data:"):
                data_json = line[5:].strip()

                try:
                    data = json.loads(data_json)

                    if data.get("done"):
                        print("\n" + "-" * 80)
                        print("✅ Stream concluído!")
                        break

                    if data.get("error"):
                        print(f"\n❌ Erro: {data['error']}")
                        break

                    text = data.get("text", "")
                    if text:
                        event_count += 1
                        full_text += text

                        # Timing do primeiro chunk
                        if first_chunk_time is None:
                            first_chunk_time = time.time() - start_time
                            print(f"⚡ Primeiro chunk recebido em: {first_chunk_time:.2f}s\n")

                        # Mostrar em tempo real
                        print(text, end="", flush=True)

                except json.JSONDecodeError as e:
                    print(f"\n⚠️ Erro ao parsear JSON: {e}")
                    print(f"Data: {data_json}")

        total_time = time.time() - start_time

        print("\n" + "=" * 80)
        print("📊 ESTATÍSTICAS:")
        print(f"   • Total de eventos: {event_count}")
        print(f"   • Tempo total: {total_time:.2f}s")
        print(f"   • Primeiro chunk: {first_chunk_time:.2f}s" if first_chunk_time else "   • Primeiro chunk: N/A")
        print(f"   • Texto completo: {len(full_text)} caracteres")
        print("=" * 80)

    except requests.exceptions.Timeout:
        print("❌ Timeout: O agente demorou mais de 60s")
    except requests.exceptions.RequestException as e:
        print(f"❌ Erro na requisição: {e}")
    except KeyboardInterrupt:
        print("\n\n⚠️ Interrompido pelo usuário")

def main():
    print("""
    ==============================================================
             TESTE DE SSE STREAMING - AGENTE REAL
    ==============================================================
    """)

    # Login
    token = login()

    # Perguntas de teste
    test_queries = [
        "Olá, qual seu nome?",
        "Qual o lucro do produto 9?",
        "Mostre as vendas totais",
    ]

    for i, query in enumerate(test_queries, 1):
        print(f"\n\n🧪 TESTE {i}/{len(test_queries)}")
        test_sse_streaming(token, query)

        if i < len(test_queries):
            print("\n⏳ Aguardando 3 segundos antes do próximo teste...")
            time.sleep(3)

    print("\n\n✅ Todos os testes concluídos!")

if __name__ == "__main__":
    main()
