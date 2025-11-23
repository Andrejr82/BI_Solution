"""
Teste A/B: Gemini 2.5 Pro vs Gemini 2.5 Flash
Compara qualidade e velocidade de geração de código para queries de BI
"""

import os
import sys
import time
import json
from datetime import datetime
from dotenv import load_dotenv

# Adicionar path do projeto
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

load_dotenv()

# Queries de teste representativas do uso real
TEST_QUERIES = [
    {
        "name": "Top 10 Produtos",
        "query": "Mostre os top 10 produtos mais vendidos",
        "complexity": "simples"
    },
    {
        "name": "Ranking por UNE",
        "query": "Ranking de vendas por UNE",
        "complexity": "simples"
    },
    {
        "name": "Filtro Específico",
        "query": "Vendas da loja 261 nos últimos 3 meses",
        "complexity": "média"
    },
    {
        "name": "Múltiplas Lojas",
        "query": "Comparar vendas das lojas bar, 261 e scr",
        "complexity": "média"
    },
    {
        "name": "Análise por Segmento",
        "query": "Top 10 produtos do segmento TECIDOS com gráfico de barras",
        "complexity": "média"
    },
    {
        "name": "Evolução Temporal",
        "query": "Evolução de vendas dos últimos 12 meses com gráfico de linha",
        "complexity": "complexa"
    },
    {
        "name": "Análise ABC",
        "query": "Análise ABC de produtos com classificação A, B e C",
        "complexity": "complexa"
    }
]

def test_model(model_name: str, query: str) -> dict:
    """Testa um modelo específico com uma query"""
    try:
        from core.factory.component_factory import ComponentFactory
        from core.agents.code_gen_agent import CodeGenAgent
        from core.connectivity.parquet_adapter import ParquetAdapter
        
        # Inicializar componentes
        llm_adapter = ComponentFactory.get_llm_adapter_by_model(model_name=model_name, temperature=0.2)
        data_adapter = ParquetAdapter()
        code_gen_agent = CodeGenAgent(llm_adapter=llm_adapter, data_adapter=data_adapter)
        
        # Medir tempo
        start_time = time.time()
        
        # Gerar código
        result = code_gen_agent.generate_analysis_code(query)
        
        elapsed_time = time.time() - start_time
        
        # Avaliar resultado
        success = result.get("success", False)
        code = result.get("code", "")
        error = result.get("error", "")
        
        # Métricas de qualidade
        has_imports = "import pandas" in code or "import plotly" in code
        has_data_load = "parquet" in code.lower() or "read_" in code
        has_visualization = "px." in code or "go." in code or "fig" in code
        has_error_handling = "try:" in code or "except" in code
        
        quality_score = sum([
            success * 40,  # Sucesso é fundamental
            has_imports * 15,
            has_data_load * 15,
            has_visualization * 15,
            has_error_handling * 15
        ])
        
        return {
            "success": success,
            "time": round(elapsed_time, 2),
            "quality_score": quality_score,
            "code_length": len(code),
            "has_error": bool(error),
            "error_msg": error[:100] if error else None,
            "metrics": {
                "has_imports": has_imports,
                "has_data_load": has_data_load,
                "has_visualization": has_visualization,
                "has_error_handling": has_error_handling
            }
        }
        
    except Exception as e:
        return {
            "success": False,
            "time": 0,
            "quality_score": 0,
            "code_length": 0,
            "has_error": True,
            "error_msg": str(e)[:100],
            "metrics": {}
        }

