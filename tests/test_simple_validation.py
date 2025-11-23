"""
Teste Simples e Direto: Validação da Migração
Testa diretamente a API do Gemini sem dependências complexas
"""

import os
from dotenv import load_dotenv

# Forçar reload do .env
load_dotenv(override=True)

def test_env_configuration():
    """Testa se o .env foi atualizado corretamente"""
    print("="*60)
    print("1️⃣  VALIDANDO ARQUIVO .ENV")
    print("="*60)
    
    code_gen_model = os.getenv("CODE_GENERATION_MODEL")
    print(f"\nCODE_GENERATION_MODEL = {code_gen_model}")
    
    if "flash" in code_gen_model.lower():
        print("✅ Configuração correta - Flash detectado")
        return True
    else:
        print(f"❌ Configuração incorreta - esperado Flash")
        return False

def test_direct_api():
    """Testa diretamente a API do Gemini com o modelo Flash"""
    print("\n" + "="*60)
    print("2️⃣  TESTANDO API GEMINI DIRETAMENTE")
    print("="*60)
    
    try:
        import google.generativeai as genai
        
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            print("❌ GEMINI_API_KEY não encontrada")
            return False
        
        genai.configure(api_key=api_key)
        
        # Testar com Flash
        model_name = "models/gemini-2.5-flash"
        print(f"\nTestando modelo: {model_name}")
        
        model = genai.GenerativeModel(model_name)
        
        # Query de teste simples
        prompt = "Gere código Python para listar os top 10 produtos. Use apenas print('OK')"
        
        import time
        start = time.time()
        response = model.generate_content(prompt)
        elapsed = time.time() - start
        
        if response.text:
            print(f"✅ Resposta recebida em {elapsed:.2f}s")
            print(f"✅ Tamanho: {len(response.text)} chars")
            print(f"✅ Modelo Flash funcionando perfeitamente!")
            return True
        else:
            print("❌ Resposta vazia")
            return False
            
    except Exception as e:
        print(f"❌ Erro: {e}")
        return False

def main():
    print("="*60)
    print("🧪 VALIDAÇÃO SIMPLES DA MIGRAÇÃO")
    print("="*60)
    
    env_ok = test_env_configuration()
    api_ok = test_direct_api()
    
    print("\n" + "="*60)
    print("📋 RESULTADO")
    print("="*60)
    
    if env_ok and api_ok:
        print("\n✅ MIGRAÇÃO BEM-SUCEDIDA!")
        print("\n   ✅ Arquivo .env atualizado")
        print("   ✅ API Gemini Flash funcionando")
        print("\n   🚀 Sistema pronto para uso!")
        print("\n📝 Próximo passo:")
        print("   Reinicie o Streamlit para aplicar as mudanças:")
        print("   streamlit run streamlit_app.py")
        return True
    else:
        print("\n❌ MIGRAÇÃO FALHOU!")
        if not env_ok:
            print("   ❌ Problema no .env")
        if not api_ok:
            print("   ❌ Problema na API")
        return False

if __name__ == "__main__":
    import sys
    success = main()
    sys.exit(0 if success else 1)
