"""
Testes de Validação do Sistema de Mapeamento de Campos
========================================================

Este arquivo contém testes para validar que o sistema de mapeamento
de campos está funcionando corretamente.
"""

import sys
import os

# Adicionar o diretório raiz ao path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.utils.field_mapper import FieldMapper, get_field_mapper


def test_basic_field_mapping():
    """Testa mapeamento básico de campos"""
    print("=" * 80)
    print("TESTE 1: Mapeamento Básico de Campos")
    print("=" * 80)
    
    mapper = FieldMapper()
    
    test_cases = [
        ("segmento", "NOMESEGMENTO"),
        ("categoria", "NomeCategoria"),
        ("codigo", "PRODUTO"),
        ("código", "PRODUTO"),
        ("estoque", "ESTOQUE_UNE"),
        ("preco", "LIQUIDO_38"),
        ("preço", "LIQUIDO_38"),
        ("vendas", "VENDA_30DD"),
        ("fabricante", "NomeFabricante"),
    ]
    
    passed = 0
    failed = 0
    
    for user_term, expected_field in test_cases:
        result = mapper.map_field(user_term)
        if result == expected_field:
            print(f"✅ '{user_term}' → '{result}' (esperado: '{expected_field}')")
            passed += 1
        else:
            print(f"❌ '{user_term}' → '{result}' (esperado: '{expected_field}')")
            failed += 1
    
    print(f"\nResultado: {passed} passou, {failed} falhou")
    return failed == 0


def test_stock_fields():
    """Testa campos de estoque"""
    print("\n" + "=" * 80)
    print("TESTE 2: Campos de Estoque")
    print("=" * 80)
    
    mapper = FieldMapper()
    
    test_cases = [
        (None, "ESTOQUE_UNE"),  # Campo padrão
        ("une", "ESTOQUE_UNE"),
        ("cd", "ESTOQUE_CD"),
        ("lv", "ESTOQUE_LV"),
    ]
    
    passed = 0
    failed = 0
    
    for stock_type, expected_field in test_cases:
        result = mapper.get_stock_field(stock_type)
        if result == expected_field:
            print(f"✅ estoque('{stock_type}') → '{result}' (esperado: '{expected_field}')")
            passed += 1
        else:
            print(f"❌ estoque('{stock_type}') → '{result}' (esperado: '{expected_field}')")
            failed += 1
    
    print(f"\nResultado: {passed} passou, {failed} falhou")
    return failed == 0


def test_filter_conditions():
    """Testa construção de condições de filtro"""
    print("\n" + "=" * 80)
    print("TESTE 3: Construção de Condições de Filtro")
    print("=" * 80)
    
    mapper = FieldMapper()
    
    test_cases = [
        ("NOMESEGMENTO", "TECIDO", "contains", "UPPER(NOMESEGMENTO) LIKE '%TECIDO%'"),
        ("PRODUTO", 369947, "==", "PRODUTO = 369947"),
        ("VENDA_30DD", 100, ">", "VENDA_30DD > 100"),
        ("NomeCategoria", "AVIAMENTOS", "contains", "UPPER(NomeCategoria) LIKE '%AVIAMENTOS%'"),
    ]
    
    passed = 0
    failed = 0
    
    for field, value, operator, expected in test_cases:
        result = mapper.build_filter_condition(field, value, operator)
        if result == expected:
            print(f"✅ {field} {operator} {value}")
            print(f"   → {result}")
            passed += 1
        else:
            print(f"❌ {field} {operator} {value}")
            print(f"   Obtido:   {result}")
            print(f"   Esperado: {expected}")
            failed += 1
    
    print(f"\nResultado: {passed} passou, {failed} falhou")
    return failed == 0


def test_zero_stock_condition():
    """Testa condição de estoque zero"""
    print("\n" + "=" * 80)
    print("TESTE 4: Condição de Estoque Zero")
    print("=" * 80)
    
    mapper = FieldMapper()
    
    result = mapper.build_zero_stock_condition()
    expected = "(ESTOQUE_UNE = 0 OR ESTOQUE_UNE IS NULL)"
    
    if result == expected:
        print(f"✅ Condição de estoque zero:")
        print(f"   → {result}")
        print("\nResultado: 1 passou, 0 falhou")
        return True
    else:
        print(f"❌ Condição de estoque zero:")
        print(f"   Obtido:   {result}")
        print(f"   Esperado: {expected}")
        print("\nResultado: 0 passou, 1 falhou")
        return False


