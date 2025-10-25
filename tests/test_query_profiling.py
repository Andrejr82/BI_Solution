"""
Script de Profiling Detalhado para Análise de Performance de Queries

Objetivo: Identificar bottlenecks na execução da query "KPIs principais por segmento une mad"
Data: 2025-10-21
"""

import sys
import os
import time
import logging
import json
from datetime import datetime
import tracemalloc
import psutil
from typing import Dict, Any

# Fix encoding para Windows
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Adicionar path do projeto
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Configurar logging detalhado
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Imports do sistema
from core.llm_adapter import GeminiLLMAdapter
from core.connectivity.parquet_adapter import ParquetAdapter
from core.agents.code_gen_agent import CodeGenAgent

class QueryProfiler:
    """Profiler detalhado para análise de queries."""

    def __init__(self):
        self.metrics = {
            'timestamps': {},
            'memory_snapshots': {},
            'cpu_usage': {},
            'io_stats': {}
        }
        self.process = psutil.Process()

    def start(self, phase: str):
        """Inicia medição de uma fase."""
        self.metrics['timestamps'][f'{phase}_start'] = time.time()

        # Memory snapshot
        mem_info = self.process.memory_info()
        self.metrics['memory_snapshots'][f'{phase}_start'] = {
            'rss_mb': mem_info.rss / (1024 ** 2),
            'vms_mb': mem_info.vms / (1024 ** 2)
        }

        # CPU snapshot
        self.metrics['cpu_usage'][f'{phase}_start'] = self.process.cpu_percent(interval=0.1)

        # IO snapshot
        try:
            io_counters = self.process.io_counters()
            self.metrics['io_stats'][f'{phase}_start'] = {
                'read_mb': io_counters.read_bytes / (1024 ** 2),
                'write_mb': io_counters.write_bytes / (1024 ** 2)
            }
        except AttributeError:
            # IO counters não disponível em todas as plataformas
            self.metrics['io_stats'][f'{phase}_start'] = {
                'read_mb': 0,
                'write_mb': 0
            }

        logger.info(f"⏱️  [{phase}] START - RAM: {self.metrics['memory_snapshots'][f'{phase}_start']['rss_mb']:.1f}MB")

    def end(self, phase: str):
        """Finaliza medição de uma fase."""
        self.metrics['timestamps'][f'{phase}_end'] = time.time()

        # Memory snapshot
        mem_info = self.process.memory_info()
        self.metrics['memory_snapshots'][f'{phase}_end'] = {
            'rss_mb': mem_info.rss / (1024 ** 2),
            'vms_mb': mem_info.vms / (1024 ** 2)
        }

        # CPU snapshot
        self.metrics['cpu_usage'][f'{phase}_end'] = self.process.cpu_percent(interval=0.1)

        # IO snapshot
        try:
            io_counters = self.process.io_counters()
            self.metrics['io_stats'][f'{phase}_end'] = {
                'read_mb': io_counters.read_bytes / (1024 ** 2),
                'write_mb': io_counters.write_bytes / (1024 ** 2)
            }
        except AttributeError:
            self.metrics['io_stats'][f'{phase}_end'] = {
                'read_mb': 0,
                'write_mb': 0
            }

        # Calcular deltas
        elapsed = self.metrics['timestamps'][f'{phase}_end'] - self.metrics['timestamps'][f'{phase}_start']
        mem_delta = self.metrics['memory_snapshots'][f'{phase}_end']['rss_mb'] - self.metrics['memory_snapshots'][f'{phase}_start']['rss_mb']
        io_read_delta = self.metrics['io_stats'][f'{phase}_end']['read_mb'] - self.metrics['io_stats'][f'{phase}_start']['read_mb']

        logger.info(f"✅ [{phase}] END - Tempo: {elapsed:.2f}s | RAM Δ: {mem_delta:+.1f}MB | Disk read: {io_read_delta:.1f}MB")

        return {
            'elapsed_s': elapsed,
            'memory_delta_mb': mem_delta,
            'io_read_delta_mb': io_read_delta
        }

    def get_report(self) -> Dict[str, Any]:
        """Gera relatório completo de profiling."""
        report = {
            'summary': {},
            'phases': {},
            'bottlenecks': []
        }

        # Calcular duração de cada fase
        phases = set([k.replace('_start', '').replace('_end', '') for k in self.metrics['timestamps'].keys()])

        for phase in phases:
            if f'{phase}_start' in self.metrics['timestamps'] and f'{phase}_end' in self.metrics['timestamps']:
                elapsed = self.metrics['timestamps'][f'{phase}_end'] - self.metrics['timestamps'][f'{phase}_start']
                mem_delta = self.metrics['memory_snapshots'][f'{phase}_end']['rss_mb'] - self.metrics['memory_snapshots'][f'{phase}_start']['rss_mb']
                io_delta = self.metrics['io_stats'][f'{phase}_end']['read_mb'] - self.metrics['io_stats'][f'{phase}_start']['read_mb']

                report['phases'][phase] = {
                    'elapsed_s': round(elapsed, 3),
                    'memory_delta_mb': round(mem_delta, 2),
                    'io_read_mb': round(io_delta, 2),
                    'cpu_avg_percent': round(
                        (self.metrics['cpu_usage'][f'{phase}_start'] + self.metrics['cpu_usage'][f'{phase}_end']) / 2, 1
                    )
                }

                # Identificar bottlenecks
                if elapsed > 1.0:
                    report['bottlenecks'].append({
                        'phase': phase,
                        'issue': 'slow_execution',
                        'elapsed_s': round(elapsed, 3),
                        'threshold_s': 1.0
                    })

                if mem_delta > 100:
                    report['bottlenecks'].append({
                        'phase': phase,
                        'issue': 'high_memory_usage',
                        'memory_delta_mb': round(mem_delta, 2),
                        'threshold_mb': 100
                    })

        # Total
        if 'total_start' in self.metrics['timestamps'] and 'total_end' in self.metrics['timestamps']:
            report['summary']['total_time_s'] = round(
                self.metrics['timestamps']['total_end'] - self.metrics['timestamps']['total_start'], 3
            )
            report['summary']['total_memory_mb'] = round(
                self.metrics['memory_snapshots']['total_end']['rss_mb'] - self.metrics['memory_snapshots']['total_start']['rss_mb'], 2
            )

        return report


