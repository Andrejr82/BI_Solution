#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Script simples para testar SSE Streaming do ChatBI"""
import requests
import json
import time
import sys

API_URL = "http://127.0.0.1:8000"

def login():
    print("[LOGIN] Fazendo login...")
    response = requests.post(
        f"{API_URL}/api/v1/auth/login",
        data={"username": "admin", "password": "Admin@2024"}
    )
    token = response.json().get("access_token")
    print(f"[LOGIN] Token obtido: {token[:20]}...")
    return token

def test_stream(token, query):
    print(f"\n{'='*80}")
    print(f"[QUERY] {query}")
    print(f"{'='*80}\n")

    url = f"{API_URL}/api/v1/chat/stream?q={query}&token={token}"

    print("[SSE] Conectando...")
    start = time.time()

    response = requests.get(url, stream=True, timeout=60)

    print("[SSE] Conectado! Recebendo eventos:\n")
    print("-" * 80)

    events = 0
    text = ""
    first = None

    for line in response.iter_lines():
        if not line:
            continue

        line = line.decode('utf-8')

        if line.startswith("data:"):
            data_json = line[5:].strip()

            try:
                data = json.loads(data_json)

                if data.get("done"):
                    print("\n" + "-" * 80)
                    break

                if data.get("error"):
                    print(f"\n[ERROR] {data['error']}")
                    break

                chunk = data.get("text", "")
                if chunk:
                    events += 1
                    text += chunk

                    if first is None:
                        first = time.time() - start
                        print(f"[TIMING] Primeiro chunk: {first:.2f}s\n")

                    print(chunk, end="", flush=True)

            except json.JSONDecodeError as e:
                print(f"\n[ERROR] JSON: {e}")

    total = time.time() - start

    print("\n" + "=" * 80)
    print(f"[STATS] Eventos: {events} | Total: {total:.2f}s | Primeiro: {first:.2f}s" if first else "")
    print(f"[STATS] Caracteres: {len(text)}")
    print("=" * 80)

if __name__ == "__main__":
    print("\n" + "=" * 80)
    print("TESTE DE SSE STREAMING - AGENTE REAL")
    print("=" * 80)

    token = login()

    # Teste simples
    test_stream(token, "Ola, qual seu nome?")

    time.sleep(2)

    # Teste com agente
    test_stream(token, "Qual o lucro do produto 9?")

    print("\n[DONE] Testes concluidos!")
