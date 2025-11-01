import ast
import re
from typing import Dict, Any, List

class CodeValidator:
    """Valida o código Python gerado pelo LLM antes da execução."""

    def validate(self, code: str, user_query: str) -> Dict[str, Any]:
        """
        Valida o código gerado contra um conjunto de regras de segurança e negócio.

        Args:
            code: O código Python a ser validado.
            user_query: A query original do usuário para contexto.

        Returns:
            Um dicionário com o status da validação.
        """
        errors = []
        warnings = []
        suggestions = []

        # --- Regras de Segurança ---

        # 1. Validar sintaxe Python
        try:
            ast.parse(code)
        except SyntaxError as e:
            errors.append(f"Erro de sintaxe: {e}")
            # Se a sintaxe é inválida, outras checagens podem falhar
            return {
                "valid": False,
                "errors": errors,
                "warnings": warnings,
                "suggestions": suggestions
            }

        # 2. Detectar operações perigosas
        BLOCKED_OPS = ['import os', 'import sys', 'eval(', 'exec(', '__import__']
        for op in BLOCKED_OPS:
            if op in code:
                errors.append(f"Operação não permitida encontrada: {op}")

        # --- Regras de Negócio ---

        # 3. Código deve carregar dados
        if "load_data(" not in code:
            errors.append("O código não carrega os dados. Use a função `load_data()`.")
            suggestions.append("Adicione `df = load_data()` no início do seu código.")

        # 4. Código deve atribuir um resultado
        if "result =" not in code:
            warnings.append("O código não atribui o resultado final à variável `result`.")
            suggestions.append("Certifique-se de que sua linha final seja algo como `result = df_final` ou `result = fig`.")

        # 5. Queries de ranking devem ter 'groupby'
        query_lower = user_query.lower()
        is_ranking_query = any(kw in query_lower for kw in ["ranking", "top", "maior", "mais vendido"])
        if is_ranking_query and ".groupby(" not in code:
            warnings.append("A query parece ser um ranking, mas o código não usa `.groupby()`.")
            suggestions.append("Para rankings, use `.groupby('coluna').agg(...)` ou `.groupby('coluna')['metrica'].sum()`.")

        # 6. Queries "top N" devem ter ".head(N)"
        top_match = re.search(r'top\s+(\d+)', query_lower)
        if top_match:
            n = top_match.group(1)
            if f".head({n})" not in code and f".nlargest({n}" not in code:
                warnings.append(f"A query pede 'top {n}', mas o código não parece limitar os resultados com `.head({n})` ou `.nlargest({n}, ...)`.")
                suggestions.append(f"Adicione `.head({n})` ao final da sua operação de ranking.")

        return {
            "valid": len(errors) == 0,
            "errors": errors,
            "warnings": warnings,
            "suggestions": suggestions
        }

if __name__ == '__main__':
    # Bloco de teste para validação rápida
    validator = CodeValidator()
    
    print("--- Testando códigos válidos ---")
    valid_code = """
df = load_data()
df_agg = df.groupby('nomesegmento')['venda_30_d'].sum().reset_index()
result = df_agg.nlargest(10, 'venda_30_d')
"""
    print(f"Código: {valid_code}")
    result = validator.validate(valid_code, "top 10 segmentos")
    print(f"Resultado: {result}\n")
    assert result['valid'] is True
    assert len(result['warnings']) == 0

    print("--- Testando códigos com erros (sintaxe) ---")
    invalid_syntax_code = "df = load_data()\nresult = df.groupby('nomesegmento'"
    print(f"Código: {invalid_syntax_code}")
    result = validator.validate(invalid_syntax_code, "query qualquer")
    print(f"Resultado: {result}\n")
    assert result['valid'] is False
    assert "Erro de sintaxe" in result['errors'][0]

    print("--- Testando códigos com erros (operação perigosa) ---")
    dangerous_code = "import os\ndf = load_data()\nresult = os.listdir('/')"
    print(f"Código: {dangerous_code}")
    result = validator.validate(dangerous_code, "query qualquer")
    print(f"Resultado: {result}\n")
    assert result['valid'] is False
    assert "Operação não permitida" in result['errors'][0]

    print("--- Testando códigos com avisos (sem result) ---")
    no_result_code = "df = load_data()\ndf.head(5)"
    print(f"Código: {no_result_code}")
    result = validator.validate(no_result_code, "query qualquer")
    print(f"Resultado: {result}\n")
    assert result['valid'] is True
    assert len(result['warnings']) > 0

    print("--- Testando códigos com avisos (ranking sem groupby) ---")
    ranking_no_groupby = "df = load_data()\nresult = df.sort_values('venda_30_d', ascending=False)"
    print(f"Código: {ranking_no_groupby}")
    result = validator.validate(ranking_no_groupby, "ranking de produtos")
    print(f"Resultado: {result}\n")
    assert result['valid'] is True
    assert len(result['warnings']) > 0

    print("--- Testando códigos com avisos (top N sem head) ---")
    top_n_no_head = "df = load_data()\nresult = df.groupby('nomesegmento')['venda_30_d'].sum().sort_values(ascending=False).reset_index()"
    print(f"Código: {top_n_no_head}")
    result = validator.validate(top_n_no_head, "top 10 segmentos")
    print(f"Resultado: {result}\n")
    assert result['valid'] is True
    assert len(result['warnings']) > 0
    
    print("--- Todos os testes do validador passaram ---")