def test_problematic_query():
    """
    Testa a query problemática com profiling detalhado.
    Query: "KPIs principais por segmento une mad"
    """
    print("\n" + "="*80)
    print("🔍 ANÁLISE DE PERFORMANCE - Query Problemática")
    print("="*80 + "\n")

    query = "KPIs principais por segmento une mad"
    print(f"Query: {query}\n")

    # Inicializar profiler
    profiler = QueryProfiler()

    try:
        # ============================================================
        # FASE 0: INICIALIZAÇÃO
        # ============================================================
        profiler.start('total')
        profiler.start('initialization')

        logger.info("Inicializando componentes...")

        # LLM Adapter
        llm_adapter = GeminiLLMAdapter()

        # Parquet Adapter
        parquet_path = os.path.join(os.getcwd(), "data", "parquet", "*.parquet")
        parquet_adapter = ParquetAdapter(parquet_path)

        # Code Gen Agent
        code_gen_agent = CodeGenAgent(llm_adapter, parquet_adapter)

        profiler.end('initialization')

        # ============================================================
        # FASE 1: GERAÇÃO DE CÓDIGO (LLM)
        # ============================================================
        profiler.start('code_generation')

        logger.info("Gerando código Python com LLM...")

        prompt = f"""
**TAREFA:** Você deve escrever um script Python para responder à pergunta do usuário.

**INSTRUÇÕES OBRIGATÓRIAS:**
1. **CARREGUE OS DADOS:** Inicie seu script com a linha: `df = load_data()`
2. **RESPONDA À PERGUNTA:** Usando o dataframe `df`, escreva o código para responder à seguinte pergunta: "{query}"
3. **SALVE O RESULTADO NA VARIÁVEL `result`:** A última linha do seu script DEVE ser a atribuição do resultado final à variável `result`.

**Seu Script Python:**
"""

        input_data = {
            "query": prompt,
            "raw_data": None
        }

        # NÃO executar ainda - apenas gerar código
        llm_response = llm_adapter.get_completion(
            messages=[
                {"role": "system", "content": "Você é um especialista em análise de dados Python."},
                {"role": "user", "content": prompt}
            ]
        )

        # Extrair código
        import re
        code_match = re.search(r'```python\n(.*)```', llm_response.get('content', ''), re.DOTALL)
        generated_code = code_match.group(1).strip() if code_match else None

        profiler.end('code_generation')

        if generated_code:
            print("\n" + "="*80)
            print("📝 CÓDIGO GERADO:")
            print("="*80)
            print(generated_code)
            print("="*80 + "\n")

        # ============================================================
        # FASE 2: LOAD_DATA() - CRÍTICO!
        # ============================================================
        profiler.start('load_data_execution')

        logger.info("🚨 Iniciando load_data() - FASE CRÍTICA...")

        # Monitorar memória durante load_data()
        tracemalloc.start()
        mem_before = psutil.virtual_memory()

        try:
            # Simular load_data() (igual ao CodeGenAgent)
            import dask.dataframe as dd

            profiler.start('dask_read_parquet')
            ddf = dd.read_parquet(parquet_path, engine='pyarrow')
            profiler.end('dask_read_parquet')

            # Conversão de tipos (igual ao código original)
            profiler.start('type_conversion')
            logger.info("Convertendo tipos de colunas...")

            if 'ESTOQUE_UNE' in ddf.columns or 'estoque_atual' in ddf.columns:
                estoque_col = 'ESTOQUE_UNE' if 'ESTOQUE_UNE' in ddf.columns else 'estoque_atual'
                ddf[estoque_col] = dd.to_numeric(ddf[estoque_col], errors='coerce').fillna(0)

            profiler.end('type_conversion')

            # COMPUTE - AQUI ESTÁ O PROBLEMA!
            profiler.start('dask_compute')
            logger.info("🚨 Chamando ddf.compute() - CARREGANDO TUDO NA MEMÓRIA...")

            df_pandas = ddf.compute()

            profiler.end('dask_compute')

            # Memória após compute
            mem_after = psutil.virtual_memory()
            current, peak = tracemalloc.get_traced_memory()
            tracemalloc.stop()

            logger.info(f"✅ load_data() concluído - DataFrame shape: {df_pandas.shape}")
            logger.info(f"📊 Memória antes: {mem_before.used / (1024**3):.2f}GB")
            logger.info(f"📊 Memória depois: {mem_after.used / (1024**3):.2f}GB")
            logger.info(f"📊 Memória alocada (tracemalloc): current={current / (1024**2):.1f}MB, peak={peak / (1024**2):.1f}MB")

        except MemoryError as e:
            logger.error(f"❌ MemoryError durante load_data(): {e}")
            profiler.end('dask_compute')
            raise
        except Exception as e:
            logger.error(f"❌ Erro durante load_data(): {e}")
            profiler.end('dask_compute')
            raise

        profiler.end('load_data_execution')

        # ============================================================
        # FASE 3: EXECUÇÃO DO CÓDIGO GERADO
        # ============================================================
        if generated_code:
            profiler.start('user_code_execution')

            logger.info("Executando código gerado do usuário...")

            # Criar escopo local (igual ao CodeGenAgent)
            import pandas as pd

            local_scope = {
                "pd": pd,
                "df": df_pandas,  # Já carregado
                "result": None
            }

            try:
                # Executar código gerado
                exec(generated_code, local_scope)
                result = local_scope.get('result')

                logger.info(f"✅ Código executado - Resultado: {type(result)}")
                if hasattr(result, 'shape'):
                    logger.info(f"   Shape: {result.shape}")

            except Exception as e:
                logger.error(f"❌ Erro ao executar código: {e}")

            profiler.end('user_code_execution')

        # ============================================================
        # FINALIZAR
        # ============================================================
        profiler.end('total')

    except Exception as e:
        logger.error(f"❌ ERRO CRÍTICO: {e}")
        import traceback
        traceback.print_exc()

        profiler.end('total')

    # ============================================================
    # GERAR RELATÓRIO
    # ============================================================
    print("\n" + "="*80)
    print("📊 RELATÓRIO DE PROFILING")
    print("="*80 + "\n")

    report = profiler.get_report()

    # Imprimir fases
    print("🕐 Tempo por Fase:")
    print("-" * 80)

    phases_sorted = sorted(report['phases'].items(), key=lambda x: x[1]['elapsed_s'], reverse=True)

    for phase, metrics in phases_sorted:
        print(f"  {phase:30s} | {metrics['elapsed_s']:8.3f}s | RAM Δ: {metrics['memory_delta_mb']:+8.2f}MB | Disk: {metrics['io_read_mb']:8.2f}MB")

    print("\n" + "="*80)
    print("🚨 BOTTLENECKS IDENTIFICADOS:")
    print("="*80 + "\n")

    if report['bottlenecks']:
        for i, bottleneck in enumerate(report['bottlenecks'], 1):
            print(f"{i}. Fase: {bottleneck['phase']}")
            print(f"   Problema: {bottleneck['issue']}")

            if 'elapsed_s' in bottleneck:
                print(f"   Tempo: {bottleneck['elapsed_s']:.3f}s (threshold: {bottleneck['threshold_s']:.1f}s)")

            if 'memory_delta_mb' in bottleneck:
                print(f"   Memória: {bottleneck['memory_delta_mb']:.2f}MB (threshold: {bottleneck['threshold_mb']:.1f}MB)")

            print()
    else:
        print("✅ Nenhum bottleneck detectado!\n")

    # Summary
    if 'summary' in report and report['summary']:
        print("="*80)
        print("📋 RESUMO GERAL:")
        print("="*80)
        print(f"  Tempo Total: {report['summary'].get('total_time_s', 0):.3f}s")
        print(f"  Memória Total: {report['summary'].get('total_memory_mb', 0):+.2f}MB")
        print()

    # Salvar relatório JSON
    output_dir = os.path.join(os.getcwd(), "reports", "profiling")
    os.makedirs(output_dir, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = os.path.join(output_dir, f"query_profiling_{timestamp}.json")

    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2, ensure_ascii=False)

    print(f"💾 Relatório salvo em: {output_file}\n")

    return report