def test_query_templates():
    """Testa geração de templates de query"""
    print("\n" + "=" * 80)
    print("TESTE 5: Templates de Query SQL")
    print("=" * 80)
    
    mapper = FieldMapper()
    
    # Teste 1: categorias_estoque_zero
    query1 = mapper.generate_query_template(
        "categorias_estoque_zero",
        segmento="TECIDO"
    )
    
    if "NOMESEGMENTO" in query1 and "NomeCategoria" in query1 and "ESTOQUE_UNE" in query1:
        print("✅ Template 'categorias_estoque_zero' gerado corretamente")
        print(f"   Contém: NOMESEGMENTO, NomeCategoria, ESTOQUE_UNE")
    else:
        print("❌ Template 'categorias_estoque_zero' incorreto")
        return False
    
    # Teste 2: produtos_por_segmento
    query2 = mapper.generate_query_template(
        "produtos_por_segmento",
        segmento="AVIAMENTOS"
    )
    
    if "PRODUTO" in query2 and "NOME" in query2 and "NOMESEGMENTO" in query2:
        print("✅ Template 'produtos_por_segmento' gerado corretamente")
        print(f"   Contém: PRODUTO, NOME, NOMESEGMENTO")
    else:
        print("❌ Template 'produtos_por_segmento' incorreto")
        return False
    
    print("\nResultado: 2 passou, 0 falhou")
    return True


def test_field_types():
    """Testa identificação de tipos de campos"""
    print("\n" + "=" * 80)
    print("TESTE 6: Tipos de Campos")
    print("=" * 80)
    
    mapper = FieldMapper()
    
    test_cases = [
        ("PRODUTO", "integer", True, False),
        ("NOME", "string", False, True),
        ("NOMESEGMENTO", "string", False, True),
        ("LIQUIDO_38", "float", True, False),
        ("ESTOQUE_UNE", "float", True, False),
    ]
    
    passed = 0
    failed = 0
    
    for field, expected_type, should_be_numeric, should_be_string in test_cases:
        field_type = mapper.get_field_type(field)
        is_numeric = mapper.is_numeric_field(field)
        is_string = mapper.is_string_field(field)
        
        if (field_type == expected_type and 
            is_numeric == should_be_numeric and 
            is_string == should_be_string):
            print(f"✅ {field}: tipo={field_type}, numérico={is_numeric}, string={is_string}")
            passed += 1
        else:
            print(f"❌ {field}: tipo={field_type} (esperado: {expected_type})")
            failed += 1
    
    print(f"\nResultado: {passed} passou, {failed} falhou")
    return failed == 0


def run_all_tests():
    """Executa todos os testes"""
    print("\n")
    print("╔" + "=" * 78 + "╗")
    print("║" + " " * 20 + "TESTES DE VALIDAÇÃO DO FIELD MAPPER" + " " * 23 + "║")
    print("╚" + "=" * 78 + "╝")
    print()
    
    tests = [
        ("Mapeamento Básico", test_basic_field_mapping),
        ("Campos de Estoque", test_stock_fields),
        ("Condições de Filtro", test_filter_conditions),
        ("Estoque Zero", test_zero_stock_condition),
        ("Templates de Query", test_query_templates),
        ("Tipos de Campos", test_field_types),
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            passed = test_func()
            results.append((test_name, passed))
        except Exception as e:
            print(f"\n❌ ERRO no teste '{test_name}': {e}")
            results.append((test_name, False))
    
    # Resumo final
    print("\n" + "=" * 80)
    print("RESUMO DOS TESTES")
    print("=" * 80)
    
    total_passed = sum(1 for _, passed in results if passed)
    total_tests = len(results)
    
    for test_name, passed in results:
        status = "✅ PASSOU" if passed else "❌ FALHOU"
        print(f"{status}: {test_name}")
    
    print("\n" + "=" * 80)
    print(f"RESULTADO FINAL: {total_passed}/{total_tests} testes passaram")
    print("=" * 80)
    
    if total_passed == total_tests:
        print("\n🎉 TODOS OS TESTES PASSARAM! Sistema de mapeamento está funcionando corretamente.")
        return 0
    else:
        print(f"\n⚠️  {total_tests - total_passed} teste(s) falharam. Revise o código.")
        return 1


if __name__ == "__main__":
    exit_code = run_all_tests()
    sys.exit(exit_code)
