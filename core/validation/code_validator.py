"""
Módulo de validação de código gerado pelo LLM.
Valida código Python antes da execução para detectar problemas comuns.
"""

import re
from typing import Dict, Any, List


class CodeValidator:
    """
    Validador de código Python para queries de BI.
    Detecta problemas comuns antes da execução.
    """

    def __init__(self):
        """Inicializa o validador com regras de validação."""
        self.required_columns = [
            "PRODUTO", "NOME", "NOMESEGMENTO", "NomeCategoria", "NOMEGRUPO",
            "VENDA_30DD", "ESTOQUE_UNE", "LIQUIDO_38", "UNE_NOME", "NomeFabricante"
        ]

        # Operações perigosas bloqueadas
        self.blocked_operations = [
            'import os',
            'import sys',
            'import subprocess',
            'eval(',
            'exec(',
            '__import__',
            'open(',  # Exceto read do Parquet que é controlado
            'rm ',
            'rmdir',
            'delete',
        ]

    def validate(self, code: str, user_query: str) -> Dict[str, Any]:
        """
        Valida código gerado pelo LLM.

        Args:
            code: Código Python a ser validado
            user_query: Query original do usuário

        Returns:
            {
                "valid": bool,
                "errors": List[str],
                "warnings": List[str],
                "suggestions": List[str]
            }
        """
        errors = []
        warnings = []
        suggestions = []

        # Regra 1: Código deve começar com load_data()
        if "df = load_data()" not in code and "load_data()" not in code:
            errors.append("Código não carrega dados com load_data()")
            suggestions.append("Adicione: df = load_data()")

        # Regra 2: Se query tem "ranking" ou "top", deve ter groupby
        if any(kw in user_query.lower() for kw in ["ranking", "top", "maior", "mais vendido", "mais vendidos"]):
            if ".groupby(" not in code:
                errors.append("Query pede ranking mas código não tem groupby()")
                suggestions.append("Adicione: .groupby('NOME')['VENDA_30DD'].sum().sort_values(ascending=False)")

        # Regra 3: Se query tem "top N", deve ter .head(N)
        top_match = re.search(r'top\s+(\d+)', user_query.lower())
        if top_match:
            n = top_match.group(1)
            if f".head({n})" not in code and ".head(" not in code:
                warnings.append(f"Query pede top {n} mas código não limita resultados")
                suggestions.append(f"Adicione: .head({n})")

        # Regra 4: Código deve salvar resultado em 'result'
        if "result =" not in code:
            errors.append("Código não salva resultado em 'result'")
            suggestions.append("Adicione: result = [seu_dataframe]")

        # Regra 5: Validar sintaxe Python
        try:
            compile(code, '<string>', 'exec')
        except SyntaxError as e:
            errors.append(f"Erro de sintaxe Python: {e}")

        # Regra 6: Verificar operações perigosas
        for blocked in self.blocked_operations:
            if blocked in code:
                # Exceção: open() é permitido apenas para Parquet
                if blocked == 'open(' and 'parquet' in code.lower():
                    continue
                errors.append(f"Operação bloqueada detectada: {blocked}")

        # Regra 7: Se query menciona segmento, verificar mapeamento correto
        segment_keywords = {
            'tecido': 'TECIDOS',
            'armarinho': 'ARMARINHO E CONFECÇÃO',
            'papelaria': 'PAPELARIA',
            'casa': 'CASA E DECORAÇÃO',
            'decoração': 'CASA E DECORAÇÃO',
            'limpeza': 'MATERIAL DE LIMPEZA',
            'higiene': 'HIGIENE E BELEZA',
        }

        for keyword, correct_value in segment_keywords.items():
            if keyword in user_query.lower():
                # Verificar se o código usa o valor correto
                if correct_value not in code:
                    warnings.append(f"Query menciona '{keyword}' mas código pode não usar '{correct_value}'")
                    suggestions.append(f"Verifique se está usando: NOMESEGMENTO == '{correct_value}'")

        # Regra 8: Se há agregação, deve ter reset_index() para DataFrame limpo
        if ".groupby(" in code and ".reset_index()" not in code:
            warnings.append("Agregação sem reset_index() pode causar problemas de visualização")
            suggestions.append("Adicione .reset_index() após agregação")

        # Regra 9: Métrica de vendas deve usar VENDA_30DD
        if any(kw in user_query.lower() for kw in ["venda", "vendas", "vendido", "vendidos", "faturamento"]):
            if "VENDA_30DD" not in code and "venda" in code.lower():
                warnings.append("Query sobre vendas mas código pode não usar VENDA_30DD")
                suggestions.append("Use a coluna VENDA_30DD para métricas de vendas")

        # Regra 10: Métrica de estoque deve usar ESTOQUE_UNE
        if any(kw in user_query.lower() for kw in ["estoque", "inventário", "disponível"]):
            if "ESTOQUE_UNE" not in code and "estoque" in code.lower():
                warnings.append("Query sobre estoque mas código pode não usar ESTOQUE_UNE")
                suggestions.append("Use a coluna ESTOQUE_UNE para métricas de estoque")

        return {
            "valid": len(errors) == 0,
            "errors": errors,
            "warnings": warnings,
            "suggestions": suggestions,
            "code": code
        }

    def auto_fix(self, validation_result: Dict[str, Any], user_query: str) -> Dict[str, Any]:
        """
        Tenta corrigir automaticamente problemas simples.

        Args:
            validation_result: Resultado da validação
            user_query: Query original do usuário

        Returns:
            {
                "fixed": bool,
                "code": str,
                "fixes_applied": List[str]
            }
        """
        if validation_result["valid"]:
            return {
                "fixed": False,
                "code": validation_result["code"],
                "fixes_applied": []
            }

        code = validation_result["code"]
        fixes_applied = []

        # Fix 1: Adicionar load_data() se não existir
        if "Código não carrega dados" in str(validation_result["errors"]):
            if "df = " not in code:
                code = "df = load_data()\n" + code
                fixes_applied.append("Adicionado: df = load_data()")

        # Fix 2: Adicionar result = se não existir
        if "Código não salva resultado" in str(validation_result["errors"]):
            # Encontrar a última linha com DataFrame
            lines = code.split('\n')
            for i in range(len(lines) - 1, -1, -1):
                line = lines[i].strip()
                if line and not line.startswith('#') and '=' in line:
                    var_name = line.split('=')[0].strip()
                    if var_name != 'result':
                        code += f"\nresult = {var_name}"
                        fixes_applied.append(f"Adicionado: result = {var_name}")
                    break

        # Fix 3: Adicionar .head(N) para top N
        top_match = re.search(r'top\s+(\d+)', user_query.lower())
        if top_match and ".head(" not in code:
            n = top_match.group(1)
            if ".reset_index()" in code:
                code = code.replace(".reset_index()", f".head({n}).reset_index()")
                fixes_applied.append(f"Adicionado .head({n}) para limitar top {n}")

        # Fix 4: ✅ NOVO - Corrigir queries de ranking sem groupby
        if "Query pede ranking mas código não tem groupby()" in str(validation_result["errors"]):
            # Detectar se é um caso simples de filtro seguido de sort
            if ".sort_values(" in code and "result =" in code:
                # Tentar inferir a coluna de agrupamento
                if any(kw in user_query.lower() for kw in ["produto", "produtos"]):
                    # Adicionar groupby por NOME (nome do produto)
                    lines = code.split('\n')
                    new_lines = []
                    for line in lines:
                        if "result =" in line and ".sort_values(" in line:
                            # Inserir groupby antes do sort
                            var_name = line.split('=')[0].strip()
                            if "groupby" not in line:
                                # Reconstruir com groupby
                                new_lines.append(f"{var_name} = {var_name}.groupby('NOME')['VENDA_30DD'].sum().sort_values(ascending=False).reset_index()")
                                fixes_applied.append("Adicionado groupby('NOME') para ranking de produtos")
                            else:
                                new_lines.append(line)
                        else:
                            new_lines.append(line)
                    code = '\n'.join(new_lines)

        # Validar novamente após correções
        new_validation = self.validate(code, user_query)

        return {
            "fixed": new_validation["valid"],
            "code": code,
            "fixes_applied": fixes_applied,
            "remaining_errors": new_validation["errors"] if not new_validation["valid"] else []
        }
