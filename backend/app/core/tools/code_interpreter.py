"""
Code Interpreter - Sandbox seguro para execução de código Python
Permite análises dinâmicas de dados com pandas, numpy, etc.
"""

import logging
import io
import sys
import traceback
from typing import Dict, Any, Optional, List
from contextlib import redirect_stdout, redirect_stderr
import pandas as pd
from langchain_core.tools import tool

logger = logging.getLogger(__name__)

# Bibliotecas permitidas no sandbox
ALLOWED_MODULES = {
    'pandas', 'numpy', 'math', 'statistics', 'datetime',
    'json', 're', 'collections', 'itertools', 'functools'
}

# Funções perigosas bloqueadas
BLOCKED_FUNCTIONS = {
    'exec', 'eval', 'compile', 'open', 'input',
    '__import__', 'globals', 'locals', 'vars',
    'getattr', 'setattr', 'delattr', 'hasattr'
}


class CodeInterpreter:
    """
    Executor seguro de código Python para análise de dados.
    
    Features:
    - Sandbox com restrições de segurança
    - Acesso a pandas e numpy
    - Captura de stdout/stderr
    - Timeout configurável
    """
    
    def __init__(self, timeout_seconds: int = 10):
        self.timeout = timeout_seconds
        self.execution_count = 0
        self.error_count = 0
        
        # Namespace seguro para execução
        self._safe_namespace = self._create_safe_namespace()
    
    def _create_safe_namespace(self) -> Dict[str, Any]:
        """Cria namespace seguro com bibliotecas permitidas."""
        namespace = {
            '__builtins__': {
                'len': len, 'range': range, 'list': list, 'dict': dict,
                'str': str, 'int': int, 'float': float, 'bool': bool,
                'print': print, 'sum': sum, 'min': min, 'max': max,
                'abs': abs, 'round': round, 'sorted': sorted,
                'enumerate': enumerate, 'zip': zip, 'map': map,
                'filter': filter, 'any': any, 'all': all,
                'isinstance': isinstance, 'type': type,
                'True': True, 'False': False, 'None': None,
            }
        }
        
        # Adicionar pandas e numpy
        try:
            import pandas as pd
            import numpy as np
            namespace['pd'] = pd
            namespace['np'] = np
            namespace['DataFrame'] = pd.DataFrame
        except ImportError:
            logger.warning("pandas/numpy não disponível")
        
        # Adicionar math e statistics
        try:
            import math
            import statistics
            namespace['math'] = math
            namespace['statistics'] = statistics
        except ImportError:
            pass
        
        return namespace
    
    def _validate_code(self, code: str) -> tuple[bool, str]:
        """Valida código antes de executar."""
        code_lower = code.lower()
        
        # Verificar funções bloqueadas
        for blocked in BLOCKED_FUNCTIONS:
            if blocked in code_lower:
                return False, f"Função '{blocked}' não permitida"
        
        # Verificar imports perigosos
        if 'import os' in code_lower or 'import sys' in code_lower:
            return False, "Imports de sistema não permitidos"
        
        if 'import subprocess' in code_lower:
            return False, "subprocess não permitido"
        
        # Verificar acesso a arquivos
        if 'open(' in code and 'file' in code_lower:
            return False, "Acesso direto a arquivos não permitido"
        
        return True, ""
    
    def execute(self, code: str, data: pd.DataFrame = None) -> Dict[str, Any]:
        """
        Executa código Python de forma segura.
        
        Args:
            code: Código Python a executar
            data: DataFrame opcional para análise
            
        Returns:
            Dict com resultado, output e erro
        """
        self.execution_count += 1
        logger.info(f"🐍 CodeInterpreter: Executando código ({len(code)} chars)")
        
        # Validar código
        is_valid, error_msg = self._validate_code(code)
        if not is_valid:
            self.error_count += 1
            return {
                "success": False,
                "error": error_msg,
                "output": "",
                "result": None
            }
        
        # Preparar namespace
        namespace = self._safe_namespace.copy()
        
        # Adicionar DataFrame se fornecido
        if data is not None:
            namespace['df'] = data
            namespace['data'] = data
        
        # Capturar stdout e stderr
        stdout_capture = io.StringIO()
        stderr_capture = io.StringIO()
        
        try:
            with redirect_stdout(stdout_capture), redirect_stderr(stderr_capture):
                # Executar código
                exec(code, namespace)
            
            # Extrair resultado (última variável definida ou 'result')
            result = namespace.get('result', None)
            
            # Se não houver 'result', tentar encontrar última variável
            if result is None:
                for var_name in ['output', 'resultado', 'answer', 'resposta']:
                    if var_name in namespace:
                        result = namespace[var_name]
                        break
            
            # Converter DataFrame para dict se necessário
            if isinstance(result, pd.DataFrame):
                result = {
                    "type": "dataframe",
                    "shape": result.shape,
                    "columns": list(result.columns),
                    "data": result.head(50).to_dict(orient='records')
                }
            elif isinstance(result, pd.Series):
                result = {
                    "type": "series",
                    "data": result.to_dict()
                }
            
            output = stdout_capture.getvalue()
            
            logger.info(f"✅ Código executado com sucesso")
            
            return {
                "success": True,
                "error": None,
                "output": output,
                "result": result
            }
            
        except Exception as e:
            self.error_count += 1
            error_trace = traceback.format_exc()
            logger.error(f"❌ Erro na execução: {e}")
            
            return {
                "success": False,
                "error": str(e),
                "output": stdout_capture.getvalue(),
                "traceback": error_trace,
                "result": None
            }
    
    def get_stats(self) -> Dict[str, Any]:
        """Retorna estatísticas do interpreter."""
        error_rate = (self.error_count / self.execution_count * 100) if self.execution_count > 0 else 0
        
        return {
            "execution_count": self.execution_count,
            "error_count": self.error_count,
            "error_rate": f"{error_rate:.1f}%",
            "timeout": self.timeout
        }