def run_comparison():
    """Executa comparação completa entre os modelos"""
    
    print("=" * 80)
    print("🔬 TESTE A/B: Gemini 2.5 Pro vs Gemini 2.5 Flash")
    print("=" * 80)
    print()
    
    models = {
        "Gemini 2.5 Pro": "models/gemini-2.5-pro",
        "Gemini 2.5 Flash": "models/gemini-2.5-flash"
    }
    
    results = {model: [] for model in models.keys()}
    
    # Testar cada query com cada modelo
    for i, test_case in enumerate(TEST_QUERIES, 1):
        print(f"\n📊 Teste {i}/{len(TEST_QUERIES)}: {test_case['name']} ({test_case['complexity']})")
        print(f"   Query: \"{test_case['query']}\"")
        print()
        
        for model_label, model_name in models.items():
            print(f"   🤖 Testando {model_label}...", end=" ")
            
            result = test_model(model_name, test_case['query'])
            results[model_label].append({
                "test_name": test_case['name'],
                "complexity": test_case['complexity'],
                **result
            })
            
            # Feedback visual
            status = "✅" if result['success'] else "❌"
            print(f"{status} {result['time']}s (qualidade: {result['quality_score']}/100)")
        
        # Pequena pausa entre queries
        time.sleep(1)
    
    # Análise comparativa
    print("\n" + "=" * 80)
    print("📈 RESULTADOS COMPARATIVOS")
    print("=" * 80)
    
    for model_label in models.keys():
        model_results = results[model_label]
        
        total_tests = len(model_results)
        successful = sum(1 for r in model_results if r['success'])
        avg_time = sum(r['time'] for r in model_results) / total_tests
        avg_quality = sum(r['quality_score'] for r in model_results) / total_tests
        
        print(f"\n🤖 {model_label}")
        print(f"   Taxa de Sucesso: {successful}/{total_tests} ({successful/total_tests*100:.1f}%)")
        print(f"   Tempo Médio: {avg_time:.2f}s")
        print(f"   Qualidade Média: {avg_quality:.1f}/100")
        
        # Análise por complexidade
        for complexity in ["simples", "média", "complexa"]:
            complex_results = [r for r in model_results if r['complexity'] == complexity]
            if complex_results:
                complex_success = sum(1 for r in complex_results if r['success'])
                complex_avg_time = sum(r['time'] for r in complex_results) / len(complex_results)
                complex_avg_quality = sum(r['quality_score'] for r in complex_results) / len(complex_results)
                
                print(f"   └─ {complexity.capitalize()}: {complex_success}/{len(complex_results)} sucesso, "
                      f"{complex_avg_time:.2f}s, qualidade {complex_avg_quality:.1f}/100")
    
    # Comparação direta
    print("\n" + "=" * 80)
    print("🏆 VENCEDOR POR CATEGORIA")
    print("=" * 80)
    
    pro_results = results["Gemini 2.5 Pro"]
    flash_results = results["Gemini 2.5 Flash"]
    
    # Velocidade
    pro_avg_time = sum(r['time'] for r in pro_results) / len(pro_results)
    flash_avg_time = sum(r['time'] for r in flash_results) / len(flash_results)
    speed_winner = "Flash" if flash_avg_time < pro_avg_time else "Pro"
    speed_diff = abs(pro_avg_time - flash_avg_time) / max(pro_avg_time, flash_avg_time) * 100
    
    print(f"\n⚡ Velocidade: {speed_winner} ({speed_diff:.1f}% mais rápido)")
    print(f"   Pro: {pro_avg_time:.2f}s | Flash: {flash_avg_time:.2f}s")
    
    # Qualidade
    pro_avg_quality = sum(r['quality_score'] for r in pro_results) / len(pro_results)
    flash_avg_quality = sum(r['quality_score'] for r in flash_results) / len(flash_results)
    quality_winner = "Pro" if pro_avg_quality > flash_avg_quality else "Flash"
    quality_diff = abs(pro_avg_quality - flash_avg_quality)
    
    print(f"\n🎯 Qualidade: {quality_winner} (+{quality_diff:.1f} pontos)")
    print(f"   Pro: {pro_avg_quality:.1f}/100 | Flash: {flash_avg_quality:.1f}/100")
    
    # Taxa de sucesso
    pro_success_rate = sum(1 for r in pro_results if r['success']) / len(pro_results) * 100
    flash_success_rate = sum(1 for r in flash_results if r['success']) / len(flash_results) * 100
    success_winner = "Pro" if pro_success_rate > flash_success_rate else "Flash"
    
    print(f"\n✅ Taxa de Sucesso: {success_winner}")
    print(f"   Pro: {pro_success_rate:.1f}% | Flash: {flash_success_rate:.1f}%")
    
    # Recomendação final
    print("\n" + "=" * 80)
    print("💡 RECOMENDAÇÃO")
    print("=" * 80)
    
    # Calcular score ponderado (velocidade 40%, qualidade 40%, sucesso 20%)
    pro_score = (100 - (pro_avg_time / flash_avg_time * 100 - 100)) * 0.4 + pro_avg_quality * 0.4 + pro_success_rate * 0.2
    flash_score = (100 - (flash_avg_time / pro_avg_time * 100 - 100)) * 0.4 + flash_avg_quality * 0.4 + flash_success_rate * 0.2
    
    if flash_score > pro_score and flash_avg_quality >= 80:
        print("\n🚀 RECOMENDADO: Gemini 2.5 Flash")
        print(f"   • {speed_diff:.1f}% mais rápido")
        print(f"   • Qualidade suficiente ({flash_avg_quality:.1f}/100)")
        print(f"   • Custo ~80% menor")
        print(f"   • Melhor experiência do usuário (respostas mais rápidas)")
    elif pro_avg_quality - flash_avg_quality > 15:
        print("\n🎯 RECOMENDADO: Gemini 2.5 Pro")
        print(f"   • Qualidade superior (+{quality_diff:.1f} pontos)")
        print(f"   • Maior taxa de sucesso ({pro_success_rate:.1f}%)")
        print(f"   • Vale a pena o tempo extra para análises complexas")
    else:
        print("\n⚖️ EMPATE TÉCNICO")
        print("   • Pro: Melhor qualidade, mais lento")
        print("   • Flash: Mais rápido, qualidade aceitável")
        print("   • Sugestão: Use Flash para queries simples/médias, Pro para complexas")
    
    # Salvar resultados
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = f"model_comparison_{timestamp}.json"
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump({
            "timestamp": timestamp,
            "models": models,
            "results": results,
            "summary": {
                "pro": {
                    "avg_time": pro_avg_time,
                    "avg_quality": pro_avg_quality,
                    "success_rate": pro_success_rate
                },
                "flash": {
                    "avg_time": flash_avg_time,
                    "avg_quality": flash_avg_quality,
                    "success_rate": flash_success_rate
                }
            }
        }, f, indent=2, ensure_ascii=False)
    
    print(f"\n📁 Resultados salvos em: {output_file}")
    print()

if __name__ == "__main__":
    try:
        run_comparison()
    except KeyboardInterrupt:
        print("\n\n⚠️ Teste interrompido pelo usuário")
    except Exception as e:
        print(f"\n\n❌ Erro durante teste: {e}")
        import traceback
        traceback.print_exc()
