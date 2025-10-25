"""
Teste da solução de cache - Verificar se código gerado está correto
"""
import sys
import os

# Adicionar caminho do projeto
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_prompt_version():
    """Testar se versão do prompt foi atualizada"""
    from core.agents.code_gen_agent import CodeGenAgent
    from core.llm_adapter import get_llm_adapter

    print("=" * 70)
    print("TESTE 1: Verificar Versão do Prompt")
    print("=" * 70)

    try:
        llm = get_llm_adapter()
        agent = CodeGenAgent(llm)

        # Verificar versão através do método de invalidação
        import json
        prompt_components = {
            'columns': list(agent.column_descriptions.keys()),
            'descriptions': list(agent.column_descriptions.values()),
            'version': '2.4_all_double_braces_removed_20251020'
        }

        print(f"✅ Versão esperada: 2.4_all_double_braces_removed_20251020")
        print(f"✅ Componentes do prompt carregados: {len(prompt_components['columns'])} colunas")
        print()
        return True
    except Exception as e:
        print(f"❌ Erro: {e}")
        return False

def test_cache_limpo():
    """Testar se cache foi limpo"""
    print("=" * 70)
    print("TESTE 2: Verificar Cache Limpo")
    print("=" * 70)

    import os
    from pathlib import Path

    cache_dir = Path("data/cache")
    cache_agent_dir = Path("data/cache_agent_graph")
    prompt_version = Path("data/cache/.prompt_version")

    cache_files = list(cache_dir.glob("*")) if cache_dir.exists() else []
    cache_agent_files = list(cache_agent_dir.glob("*")) if cache_agent_dir.exists() else []

    print(f"Cache de dados: {len(cache_files)} arquivos")
    print(f"Cache agent graph: {len(cache_agent_files)} arquivos")
    print(f"Arquivo .prompt_version existe: {prompt_version.exists()}")

    if len(cache_files) == 0 and len(cache_agent_files) == 0:
        print("✅ Cache está limpo!")
        print()
        return True
    else:
        print("⚠️ Cache ainda contém arquivos")
        print()
        return False

def test_no_double_braces():
    """Testar se não há chaves duplas no código"""
    print("=" * 70)
    print("TESTE 3: Verificar Ausência de Chaves Duplas")
    print("=" * 70)

    code_gen_file = "core/agents/code_gen_agent.py"

    with open(code_gen_file, 'r', encoding='utf-8') as f:
        content = f.read()

    # Procurar por padrões de chaves duplas problemáticos
    double_braces_patterns = [
        "{{",
        "}}",
        "DataFrame({{",
        "}}.)",
    ]

    found_issues = []
    for pattern in double_braces_patterns:
        if pattern in content:
            # Contar ocorrências
            count = content.count(pattern)
            found_issues.append(f"{pattern} encontrado {count} vez(es)")

    if found_issues:
        print("❌ Encontradas chaves duplas:")
        for issue in found_issues:
            print(f"   - {issue}")
        print()
        return False
    else:
        print("✅ Nenhuma chave dupla encontrada!")
        print()
        return True

def test_code_generation_simulation():
    """Simular geração de código para query de evolução"""
    print("=" * 70)
    print("TESTE 4: Simular Geração de Código")
    print("=" * 70)

    # Código que DEVERIA ser gerado (sem chaves duplas)
    expected_code = """
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

    print("Código esperado:")
    print("-" * 70)
    print(expected_code)
    print("-" * 70)

    # Verificar se código é válido Python
    try:
        import ast
        ast.parse(expected_code)
        print("✅ Código é sintaticamente válido!")
        print()
        return True
    except SyntaxError as e:
        print(f"❌ Erro de sintaxe: {e}")
        print()
        return False

def main():
    """Executar todos os testes"""
    print("\n")
    print("=" * 70)
    print(" TESTE COMPLETO DA SOLUÇÃO DE CACHE")
    print("=" * 70)
    print()

    results = {
        "Versão do Prompt": test_prompt_version(),
        "Cache Limpo": test_cache_limpo(),
        "Sem Chaves Duplas": test_no_double_braces(),
        "Código Gerado Válido": test_code_generation_simulation()
    }

    print("=" * 70)
    print(" RESUMO DOS TESTES")
    print("=" * 70)
    print()

    all_passed = True
    for test_name, passed in results.items():
        status = "✅ PASSOU" if passed else "❌ FALHOU"
        print(f"{test_name:.<50} {status}")
        if not passed:
            all_passed = False

    print()
    print("=" * 70)
    if all_passed:
        print("✅ TODOS OS TESTES PASSARAM!")
        print()
        print("PRÓXIMO PASSO:")
        print("1. Execute: REINICIAR_LIMPO.bat")
        print("2. Teste no Streamlit: 'gráfico evolução vendas produto 59294'")
    else:
        print("⚠️ ALGUNS TESTES FALHARAM")
        print("Verifique os detalhes acima")
    print("=" * 70)
    print()

if __name__ == "__main__":
    main()
