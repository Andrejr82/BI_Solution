"""
Teste rápido para validar correção do erro de format specifier
"""
import sys
import os

print("=" * 80)
print("TESTE: Validação da Correção de Format Specifier")
print("=" * 80)

# Importar módulos necessários
try:
    from core.llm_adapter import GeminiLLMAdapter
    from core.agents.code_gen_agent import CodeGenAgent
    from core.connectivity.hybrid_adapter import HybridDataAdapter
    from dotenv import load_dotenv

    print("[OK] Imports bem-sucedidos")
except Exception as e:
    print(f"[ERRO] Falha ao importar: {e}")
    sys.exit(1)

# Carregar variáveis de ambiente
load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    print("[ERRO] GEMINI_API_KEY não encontrada no .env")
    sys.exit(1)

print("[OK] API Key carregada")

# Inicializar agentes
try:
    llm_adapter = GeminiLLMAdapter(api_key=api_key, model_name="gemini-2.5-flash")
    data_adapter = HybridDataAdapter()
    code_gen_agent = CodeGenAgent(llm_adapter=llm_adapter, data_adapter=data_adapter)
    print("[OK] Agentes inicializados")
except Exception as e:
    print(f"[ERRO] Falha ao inicializar agentes: {e}")
    sys.exit(1)

# Testar construção do prompt (onde estava o erro)
try:
    test_query = "gere um gráfico de evolução do produto 369947 na une 2365"
    print(f"\n[TESTE] Construindo prompt para: '{test_query}'")

    # Chamar o método interno que estava com erro
    prompt = code_gen_agent._build_structured_prompt(test_query, rag_examples=[])

    print("[OK] Prompt construído com sucesso (sem erro de format specifier)")
    print(f"[INFO] Tamanho do prompt: {len(prompt)} caracteres")

    # Verificar se os escapes estão corretos
    if "{{'periodo'" in prompt:
        print("[OK] Dicionários escapados corretamente encontrados no prompt")

    print("\n" + "=" * 80)
    print("SUCESSO! Correção validada - Prompt constrói sem erros")
    print("=" * 80)

except ValueError as e:
    if "Invalid format specifier" in str(e):
        print(f"\n[ERRO] Ainda há erro de format specifier: {e}")
        print("[INFO] Verifique se todos os dicts literais foram escapados")
        sys.exit(1)
    else:
        raise
except Exception as e:
    print(f"\n[ERRO] Erro inesperado: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
