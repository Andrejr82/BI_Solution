# backend/app/core/agents/code_gen_agent.py

import json
import re
from typing import Any, Dict, List, Optional
from langchain_core.language_models import BaseChatModel
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.runnables import RunnablePassthrough

from app.core.utils.field_mapper import FieldMapper
from app.core.utils.error_handler import APIError
from app.core.utils.query_history import QueryHistory
from app.core.utils.response_cache import ResponseCache # Placeholder, will be implemented later
from app.config.settings import settings # For cache settings

import logging
logger = logging.getLogger(__name__) # Added logger

from app.core.learning.pattern_matcher import PatternMatcher
from app.core.rag.query_retriever import QueryRetriever

import os
from functools import lru_cache

# Helper to load prompts from files
@lru_cache(maxsize=None)
def _load_prompt_template(filename: str) -> str:
    current_dir = os.path.dirname(__file__)
    prompt_path = os.path.join(current_dir, "..", "prompts", filename)
    with open(prompt_path, "r", encoding="utf-8") as f:
        return f.read()

class CodeGenAgent:
    """
    Agent responsible for generating, validating, executing Python code for data analysis,
    and self-healing in case of errors.
    """
    def __init__(
        self,
        llm: BaseChatModel,
        field_mapper: FieldMapper,
        query_retriever: QueryRetriever,
        pattern_matcher: PatternMatcher,
        response_cache: ResponseCache = None,
        query_history: QueryHistory = None,
    ):
        self.llm = llm
        self.field_mapper = field_mapper
        self.query_retriever = query_retriever
        self.pattern_matcher = pattern_matcher
        self.response_cache = response_cache if response_cache else ResponseCache()
        self.query_history = query_history if query_history else QueryHistory()

        self.code_gen_prompt_template = _load_prompt_template("code_generation_system_prompt.md")
        self.code_gen_prompt = ChatPromptTemplate.from_messages([
            ("system", self.code_gen_prompt_template), # available_columns will be formatted at invoke time
            ("human", "{user_query}\nSchema: {data_schema_info}\nExamples: {few_shot_examples}\nCode:"),
        ])
        
        # Output parser for structured response from LLM
        self.output_parser = JsonOutputParser()

    def _get_code_generation_system_prompt(self) -> str:
        # This method is no longer needed as prompt is loaded from file
        pass

    def generate_and_execute_python_code(self, user_query: str, data_schema: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generates Python code based on user query and data schema, executes it,
        and returns results, including chart specifications if requested.
        Includes self-healing for common errors.
        """
        cache_key = self.response_cache.generate_key(user_query)
        cached_response = self.response_cache.get(cache_key)
        if cached_response:
            print(f"CodeGenAgent: Cache hit for query: {user_query}")
            return cached_response

        # Override available_columns with ACTUAL DataFrame columns from une_tools
        # This prevents the LLM from hallucinating column names based on the FieldMapper catalog
        available_columns = ['codigo', 'nome_produto', 'une', 'estoque_atual', 'linha_verde', 'mc', 'venda_30_d', 'nomesegmento', 'NOMEFABRICANTE']

        # T2.3.1: Integrate with PatternMatcher (few-shot) and QueryRetriever (RAG)
        few_shot_examples = self._get_few_shot_examples(user_query)

        # T2.3.5: Create prompt of code generation
        code_gen_chain = (
            RunnablePassthrough.assign(
                available_columns=lambda x: ", ".join(available_columns),
                few_shot_examples=lambda x: self._get_few_shot_examples(x["user_query"]) # Will use query_retriever later
            )
            | self.code_gen_prompt.partial(available_columns=", ".join(available_columns)) # Format system prompt here
            | self.llm
            | self.output_parser
        )

        retries = 0
        max_retries = 3
        generated_code_output = None
        while retries <= max_retries:
            try:
                # Assuming the LLM will return a JSON string
                llm_response = code_gen_chain.invoke({
                    "user_query": user_query,
                    "data_schema_info": data_schema,
                    "available_columns": available_columns,
                    "few_shot_examples": few_shot_examples
                })
                
                generated_code_output = llm_response # LLM should return parsed JSON

                # T2.3.2: Validate generated code for 'top N' and auto-recovery (T2.3.3)
                code_to_execute = self._validate_and_heal_code(generated_code_output.get("code", ""), user_query, retries)
                
                # Execute the code - Placeholder for a safe execution environment
                execution_result = self._safely_execute_code(code_to_execute, available_columns)
                
                final_response = {
                    "type": "code_result",
                    "result": execution_result,
                    "chart_spec": generated_code_output.get("chart_spec") # Pass through chart spec if present
                }
                self.response_cache.set(cache_key, final_response)
                return final_response

            except APIError as e:
                logger.warning(f"CodeGenAgent: APIError during code generation/execution: {e.message}. Retrying...")
                retries += 1
                if retries > max_retries:
                    raise APIError(f"Falha na geração/execução de código após {max_retries} tentativas: {e.message}", status_code=500) from e
                # Potentially modify prompt for retry based on error
                user_query = f"{user_query}\n\nPrevious attempt failed with error: {e.message}. Please refine the code."
            except Exception as e:
                logger.error(f"CodeGenAgent: Unexpected error during code generation/execution: {e}", exc_info=True)
                retries += 1
                if retries > max_retries:
                    raise APIError(f"Erro inesperado durante a geração/execução de código após {max_retries} tentativas: {str(e)}", status_code=500) from e
                user_query = f"{user_query}\n\nPrevious attempt failed with a general error: {str(e)}. Please refine the code."

        raise APIError("CodeGenAgent: Falha crítica na geração e execução de código.", status_code=500)

    def _get_few_shot_examples(self, user_query: str) -> str:
        """
        Combines pattern matching and RAG to provide few-shot examples.
        T2.3.1: Integrate with PatternMatcher (few-shot) and QueryRetriever (RAG).
        """
        examples_str = ""
        # From PatternMatcher (exact/known patterns)
        pattern_match = self.pattern_matcher.match_pattern(user_query)
        if pattern_match and pattern_match.get("example_code"):
            examples_str += f"Exemplo de padrão correspondente: {pattern_match['pattern_name']}\n```python\n{pattern_match['example_code']}\n```\n"

        # From QueryRetriever (semantically similar past queries)
        similar_queries = self.query_retriever.get_similar_queries(user_query)
        if similar_queries:
            examples_str += "Exemplos de queries similares passadas:\n"
            for sq in similar_queries:
                examples_str += f"- Query: {sq.get('query')}\n  Código: ```python\n{sq.get('code')}\n```\n"
        
        if not examples_str:
            examples_str = "Nenhum exemplo few-shot adicional encontrado."
        return examples_str


    def _validate_and_heal_code(self, code: str, user_query: str, attempt: int) -> str:
        """
        T2.3.2: Implement validation for 'top N' and T2.3.3: auto-recovery of common errors.
        """
        if not code:
            raise APIError("Generated code is empty.", status_code=400)
        
        # T2.3.2: Implement validation of `top N`
        code = self._validate_top_n(code, user_query)

        # T2.3.3: Implement auto-recovery of common errors based on attempt
        if attempt > 0: # Only try healing on subsequent attempts
            code = self._attempt_auto_healing(code, user_query)
        
        return code

    def _validate_top_n(self, code: str, user_query: str) -> str:
        """
        Detects "top N" or similar phrases in the user query and ensures
        '.head(N)' or '.tail(N)' is applied to the final result if relevant.
        """
        # Example: "top 10 produtos", "os 5 maiores"
        top_n_match = re.search(r'(top|os|as)\s*(\d+)\s*(maiores|menores)?', user_query, re.IGNORECASE)
        if top_n_match:
            n = int(top_n_match.group(2))
            maior_menor = top_n_match.group(3)
            
            # Simple heuristic: look for the last assignment to 'result' or 'final_output'
            # and append .head(n) or .tail(n) if not already present.
            lines = code.split('\n')
            new_lines = []
            applied_head_tail = False
            for line in reversed(lines):
                if not applied_head_tail and ("result =" in line or "final_output =" in line) and ".head(" not in line and ".tail(" not in line:
                    indent = len(line) - len(line.lstrip())
                    if maior_menor and "menores" in maior_menor.lower():
                        new_lines.append(f"{ ' ' * indent}{line.strip()}.tail({n})")
                    else:
                        new_lines.append(f"{ ' ' * indent}{line.strip()}.head({n})")
                    applied_head_tail = True
                else:
                    new_lines.append(line)
            return "\n".join(reversed(new_lines))
        return code

    def _attempt_auto_healing(self, code: str, user_query: str) -> str:
        """
        Implements basic self-healing for common code errors.
        This is a very simplistic example and would be more sophisticated with LLM interaction.
        """
        # Example 1: Remove .compute() if it's causing issues with Polars
        if ".compute()" in code and "PolarsError: compute" in user_query: # Check for error msg in user_query for context
            code = code.replace(".compute()", "")
            logger.info("Auto-healing: Removed .compute() from code.")
            
        # Example 2: Add .dropna() for ambiguous NA errors
        if "NA ambiguous" in user_query and ".dropna()" not in code:
            # Find a suitable place to insert .dropna()
            lines = code.split('\n')
            new_lines = []
            inserted_dropna = False
            for line in lines:
                new_lines.append(line)
                if "df." in line and "groupby" in line and not inserted_dropna: # Example heuristic
                    new_lines.append(f"{ ' ' * (len(line) - len(line.lstrip()))}.dropna()")
                    inserted_dropna = True
            if inserted_dropna:
                code = "\n".join(new_lines)
                logger.info("Auto-healing: Added .dropna() to code.")
        
        # Example 3: Suggest column correction via FieldMapper if error indicates missing column
        if "ColumnNotFound" in user_query: # Placeholder for error message
            missing_col_match = re.search(r"ColumnNotFound:\s*'([^']+)'", user_query)
            if missing_col_match:
                missing_col = missing_col_match.group(1)
                suggestion = self.field_mapper.suggest_correction(missing_col)
                if suggestion and suggestion != missing_col:
                    logger.info(f"Auto-healing: Suggested correction for missing column '{missing_col}' to '{suggestion}'.")
                    # This would ideally involve regenerating code with the corrected column
                    # For now, it's just a log.
        return code

    def _safely_execute_code(self, code: str, data_schema: Dict[str, Any]) -> Dict[str, Any]:
        """
        Executes the generated Python code in a safe environment.
        This is a critical component for security.
        """
        # CRITICAL: This is a simplified example. In a production system,
        # code execution should happen in an isolated sandbox (e.g., Docker container, separate process)
        # to prevent arbitrary code execution vulnerabilities.
        
        # Load real data from Parquet using une_tools
        import polars as pl # Import polars here to ensure it's available for execution context
        from app.core.tools.une_tools import _load_data

        # Load real data from Parquet files
        pandas_df = _load_data()  # Returns pandas DataFrame
        df = pl.from_pandas(pandas_df)  # Convert to polars DataFrame
        
        # Provide necessary libraries and the DataFrame in the execution context
        # Restrict builtins for enhanced safety
        exec_globals = {
            "pl": pl,
            "df": df,
            "json": json,
            "__builtins__": {
                "list": list, "dict": dict, "str": str, "int": int, "float": float,
                "len": len, "sum": sum, "min": min, "max": max, "range": range,
                "round": round, "abs": abs, "Exception": Exception, "ValueError": ValueError,
                "TypeError": TypeError, "sorted": sorted, "enumerate": enumerate, 
                "zip": zip, "set": set, "tuple": tuple, "any": any, "all": all, "bool": bool
            }
        }

        try:
            exec(code, exec_globals)
            
            result = exec_globals.get("final_output", {}).get("result", {})
            chart_spec = exec_globals.get("final_output", {}).get("chart_spec")

            # Ensure result is JSON-serializable if it's a Polars object
            if isinstance(result, pl.DataFrame):
                result = result.to_dicts()
            elif isinstance(result, pl.Series):
                 result = result.to_list()
            elif isinstance(result, list) and all(isinstance(i, (pl.Series, pl.DataFrame)) for i in result):
                 result = [item.to_dicts() if isinstance(item, pl.DataFrame) else item.to_list() for item in result]
            
            return {"result": result, "chart_spec": chart_spec}

        except Exception as e:
            # This exception is caught by the error_handler_decorator
            raise APIError(
                message=f"Erro durante a execução do código Python: {str(e)}",
                status_code=400,
                details={"code_executed": code, "error_type": type(e).__name__, "error_detail": str(e)}
            )

