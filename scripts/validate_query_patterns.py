"""
Script de Validação da Biblioteca de Padrões de Queries
FASE 2.1 - Few-Shot Learning Pattern Library

Valida:
1. Sintaxe JSON
2. Estrutura dos padrões
3. Código Polars válido
4. Keywords e metadata
5. Estatísticas de cobertura
"""

import json
import sys
from pathlib import Path
from typing import Dict, List, Tuple

# Adicionar path do projeto
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


class QueryPatternValidator:
    """Validador da biblioteca de padrões de queries"""

    def __init__(self, patterns_file: str):
        self.patterns_file = Path(patterns_file)
        self.patterns_data = None
        self.errors = []
        self.warnings = []
        self.stats = {
            'total_patterns': 0,
            'total_examples': 0,
            'categories': set(),
            'priorities': {'high': 0, 'medium': 0, 'low': 0},
            'frequencies': {'muito_alta': 0, 'alta': 0, 'media': 0, 'baixa': 0}
        }

    def load_patterns(self) -> bool:
        """Carrega e valida JSON"""
        try:
            with open(self.patterns_file, 'r', encoding='utf-8') as f:
                self.patterns_data = json.load(f)
            print("[OK] JSON carregado com sucesso")
            return True
        except json.JSONDecodeError as e:
            self.errors.append(f"Erro de sintaxe JSON: {e}")
            print(f"[ERRO] {self.errors[-1]}")
            return False
        except FileNotFoundError:
            self.errors.append(f"Arquivo não encontrado: {self.patterns_file}")
            print(f"[ERRO] {self.errors[-1]}")
            return False

    def validate_structure(self) -> bool:
        """Valida estrutura do JSON"""
        required_keys = ['metadata', 'categories', 'patterns', 'usage_guide', 'statistics']

        for key in required_keys:
            if key not in self.patterns_data:
                self.errors.append(f"Chave obrigatória ausente: {key}")

        if self.errors:
            print(f"[ERRO] Estrutura inválida: {len(self.errors)} erros")
            return False

        print("[OK] Estrutura do JSON válida")
        return True

    def validate_patterns(self) -> bool:
        """Valida cada padrão individualmente"""
        patterns = self.patterns_data.get('patterns', [])
        self.stats['total_patterns'] = len(patterns)

        required_pattern_keys = [
            'id', 'category', 'priority', 'description',
            'keywords', 'usage_frequency', 'complexity',
            'code_template', 'examples'
        ]

        for idx, pattern in enumerate(patterns):
            pattern_id = pattern.get('id', f'pattern_{idx}')

            # Validar chaves obrigatórias
            for key in required_pattern_keys:
                if key not in pattern:
                    self.errors.append(f"Padrão '{pattern_id}': chave ausente '{key}'")

            # Validar keywords (deve ter pelo menos 2)
            keywords = pattern.get('keywords', [])
            if len(keywords) < 2:
                self.warnings.append(f"Padrão '{pattern_id}': poucas keywords ({len(keywords)})")

            # Validar exemplos (deve ter pelo menos 1)
            examples = pattern.get('examples', [])
            if len(examples) < 1:
                self.errors.append(f"Padrão '{pattern_id}': sem exemplos")
            else:
                self.stats['total_examples'] += len(examples)

                # Validar cada exemplo
                for ex_idx, example in enumerate(examples):
                    if 'query' not in example:
                        self.errors.append(f"Padrão '{pattern_id}', exemplo {ex_idx}: sem 'query'")
                    if 'code' not in example:
                        self.errors.append(f"Padrão '{pattern_id}', exemplo {ex_idx}: sem 'code'")

            # Coletar estatísticas
            self.stats['categories'].add(pattern.get('category', 'unknown'))

            priority = pattern.get('priority', '')
            if priority in self.stats['priorities']:
                self.stats['priorities'][priority] += 1

            frequency = pattern.get('usage_frequency', '')
            if frequency in self.stats['frequencies']:
                self.stats['frequencies'][frequency] += 1

        if self.errors:
            print(f"[ERRO] Validação de padrões: {len(self.errors)} erros")
            return False

        if self.warnings:
            print(f"[AVISO] {len(self.warnings)} avisos encontrados")

        print(f"[OK] {self.stats['total_patterns']} padrões validados com sucesso")
        return True

    def validate_code_syntax(self) -> bool:
        """Valida sintaxe básica do código Polars"""
        patterns = self.patterns_data.get('patterns', [])
        invalid_code = []

        for pattern in patterns:
            pattern_id = pattern.get('id')

            # Validar template
            template = pattern.get('code_template', '')
            if 'df.' not in template and 'pl.' not in template:
                invalid_code.append(f"Padrão '{pattern_id}': template sem código Polars válido")

            # Validar exemplos
            for example in pattern.get('examples', []):
                code = example.get('code', '')
                if 'df.' not in code and 'pl.' not in code:
                    invalid_code.append(
                        f"Padrão '{pattern_id}', query '{example.get('query')}': código sem Polars"
                    )

        if invalid_code:
            self.warnings.extend(invalid_code)
            print(f"[AVISO] {len(invalid_code)} problemas de sintaxe encontrados")
        else:
            print("[OK] Sintaxe de código validada")

        return True

    def validate_coverage(self) -> bool:
        """Valida cobertura de padrões"""
        metadata = self.patterns_data.get('metadata', {})
        statistics = self.patterns_data.get('statistics', {})

        target_coverage = int(metadata.get('coverage_target', '80%').replace('%', ''))
        estimated_coverage = int(statistics.get('estimated_coverage', '0%').replace('%', ''))

        if estimated_coverage < target_coverage:
            self.warnings.append(
                f"Cobertura estimada ({estimated_coverage}%) abaixo da meta ({target_coverage}%)"
            )
        else:
            print(f"[OK] Cobertura: {estimated_coverage}% (meta: {target_coverage}%)")

        # Validar distribuição de prioridades
        high_priority = self.stats['priorities']['high']
        total_patterns = self.stats['total_patterns']

        if high_priority < total_patterns * 0.4:  # Pelo menos 40% high priority
            self.warnings.append(
                f"Poucos padrões de alta prioridade: {high_priority}/{total_patterns}"
            )
        else:
            print(f"[OK] Padrões de alta prioridade: {high_priority}/{total_patterns}")

        return True

    def print_statistics(self):
        """Imprime estatísticas da biblioteca"""
        print("\n" + "="*70)
        print("ESTATÍSTICAS DA BIBLIOTECA DE PADRÕES")
        print("="*70)

        print(f"\nTotal de Padrões: {self.stats['total_patterns']}")
        print(f"Total de Exemplos: {self.stats['total_examples']}")
        print(f"Categorias: {len(self.stats['categories'])}")

        print(f"\nDistribuição por Prioridade:")
        for priority, count in self.stats['priorities'].items():
            pct = (count / self.stats['total_patterns'] * 100) if self.stats['total_patterns'] else 0
            print(f"  {priority.capitalize()}: {count} ({pct:.1f}%)")

        print(f"\nDistribuição por Frequência:")
        for freq, count in self.stats['frequencies'].items():
            pct = (count / self.stats['total_patterns'] * 100) if self.stats['total_patterns'] else 0
            print(f"  {freq}: {count} ({pct:.1f}%)")

        print(f"\nCategorias Cobertas:")
        for category in sorted(self.stats['categories']):
            patterns_in_category = sum(
                1 for p in self.patterns_data['patterns']
                if p.get('category') == category
            )
            print(f"  {category}: {patterns_in_category} padrões")

    def print_summary(self):
        """Imprime resumo da validação"""
        print("\n" + "="*70)
        print("RESUMO DA VALIDAÇÃO")
        print("="*70)

        if not self.errors and not self.warnings:
            print("\n[SUCCESS] Biblioteca validada com 100% de sucesso!")
            print("Todos os padrões estão corretos e prontos para uso.")
        else:
            if self.errors:
                print(f"\n[ERRO] {len(self.errors)} erros críticos encontrados:")
                for error in self.errors[:10]:  # Mostrar primeiros 10
                    print(f"  - {error}")
                if len(self.errors) > 10:
                    print(f"  ... e mais {len(self.errors) - 10} erros")

            if self.warnings:
                print(f"\n[AVISO] {len(self.warnings)} avisos:")
                for warning in self.warnings[:10]:  # Mostrar primeiros 10
                    print(f"  - {warning}")
                if len(self.warnings) > 10:
                    print(f"  ... e mais {len(self.warnings) - 10} avisos")

        print("\n" + "="*70)

    def validate_all(self) -> bool:
        """Executa todas as validações"""
        print("\n" + "="*70)
        print("VALIDAÇÃO DA BIBLIOTECA DE PADRÕES DE QUERIES - FASE 2.1")
        print("="*70 + "\n")

        steps = [
            ("Carregando JSON", self.load_patterns),
            ("Validando estrutura", self.validate_structure),
            ("Validando padrões", self.validate_patterns),
            ("Validando código", self.validate_code_syntax),
            ("Validando cobertura", self.validate_coverage)
        ]

        for step_name, step_func in steps:
            print(f"\n[STEP] {step_name}...")
            if not step_func():
                return False

        self.print_statistics()
        self.print_summary()

        return len(self.errors) == 0


