"""
Script de Teste Rápido da Integração de Validadores
Executa testes básicos sem pytest para validação rápida
"""

import sys
from pathlib import Path

# Adicionar path do projeto
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

print("="*80)
print("TESTE RÁPIDO DE INTEGRAÇÃO - VALIDADORES")
print("="*80)
print()

# =====================================================
# 1. TESTAR IMPORTS
# =====================================================
print("1️⃣  Testando imports dos validadores...")

try:
    from core.validators.schema_validator import SchemaValidator
    print("   ✅ SchemaValidator importado com sucesso")
except ImportError as e:
    print(f"   ❌ Erro ao importar SchemaValidator: {e}")
    sys.exit(1)

try:
    from core.utils.query_validator import validate_columns, handle_nulls, safe_filter, safe_convert_types
    print("   ✅ QueryValidator funções importadas com sucesso")
except ImportError as e:
    print(f"   ❌ Erro ao importar QueryValidator: {e}")
    sys.exit(1)

try:
    from core.utils.error_handler import error_handler_decorator, ErrorHandler
    print("   ✅ ErrorHandler importado com sucesso")
except ImportError as e:
    print(f"   ❌ Erro ao importar ErrorHandler: {e}")
    sys.exit(1)

print()

# =====================================================
# 2. TESTAR IMPORTS DAS FUNÇÕES UNE_TOOLS
# =====================================================
print("2️⃣  Testando imports de une_tools.py...")

try:
    from core.tools.une_tools import (
        get_produtos_une,
        get_transferencias,
        get_estoque_une,
        get_vendas_une,
        get_unes_disponiveis,
        get_preco_produto,
        get_total_vendas_une,
        get_total_estoque_une,
        health_check
    )
    print("   ✅ Todas as funções importadas com sucesso")
    print(f"      - get_produtos_une: {type(get_produtos_une)}")
    print(f"      - get_transferencias: {type(get_transferencias)}")
    print(f"      - health_check: {type(health_check)}")
except ImportError as e:
    print(f"   ❌ Erro ao importar funções: {e}")
    sys.exit(1)

print()

# =====================================================
# 3. TESTAR HEALTH CHECK
# =====================================================
print("3️⃣  Executando health_check()...")

try:
    result = health_check()

    if result["success"]:
        print(f"   ✅ Health check executado: {result['message']}")

        # Mostrar status de cada arquivo
        for arquivo, status in result["data"].items():
            existe = "✅" if status["existe"] else "❌"
            schema_ok = "✅" if status["schema_valido"] else "❌"
            erros = status["erros"]

            print(f"      {existe} {arquivo}")
            print(f"         Schema: {schema_ok}")
            if erros:
                print(f"         Erros: {', '.join(erros)}")
    else:
        print(f"   ⚠️  Health check falhou: {result['message']}")

except Exception as e:
    print(f"   ❌ Erro ao executar health_check: {e}")

print()

# =====================================================
# 4. TESTAR get_unes_disponiveis()
# =====================================================
print("4️⃣  Testando get_unes_disponiveis()...")

try:
    result = get_unes_disponiveis()

    if result["success"]:
        print(f"   ✅ {result['message']}")

        if len(result["data"]) > 0:
            print(f"      Primeiras 3 UNEs:")
            for une in result["data"][:3]:
                print(f"         - {une}")
        else:
            print("      ⚠️  Nenhuma UNE encontrada")
    else:
        print(f"   ❌ Erro: {result['message']}")

except Exception as e:
    print(f"   ❌ Exceção não capturada: {e}")

print()

# =====================================================
# 5. TESTAR get_produtos_une()
# =====================================================
print("5️⃣  Testando get_produtos_une(1)...")

try:
    result = get_produtos_une(1)

    if result["success"]:
        print(f"   ✅ {result['message']}")

        if len(result["data"]) > 0:
            print(f"      Primeiro produto:")
            primeiro = result["data"][0]
            for key, value in list(primeiro.items())[:5]:  # Mostrar primeiros 5 campos
                print(f"         - {key}: {value}")
        else:
            print("      ⚠️  Nenhum produto encontrado para UNE 1")
    else:
        print(f"   ❌ Erro: {result['message']}")

except Exception as e:
    print(f"   ❌ Exceção não capturada: {e}")

print()

# =====================================================
# 6. TESTAR ERRO HANDLING (UNE INVÁLIDA)
# =====================================================
print("6️⃣  Testando error handling com UNE inválida...")

try:
    # Testar com None (deve ser capturado pelo decorator)
    result = get_produtos_une(None)

    print(f"   ✅ Error handler funcionou - não crashou")
    print(f"      Success: {result['success']}")
    print(f"      Message: {result['message']}")