if __name__ == "__main__":
    try:
        report = test_problematic_query()

        # Análise final
        print("\n" + "="*80)
        print("🎯 CONCLUSÕES E RECOMENDAÇÕES")
        print("="*80 + "\n")

        # Identificar fase mais lenta
        if 'phases' in report and report['phases']:
            slowest_phase = max(report['phases'].items(), key=lambda x: x[1]['elapsed_s'])
            print(f"⏱️  Fase mais lenta: {slowest_phase[0]} ({slowest_phase[1]['elapsed_s']:.3f}s)")

            # Recomendações baseadas na fase
            if 'load_data' in slowest_phase[0] or 'dask_compute' in slowest_phase[0]:
                print("\n🔧 RECOMENDAÇÕES:")
                print("  1. ⚠️  load_data() está carregando TODOS os dados (2.2M linhas)")
                print("  2. ✅ SOLUÇÃO: Aplicar filtros ANTES de compute()")
                print("  3. ✅ Implementar Plano A: load_data(filters={'UNE': 'MAD'})")
                print("  4. ✅ Ou Plano B: Retornar Polars LazyFrame e filtrar lazy")
                print()

            if 'code_generation' in slowest_phase[0]:
                print("\n🔧 RECOMENDAÇÕES:")
                print("  1. ⚠️  LLM está demorando muito para gerar código")
                print("  2. ✅ Cache de código pode ajudar")
                print("  3. ✅ Reduzir tamanho do prompt")
                print()

        print("="*80 + "\n")

    except KeyboardInterrupt:
        print("\n\n⚠️  Teste interrompido pelo usuário.\n")
    except Exception as e:
        print(f"\n\n❌ ERRO CRÍTICO: {e}\n")
        import traceback
        traceback.print_exc()
