#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Exemplo de uso das dependências RAG instaladas.

Este exemplo demonstra como usar sentence-transformers, FAISS e spaCy
para implementar um sistema RAG básico.

Autor: Code Agent
Data: 2025-10-24
Versão: 1.0.0

Pré-requisitos:
    - Dependências RAG instaladas (execute scripts/INSTALAR_RAG.bat)
    - Validação bem-sucedida (execute tests/test_rag_dependencies.py)
"""

from sentence_transformers import SentenceTransformer
import faiss
import spacy
import numpy as np
from typing import List, Tuple
from datetime import datetime


class SimpleRAG:
    """
    Sistema RAG básico para demonstração.

    Implementa pipeline completo:
    1. Processamento de texto (spaCy)
    2. Geração de embeddings (sentence-transformers)
    3. Indexação e busca (FAISS)
    """

    def __init__(self):
        """Inicializa modelos e índice."""
        print("🚀 Inicializando SimpleRAG...")

        # Carregar modelo de embeddings
        print("   📥 Carregando modelo de embeddings...")
        self.embedding_model = SentenceTransformer(
            'paraphrase-multilingual-MiniLM-L12-v2'
        )
        self.dimension = 384  # Dimensão do modelo

        # Carregar spaCy
        print("   📥 Carregando modelo spaCy português...")
        self.nlp = spacy.load('pt_core_news_sm')

        # Inicializar índice FAISS
        print("   🏗️  Criando índice FAISS...")
        self.index = faiss.IndexFlatL2(self.dimension)

        # Armazenamento de documentos
        self.documents = []

        print("   ✅ SimpleRAG inicializado!\n")

    def preprocess(self, text: str) -> str:
        """
        Pré-processa texto usando spaCy.

        Args:
            text: Texto para processar

        Returns:
            Texto processado (lematizado e sem stopwords)
        """
        doc = self.nlp(text.lower())

        # Lematizar e remover stopwords/pontuação
        tokens = [
            token.lemma_ for token in doc
            if not token.is_stop and not token.is_punct
        ]

        return ' '.join(tokens)

    def add_documents(self, documents: List[str]):
        """
        Adiciona documentos ao índice RAG.

        Args:
            documents: Lista de documentos (strings)
        """
        print(f"📚 Adicionando {len(documents)} documentos ao índice...")

        # Gerar embeddings
        print("   🔄 Gerando embeddings...")
        embeddings = self.embedding_model.encode(documents)

        # Adicionar ao índice FAISS
        print("   🔄 Indexando vetores...")
        self.index.add(embeddings.astype('float32'))

        # Armazenar documentos
        self.documents.extend(documents)

        print(f"   ✅ {len(documents)} documentos indexados!")
        print(f"   📊 Total no índice: {self.index.ntotal}\n")

    def search(
        self,
        query: str,
        k: int = 3,
        preprocess_query: bool = True
    ) -> List[Tuple[str, float]]:
        """
        Busca documentos similares à query.

        Args:
            query: Texto da consulta
            k: Número de resultados a retornar
            preprocess_query: Se deve pré-processar a query

        Returns:
            Lista de tuplas (documento, distância)
        """
        print(f"🔍 Buscando: '{query}'")

        # Pré-processar query se solicitado
        if preprocess_query:
            processed_query = self.preprocess(query)
            print(f"   📝 Query processada: '{processed_query}'")
        else:
            processed_query = query

        # Gerar embedding da query
        print("   🔄 Gerando embedding da query...")
        query_embedding = self.embedding_model.encode([processed_query])

        # Buscar no índice
        print(f"   🔄 Buscando top-{k} resultados...")
        distances, indices = self.index.search(
            query_embedding.astype('float32'),
            k
        )

        # Montar resultados
        results = []
        for idx, dist in zip(indices[0], distances[0]):
            if idx < len(self.documents):
                results.append((self.documents[idx], float(dist)))

        print(f"   ✅ {len(results)} resultados encontrados!\n")

        return results

    def get_stats(self) -> dict:
        """
        Retorna estatísticas do índice.

        Returns:
            Dicionário com estatísticas
        """
        return {
            'total_documents': len(self.documents),
            'index_size': self.index.ntotal,
            'dimension': self.dimension,
            'model': 'paraphrase-multilingual-MiniLM-L12-v2'
        }


def main():
    """Exemplo de uso do SimpleRAG."""
    print("\n" + "="*60)
    print("📖 EXEMPLO DE USO - RAG SYSTEM")
    print("="*60)
    print(f"Data: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

    # 1. Inicializar RAG
    rag = SimpleRAG()

    # 2. Documentos de exemplo (perguntas de negócio)
    documents = [
        "Qual foi o faturamento total da empresa em 2024?",
        "Mostre os produtos mais vendidos no último trimestre",
        "Análise de vendas por região geográfica do Brasil",
        "Qual a margem de lucro dos produtos da categoria A?",
        "Histórico completo de vendas dos últimos 12 meses",
        "Ranking de vendedores por performance",
        "Produtos com estoque abaixo do mínimo",
        "Comparativo de vendas entre filiais",
        "Clientes com maior ticket médio",
        "Sazonalidade de vendas por mês"
    ]

    # 3. Adicionar documentos ao índice
    rag.add_documents(documents)

    # 4. Estatísticas
    stats = rag.get_stats()
    print("📊 ESTATÍSTICAS DO ÍNDICE:")
    print(f"   Total de documentos: {stats['total_documents']}")
    print(f"   Tamanho do índice: {stats['index_size']}")
    print(f"   Dimensão: {stats['dimension']}")
    print(f"   Modelo: {stats['model']}\n")

    # 5. Exemplos de busca
    queries = [
        "Quero ver faturamento",
        "Produtos em falta no estoque",
        "Análise geográfica",
        "Performance dos vendedores"
    ]

    print("="*60)
    print("🔍 EXEMPLOS DE BUSCA SEMÂNTICA")
    print("="*60 + "\n")

    for i, query in enumerate(queries, 1):
        print(f"{'─'*60}")
        print(f"BUSCA {i}/{len(queries)}")
        print(f"{'─'*60}")

        results = rag.search(query, k=3)

        print(f"📋 Resultados para '{query}':\n")

        for j, (doc, dist) in enumerate(results, 1):
            similarity = 1 / (1 + dist)  # Converter distância em similaridade
            print(f"   {j}. [Similaridade: {similarity:.4f}]")
            print(f"      {doc}\n")

    # 6. Demonstração de pré-processamento
    print("="*60)
    print("🔧 DEMONSTRAÇÃO DE PRÉ-PROCESSAMENTO")
    print("="*60 + "\n")

    test_text = "Os produtos mais vendidos da empresa foram analisados"
    processed = rag.preprocess(test_text)

    print(f"Original:    {test_text}")
    print(f"Processado:  {processed}\n")

    # 7. Análise spaCy
    print("="*60)
    print("🧠 ANÁLISE NLP (spaCy)")
    print("="*60 + "\n")

    doc = rag.nlp(test_text)

    print(f"Tokens: {[token.text for token in doc]}")
    print(f"Lemmas: {[token.lemma_ for token in doc]}")
    print(f"POS:    {[(token.text, token.pos_) for token in doc]}")
    print(f"Stop:   {[(token.text, token.is_stop) for token in doc]}\n")

    # 8. Informações sobre embeddings
    print("="*60)
    print("📐 INFORMAÇÕES SOBRE EMBEDDINGS")
    print("="*60 + "\n")

    sample_text = "Exemplo de texto para análise"
    embedding = rag.embedding_model.encode([sample_text])

    print(f"Texto: '{sample_text}'")
    print(f"Shape do embedding: {embedding.shape}")
    print(f"Tipo: {type(embedding)}")
    print(f"Dimensão: {embedding.shape[1]}")
    print(f"Primeiros 10 valores: {embedding[0][:10]}")
    print(f"Min: {embedding.min():.4f}, Max: {embedding.max():.4f}")
    print(f"Mean: {embedding.mean():.4f}, Std: {embedding.std():.4f}\n")

    # 9. Conclusão
    print("="*60)
    print("✅ EXEMPLO CONCLUÍDO COM SUCESSO!")
    print("="*60)
    print("\n📚 Próximos passos:")
    print("   1. Adaptar para seu caso de uso específico")
    print("   2. Adicionar seus documentos/metadados")
    print("   3. Integrar com sistema de queries")
    print("   4. Implementar cache de embeddings")
    print("   5. Otimizar parâmetros de busca\n")


if __name__ == '__main__':
    try:
        main()
    except ImportError as e:
        print("\n❌ ERRO: Dependências RAG não instaladas!")
        print(f"   {str(e)}\n")
        print("Execute primeiro:")
        print("   scripts\\INSTALAR_RAG.bat\n")
    except Exception as e:
        print(f"\n❌ ERRO: {str(e)}\n")
        import traceback
        traceback.print_exc()