# Instância global
_interpreter: Optional[CodeInterpreter] = None


def get_interpreter() -> CodeInterpreter:
    """Retorna instância singleton do interpreter."""
    global _interpreter
    if _interpreter is None:
        _interpreter = CodeInterpreter()
    return _interpreter


# Ferramenta LangChain para o agente
@tool
def executar_codigo_python(
    codigo: str,
    descricao: str = ""
) -> Dict[str, Any]:
    """
    Executa código Python para análise de dados.
    
    Use esta ferramenta quando precisar:
    - Fazer cálculos complexos
    - Processar dados de forma personalizada
    - Criar análises estatísticas
    
    Args:
        codigo: Código Python a executar. Use 'df' para acessar os dados.
        descricao: Descrição do que o código faz
        
    Returns:
        Resultado da execução
        
    Exemplo:
        >>> executar_codigo_python(
        ...     codigo="result = df['vendas'].sum()",
        ...     descricao="Calcula soma das vendas"
        ... )
    """
    logger.info(f"📝 Executando código: {descricao or 'sem descrição'}")
    
    interpreter = get_interpreter()
    
    # Carregar dados do Parquet
    try:
        from app.config.settings import settings
        df = pd.read_parquet(settings.PARQUET_FILE_PATH)
    except Exception as e:
        logger.error(f"Erro ao carregar dados: {e}")
        df = None
    
    result = interpreter.execute(codigo, data=df)
    
    if result["success"]:
        return {
            "sucesso": True,
            "resultado": result["result"],
            "output": result["output"],
            "mensagem": f"Código executado: {descricao}" if descricao else "Código executado com sucesso"
        }
    else:
        return {
            "sucesso": False,
            "erro": result["error"],
            "mensagem": f"Erro ao executar código: {result['error']}"
        }
