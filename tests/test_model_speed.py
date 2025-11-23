"""
Teste A/B Simplificado: Gemini 2.5 Pro vs Gemini 2.5 Flash
Compara velocidade de geração de código para queries de BI
"""

import os
import sys
import time
from datetime import datetime
from dotenv import load_dotenv

# Adicionar path do projeto
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

load_dotenv()

# Queries de teste representativas
TEST_QUERIES = [
    "Mostre os top 10 produtos mais vendidos",
    "Ranking de vendas por UNE",
    "Vendas da loja 261",
    "Top 10 produtos do segmento TECIDOS"
]

def test_single_model(model_name: str):
    """Testa um modelo com queries simples"""
    print(f"\n{'='*60}")
    print(f"🤖 Testando: {model_name}")
    print(f"{'='*60}")
    
    from google import generativeai as genai
    
    # Configurar API
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("❌ GEMINI_API_KEY não encontrada")
        return None
    
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel(model_name)
    
    times = []
    successes = 0
    
    for i, query in enumerate(TEST_QUERIES, 1):
        print(f"\n📊 Teste {i}/{len(TEST_QUERIES)}: {query[:50]}...")
        
        prompt = f"""Você é um assistente de BI. Gere código Python usando Pandas e Plotly para:

Query: {query}

Retorne apenas o código Python, sem explicações.
Use dados de um arquivo parquet em 'data/parquet/admmat.parquet'."""

        try:
            start = time.time()
            response = model.generate_content(prompt)
            elapsed = time.time() - start
            
            times.append(elapsed)
            successes += 1
            
            code_length = len(response.text) if response.text else 0
            print(f"   ✅ {elapsed:.2f}s ({code_length} chars)")
            
        except Exception as e:
            print(f"   ❌ Erro: {str(e)[:100]}")
        
        # Pausa entre requests
        time.sleep(2)
    
    if times:
        avg_time = sum(times) / len(times)
        min_time = min(times)
        max_time = max(times)
        
        print(f"\n📈 Resumo:")
        print(f"   Sucesso: {successes}/{len(TEST_QUERIES)} ({successes/len(TEST_QUERIES)*100:.0f}%)")
        print(f"   Tempo Médio: {avg_time:.2f}s")
        print(f"   Tempo Min: {min_time:.2f}s")
        print(f"   Tempo Max: {max_time:.2f}s")
        
        return {
            "model": model_name,
            "success_rate": successes/len(TEST_QUERIES)*100,
            "avg_time": avg_time,
            "min_time": min_time,
            "max_time": max_time
        }
    
    return None

def main():
    print("="*60)
    print("🔬 TESTE A/B: Gemini 2.5 Pro vs Flash")
    print("="*60)
    
    models = [
        "models/gemini-2.5-flash",
        "models/gemini-2.5-pro"
    ]
    
    results = []
    
    for model in models:
        result = test_single_model(model)
        if result:
            results.append(result)
    
    # Comparação final
    if len(results) == 2:
        print("\n" + "="*60)
        print("🏆 COMPARAÇÃO FINAL")
        print("="*60)
        
        flash = results[0]
        pro = results[1]
        
        print(f"\n⚡ Velocidade:")
        print(f"   Flash: {flash['avg_time']:.2f}s")
        print(f"   Pro:   {pro['avg_time']:.2f}s")
        
        if flash['avg_time'] < pro['avg_time']:
            diff = ((pro['avg_time'] - flash['avg_time']) / pro['avg_time']) * 100
            print(f"   → Flash é {diff:.1f}% mais rápido! ✅")
        else:
            diff = ((flash['avg_time'] - pro['avg_time']) / flash['avg_time']) * 100
            print(f"   → Pro é {diff:.1f}% mais rápido! ✅")
        
        print(f"\n✅ Taxa de Sucesso:")
        print(f"   Flash: {flash['success_rate']:.0f}%")
        print(f"   Pro:   {pro['success_rate']:.0f}%")
        
        print(f"\n💡 Recomendação:")
        if flash['avg_time'] < pro['avg_time'] and flash['success_rate'] >= 75:
            print("   🚀 Use Gemini 2.5 Flash!")
            print("   • Mais rápido")
            print("   • Taxa de sucesso aceitável")
            print("   • ~80% mais barato")
        else:
            print("   🎯 Use Gemini 2.5 Pro")
            print("   • Maior qualidade")
            print("   • Melhor para análises complexas")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️ Teste interrompido")
    except Exception as e:
        print(f"\n\n❌ Erro: {e}")
        import traceback
        traceback.print_exc()
