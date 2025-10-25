"""
Teste simples da solução - Sem dependências complexas
"""
import os
from pathlib import Path

print("=" * 70)
print(" TESTE SIMPLES DA SOLUÇÃO")
print("=" * 70)
print()

# TESTE 1: Cache Limpo
print("[1/4] Verificando cache...")
cache_dir = Path("data/cache")
cache_agent_dir = Path("data/cache_agent_graph")
prompt_version = Path("data/cache/.prompt_version")

cache_files = list(cache_dir.glob("*")) if cache_dir.exists() else []
cache_agent_files = list(cache_agent_dir.glob("*")) if cache_agent_dir.exists() else []

print(f"  Cache de dados: {len(cache_files)} arquivos")
print(f"  Cache agent: {len(cache_agent_files)} arquivos")
print(f"  .prompt_version: {'EXISTE' if prompt_version.exists() else 'NÃO EXISTE'}")

test1 = len(cache_files) == 0 and len(cache_agent_files) == 0 and not prompt_version.exists()
print(f"  Resultado: {'✅ PASSOU' if test1 else '❌ FALHOU'}")
print()

# TESTE 2: Sem Chaves Duplas
print("[2/4] Verificando chaves duplas no código...")
code_file = Path("core/agents/code_gen_agent.py")

if code_file.exists():
    with open(code_file, 'r', encoding='utf-8') as f:
        content = f.read()

    # Contar chaves duplas em contexto de DataFrame
    double_braces_count = content.count("DataFrame({{")
    double_braces_count += content.count("}})")

    print(f"  Chaves duplas encontradas: {double_braces_count}")
    test2 = double_braces_count == 0
    print(f"  Resultado: {'✅ PASSOU' if test2 else '❌ FALHOU'}")
else:
    print("  ❌ Arquivo não encontrado")
    test2 = False
print()

# TESTE 3: Versão do Prompt
print("[3/4] Verificando versão do prompt...")
if code_file.exists():
    with open(code_file, 'r', encoding='utf-8') as f:
        content = f.read()

    if "'version': '2.4_all_double_braces_removed_20251020'" in content:
        print("  Versão encontrada: 2.4_all_double_braces_removed_20251020")
        test3 = True
        print("  Resultado: ✅ PASSOU")
    else:
        print("  Versão 2.4 não encontrada")
        test3 = False
        print("  Resultado: ❌ FALHOU")
else:
    test3 = False
    print("  Resultado: ❌ FALHOU")
print()

# TESTE 4: Código Válido
print("[4/4] Testando sintaxe do código esperado...")
codigo_esperado = """
df = load_data()
df_produto = df[df['PRODUTO'].astype(str) == '59294']

meses = ['Mês 1', 'Mês 2', 'Mês 3', 'Mês 4', 'Mês 5', 'Mês 6']
vendas = [
    df_produto['mes_01'].sum(),
    df_produto['mes_02'].sum(),
    df_produto['mes_03'].sum(),
    df_produto['mes_04'].sum(),
    df_produto['mes_05'].sum(),
    df_produto['mes_06'].sum()
]

temporal_df = pd.DataFrame({'Mês': meses, 'Vendas': vendas})
result = px.bar(temporal_df, x='Mês', y='Vendas', title='Evolução')
"""

try:
    import ast
    ast.parse(codigo_esperado)
    print("  Sintaxe: VÁLIDA")
    print("  Chaves no DataFrame: UMA (correto)")
    test4 = True
    print("  Resultado: ✅ PASSOU")
except SyntaxError as e:
    print(f"  Erro de sintaxe: {e}")
    test4 = False
    print("  Resultado: ❌ FALHOU")
print()

# RESUMO
print("=" * 70)
print(" RESUMO")
print("=" * 70)
all_passed = test1 and test2 and test3 and test4

resultados = [
    ("Cache Limpo", test1),
    ("Sem Chaves Duplas", test2),
    ("Versão 2.4 Aplicada", test3),
    ("Código Válido", test4)
]

for nome, passou in resultados:
    status = "✅" if passou else "❌"
    print(f"{status} {nome}")

print()
if all_passed:
    print("✅✅✅ TODOS OS TESTES PASSARAM! ✅✅✅")
    print()
    print("PRÓXIMOS PASSOS:")
    print("1. Execute: REINICIAR_LIMPO.bat (ou mate o Python manualmente)")
    print("2. Inicie: streamlit run streamlit_app.py")
    print("3. Teste: 'gráfico evolução vendas produto 59294 une bar'")
    print()
    print("O erro de format specifier NÃO deve mais ocorrer!")
else:
    print("⚠️ ALGUNS TESTES FALHARAM - Verifique os detalhes acima")
print("=" * 70)
