"""
Script de Validação de Integridade de Dados e Performance
Agent_Solution_BI - BI Agent (Caçulinha BI)

Valida estrutura de dados, cache, learning e gera KPIs do sistema.
"""

import os
import json
import pandas as pd
import pyarrow.parquet as pq
from pathlib import Path
from datetime import datetime, timedelta
from collections import defaultdict
import hashlib
import traceback

# Configuração de caminhos
BASE_DIR = Path(r"C:\Users\André\Documents\Agent_Solution_BI")
DATA_DIR = BASE_DIR / "data"
CACHE_DIR = DATA_DIR / "cache"
CACHE_AGENT_DIR = DATA_DIR / "cache_agent_graph"
LEARNING_DIR = DATA_DIR / "learning"
QUERY_HISTORY_DIR = DATA_DIR / "query_history"
REPORTS_DIR = BASE_DIR / "reports"

class DataIntegrityValidator:
    """Validador de integridade de dados e performance"""

    def __init__(self):
        self.results = {
            "timestamp": datetime.now().isoformat(),
            "parquet_files": {},
            "cache_analysis": {},
            "learning_analysis": {},
            "kpis": {},
            "health_score": 0,
            "issues": [],
            "recommendations": []
        }

    def validate_parquet_files(self):
        """Valida arquivos Parquet em data/"""
        print("\n=== Validando Arquivos Parquet ===")

        parquet_files = list(DATA_DIR.glob("*.parquet"))

        if not parquet_files:
            self.results["issues"].append({
                "severity": "WARNING",
                "category": "Parquet",
                "message": "Nenhum arquivo Parquet encontrado em data/"
            })
            return

        for parquet_file in parquet_files:
            file_name = parquet_file.name
            print(f"\nAnalisando: {file_name}")

            try:
                # Ler arquivo
                df = pd.read_parquet(parquet_file)

                # Calcular estatísticas
                stats = {
                    "path": str(parquet_file),
                    "size_mb": parquet_file.stat().st_size / (1024 * 1024),
                    "rows": len(df),
                    "columns": len(df.columns),
                    "column_names": list(df.columns),
                    "dtypes": {col: str(dtype) for col, dtype in df.dtypes.items()},
                    "null_counts": df.isnull().sum().to_dict(),
                    "duplicate_rows": df.duplicated().sum(),
                    "memory_usage_mb": df.memory_usage(deep=True).sum() / (1024 * 1024),
                    "status": "OK"
                }

                # Verificar problemas
                total_nulls = sum(stats["null_counts"].values())
                null_percentage = (total_nulls / (len(df) * len(df.columns))) * 100 if len(df) > 0 else 0

                if null_percentage > 30:
                    self.results["issues"].append({
                        "severity": "WARNING",
                        "category": "Parquet",
                        "file": file_name,
                        "message": f"Alto percentual de valores nulos: {null_percentage:.2f}%"
                    })
                    stats["status"] = "WARNING"

                if stats["duplicate_rows"] > len(df) * 0.1:
                    self.results["issues"].append({
                        "severity": "WARNING",
                        "category": "Parquet",
                        "file": file_name,
                        "message": f"Alto número de duplicatas: {stats['duplicate_rows']} ({stats['duplicate_rows']/len(df)*100:.2f}%)"
                    })

                # Verificar consistência de schema
                expected_columns = self._get_expected_columns(file_name)
                if expected_columns:
                    missing_cols = set(expected_columns) - set(df.columns)
                    extra_cols = set(df.columns) - set(expected_columns)

                    if missing_cols:
                        self.results["issues"].append({
                            "severity": "CRITICAL",
                            "category": "Schema",
                            "file": file_name,
                            "message": f"Colunas faltando: {missing_cols}"
                        })
                        stats["status"] = "CRITICAL"

                    if extra_cols:
                        self.results["issues"].append({
                            "severity": "INFO",
                            "category": "Schema",
                            "file": file_name,
                            "message": f"Colunas extras: {extra_cols}"
                        })

                self.results["parquet_files"][file_name] = stats
                print(f"  - {stats['rows']:,} linhas, {stats['columns']} colunas")
                print(f"  - Tamanho: {stats['size_mb']:.2f} MB")
                print(f"  - Status: {stats['status']}")

            except Exception as e:
                error_msg = f"Erro ao ler {file_name}: {str(e)}"
                print(f"  ERRO: {error_msg}")
                self.results["issues"].append({
                    "severity": "CRITICAL",
                    "category": "Parquet",
                    "file": file_name,
                    "message": error_msg
                })
                self.results["parquet_files"][file_name] = {
                    "status": "ERROR",
                    "error": str(e)
                }

    def _get_expected_columns(self, file_name):
        """Retorna colunas esperadas para cada tipo de arquivo"""
        expected_schemas = {
            "produtos.parquet": ["CODIGO", "DESCRICAO", "UNIDADE", "PRECO"],
            "estoque.parquet": ["CODIGO", "UNE", "ESTOQUE", "DATA"],
            "vendas.parquet": ["CODIGO", "UNE", "QUANTIDADE", "DATA"],
            "transferencias.parquet": ["CODIGO", "UNE_ORIGEM", "UNE_DESTINO", "QUANTIDADE", "DATA"]
        }
        return expected_schemas.get(file_name)

    def analyze_cache_system(self):
        """Analisa sistema de cache"""
        print("\n=== Analisando Sistema de Cache ===")

        cache_analysis = {
            "json_cache": self._analyze_json_cache(),
            "agent_graph_cache": self._analyze_agent_cache()
        }

        self.results["cache_analysis"] = cache_analysis

    def _analyze_json_cache(self):
        """Analisa cache JSON"""
        print("\nCache JSON:")

        if not CACHE_DIR.exists():
            print("  Diretório de cache não existe")
            return {"status": "NOT_FOUND"}

        cache_files = list(CACHE_DIR.glob("*.json"))

        if not cache_files:
            print("  Nenhum arquivo em cache")
            return {"status": "EMPTY", "count": 0}

        total_size = 0
        cache_data = []

        for cache_file in cache_files:
            try:
                size = cache_file.stat().st_size
                total_size += size
                modified = datetime.fromtimestamp(cache_file.stat().st_mtime)

                with open(cache_file, 'r', encoding='utf-8') as f:
                    content = json.load(f)

                cache_data.append({
                    "file": cache_file.name,
                    "size_kb": size / 1024,
                    "modified": modified.isoformat(),
                    "age_hours": (datetime.now() - modified).total_seconds() / 3600,
                    "has_data": bool(content)
                })
            except Exception as e:
                print(f"  Erro ao ler {cache_file.name}: {e}")

        # Calcular estatísticas
        avg_size = total_size / len(cache_files) if cache_files else 0
        old_cache = sum(1 for c in cache_data if c["age_hours"] > 24)

        stats = {
            "status": "OK",
            "count": len(cache_files),
            "total_size_mb": total_size / (1024 * 1024),
            "avg_size_kb": avg_size / 1024,
            "old_cache_count": old_cache,
            "oldest_hours": max(c["age_hours"] for c in cache_data) if cache_data else 0,
            "newest_hours": min(c["age_hours"] for c in cache_data) if cache_data else 0
        }

        print(f"  - Total: {stats['count']} arquivos")
        print(f"  - Tamanho total: {stats['total_size_mb']:.2f} MB")
        print(f"  - Cache antigo (>24h): {stats['old_cache_count']}")

        # Recomendar limpeza se necessário
        if stats["old_cache_count"] > 50:
            self.results["recommendations"].append({
                "priority": "MEDIUM",
                "category": "Cache",
                "action": "Executar limpeza de cache",
                "reason": f"{stats['old_cache_count']} arquivos com mais de 24 horas"
            })

        return stats

    def _analyze_agent_cache(self):
        """Analisa cache do agent graph"""
        print("\nCache Agent Graph:")

        if not CACHE_AGENT_DIR.exists():
            print("  Diretório não existe")
            return {"status": "NOT_FOUND"}

        cache_files = list(CACHE_AGENT_DIR.glob("*.pkl"))

        if not cache_files:
            print("  Vazio")
            return {"status": "EMPTY", "count": 0}

        total_size = sum(f.stat().st_size for f in cache_files)

        stats = {
            "status": "OK",
            "count": len(cache_files),
            "total_size_mb": total_size / (1024 * 1024)
        }

        print(f"  - Total: {stats['count']} arquivos")
        print(f"  - Tamanho: {stats['total_size_mb']:.2f} MB")

        return stats

    def analyze_learning_system(self):
        """Analisa sistema de learning"""
        print("\n=== Analisando Sistema de Learning ===")

        if not LEARNING_DIR.exists():
            print("Diretório de learning não existe")
            self.results["issues"].append({
                "severity": "WARNING",
                "category": "Learning",
                "message": "Sistema de learning não inicializado"
            })
            return

        # Analisar queries bem-sucedidas
        successful_queries = self._analyze_successful_queries()

        # Analisar erros
        error_analysis = self._analyze_errors()

        self.results["learning_analysis"] = {
            "successful_queries": successful_queries,
            "errors": error_analysis
        }

    def _analyze_successful_queries(self):
        """Analisa queries bem-sucedidas"""
        print("\nQueries Bem-Sucedidas:")

        query_files = list(LEARNING_DIR.glob("successful_queries_*.jsonl"))

        if not query_files:
            print("  Nenhum registro encontrado")
            return {"status": "EMPTY"}

        all_queries = []
        query_types = defaultdict(int)

        for query_file in query_files:
            try:
                with open(query_file, 'r', encoding='utf-8') as f:
                    for line in f:
                        if line.strip():
                            query = json.loads(line)
                            all_queries.append(query)

                            # Classificar tipo de query
                            query_text = query.get("query", "").lower()
                            if "transferencia" in query_text or "transfer" in query_text:
                                query_types["transferencias"] += 1
                            elif "estoque" in query_text:
                                query_types["estoque"] += 1
                            elif "venda" in query_text:
                                query_types["vendas"] += 1
                            elif "produto" in query_text:
                                query_types["produtos"] += 1
                            else:
                                query_types["outros"] += 1
            except Exception as e:
                print(f"  Erro ao ler {query_file.name}: {e}")

        stats = {
            "status": "OK",
            "total_queries": len(all_queries),
            "by_type": dict(query_types),
            "unique_patterns": len(set(q.get("query", "") for q in all_queries))
        }

        print(f"  - Total: {stats['total_queries']} queries")
        print(f"  - Padrões únicos: {stats['unique_patterns']}")
        print(f"  - Por tipo: {dict(query_types)}")

        return stats

    def _analyze_errors(self):
        """Analisa logs de erro"""
        print("\nAnálise de Erros:")

        error_log_files = list(LEARNING_DIR.glob("error_log_*.jsonl"))
        error_count_files = list(LEARNING_DIR.glob("error_counts_*.json"))

        all_errors = []
        error_types = defaultdict(int)

        # Analisar logs
        for error_file in error_log_files:
            try:
                with open(error_file, 'r', encoding='utf-8') as f:
                    for line in f:
                        if line.strip():
                            error = json.loads(line)
                            all_errors.append(error)
                            error_types[error.get("error_type", "unknown")] += 1
            except Exception as e:
                print(f"  Erro ao ler {error_file.name}: {e}")

        # Analisar contadores
        total_error_counts = defaultdict(int)
        for count_file in error_count_files:
            try:
                with open(count_file, 'r', encoding='utf-8') as f:
                    counts = json.load(f)
                    for error_type, count in counts.items():
                        total_error_counts[error_type] += count
            except Exception as e:
                print(f"  Erro ao ler {count_file.name}: {e}")

        stats = {
            "status": "OK",
            "total_errors": len(all_errors),
            "by_type": dict(error_types),
            "accumulated_counts": dict(total_error_counts),
            "error_rate": 0  # Será calculado em KPIs
        }

        print(f"  - Total de erros: {stats['total_errors']}")
        print(f"  - Por tipo: {dict(error_types)}")

        # Identificar erros críticos
        if stats["total_errors"] > 100:
            self.results["issues"].append({
                "severity": "WARNING",
                "category": "Errors",
                "message": f"Alto número de erros registrados: {stats['total_errors']}"
            })

        return stats

    def calculate_kpis(self):
        """Calcula KPIs do sistema"""
        print("\n=== Calculando KPIs do Sistema ===")

        kpis = {}

        # KPI: Taxa de erro
        successful = self.results["learning_analysis"].get("successful_queries", {}).get("total_queries", 0)
        errors = self.results["learning_analysis"].get("errors", {}).get("total_errors", 0)
        total_queries = successful + errors

        if total_queries > 0:
            error_rate = (errors / total_queries) * 100
            success_rate = (successful / total_queries) * 100
        else:
            error_rate = 0
            success_rate = 0

        kpis["error_rate_percent"] = round(error_rate, 2)
        kpis["success_rate_percent"] = round(success_rate, 2)
        kpis["total_queries"] = total_queries

        # KPI: Uso de cache
        cache_count = self.results["cache_analysis"].get("json_cache", {}).get("count", 0)
        cache_size_mb = self.results["cache_analysis"].get("json_cache", {}).get("total_size_mb", 0)

        kpis["cache_entries"] = cache_count
        kpis["cache_size_mb"] = round(cache_size_mb, 2)
        kpis["avg_cache_size_kb"] = round(
            self.results["cache_analysis"].get("json_cache", {}).get("avg_size_kb", 0), 2
        )

        # KPI: Dados Parquet
        total_rows = sum(
            file_data.get("rows", 0)
            for file_data in self.results["parquet_files"].values()
            if isinstance(file_data, dict) and "rows" in file_data
        )
        total_parquet_size = sum(
            file_data.get("size_mb", 0)
            for file_data in self.results["parquet_files"].values()
            if isinstance(file_data, dict) and "size_mb" in file_data
        )

        kpis["total_data_rows"] = total_rows
        kpis["total_parquet_size_mb"] = round(total_parquet_size, 2)

        # KPI: Qualidade dos dados
        parquet_ok = sum(
            1 for file_data in self.results["parquet_files"].values()
            if isinstance(file_data, dict) and file_data.get("status") == "OK"
        )
        total_parquet = len(self.results["parquet_files"])

        if total_parquet > 0:
            data_quality_score = (parquet_ok / total_parquet) * 100
        else:
            data_quality_score = 0

        kpis["data_quality_score"] = round(data_quality_score, 2)

        self.results["kpis"] = kpis

        print(f"\nKPIs Principais:")
        print(f"  - Taxa de sucesso: {kpis['success_rate_percent']}%")
        print(f"  - Taxa de erro: {kpis['error_rate_percent']}%")
        print(f"  - Qualidade dos dados: {kpis['data_quality_score']}%")
        print(f"  - Total de linhas: {kpis['total_data_rows']:,}")
        print(f"  - Cache: {kpis['cache_entries']} entradas ({kpis['cache_size_mb']} MB)")

    def calculate_health_score(self):
        """Calcula score de saúde geral (0-100)"""
        print("\n=== Calculando Health Score ===")

        score = 100

        # Penalidades por problemas críticos
        critical_issues = sum(1 for issue in self.results["issues"] if issue["severity"] == "CRITICAL")
        warning_issues = sum(1 for issue in self.results["issues"] if issue["severity"] == "WARNING")

        score -= critical_issues * 15
        score -= warning_issues * 5

        # Bonus por qualidade de dados
        data_quality = self.results["kpis"].get("data_quality_score", 0)
        if data_quality < 80:
            score -= (80 - data_quality) / 2

        # Penalidade por taxa de erro alta
        error_rate = self.results["kpis"].get("error_rate_percent", 0)
        if error_rate > 10:
            score -= (error_rate - 10)

        # Penalidade por cache excessivo
        cache_size = self.results["cache_analysis"].get("json_cache", {}).get("total_size_mb", 0)
        if cache_size > 100:
            score -= (cache_size - 100) / 10

        # Garantir que score está entre 0 e 100
        score = max(0, min(100, score))

        self.results["health_score"] = round(score, 2)

        print(f"\nHealth Score: {self.results['health_score']}/100")

        if score >= 90:
            status = "EXCELENTE"
        elif score >= 75:
            status = "BOM"
        elif score >= 60:
            status = "REGULAR"
        else:
            status = "CRITICO"

        print(f"Status: {status}")

        return status

    def generate_recommendations(self):
        """Gera recomendações baseadas na análise"""
        print("\n=== Gerando Recomendações ===")

        # Recomendações já adicionadas durante análise
        # Adicionar recomendações baseadas em KPIs

        error_rate = self.results["kpis"].get("error_rate_percent", 0)
        if error_rate > 10:
            self.results["recommendations"].append({
                "priority": "HIGH",
                "category": "Performance",
                "action": "Investigar e corrigir erros recorrentes",
                "reason": f"Taxa de erro elevada: {error_rate}%"
            })

        cache_size = self.results["cache_analysis"].get("json_cache", {}).get("total_size_mb", 0)
        if cache_size > 50:
            self.results["recommendations"].append({
                "priority": "MEDIUM",
                "category": "Cache",
                "action": "Implementar política de cache TTL (Time To Live)",
                "reason": f"Cache ocupando {cache_size:.2f} MB"
            })

        total_queries = self.results["kpis"].get("total_queries", 0)
        if total_queries < 50:
            self.results["recommendations"].append({
                "priority": "LOW",
                "category": "Learning",
                "action": "Aumentar coleta de dados de treinamento",
                "reason": f"Apenas {total_queries} queries registradas"
            })

        # Ordenar por prioridade
        priority_order = {"HIGH": 1, "MEDIUM": 2, "LOW": 3}
        self.results["recommendations"].sort(
            key=lambda x: priority_order.get(x.get("priority", "LOW"), 3)
        )

        print(f"\nTotal de recomendações: {len(self.results['recommendations'])}")

    def generate_report(self):
        """Gera relatório markdown"""
        print("\n=== Gerando Relatório ===")

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_file = REPORTS_DIR / f"data_integrity_report_{timestamp}.md"

        # Criar diretório se não existir
        REPORTS_DIR.mkdir(exist_ok=True)

        # Construir relatório
        report = self._build_markdown_report()

        # Salvar
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(report)

        print(f"\nRelatório salvo em: {report_file}")

        # Salvar JSON para análise programática
        json_file = REPORTS_DIR / f"data_integrity_report_{timestamp}.json"
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(self.results, f, indent=2, ensure_ascii=False)

        print(f"Dados JSON salvos em: {json_file}")

        return report_file

    def _build_markdown_report(self):
        """Constrói relatório em Markdown"""
        health_score = self.results["health_score"]

        if health_score >= 90:
            status_emoji = "✅"
            status_text = "EXCELENTE"
        elif health_score >= 75:
            status_emoji = "✔️"
            status_text = "BOM"
        elif health_score >= 60:
            status_emoji = "⚠️"
            status_text = "REGULAR"
        else:
            status_emoji = "❌"
            status_text = "CRITICO"

        report = f"""# Relatório de Integridade de Dados e Performance
## Agent_Solution_BI - BI Agent (Caçulinha BI)

**Data/Hora**: {self.results["timestamp"]}
**Health Score**: {health_score}/100 {status_emoji}
**Status**: {status_text}

---

## 1. Sumário Executivo

### Score de Saúde dos Dados: {health_score}/100

O sistema Agent_Solution_BI foi analisado quanto à integridade de dados, performance de cache e eficácia do sistema de learning.

"""

        # KPIs principais
        kpis = self.results["kpis"]
        report += f"""### Métricas Principais

| Métrica | Valor |
|---------|-------|
| Taxa de Sucesso | {kpis.get('success_rate_percent', 0)}% |
| Taxa de Erro | {kpis.get('error_rate_percent', 0)}% |
| Qualidade dos Dados | {kpis.get('data_quality_score', 0)}% |
| Total de Queries | {kpis.get('total_queries', 0):,} |
| Total de Linhas (Parquet) | {kpis.get('total_data_rows', 0):,} |
| Tamanho Total Parquet | {kpis.get('total_parquet_size_mb', 0)} MB |
| Entradas de Cache | {kpis.get('cache_entries', 0)} |
| Tamanho de Cache | {kpis.get('cache_size_mb', 0)} MB |

---

## 2. Análise de Arquivos Parquet

"""

        # Arquivos Parquet
        if self.results["parquet_files"]:
            report += "### Arquivos Encontrados\n\n"
            for file_name, file_data in self.results["parquet_files"].items():
                if isinstance(file_data, dict) and "rows" in file_data:
                    status_icon = "✅" if file_data.get("status") == "OK" else "⚠️"
                    report += f"""#### {status_icon} {file_name}

- **Status**: {file_data.get('status', 'UNKNOWN')}
- **Linhas**: {file_data.get('rows', 0):,}
- **Colunas**: {file_data.get('columns', 0)}
- **Tamanho**: {file_data.get('size_mb', 0):.2f} MB
- **Uso de Memória**: {file_data.get('memory_usage_mb', 0):.2f} MB
- **Linhas Duplicadas**: {file_data.get('duplicate_rows', 0):,}

**Colunas**: {', '.join(file_data.get('column_names', []))}

**Valores Nulos por Coluna**:
"""
                    null_counts = file_data.get('null_counts', {})
                    if null_counts:
                        for col, count in null_counts.items():
                            if count > 0:
                                report += f"- {col}: {count:,}\n"
                    else:
                        report += "- Nenhum valor nulo\n"

                    report += "\n"
                else:
                    report += f"#### ❌ {file_name}\n\n- **Status**: ERROR\n- **Erro**: {file_data.get('error', 'Desconhecido')}\n\n"
        else:
            report += "⚠️ Nenhum arquivo Parquet encontrado.\n\n"

        # Cache
        report += """---

## 3. Análise de Sistema de Cache

"""

        json_cache = self.results["cache_analysis"].get("json_cache", {})
        if json_cache.get("status") == "OK":
            report += f"""### Cache JSON

- **Status**: ✅ Operacional
- **Total de Arquivos**: {json_cache.get('count', 0):,}
- **Tamanho Total**: {json_cache.get('total_size_mb', 0):.2f} MB
- **Tamanho Médio**: {json_cache.get('avg_size_kb', 0):.2f} KB
- **Cache Antigo (>24h)**: {json_cache.get('old_cache_count', 0)}
- **Arquivo Mais Antigo**: {json_cache.get('oldest_hours', 0):.1f} horas
- **Arquivo Mais Recente**: {json_cache.get('newest_hours', 0):.1f} horas

"""
        else:
            report += f"### Cache JSON\n\n- **Status**: {json_cache.get('status', 'UNKNOWN')}\n\n"

        agent_cache = self.results["cache_analysis"].get("agent_graph_cache", {})
        if agent_cache.get("status") == "OK":
            report += f"""### Cache Agent Graph

- **Status**: ✅ Operacional
- **Total de Arquivos**: {agent_cache.get('count', 0):,}
- **Tamanho Total**: {agent_cache.get('total_size_mb', 0):.2f} MB

"""
        else:
            report += f"### Cache Agent Graph\n\n- **Status**: {agent_cache.get('status', 'UNKNOWN')}\n\n"

        # Learning
        report += """---

## 4. Análise do Sistema de Learning

"""

        successful = self.results["learning_analysis"].get("successful_queries", {})
        if successful.get("status") == "OK":
            report += f"""### Queries Bem-Sucedidas

- **Total de Queries**: {successful.get('total_queries', 0):,}
- **Padrões Únicos**: {successful.get('unique_patterns', 0)}

**Distribuição por Tipo**:
"""
            by_type = successful.get('by_type', {})
            for query_type, count in sorted(by_type.items(), key=lambda x: x[1], reverse=True):
                percentage = (count / successful.get('total_queries', 1)) * 100
                report += f"- {query_type.capitalize()}: {count} ({percentage:.1f}%)\n"

            report += "\n"
        else:
            report += f"### Queries Bem-Sucedidas\n\n- **Status**: {successful.get('status', 'UNKNOWN')}\n\n"

        errors = self.results["learning_analysis"].get("errors", {})
        if errors.get("status") == "OK":
            report += f"""### Análise de Erros

- **Total de Erros**: {errors.get('total_errors', 0):,}

**Distribuição por Tipo**:
"""
            by_type = errors.get('by_type', {})
            for error_type, count in sorted(by_type.items(), key=lambda x: x[1], reverse=True):
                report += f"- {error_type}: {count}\n"

            report += "\n"
        else:
            report += f"### Análise de Erros\n\n- **Status**: {errors.get('status', 'UNKNOWN')}\n\n"

        # Problemas identificados
        report += """---

## 5. Problemas Identificados

"""

        if self.results["issues"]:
            # Agrupar por severidade
            critical = [i for i in self.results["issues"] if i["severity"] == "CRITICAL"]
            warnings = [i for i in self.results["issues"] if i["severity"] == "WARNING"]
            info = [i for i in self.results["issues"] if i["severity"] == "INFO"]

            if critical:
                report += "### ❌ Problemas Críticos\n\n"
                for issue in critical:
                    report += f"- **{issue.get('category', 'Geral')}**: {issue.get('message', '')}\n"
                    if 'file' in issue:
                        report += f"  - Arquivo: `{issue['file']}`\n"
                report += "\n"

            if warnings:
                report += "### ⚠️ Avisos\n\n"
                for issue in warnings:
                    report += f"- **{issue.get('category', 'Geral')}**: {issue.get('message', '')}\n"
                    if 'file' in issue:
                        report += f"  - Arquivo: `{issue['file']}`\n"
                report += "\n"

            if info:
                report += "### ℹ️ Informações\n\n"
                for issue in info:
                    report += f"- **{issue.get('category', 'Geral')}**: {issue.get('message', '')}\n"
                    if 'file' in issue:
                        report += f"  - Arquivo: `{issue['file']}`\n"
                report += "\n"
        else:
            report += "✅ Nenhum problema identificado.\n\n"

        # Recomendações
        report += """---

## 6. Recomendações Priorizadas

"""

        if self.results["recommendations"]:
            # Agrupar por prioridade
            high = [r for r in self.results["recommendations"] if r["priority"] == "HIGH"]
            medium = [r for r in self.results["recommendations"] if r["priority"] == "MEDIUM"]
            low = [r for r in self.results["recommendations"] if r["priority"] == "LOW"]

            if high:
                report += "### 🔴 Prioridade Alta\n\n"
                for i, rec in enumerate(high, 1):
                    report += f"{i}. **{rec.get('action', '')}**\n"
                    report += f"   - Categoria: {rec.get('category', 'Geral')}\n"
                    report += f"   - Razão: {rec.get('reason', '')}\n\n"

            if medium:
                report += "### 🟡 Prioridade Média\n\n"
                for i, rec in enumerate(medium, 1):
                    report += f"{i}. **{rec.get('action', '')}**\n"
                    report += f"   - Categoria: {rec.get('category', 'Geral')}\n"
                    report += f"   - Razão: {rec.get('reason', '')}\n\n"

            if low:
                report += "### 🟢 Prioridade Baixa\n\n"
                for i, rec in enumerate(low, 1):
                    report += f"{i}. **{rec.get('action', '')}**\n"
                    report += f"   - Categoria: {rec.get('category', 'Geral')}\n"
                    report += f"   - Razão: {rec.get('reason', '')}\n\n"
        else:
            report += "✅ Nenhuma recomendação necessária no momento.\n\n"

        # Comentário do Analista
        report += f"""---

## 💬 Comentário do Analista

Com base na análise realizada, o sistema Agent_Solution_BI apresenta um **Health Score de {health_score}/100**, classificado como **{status_text}**.

"""

        if health_score >= 90:
            report += """**Pontos Fortes**:
- Sistema operando em condições excelentes
- Integridade de dados preservada
- Performance de cache otimizada
- Sistema de learning funcionando adequadamente

**Próximos Passos**:
- Manter monitoramento regular
- Continuar coleta de dados de learning
"""
        elif health_score >= 75:
            report += """**Pontos Fortes**:
- Sistema operando em condições satisfatórias
- Dados principais íntegros

**Áreas de Atenção**:
- Revisar avisos identificados
- Implementar recomendações de prioridade média/alta

**Próximos Passos**:
- Corrigir problemas identificados
- Otimizar áreas com avisos
"""
        elif health_score >= 60:
            report += """**Pontos de Atenção**:
- Sistema operacional, mas com problemas que requerem atenção
- Algumas áreas críticas precisam de correção

**Ações Recomendadas**:
- Priorizar correção de problemas críticos
- Implementar todas as recomendações de alta prioridade
- Revisar processos de manutenção de dados

**Próximos Passos**:
- Executar correções imediatamente
- Agendar revisão em 48 horas
"""
        else:
            report += """**⚠️ ATENÇÃO: Sistema em Estado Crítico**

**Problemas Graves Detectados**:
- Múltiplos problemas críticos identificados
- Integridade de dados comprometida ou performance degradada

**Ações Urgentes**:
1. Revisar todos os problemas críticos imediatamente
2. Implementar correções de emergência
3. Validar integridade dos dados de produção
4. Considerar rollback se necessário

**Próximos Passos**:
- Correção imediata de problemas críticos
- Revisão completa do sistema
- Implementação de monitoramento contínuo
"""

        report += f"""
---

**Relatório gerado em**: {datetime.now().strftime("%d/%m/%Y às %H:%M:%S")}
**Período de análise**: Histórico completo do sistema
**Origem dos dados**: {BASE_DIR}

---

*BI Agent (Caçulinha BI) - Agent_Solution_BI*
"""

        return report

    def run_validation(self):
        """Executa validação completa"""
        print("=" * 60)
        print("VALIDAÇÃO DE INTEGRIDADE DE DADOS E PERFORMANCE")
        print("Agent_Solution_BI - BI Agent (Caçulinha BI)")
        print("=" * 60)

        try:
            self.validate_parquet_files()
            self.analyze_cache_system()
            self.analyze_learning_system()
            self.calculate_kpis()
            self.calculate_health_score()
            self.generate_recommendations()
            report_file = self.generate_report()

            print("\n" + "=" * 60)
            print("VALIDAÇÃO CONCLUÍDA COM SUCESSO")
            print("=" * 60)
            print(f"\nHealth Score: {self.results['health_score']}/100")
            print(f"Relatório: {report_file}")

            return self.results

        except Exception as e:
            print(f"\n❌ ERRO durante validação: {e}")
            traceback.print_exc()
            return None


def main():
    """Função principal"""
    validator = DataIntegrityValidator()
    results = validator.run_validation()

    if results:
        print("\n✅ Validação concluída com sucesso!")
        return 0
    else:
        print("\n❌ Validação falhou!")
        return 1


if __name__ == "__main__":
    exit(main())
