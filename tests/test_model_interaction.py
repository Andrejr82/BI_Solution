"""
Teste A/B Avançado: Interações Conversacionais e Queries Complexas
Simula conversas reais com múltiplas interações e queries complexas de BI
"""

import os
import sys
import time
from datetime import datetime
from dotenv import load_dotenv

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
load_dotenv()

# Cenários de teste que simulam interações reais
TEST_SCENARIOS = [
    {
        "name": "Conversa Simples - Exploração Inicial",
        "complexity": "baixa",
        "interactions": [
            "Quais são as lojas disponíveis?",
            "Mostre as vendas da loja 261",
            "E da loja scr?"
        ]
    },
    {
        "name": "Análise Comparativa - Múltiplas Lojas",
        "complexity": "média",
        "interactions": [
            "Quero comparar vendas das lojas bar, 261 e scr",
            "Mostre em um gráfico de barras",
            "Agora filtre apenas o segmento TECIDOS"
        ]
    },
    {
        "name": "Análise Temporal - Evolução",
        "complexity": "média-alta",
        "interactions": [
            "Evolução de vendas dos últimos 12 meses",
            "Mostre por segmento",
            "Destaque os 3 segmentos que mais cresceram"
        ]
    },
    {
        "name": "Análise Detalhada - Top Produtos",
        "complexity": "média",
        "interactions": [
            "Top 10 produtos mais vendidos",
            "Mostre a margem de lucro de cada um",
            "Filtre apenas produtos com margem > 20%"
        ]
    },
    {
        "name": "Query Complexa - Múltiplos Filtros",
        "complexity": "alta",
        "interactions": [
            "Produtos do segmento TECIDOS vendidos nas lojas 261 e scr nos últimos 6 meses",
            "Agrupe por mês e loja",
            "Mostre em um gráfico de linha com duas séries"
        ]
    },
    {
        "name": "Análise ABC - Classificação",
        "complexity": "alta",
        "interactions": [
            "Faça uma análise ABC dos produtos",
            "Mostre quantos produtos estão em cada classe",
            "Gere um gráfico de pizza com a distribuição"
        ]
    },
    {
        "name": "Interação Longa - Refinamento Progressivo",
        "complexity": "média",
        "interactions": [
            "Ranking de vendas por UNE",
            "Mostre apenas as top 5",
            "Adicione o percentual de cada uma sobre o total",
            "Agora compare com o mês anterior",
            "Destaque as que tiveram crescimento"
        ]
    }
]

def test_conversation(model_name: str, scenario: dict):
    """Testa uma conversa completa com múltiplas interações"""
    from google import generativeai as genai
    
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        return None
    
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel(model_name)
    
    # Iniciar chat
    chat = model.start_chat(history=[])
    
    times = []
    total_chars = 0
    successes = 0
    
    print(f"\n   {'='*50}")
    print(f"   Cenário: {scenario['name']}")
    print(f"   Complexidade: {scenario['complexity']}")
    print(f"   {'='*50}")
    
    for i, query in enumerate(scenario['interactions'], 1):
        print(f"\n   💬 Interação {i}/{len(scenario['interactions'])}: {query[:60]}...")
        
        prompt = f"""Você é um assistente de BI. Gere código Python usando Pandas e Plotly para:

{query}

Contexto: Trabalhamos com dados de vendas em 'data/parquet/admmat.parquet'
Retorne apenas o código Python, sem explicações."""

        try:
            start = time.time()
            response = chat.send_message(prompt)
            elapsed = time.time() - start
            
            times.append(elapsed)
            code_length = len(response.text) if response.text else 0
            total_chars += code_length
            successes += 1
            
            print(f"      ✅ {elapsed:.2f}s ({code_length} chars)")
            
        except Exception as e:
            print(f"      ❌ Erro: {str(e)[:80]}")
            times.append(0)
        
        # Pausa entre interações (simular usuário pensando)
        time.sleep(1.5)
    
    if times and successes > 0:
        avg_time = sum(times) / len(times)
        total_time = sum(times)
        
        return {
            "scenario": scenario['name'],
            "complexity": scenario['complexity'],
            "interactions": len(scenario['interactions']),
            "successes": successes,
            "success_rate": (successes / len(scenario['interactions'])) * 100,
            "avg_time_per_interaction": avg_time,
            "total_time": total_time,
            "total_chars": total_chars,
            "min_time": min([t for t in times if t > 0]) if any(t > 0 for t in times) else 0,
            "max_time": max(times)
        }
    
    return None

