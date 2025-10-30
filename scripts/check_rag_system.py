"""
Script para verificar integridade do sistema RAG e embeddings FAISS
"""
import json
import os
import sys
import io
from pathlib import Path

# Configurar encoding UTF-8
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Adicionar path do projeto
sys.path.insert(0, str(Path(__file__).parent.parent))

def check_query_examples():
    """Verifica integridade do arquivo query_examples.json"""
    print("="*70)
    print(" VERIFICAÇÃO DO SISTEMA RAG ")
    print("="*70)
    print()

    file_path = Path("data/query_examples.json")

    if not file_path.exists():
        print(f"❌ Arquivo NÃO encontrado: {file_path}")
        return False

    print(f"✅ Arquivo encontrado: {file_path}")
    print(f"   Tamanho: {file_path.stat().st_size / 1024:.1f} KB")
    print()

    # Carregar e validar JSON
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            examples = json.load(f)

        print(f"✅ JSON válido: {len(examples)} exemplos")
        print()

        # Estatísticas
        intents = {}
        with_code = 0
        with_sql = 0
        total_chars = 0

        for i, example in enumerate(examples):
            # Verificar estrutura
            if 'query' not in example:
                print(f"❌ Exemplo {i}: Faltando campo 'query'")

            intent = example.get('intent', 'unknown')
            intents[intent] = intents.get(intent, 0) + 1

            if example.get('code'):
                with_code += 1
                total_chars += len(example['code'])

            if example.get('sql'):
                with_sql += 1

        print("📊 ESTATÍSTICAS DOS EXEMPLOS:")
        print(f"   Total de exemplos: {len(examples)}")
        print(f"   Com código Python: {with_code}")
        print(f"   Com SQL: {with_sql}")
        print(f"   Tamanho médio código: {total_chars / with_code if with_code > 0 else 0:.0f} caracteres")
        print()

        print("📋 DISTRIBUIÇÃO POR INTENT:")
        for intent, count in sorted(intents.items(), key=lambda x: x[1], reverse=True):
            print(f"   {intent}: {count}")
        print()

        # Verificar exemplos problemáticos
        print("🔍 VERIFICANDO EXEMPLOS...")
        issues = []

        for i, example in enumerate(examples):
            code = example.get('code', '')

            # Verificar uso de colunas legadas
            legacy_columns = ['PRODUTO', 'NOME', 'VENDA_30DD', 'ESTOQUE_UNE', 'LIQUIDO_38']
            for col in legacy_columns:
                if col in code:
                    issues.append(f"Exemplo {i}: Usa coluna legada '{col}'")
                    break

        if issues:
            print(f"⚠️  Encontrados {len(issues)} exemplos com possíveis problemas:")
            for issue in issues[:10]:  # Mostrar primeiros 10
                print(f"   {issue}")
        else:
            print("✅ Nenhum problema encontrado nos exemplos")

        print()
        return True

    except json.JSONDecodeError as e:
        print(f"❌ Erro ao parsear JSON: {e}")
        return False
    except Exception as e:
        print(f"❌ Erro: {e}")
        return False

def check_faiss_index():
    """Verifica índice FAISS"""
    print("="*70)
    print(" VERIFICAÇÃO DO ÍNDICE FAISS ")
    print("="*70)
    print()

    faiss_file = Path("data/rag_embeddings/faiss_index.bin")
    metadata_file = Path("data/rag_embeddings/metadata.json")

    if faiss_file.exists():
        size = faiss_file.stat().st_size
        print(f"✅ Índice FAISS encontrado: {faiss_file}")
        print(f"   Tamanho: {size / 1024:.1f} KB")
    else:
        print(f"⚠️  Índice FAISS NÃO encontrado: {faiss_file}")
        print("   Execute o script de treinamento para criar")

    print()

    if metadata_file.exists():
        print(f"✅ Metadados encontrados: {metadata_file}")
        try:
            with open(metadata_file, 'r', encoding='utf-8') as f:
                metadata = json.load(f)
            print(f"   Exemplos indexados: {len(metadata.get('examples', []))}")
            print(f"   Modelo: {metadata.get('model', 'N/A')}")
            print(f"   Data criação: {metadata.get('created_at', 'N/A')}")
        except:
            print("   ⚠️  Erro ao ler metadados")
    else:
        print(f"⚠️  Metadados NÃO encontrados: {metadata_file}")

    print()

def check_catalog():
    """Verifica catálogo de colunas"""
    print("="*70)
    print(" VERIFICAÇÃO DO CATÁLOGO DE COLUNAS ")
    print("="*70)
    print()

    catalog_file = Path("data/catalog_focused.json")

    if not catalog_file.exists():
        print(f"❌ Catálogo NÃO encontrado: {catalog_file}")
        return False

    print(f"✅ Catálogo encontrado: {catalog_file}")

    try:
        with open(catalog_file, 'r', encoding='utf-8') as f:
            catalog = json.load(f)

        columns = catalog.get('columns', [])
        print(f"   Total de colunas: {len(columns)}")
        print()

        # Verificar colunas essenciais
        essential_columns = ['codigo', 'nome_produto', 'une', 'nomesegmento',
                            'venda_30_d', 'estoque_atual', 'preco_38_percent']

        print("🔍 VERIFICANDO COLUNAS ESSENCIAIS:")
        missing = []
        for col in essential_columns:
            found = any(c['name'] == col for c in columns)
            if found:
                print(f"   ✅ {col}")
            else:
                print(f"   ❌ {col} (FALTANDO)")
                missing.append(col)

        if missing:
            print()
            print(f"⚠️  {len(missing)} colunas essenciais faltando no catálogo!")

        print()
        return True

    except Exception as e:
        print(f"❌ Erro ao ler catálogo: {e}")
        return False

def main():
    """Executa todas as verificações"""
    os.chdir(Path(__file__).parent.parent)

    check_query_examples()
    check_faiss_index()
    check_catalog()

    print("="*70)
    print(" VERIFICAÇÃO COMPLETA ")
    print("="*70)

if __name__ == "__main__":
    main()
