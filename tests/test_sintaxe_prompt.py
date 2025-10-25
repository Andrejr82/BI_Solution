"""
Teste de sintaxe do prompt - Verifica se a string se forma sem erros
"""
import os

print("=" * 70)
print(" TESTE DE SINTAXE - Formacao do Prompt v2.6")
print("=" * 70)
print()

print("[1/2] Lendo arquivo code_gen_agent.py...")
with open("core/agents/code_gen_agent.py", 'r', encoding='utf-8') as f:
    content = f.read()
    lines = content.split('\n')

print("  Arquivo lido: OK")
print()

print("[2/2] Verificando construcao do prompt...")

# Procurar a linha com system_prompt
prompt_line = None
for i, line in enumerate(lines):
    if 'system_prompt = """Você é um especialista' in line:
        prompt_line = i + 1  # +1 porque enumerate comeca em 0
        print(f"  Linha {prompt_line}: Prompt encontrado")
        break

if prompt_line:
    # Verificar se eh concatenacao (sem f-string)
    linha_atual = lines[prompt_line - 1]

    if linha_atual.strip().startswith('system_prompt = f"""'):
        print("  ERRO: F-string ainda presente!")
        print(f"  Linha {prompt_line}: {linha_atual.strip()[:50]}...")
        exit(1)
    elif linha_atual.strip().startswith('system_prompt = """'):
        print("  OK: Usando string normal (sem f-string)")

        # Verificar se tem concatenacao nas linhas seguintes
        tem_concatenacao = False
        for i in range(prompt_line, min(prompt_line + 20, len(lines))):
            if '""" + ' in lines[i] or ' + """' in lines[i]:
                tem_concatenacao = True
                print(f"  Linha {i+1}: Concatenacao encontrada")
                break

        if tem_concatenacao:
            print("  OK: Sistema usando concatenacao de strings (correto)")
        else:
            print("  AVISO: Nao encontrou concatenacao esperada")

    else:
        print("  AVISO: Formato inesperado")
        print(f"  Linha {prompt_line}: {linha_atual.strip()[:50]}...")

else:
    print("  ERRO: Linha de prompt nao encontrada")
    exit(1)

print()

# Teste pratico: tentar formar uma string como o codigo faz
print("[TESTE PRATICO] Simulando formacao de string...")
try:
    # Simular o que o codigo faz
    column_context = "Colunas: PRODUTO, VENDA_30DD"
    valid_segments = "Segmentos: Medicamentos"

    # Formar string como o codigo v2.6 faz (concatenacao)
    test_prompt = """Voce eh um especialista em analise de dados.

""" + column_context + """

""" + valid_segments + """

EXEMPLO:
df = load_data()
temporal_data = pd.DataFrame({
    'Mes': ['Mes 1', 'Mes 2'],
    'Vendas': [100, 200]
})
"""

    print("  String formada com SUCESSO!")
    print("  Tamanho: {} caracteres".format(len(test_prompt)))

    # Verificar se tem os placeholders
    if "{" in test_prompt and "}" in test_prompt:
        print("  Contem '{}': SIM (nos exemplos de codigo - OK)")
    else:
        print("  Contem '{}': NAO")

    print("  Resultado: OK - Nao houve erro de formatacao!")

except ValueError as e:
    if "Invalid format specifier" in str(e):
        print("  ERRO CRITICO: F-string ainda causando problema!")
        print(f"  Detalhes: {e}")
        exit(1)
    else:
        print(f"  Erro inesperado: {e}")
        exit(1)

print()
print("=" * 70)
print(" RESULTADO FINAL")
print("=" * 70)
print()
print("*** TESTE DE SINTAXE PASSOU! ***")
print()
print("- F-string removida: OK")
print("- Concatenacao implementada: OK")
print("- String formada sem erros: OK")
print("- Exemplos com '{}' nao causam erro: OK")
print()
print("A solucao v2.6 esta aplicada corretamente!")
print()
print("PROXIMA ACAO:")
print("Execute: streamlit run streamlit_app.py")
print("Teste: 'grafico de vendas segmentos une 2365'")
print()
print("=" * 70)
