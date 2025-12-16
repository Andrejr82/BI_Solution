"""Diagnostico Simplificado"""
import sys, os
os.environ['PYTHONIOENCODING'] = 'utf-8'
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

output = []
def log(msg):
    print(msg)
    output.append(msg)

log("=" * 60)
log("DIAGNOSTICO")
log("=" * 60)

try:
    log("\n[1] Testando ferramenta...")
    from app.core.tools.flexible_query_tool import consultar_dados_flexivel
    
    log(f"Tipo: {type(consultar_dados_flexivel)}")
    
    resultado = consultar_dados_flexivel.invoke({
        "filtros": {"une": "2365"},
        "ordenar_por": "venda_30dd",
        "ordem_desc": True,
        "limite": 10
    })
    
    log(f"Resultado tipo: {type(resultado)}")
    if isinstance(resultado, dict):
        log(f"Keys: {list(resultado.keys())}")
        log(f"Total: {resultado.get('total_resultados', 'N/A')}")
        mensagem = str(resultado.get('mensagem', ''))
        log(f"Mensagem ({len(mensagem)} chars):")
        log(mensagem[:1500])
    else:
        log(f"Resultado: {resultado}")
        
except Exception as e:
    log(f"ERRO ferramenta: {e}")
    import traceback
    log(traceback.format_exc())

log("\n" + "=" * 60)

try:
    log("\n[2] Testando agente...")
    from app.core.agents.caculinha_bi_agent import CaculinhaBIAgent
    
    agent = CaculinhaBIAgent()
    log("Agente OK")
    
    log("\n[3] Query: top 10 vendas une 2365")
    resultado = agent.run(user_query="top 10 vendas une 2365", chat_history=[])
    
    log(f"\n[4] Resultado:")
    log(f"Tipo: {type(resultado)}")
    if isinstance(resultado, dict):
        log(f"type: {resultado.get('type')}")
        result_str = str(resultado.get('result', ''))
        log(f"Result ({len(result_str)} chars):")
        log(result_str[:2000])
    else:
        log(f"Raw: {resultado}")
        
except Exception as e:
    log(f"ERRO agente: {e}")
    import traceback
    log(traceback.format_exc())

log("\n" + "=" * 60)

# Salvar em arquivo
with open('diagnostico_output.txt', 'w', encoding='utf-8') as f:
    f.write('\n'.join(output))
log("Salvo em diagnostico_output.txt")
