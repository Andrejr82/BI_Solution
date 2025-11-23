"""
Teste de Validação: Migração para Gemini 2.5 Flash
Valida que o sistema funciona corretamente após a migração
"""

import os
import sys
import time
from datetime import datetime

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from dotenv import load_dotenv
load_dotenv(override=True)  # Forçar reload do .env

# Queries de teste
TEST_QUERIES = [
    {
        "name": "Query Simples",
        "query": "Top 10 produtos mais vendidos",
        "expected_time": 15  # segundos
    },
    {
        "name": "Query com Filtro",
        "query": "Vendas da loja 261 nos últimos 3 meses",
        "expected_time": 15
    },
    {
        "name": "Query Complexa",
        "query": "Análise ABC de produtos com gráfico",
        "expected_time": 20
    },
    {
        "name": "Query Múltipla",
        "query": "Comparar vendas das lojas bar, 261 e scr",
        "expected_time": 15
    }
]

def validate_configuration():
    """Valida que a configuração foi atualizada corretamente"""
    print("\n" + "="*60)
    print("1️⃣  VALIDANDO CONFIGURAÇÃO")
    print("="*60)
    
    # Verificar variável de ambiente
    code_gen_model = os.getenv("CODE_GENERATION_MODEL")
    
    print(f"\n📋 CODE_GENERATION_MODEL: {code_gen_model}")
    
    if "flash" in code_gen_model.lower():
        print("✅ Configuração correta - usando Flash")
        return True
    else:
        print(f"❌ Configuração incorreta - esperado Flash, obtido {code_gen_model}")
        return False

def test_model_loading():
    """Testa se o modelo Flash carrega corretamente"""
    print("\n" + "="*60)
    print("2️⃣  TESTANDO CARREGAMENTO DO MODELO")
    print("="*60)
    
    try:
        from core.factory.component_factory import ComponentFactory
        
        # Carregar modelo Flash
        llm_adapter = ComponentFactory.get_code_generation_llm()
        
        if llm_adapter:
            model_name = getattr(llm_adapter, 'model_name', 'unknown')
            print(f"\n✅ Modelo carregado: {model_name}")
            
            if "flash" in model_name.lower():
                print("✅ Modelo correto - Flash")
                return True
            else:
                print(f"❌ Modelo incorreto - esperado Flash, obtido {model_name}")
                return False
        else:
            print("❌ Falha ao carregar modelo")
            return False
            
    except Exception as e:
        print(f"❌ Erro ao carregar modelo: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_code_generation():
    """Testa geração de código com queries reais"""
    print("\n" + "="*60)
    print("3️⃣  TESTANDO GERAÇÃO DE CÓDIGO")
    print("="*60)
    
    try:
        from core.factory.component_factory import ComponentFactory
        from core.agents.code_gen_agent import CodeGenAgent
        from core.connectivity.parquet_adapter import ParquetAdapter
        
        # Inicializar componentes
        llm_adapter = ComponentFactory.get_code_generation_llm()
        data_adapter = ParquetAdapter()
        code_gen_agent = CodeGenAgent(llm_adapter=llm_adapter, data_adapter=data_adapter)
        
        results = []
        
        for i, test in enumerate(TEST_QUERIES, 1):
            print(f"\n   📊 Teste {i}/{len(TEST_QUERIES)}: {test['name']}")
            print(f"      Query: \"{test['query']}\"")
            
            start = time.time()
            result = code_gen_agent.generate_analysis_code(test['query'])
            elapsed = time.time() - start
            
            success = result.get("success", False)
            code = result.get("code", "")
            
            # Validações
            has_code = len(code) > 100
            within_time = elapsed <= test['expected_time']
            has_imports = "import" in code
            
            status = "✅" if (success and has_code and within_time) else "❌"
            
            print(f"      {status} Tempo: {elapsed:.2f}s (limite: {test['expected_time']}s)")
            print(f"      {status} Código gerado: {len(code)} chars")
            print(f"      {status} Sucesso: {success}")
            
            results.append({
                "name": test['name'],
                "success": success and has_code and within_time,
                "time": elapsed
            })
            
            time.sleep(2)  # Pausa entre testes
        
        # Resumo
        print(f"\n   {'─'*56}")
        successes = sum(1 for r in results if r['success'])
        avg_time = sum(r['time'] for r in results) / len(results)
        
        print(f"   📈 Resumo:")
        print(f"      Taxa de sucesso: {successes}/{len(results)} ({successes/len(results)*100:.0f}%)")
        print(f"      Tempo médio: {avg_time:.2f}s")
        
        return successes == len(results)
        
    except Exception as e:
        print(f"\n   ❌ Erro durante testes: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    print("="*60)
    print("🧪 VALIDAÇÃO DA MIGRAÇÃO PARA FLASH")
    print("="*60)
    print(f"Data: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Executar validações
    config_ok = validate_configuration()
    
    if not config_ok:
        print("\n❌ FALHA: Configuração incorreta")
        print("   Execute o rollback: cp .env.backup_* .env")
        return False
    
    model_ok = test_model_loading()
    
    if not model_ok:
        print("\n❌ FALHA: Modelo não carregou corretamente")
        print("   Execute o rollback: cp .env.backup_* .env")
        return False
    
    code_ok = test_code_generation()
    
    # Resultado final
    print("\n" + "="*60)
    print("📋 RESULTADO FINAL")
    print("="*60)
    
    if config_ok and model_ok and code_ok:
        print("\n✅ MIGRAÇÃO BEM-SUCEDIDA!")
        print("\n   Todas as validações passaram:")
        print("   ✅ Configuração atualizada")
        print("   ✅ Modelo Flash carregado")
        print("   ✅ Geração de código funcionando")
        print("\n   🚀 Sistema pronto para uso com Gemini 2.5 Flash!")
        return True
    else:
        print("\n❌ MIGRAÇÃO FALHOU!")
        print("\n   Problemas encontrados:")
        if not config_ok:
            print("   ❌ Configuração")
        if not model_ok:
            print("   ❌ Carregamento do modelo")
        if not code_ok:
            print("   ❌ Geração de código")
        print("\n   🔄 Execute o rollback:")
        print("      Get-ChildItem .env.backup_* | Sort-Object LastWriteTime -Descending | Select-Object -First 1 | Copy-Item -Destination .env")
        return False

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n⚠️ Teste interrompido")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Erro fatal: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