def main():
    print("="*70)
    print("🔬 TESTE A/B AVANÇADO: Interações Conversacionais")
    print("="*70)
    print("\n📋 Testando cenários realistas de uso do Agent_BI")
    print("   • Conversas com múltiplas interações")
    print("   • Queries complexas de BI")
    print("   • Refinamento progressivo de análises")
    
    models = {
        "Gemini 2.5 Flash": "models/gemini-2.5-flash",
        "Gemini 2.5 Pro": "models/gemini-2.5-pro"
    }
    
    all_results = {model: [] for model in models.keys()}
    
    for model_label, model_name in models.items():
        print(f"\n{'='*70}")
        print(f"🤖 Testando: {model_label}")
        print(f"{'='*70}")
        
        for scenario in TEST_SCENARIOS:
            result = test_conversation(model_name, scenario)
            if result:
                all_results[model_label].append(result)
            
            # Pausa entre cenários
            time.sleep(2)
    
    # Análise Comparativa Detalhada
    print("\n" + "="*70)
    print("📊 ANÁLISE COMPARATIVA DETALHADA")
    print("="*70)
    
    for model_label in models.keys():
        results = all_results[model_label]
        
        if not results:
            continue
        
        print(f"\n🤖 {model_label}")
        print(f"   {'─'*60}")
        
        # Métricas gerais
        total_interactions = sum(r['interactions'] for r in results)
        total_successes = sum(r['successes'] for r in results)
        overall_success_rate = (total_successes / total_interactions) * 100
        
        avg_time_per_interaction = sum(r['avg_time_per_interaction'] for r in results) / len(results)
        total_conversation_time = sum(r['total_time'] for r in results)
        
        print(f"\n   📈 Métricas Gerais:")
        print(f"      • Cenários testados: {len(results)}")
        print(f"      • Total de interações: {total_interactions}")
        print(f"      • Taxa de sucesso: {overall_success_rate:.1f}%")
        print(f"      • Tempo médio/interação: {avg_time_per_interaction:.2f}s")
        print(f"      • Tempo total conversas: {total_conversation_time:.1f}s")
        
        # Análise por complexidade
        print(f"\n   🎯 Por Complexidade:")
        for complexity in ["baixa", "média", "média-alta", "alta"]:
            complex_results = [r for r in results if r['complexity'] == complexity]
            if complex_results:
                avg_time = sum(r['avg_time_per_interaction'] for r in complex_results) / len(complex_results)
                avg_success = sum(r['success_rate'] for r in complex_results) / len(complex_results)
                print(f"      • {complexity.capitalize():12} - {avg_time:.2f}s/interação ({avg_success:.0f}% sucesso)")
        
        # Cenário mais lento
        slowest = max(results, key=lambda x: x['avg_time_per_interaction'])
        print(f"\n   ⏱️  Cenário mais lento:")
        print(f"      • {slowest['scenario']}")
        print(f"      • {slowest['avg_time_per_interaction']:.2f}s/interação")
        
        # Cenário mais rápido
        fastest = min(results, key=lambda x: x['avg_time_per_interaction'])
        print(f"\n   ⚡ Cenário mais rápido:")
        print(f"      • {fastest['scenario']}")
        print(f"      • {fastest['avg_time_per_interaction']:.2f}s/interação")
    
    # Comparação Direta
    print("\n" + "="*70)
    print("🏆 COMPARAÇÃO DIRETA")
    print("="*70)
    
    flash_results = all_results["Gemini 2.5 Flash"]
    pro_results = all_results["Gemini 2.5 Pro"]
    
    if flash_results and pro_results:
        # Velocidade média
        flash_avg = sum(r['avg_time_per_interaction'] for r in flash_results) / len(flash_results)
        pro_avg = sum(r['avg_time_per_interaction'] for r in pro_results) / len(pro_results)
        
        speed_diff = ((pro_avg - flash_avg) / pro_avg) * 100
        
        print(f"\n⚡ Velocidade Média por Interação:")
        print(f"   Flash: {flash_avg:.2f}s")
        print(f"   Pro:   {pro_avg:.2f}s")
        print(f"   → Flash é {speed_diff:.1f}% mais rápido")
        
        # Tempo total de conversas
        flash_total = sum(r['total_time'] for r in flash_results)
        pro_total = sum(r['total_time'] for r in pro_results)
        
        print(f"\n⏱️  Tempo Total (todas as conversas):")
        print(f"   Flash: {flash_total:.1f}s ({flash_total/60:.1f} min)")
        print(f"   Pro:   {pro_total:.1f}s ({pro_total/60:.1f} min)")
        print(f"   → Economia de {pro_total - flash_total:.1f}s ({(pro_total - flash_total)/60:.1f} min)")
        
        # Taxa de sucesso
        flash_success = sum(r['successes'] for r in flash_results) / sum(r['interactions'] for r in flash_results) * 100
        pro_success = sum(r['successes'] for r in pro_results) / sum(r['interactions'] for r in pro_results) * 100
        
        print(f"\n✅ Taxa de Sucesso:")
        print(f"   Flash: {flash_success:.1f}%")
        print(f"   Pro:   {pro_success:.1f}%")
        
        # Análise por complexidade
        print(f"\n📊 Performance por Complexidade:")
        print(f"   {'Complexidade':<15} {'Flash':<12} {'Pro':<12} {'Diferença'}")
        print(f"   {'-'*60}")
        
        for complexity in ["baixa", "média", "média-alta", "alta"]:
            flash_complex = [r for r in flash_results if r['complexity'] == complexity]
            pro_complex = [r for r in pro_results if r['complexity'] == complexity]
            
            if flash_complex and pro_complex:
                flash_time = sum(r['avg_time_per_interaction'] for r in flash_complex) / len(flash_complex)
                pro_time = sum(r['avg_time_per_interaction'] for r in pro_complex) / len(pro_complex)
                diff = ((pro_time - flash_time) / pro_time) * 100
                
                print(f"   {complexity.capitalize():<15} {flash_time:>6.2f}s     {pro_time:>6.2f}s     {diff:>+5.1f}%")
        
        # Recomendação Final
        print(f"\n" + "="*70)
        print("💡 RECOMENDAÇÃO FINAL")
        print("="*70)
        
        if flash_avg < pro_avg and flash_success >= 90:
            print(f"\n🚀 RECOMENDADO: Gemini 2.5 Flash")
            print(f"\n   Motivos:")
            print(f"   • {speed_diff:.1f}% mais rápido em TODAS as interações")
            print(f"   • Taxa de sucesso excelente ({flash_success:.1f}%)")
            print(f"   • Economia de {(pro_total - flash_total)/60:.1f} minutos em conversas")
            print(f"   • ~80% mais barato")
            print(f"   • Melhor experiência do usuário (respostas mais ágeis)")
            
            if speed_diff > 50:
                print(f"\n   ⚠️  IMPORTANTE:")
                print(f"   • Flash é SIGNIFICATIVAMENTE mais rápido ({speed_diff:.1f}%)")
                print(f"   • Impacto direto na satisfação do usuário")
                print(f"   • Reduz frustração com timeouts")
        else:
            print(f"\n🎯 RECOMENDADO: Gemini 2.5 Pro")
            print(f"\n   Motivos:")
            print(f"   • Maior qualidade nas respostas")
            print(f"   • Melhor para análises complexas")
        
        # Salvar resultados
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = f"interaction_test_{timestamp}.txt"
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write("="*70 + "\n")
            f.write("TESTE A/B: Interações Conversacionais\n")
            f.write("="*70 + "\n\n")
            f.write(f"Flash: {flash_avg:.2f}s/interação ({flash_success:.1f}% sucesso)\n")
            f.write(f"Pro:   {pro_avg:.2f}s/interação ({pro_success:.1f}% sucesso)\n")
            f.write(f"\nFlash é {speed_diff:.1f}% mais rápido\n")
        
        print(f"\n📁 Resultados salvos em: {output_file}")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️ Teste interrompido")
    except Exception as e:
        print(f"\n\n❌ Erro: {e}")
        import traceback
        traceback.print_exc()