def main():
    """Função principal"""
    # Caminhos dos arquivos
    patterns_file = project_root / "query_patterns_complete.json"

    if not patterns_file.exists():
        print(f"[ERRO] Arquivo não encontrado: {patterns_file}")
        print("Execute primeiro a criação da biblioteca de padrões.")
        return 1

    # Validar
    validator = QueryPatternValidator(patterns_file)
    success = validator.validate_all()

    # Salvar relatório
    report_file = project_root / "data" / "reports" / "pattern_validation_report.txt"
    report_file.parent.mkdir(parents=True, exist_ok=True)

    with open(report_file, 'w', encoding='utf-8') as f:
        f.write("RELATÓRIO DE VALIDAÇÃO - BIBLIOTECA DE PADRÕES\n")
        f.write("="*70 + "\n\n")
        f.write(f"Arquivo: {patterns_file}\n")
        f.write(f"Total de Padrões: {validator.stats['total_patterns']}\n")
        f.write(f"Total de Exemplos: {validator.stats['total_examples']}\n")
        f.write(f"Erros: {len(validator.errors)}\n")
        f.write(f"Avisos: {len(validator.warnings)}\n\n")

        if validator.errors:
            f.write("ERROS:\n")
            for error in validator.errors:
                f.write(f"  - {error}\n")

        if validator.warnings:
            f.write("\nAVISOS:\n")
            for warning in validator.warnings:
                f.write(f"  - {warning}\n")

    print(f"\nRelatório salvo em: {report_file}")

    return 0 if success else 1


if __name__ == "__main__":
    exit(main())
