"""
Validação Crítica: Dados Repetidos/Mockados
Testa 5 perguntas diferentes para garantir respostas únicas.
"""
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

# Carregar .env
from pathlib import Path
env_path = Path(__file__).parent.parent / '.env'
if env_path.exists():
    with open(env_path, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                key, value = line.split('=', 1)
                os.environ[key.strip()] = value.strip().strip('"')

from core.connectivity.hybrid_adapter import HybridDataAdapter
from core.business_intelligence.direct_query_engine import DirectQueryEngine

print("\n" + "="*70)
print("VALIDACAO: DADOS REPETIDOS/MOCKADOS")
print("="*70 + "\n")

# Inicializar
adapter = HybridDataAdapter()
engine = DirectQueryEngine(adapter)

status = adapter.get_status()
print(f"Fonte de dados: {status['current_source'].upper()}\n")

# 5 perguntas MUITO diferentes
perguntas = [
    "produto mais vendido",
    "ranking de unes por vendas",
    "top 5 produtos do segmento TECIDOS",
    "produtos sem movimento",
    "vendas totais da une 2720"
]

resultados = []

for i, pergunta in enumerate(perguntas, 1):
    print(f"{i}. Testando: '{pergunta}'")

    try:
        result = engine.process_query(pergunta)

        # Extrair dados relevantes
        query_type = result.get('query_type', 'N/A')
        resultado_str = str(result.get('result', {}))[:200]

        resultados.append({
            'pergunta': pergunta,
            'query_type': query_type,
            'resultado': resultado_str,
            'sucesso': result.get('type') != 'error'
        })

        print(f"   Query Type: {query_type}")
        print(f"   Resultado: {resultado_str[:100]}...")
        print(f"   Status: {'OK' if resultados[-1]['sucesso'] else 'ERRO'}\n")

    except Exception as e:
        print(f"   [ERRO] {e}\n")
        resultados.append({'pergunta': pergunta, 'erro': str(e)})

# VALIDAÇÃO CRÍTICA
print("="*70)
print("ANALISE DE DADOS REPETIDOS")
print("="*70 + "\n")

# Verificar se todos os query_types são diferentes
query_types = [r.get('query_type') for r in resultados if 'query_type' in r]
query_types_unicos = set(query_types)

print(f"Query types retornados: {len(query_types)}")
print(f"Query types unicos: {len(query_types_unicos)}")

if len(query_types_unicos) < len(query_types):
    print("\n[AVISO] Algumas perguntas retornaram mesmo query_type!")
    print(f"Types: {query_types}")

# Verificar se resultados são diferentes
resultados_str = [r.get('resultado', '') for r in resultados]
resultados_unicos = set(resultados_str)

print(f"\nResultados diferentes: {len(resultados_unicos)}")

# DIAGNÓSTICO
print("\n" + "="*70)

if len(resultados_unicos) >= 4:  # Pelo menos 4 de 5 diferentes
    print("RESULTADO: OK - Dados NAO estao mockados/repetidos")
    print("Sistema retorna respostas DIFERENTES para perguntas DIFERENTES")
    print("="*70 + "\n")
    sys.exit(0)
else:
    print("RESULTADO: PROBLEMA DETECTADO - Dados repetidos/mockados")
    print("Sistema retorna respostas IGUAIS para perguntas DIFERENTES")
    print("\nPOSSIVEIS CAUSAS:")
    print("1. Cache retornando sempre mesma amostra")
    print("2. DirectQueryEngine carregando dados limitados")
    print("3. Adapter retornando sempre mesmos 500 registros")
    print("="*70 + "\n")
    sys.exit(1)
