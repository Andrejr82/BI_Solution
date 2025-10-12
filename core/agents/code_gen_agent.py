"""
Módulo para core/agents/code_gen_agent.py. Define a classe principal 'CodeGenAgent'. Fornece as funções: generate_and_execute_code, worker.
"""

# core/agents/code_gen_agent.py
import logging
import os
import json
import re
import pandas as pd
import time
import plotly.express as px
from typing import List, Dict, Any # Import necessary types
import threading
from queue import Queue
import pickle
import faiss
import numpy as np
from sentence_transformers import SentenceTransformer
import io
import sys
import plotly.io as pio
import uuid
from core.utils.json_utils import _clean_json_values # Import the cleaning function

from core.llm_base import BaseLLMAdapter
from core.learning.pattern_matcher import PatternMatcher
from core.validation.code_validator import CodeValidator

class CodeGenAgent:
    """
    Agente especializado em gerar e executar código Python para análise de dados.
    """
    def __init__(self, llm_adapter: BaseLLMAdapter):
        """
        Inicializa o agente, carregando o LLM, o catálogo de dados e o diretório de dados.
        """
        self.logger = logging.getLogger(__name__)
        self.llm = llm_adapter # Use o adaptador injetado
        self.parquet_dir = os.path.join(os.getcwd(), "data", "parquet")
        self.code_cache = {}

        # Carregar catálogo com descrições das colunas
        catalog_path = os.path.join(os.getcwd(), "data", "catalog_focused.json")
        try:
            with open(catalog_path, 'r', encoding='utf-8') as f:
                catalog_data = json.load(f)
                # Obter descrições das colunas do primeiro arquivo (admatao.parquet)
                self.column_descriptions = catalog_data[0].get("column_descriptions", {})
                self.logger.info(f"✅ Catálogo carregado com {len(self.column_descriptions)} colunas descritas")
        except Exception as e:
            self.logger.warning(f"⚠️ Erro ao carregar catálogo: {e}")
            self.column_descriptions = {}

        # 🚀 QUICK WIN 1: Diretórios para logs e contadores
        self.logs_dir = os.path.join(os.getcwd(), "data", "learning")
        os.makedirs(self.logs_dir, exist_ok=True)

        # 🚀 QUICK WIN 2: Contador de erros por tipo
        from collections import defaultdict
        self.error_counts = defaultdict(int)

        # 🎯 FASE 1: Pattern Matcher para exemplos contextuais
        try:
            self.pattern_matcher = PatternMatcher()
            self.logger.info("✅ PatternMatcher inicializado")
        except Exception as e:
            self.logger.warning(f"⚠️ PatternMatcher não disponível: {e}")
            self.pattern_matcher = None

        # ✅ FASE 1: Code Validator para validação pré-execução
        self.code_validator = CodeValidator()
        self.logger.info("✅ CodeValidator inicializado")

        self.logger.info("CodeGenAgent inicializado com cache de código e sistema de aprendizado.")

    def _execute_generated_code(self, code: str, local_scope: Dict[str, Any]):
        q = Queue()
        output_capture = io.StringIO()
        original_stdout = sys.stdout
        original_stderr = sys.stderr

        def worker():
            sys.stdout = output_capture
            sys.stderr = output_capture
            try:
                exec(code, local_scope)
                q.put(local_scope.get('result'))
            except Exception as e:
                q.put(e)
            finally:
                sys.stdout = original_stdout
                sys.stderr = original_stderr

        thread = threading.Thread(target=worker)
        thread.start()
        thread.join(timeout=120.0)

        captured_output = output_capture.getvalue()
        if captured_output:
            self.logger.info(f"Saída do código gerado:\n{captured_output}")

        if thread.is_alive():
            raise TimeoutError("A execução do código gerado excedeu o tempo limite.")
        else:
            result = q.get()
            if isinstance(result, Exception):
                raise result
            return result

    def generate_and_execute_code(self, input_data: Dict[str, Any]) -> dict:
        """
        Gera, executa e retorna o resultado do código Python para uma dada consulta.
        Esta versão foi refatorada para usar diretamente o prompt fornecido e injetar uma função `load_data`.
        """
        prompt = input_data.get("query", "")
        raw_data = input_data.get("raw_data", [])
        
        # O cache é simplificado, pois a lógica de RAG foi removida.
        cache_key = hash(prompt + json.dumps(raw_data, sort_keys=True) if raw_data else "")

        if cache_key in self.code_cache:
            code_to_execute = self.code_cache[cache_key]
            self.logger.info(f"Código recuperado do cache.")
        else:
            # Construir contexto com descrições das colunas mais importantes
            important_columns = [
                "PRODUTO", "NOME", "NOMESEGMENTO", "NomeCategoria", "NOMEGRUPO",
                "VENDA_30DD", "ESTOQUE_UNE", "LIQUIDO_38", "UNE_NOME", "NomeFabricante"
            ]

            column_context = "📊 COLUNAS DISPONÍVEIS:\n"
            for col in important_columns:
                if col in self.column_descriptions:
                    column_context += f"- {col}: {self.column_descriptions[col]}\n"

            # Adicionar valores válidos de segmentos com mapeamento inteligente
            valid_segments = """
**VALORES VÁLIDOS DE SEGMENTOS (NOMESEGMENTO):**
Use EXATAMENTE estes valores no código Python (incluindo acentos e plural/singular):

1. 'TECIDOS' → se usuário mencionar: tecido, tecidos, segmento tecido, tecidos e armarinhos
2. 'ARMARINHO E CONFECÇÃO' → se usuário mencionar: armarinho, confecção, aviamentos
3. 'PAPELARIA' → se usuário mencionar: papelaria, papel, cadernos
4. 'CASA E DECORAÇÃO' → se usuário mencionar: casa, decoração, utilidades domésticas
5. 'ARTES' → se usuário mencionar: artes, artesanato, pintura
6. 'SAZONAIS' → se usuário mencionar: sazonais, páscoa, natal, datas comemorativas
7. 'FESTAS' → se usuário mencionar: festas, aniversário, balões
8. 'INFORMÁTICA' → se usuário mencionar: informática, eletrônica, computadores
9. 'HIGIENE E BELEZA' → se usuário mencionar: higiene, beleza, cosméticos
10. 'ESPORTE E LAZER' → se usuário mencionar: esporte, lazer, brinquedos
11. 'EMBALAGENS E DESCARTÁVEIS' → se usuário mencionar: embalagens, descartáveis
12. 'BAZAR' → se usuário mencionar: bazar, utilidades
13. 'ELÉTRICA E MANUTENÇÃO' → se usuário mencionar: elétrica, manutenção, ferramentas
14. 'MATERIAL DE LIMPEZA' → se usuário mencionar: limpeza, produtos de limpeza

**REGRA DE OURO:** Interprete a intenção do usuário e mapeie para o valor EXATO da lista acima!
"""

            # 🎯 FASE 1: Injetar exemplos contextuais baseados em padrões
            examples_context = ""
            if self.pattern_matcher:
                try:
                    user_query = input_data.get("query", "")
                    examples_context = self.pattern_matcher.build_examples_context(user_query, max_examples=2)
                    if examples_context:
                        self.logger.info("🎯 Exemplos contextuais injetados no prompt")
                except Exception as e:
                    self.logger.warning(f"⚠️ Erro ao buscar padrões: {e}")

            system_prompt = f"""Você é um especialista em análise de dados Python com pandas e interpretação de linguagem natural.

{column_context}

{valid_segments}

{examples_context}

**INSTRUÇÕES CRÍTICAS:**
1. **INTERPRETAÇÃO INTELIGENTE**: Se o usuário mencionar "tecido" (singular), você DEVE usar 'TECIDOS' (plural) no código!
2. **MAPEAMENTO AUTOMÁTICO**: Use a lista de valores válidos acima para mapear termos do usuário → valores exatos do banco
3. **NOMES DE COLUNAS**: Use sempre MAIÚSCULAS conforme listado
4. **ACENTOS**: Mantenha acentuação exata (CONFECÇÃO, DECORAÇÃO, INFORMÁTICA, etc.)
5. **VENDAS**: Sempre use VENDA_30DD para métricas de vendas
6. **ESTOQUE**: Use ESTOQUE_UNE para estoque
7. **USE OS EXEMPLOS ACIMA** como referência se foram fornecidos!

**EXEMPLO DE MAPEAMENTO:**
- Usuário diz: "segmento tecido" → Você usa: df[df['NOMESEGMENTO'] == 'TECIDOS']
- Usuário diz: "produtos de limpeza" → Você usa: df[df['NOMESEGMENTO'] == 'MATERIAL DE LIMPEZA']
- Usuário diz: "armarinho" → Você usa: df[df['NOMESEGMENTO'] == 'ARMARINHO E CONFECÇÃO']

Siga as instruções do usuário E faça o mapeamento inteligente de termos!"""

            # O agente agora usa o prompt diretamente, sem construir um novo.
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt}
            ]

            start_llm_query = time.time()
            llm_response = self.llm.get_completion(messages=messages)
            end_llm_query = time.time()
            self.logger.info(f"Tempo de consulta LLM: {end_llm_query - start_llm_query:.4f} segundos")

            if "error" in llm_response:
                self.logger.error(f"Erro ao obter resposta do LLM: {llm_response['error']}")
                return {"type": "error", "output": "Não foi possível gerar o código de análise."}

            code_to_execute = self._extract_python_code(llm_response.get("content", ""))

            if not code_to_execute:
                self.logger.warning("Nenhum código Python foi gerado pelo LLM.")
                return {"type": "text", "output": "Não consegui gerar um script para responder à sua pergunta."}

            # 🚀 QUICK WIN 1: Validar e corrigir Top N automaticamente
            user_query = input_data.get("query", "")
            code_to_execute = self._validate_top_n(code_to_execute, user_query)

            # ✅ FASE 1: Validar código antes de executar
            validation_result = self.code_validator.validate(code_to_execute, user_query)

            if not validation_result['valid']:
                self.logger.warning(f"⚠️ Código com problemas: {validation_result['errors']}")

                # Tentar correção automática
                fix_result = self.code_validator.auto_fix(validation_result, user_query)

                if fix_result['fixed']:
                    self.logger.info(f"✅ Código corrigido automaticamente: {fix_result['fixes_applied']}")
                    code_to_execute = fix_result['code']
                else:
                    self.logger.warning(f"⚠️ Correção automática falhou. Erros restantes: {fix_result.get('remaining_errors', [])}")
                    # Continuar mesmo assim, mas com log

            # Validações adicionais com warnings (não bloqueiam execução)
            if validation_result.get('warnings'):
                self.logger.info(f"ℹ️ Avisos: {validation_result['warnings']}")

            if validation_result.get('suggestions'):
                self.logger.debug(f"💡 Sugestões: {validation_result['suggestions']}")

            self.code_cache[cache_key] = code_to_execute

        self.logger.info(f"\nCódigo a ser executado:\n---\n{code_to_execute}\n---")

        try:
            # Função helper para ser injetada no escopo de execução
            def load_data():
                parquet_file = os.path.join(self.parquet_dir, "admmat.parquet")
                if not os.path.exists(parquet_file):
                    raise FileNotFoundError(f"Arquivo Parquet não encontrado em {parquet_file}")
                # Usamos pandas diretamente aqui para simplicidade, pois o Dask já foi usado na filtragem inicial
                # ou a análise é complexa e será feita em memória.
                df = pd.read_parquet(parquet_file)

                # ✅ NORMALIZAR COLUNAS: Mapear para os nomes esperados pelo LLM
                column_mapping = {
                    'nomesegmento': 'NOMESEGMENTO',
                    'codigo': 'PRODUTO',
                    'nome_produto': 'NOME',
                    'une_nome': 'UNE',
                    'nomegrupo': 'NOMEGRUPO',
                    'ean': 'EAN',
                    'preco_38_percent': 'LIQUIDO_38',
                    'venda_30_d': 'VENDA_30DD',
                    'estoque_atual': 'ESTOQUE_UNE',
                    'embalagem': 'EMBALAGEM',
                    'tipo': 'TIPO'
                }

                # Aplicar mapeamento apenas para colunas que existem
                rename_dict = {k: v for k, v in column_mapping.items() if k in df.columns}
                df = df.rename(columns=rename_dict)

                # Converter colunas restantes para MAIÚSCULAS
                df.columns = [col.upper() if col.islower() else col for col in df.columns]

                return df

            local_scope = {
                "pd": pd,
                "px": px,
                "result": None,
                "df_raw_data": pd.DataFrame(raw_data) if raw_data else None,
                "load_data": load_data # Injeta a função no escopo
            }
            
            px.defaults.template = "plotly_white"

            start_code_execution = time.time()
            result = self._execute_generated_code(code_to_execute, local_scope)
            end_code_execution = time.time()
            self.logger.info(f"Tempo de execução do código: {end_code_execution - start_code_execution:.4f} segundos")

            # Análise do tipo de resultado
            if isinstance(result, pd.DataFrame):
                self.logger.info(f"Resultado: DataFrame com {len(result)} linhas.")
                # 🚀 QUICK WIN 2: Registrar query bem-sucedida
                self._log_successful_query(user_query, code_to_execute, len(result))
                return {"type": "dataframe", "output": result}
            elif 'plotly' in str(type(result)):
                self.logger.info(f"Resultado: Gráfico Plotly.")
                # 🚀 QUICK WIN 2: Registrar query bem-sucedida (gráfico)
                self._log_successful_query(user_query, code_to_execute, 1)
                return {"type": "chart", "output": pio.to_json(result)}
            else:
                self.logger.info(f"Resultado: Texto.")
                return {"type": "text", "output": str(result)}
        
        except TimeoutError as e:
            self.logger.error("A execução do código excedeu o tempo limite.")
            # 🚀 QUICK WIN 3: Registrar erro
            self._log_error(user_query, code_to_execute, "timeout", str(e))
            return {"type": "error", "output": "A análise demorou muito e foi interrompida."}
        except Exception as e:
            self.logger.error(f"Erro ao executar o código gerado: {e}", exc_info=True)
            # 🚀 QUICK WIN 3: Registrar erro
            error_type = type(e).__name__
            self._log_error(user_query, code_to_execute, error_type, str(e))
            return {"type": "error", "output": f"Ocorreu um erro ao executar a análise: {e}"}
    def _extract_python_code(self, text: str) -> str | None:
        """Extrai o bloco de código Python da resposta do LLM."""
        match = re.search(r'```python\n(.*)```', text, re.DOTALL)
        return match.group(1).strip() if match else None

    # 🚀 QUICK WIN METHODS
    def _validate_top_n(self, code: str, user_query: str) -> str:
        """
        QUICK WIN 1: Valida se código tem .head(N) quando usuário pede 'top N'.
        Corrige automaticamente se necessário.
        """
        query_lower = user_query.lower()

        # Verificar se usuário pediu "top N"
        top_match = re.search(r'top\s+(\d+)', query_lower)

        if top_match and '.head(' not in code:
            n = top_match.group(1)
            self.logger.warning(f"⚠️ Query pede top {n} mas código não tem .head(). Corrigindo automaticamente...")

            # Tentar adicionar .head(N) antes de .reset_index()
            if '.reset_index()' in code:
                code = code.replace('.reset_index()', f'.head({n}).reset_index()')
            # Ou antes do resultado final
            elif 'result = ' in code:
                # Encontrar a última atribuição a result
                lines = code.split('\n')
                for i in range(len(lines) - 1, -1, -1):
                    if lines[i].strip().startswith('result = '):
                        # Adicionar .head(N) se ainda não existir
                        if '.head(' not in lines[i]:
                            lines[i] = lines[i].replace('result = ', f'result = ').rstrip()
                            if not lines[i].endswith(')'):
                                lines[i] = f"{lines[i]}.head({n})"
                        break
                code = '\n'.join(lines)

            self.logger.info(f"✅ Código corrigido automaticamente com .head({n})")

        return code

    def _log_successful_query(self, user_query: str, code: str, result_rows: int):
        """
        QUICK WIN 2: Registra queries bem-sucedidas para análise futura.
        """
        from datetime import datetime

        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'query': user_query,
            'code': code,
            'rows': result_rows,
            'success': True
        }

        # Salvar em arquivo diário
        date_str = datetime.now().strftime('%Y%m%d')
        log_file = os.path.join(self.logs_dir, f'successful_queries_{date_str}.jsonl')

        try:
            with open(log_file, 'a', encoding='utf-8') as f:
                f.write(json.dumps(log_entry, ensure_ascii=False) + '\n')
            self.logger.debug(f"✅ Query registrada em {log_file}")
        except Exception as e:
            self.logger.warning(f"⚠️ Erro ao registrar query: {e}")

    def _log_error(self, user_query: str, code: str, error_type: str, error_message: str):
        """
        QUICK WIN 3: Registra erros por tipo para análise de padrões.
        """
        from datetime import datetime

        # Incrementar contador
        self.error_counts[error_type] += 1

        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'query': user_query,
            'code': code,
            'error_type': error_type,
            'error_message': str(error_message),
            'success': False
        }

        # Salvar em arquivo diário
        date_str = datetime.now().strftime('%Y%m%d')
        log_file = os.path.join(self.logs_dir, f'error_log_{date_str}.jsonl')

        try:
            with open(log_file, 'a', encoding='utf-8') as f:
                f.write(json.dumps(log_entry, ensure_ascii=False) + '\n')

            # Também salvar contador consolidado
            counter_file = os.path.join(self.logs_dir, f'error_counts_{date_str}.json')
            with open(counter_file, 'w', encoding='utf-8') as f:
                json.dump(dict(self.error_counts), f, indent=2, ensure_ascii=False)

            self.logger.debug(f"⚠️ Erro registrado: {error_type} (total: {self.error_counts[error_type]})")
        except Exception as e:
            self.logger.warning(f"⚠️ Erro ao registrar erro: {e}")
