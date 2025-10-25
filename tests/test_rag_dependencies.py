#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Teste de validação das dependências RAG.

Autor: Code Agent
Data: 2025-10-24
Versão: 1.0.0

Testa:
- Imports básicos
- Carregamento de modelos
- Operações básicas de embedding e busca vetorial
"""

import sys
import traceback
from datetime import datetime


def test_sentence_transformers():
    """Testa sentence-transformers com operações reais."""
    print("\n" + "="*60)
    print("🧪 TESTE: sentence-transformers")
    print("="*60)

    try:
        from sentence_transformers import SentenceTransformer

        print("✅ Import bem-sucedido")

        # Testar carregamento de modelo multilíngue
        print("📥 Carregando modelo multilíngue...")
        model = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')

        print("✅ Modelo carregado")

        # Testar encoding
        texts = [
            "Qual foi o faturamento total em 2024?",
            "Mostre os produtos mais vendidos",
            "Análise de vendas por região"
        ]

        print(f"🔄 Gerando embeddings para {len(texts)} textos...")
        embeddings = model.encode(texts)

        print(f"✅ Embeddings gerados: shape={embeddings.shape}")
        print(f"   Dimensão: {embeddings.shape[1]}")
        print(f"   Tipo: {type(embeddings)}")

        return True, "sentence-transformers OK"

    except Exception as e:
        print(f"❌ FALHOU: {str(e)}")
        traceback.print_exc()
        return False, str(e)


def test_faiss():
    """Testa faiss com operações de busca vetorial."""
    print("\n" + "="*60)
    print("🧪 TESTE: faiss-cpu")
    print("="*60)

    try:
        import faiss
        import numpy as np

        print("✅ Import bem-sucedido")

        # Criar índice de teste
        dimension = 384  # Dimensão do modelo multilíngue
        n_vectors = 100

        print(f"🏗️  Criando índice FAISS (dim={dimension})...")
        index = faiss.IndexFlatL2(dimension)

        print(f"✅ Índice criado: {type(index)}")

        # Adicionar vetores de teste
        vectors = np.random.random((n_vectors, dimension)).astype('float32')
        index.add(vectors)

        print(f"✅ {n_vectors} vetores adicionados")

        # Testar busca
        k = 5
        query = np.random.random((1, dimension)).astype('float32')

        print(f"🔍 Buscando top-{k} vizinhos mais próximos...")
        distances, indices = index.search(query, k)

        print(f"✅ Busca realizada")
        print(f"   Índices: {indices[0]}")
        print(f"   Distâncias: {distances[0]}")

        return True, "faiss-cpu OK"

    except Exception as e:
        print(f"❌ FALHOU: {str(e)}")
        traceback.print_exc()
        return False, str(e)


def test_spacy():
    """Testa spacy com modelo português."""
    print("\n" + "="*60)
    print("🧪 TESTE: spacy + pt_core_news_sm")
    print("="*60)

    try:
        import spacy

        print("✅ Import bem-sucedido")

        # Carregar modelo português
        print("📥 Carregando modelo pt_core_news_sm...")
        nlp = spacy.load('pt_core_news_sm')

        print("✅ Modelo carregado")

        # Testar processamento
        text = "O Caculinha BI é um sistema de análise de dados corporativos."

        print(f"🔄 Processando texto: '{text}'")
        doc = nlp(text)

        print(f"✅ Processamento concluído")
        print(f"   Tokens: {len(doc)}")
        print(f"   Entidades: {[(ent.text, ent.label_) for ent in doc.ents]}")

        # Testar tokenização
        tokens = [token.text for token in doc]
        print(f"   Tokens: {tokens}")

        # Testar POS tagging
        pos_tags = [(token.text, token.pos_) for token in doc]
        print(f"   POS Tags: {pos_tags[:5]}...")

        return True, "spacy OK"

    except Exception as e:
        print(f"❌ FALHOU: {str(e)}")
        traceback.print_exc()
        return False, str(e)


def test_integration():
    """Testa integração entre as bibliotecas."""
    print("\n" + "="*60)
    print("🧪 TESTE: Integração RAG")
    print("="*60)

    try:
        from sentence_transformers import SentenceTransformer
        import faiss
        import spacy
        import numpy as np

        print("✅ Todos os imports bem-sucedidos")

        # Pipeline completo RAG simulado
        print("\n🔄 Executando pipeline RAG completo...")

        # 1. Processar textos com spacy
        nlp = spacy.load('pt_core_news_sm')
        texts = [
            "Qual foi o faturamento total em 2024?",
            "Mostre os produtos mais vendidos no último trimestre",
            "Análise de vendas por região geográfica",
            "Qual a margem de lucro dos produtos categoria A?",
            "Histórico de vendas dos últimos 12 meses"
        ]

        print(f"   1️⃣  Processando {len(texts)} textos com spacy...")
        processed = [nlp(text) for text in texts]
        print(f"      ✅ {len(processed)} textos processados")

        # 2. Gerar embeddings
        model = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')
        print(f"   2️⃣  Gerando embeddings...")
        embeddings = model.encode(texts)
        print(f"      ✅ Embeddings gerados: {embeddings.shape}")

        # 3. Criar índice FAISS
        dimension = embeddings.shape[1]
        index = faiss.IndexFlatL2(dimension)
        print(f"   3️⃣  Criando índice FAISS (dim={dimension})...")
        index.add(embeddings.astype('float32'))
        print(f"      ✅ {index.ntotal} vetores indexados")

        # 4. Testar busca
        query = "Quero ver análise de vendas"
        print(f"   4️⃣  Buscando similaridade para: '{query}'")
        query_embedding = model.encode([query])
        distances, indices = index.search(query_embedding.astype('float32'), k=3)

        print(f"      ✅ Top-3 resultados:")
        for i, (idx, dist) in enumerate(zip(indices[0], distances[0]), 1):
            print(f"         {i}. [{dist:.4f}] {texts[idx]}")

        return True, "Integração RAG OK"

    except Exception as e:
        print(f"❌ FALHOU: {str(e)}")
        traceback.print_exc()
        return False, str(e)


def main():
    """Executa todos os testes."""
    print("\n" + "="*60)
    print("🚀 VALIDAÇÃO DE DEPENDÊNCIAS RAG")
    print("="*60)
    print(f"Data: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Python: {sys.version}")

    results = {}

    # Executar testes
    tests = [
        ("sentence-transformers", test_sentence_transformers),
        ("faiss-cpu", test_faiss),
        ("spacy", test_spacy),
        ("integration", test_integration)
    ]

    for name, test_func in tests:
        try:
            success, message = test_func()
            results[name] = {'success': success, 'message': message}
        except Exception as e:
            results[name] = {'success': False, 'message': str(e)}

    # Relatório final
    print("\n" + "="*60)
    print("📊 RELATÓRIO FINAL")
    print("="*60)

    total = len(results)
    passed = sum(1 for r in results.values() if r['success'])

    print(f"\n✅ Testes aprovados: {passed}/{total}")

    for name, result in results.items():
        status = "✅" if result['success'] else "❌"
        print(f"{status} {name}: {result['message']}")

    if passed == total:
        print("\n🎉 TODAS AS DEPENDÊNCIAS RAG VALIDADAS COM SUCESSO!")
        return 0
    else:
        print("\n⚠️  ALGUMAS VALIDAÇÕES FALHARAM")
        return 1


if __name__ == '__main__':
    sys.exit(main())