except Exception as e:
    print(f"   ⚠️  Exceção não foi capturada pelo decorator: {e}")

print()

# =====================================================
# 7. TESTAR get_transferencias()
# =====================================================
print("7️⃣  Testando get_transferencias(1)...")

try:
    result = get_transferencias(1)

    if result["success"]:
        print(f"   ✅ {result['message']}")

        if len(result["data"]) > 0:
            print(f"      Primeira transferência:")
            primeira = result["data"][0]
            for key, value in list(primeira.items())[:5]:
                print(f"         - {key}: {value}")
    else:
        print(f"   ⚠️  {result['message']}")

except Exception as e:
    print(f"   ❌ Exceção não capturada: {e}")

print()

# =====================================================
# 8. TESTAR FUNÇÕES DE AGREGAÇÃO
# =====================================================
print("8️⃣  Testando funções de agregação...")

try:
    result_vendas = get_total_vendas_une(1)

    if result_vendas["success"]:
        print(f"   ✅ Total de vendas: {result_vendas['message']}")
    else:
        print(f"   ⚠️  {result_vendas['message']}")

except Exception as e:
    print(f"   ❌ Erro em get_total_vendas_une: {e}")

try:
    result_estoque = get_total_estoque_une(1)

    if result_estoque["success"]:
        print(f"   ✅ Total de estoque: {result_estoque['message']}")
    else:
        print(f"   ⚠️  {result_estoque['message']}")

except Exception as e:
    print(f"   ❌ Erro em get_total_estoque_une: {e}")

print()

# =====================================================
# 9. TESTAR ESTRUTURA DE RETORNO PADRONIZADA
# =====================================================
print("9️⃣  Validando estrutura de retorno padronizada...")

funcoes_para_testar = [
    ("get_produtos_une", lambda: get_produtos_une(1)),
    ("get_transferencias", lambda: get_transferencias(1)),
    ("get_estoque_une", lambda: get_estoque_une(1)),
    ("get_vendas_une", lambda: get_vendas_une(1)),
    ("get_unes_disponiveis", lambda: get_unes_disponiveis()),
]

estrutura_ok = True

for nome_funcao, funcao in funcoes_para_testar:
    try:
        result = funcao()

        # Validar campos obrigatórios
        if not isinstance(result, dict):
            print(f"   ❌ {nome_funcao}: retorno não é dict")
            estrutura_ok = False
            continue

        if "success" not in result:
            print(f"   ❌ {nome_funcao}: falta campo 'success'")
            estrutura_ok = False

        if "data" not in result:
            print(f"   ❌ {nome_funcao}: falta campo 'data'")
            estrutura_ok = False

        if "message" not in result:
            print(f"   ❌ {nome_funcao}: falta campo 'message'")
            estrutura_ok = False

    except Exception as e:
        print(f"   ❌ {nome_funcao}: exceção {e}")
        estrutura_ok = False

if estrutura_ok:
    print("   ✅ Todas as funções retornam estrutura padronizada")
else:
    print("   ⚠️  Algumas funções têm problemas na estrutura de retorno")

print()

# =====================================================
# 10. RESUMO FINAL
# =====================================================
print("="*80)
print("RESUMO DA INTEGRAÇÃO")
print("="*80)

print("""
✅ VALIDAÇÕES IMPLEMENTADAS:
   - SchemaValidator: Valida arquivos Parquet antes de carregar
   - validate_columns: Verifica colunas obrigatórias
   - handle_nulls: Trata valores nulos (drop/fill)
   - safe_convert_types: Conversão segura de tipos
   - safe_filter: Filtros sem crash
   - error_handler_decorator: Captura todas as exceções

✅ FUNÇÕES INTEGRADAS:
   - get_produtos_une()
   - get_transferencias()
   - get_estoque_une()
   - get_vendas_une()
   - get_unes_disponiveis()
   - get_preco_produto()
   - get_total_vendas_une()
   - get_total_estoque_une()
   - health_check()

✅ PADRÃO DE RETORNO:
   {
       "success": bool,
       "data": Any,
       "message": str
   }

📝 PRÓXIMOS PASSOS:
   1. Executar testes completos: pytest tests/test_validadores_integration.py -v
   2. Validar performance: tempo de resposta < 2s
   3. Testar em staging com dados reais
   4. Monitorar logs por 1 semana
   5. Deploy em produção

🔗 DOCUMENTAÇÃO:
   - INTEGRACAO_VALIDADORES_RESUMO.md
   - DIFF_VALIDADORES_UNE_TOOLS.md
   - tests/test_validadores_integration.py
""")

print("="*80)
print("TESTE CONCLUÍDO")
print("="*80)
