import sys
import os
import logging

# Adiciona a raiz do projeto ao path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from core.config.safe_settings import get_safe_settings
from core.factory.component_factory import ComponentFactory

def test_hybrid_configuration():
    print("Testando Configuração Híbrida...")
    settings = get_safe_settings()
    
    print(f"INTENT_CLASSIFICATION_MODEL: {settings.INTENT_CLASSIFICATION_MODEL}")
    print(f"CODE_GENERATION_MODEL: {settings.CODE_GENERATION_MODEL}")
    
    # Verificações relaxadas para permitir variações, mas garantindo a presença dos modelos chave
    assert "gemini-2.5-flash" in settings.INTENT_CLASSIFICATION_MODEL, f"Esperado gemini-2.5-flash, obtido {settings.INTENT_CLASSIFICATION_MODEL}"
    assert "gemini-3-pro" in settings.CODE_GENERATION_MODEL, f"Esperado gemini-3-pro, obtido {settings.CODE_GENERATION_MODEL}"
    print("✅ Configuração parece correta.")

def test_component_factory():
    print("\nTestando Fábrica de Componentes...")
    
    # Teste LLM de Classificação de Intenção
    intent_llm = ComponentFactory.get_intent_classification_llm()
    if intent_llm:
        print(f"Modelo LLM Intenção: {intent_llm.model_name}")
        print(f"Temperatura LLM Intenção: {intent_llm.temperature}")
        assert "gemini-2.5-flash" in intent_llm.model_name
        assert intent_llm.temperature == 0.0
        print("✅ LLM de Classificação de Intenção configurado corretamente.")
    else:
        print("⚠️ LLM de Intenção não disponível (API Key pode estar faltando).")

    # Teste LLM de Geração de Código
    code_llm = ComponentFactory.get_code_generation_llm()
    if code_llm:
        print(f"Modelo LLM Code Gen: {code_llm.model_name}")
        print(f"Temperatura LLM Code Gen: {code_llm.temperature}")
        assert "gemini-3-pro" in code_llm.model_name
        assert code_llm.temperature == 0.2
        print("✅ LLM de Geração de Código configurado corretamente.")
    else:
        print("⚠️ LLM de Code Gen não disponível (API Key pode estar faltando).")

if __name__ == "__main__":
    try:
        test_hybrid_configuration()
        test_component_factory()
        print("\n🎉 Todos os testes de verificação passaram!")
    except AssertionError as e:
        print(f"\n❌ Teste Falhou: {e}")
    except Exception as e:
        print(f"\n❌ Ocorreu um erro: {e}")
