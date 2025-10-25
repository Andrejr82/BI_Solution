# Instalação de Dependências RAG

**Autor:** Code Agent
**Data:** 2025-10-24
**Versão:** 1.0.0

---

## 📋 Índice

1. [Visão Geral](#visão-geral)
2. [Dependências](#dependências)
3. [Instalação Automática](#instalação-automática)
4. [Instalação Manual](#instalação-manual)
5. [Validação](#validação)
6. [Troubleshooting](#troubleshooting)

---

## 🎯 Visão Geral

Este documento descreve a instalação das dependências necessárias para o sistema **RAG (Retrieval-Augmented Generation)** do Caculinha BI.

### Por que RAG?

O sistema RAG permite:
- ✅ Busca semântica em documentação e metadados
- ✅ Respostas contextualizadas baseadas em conhecimento específico
- ✅ Recuperação eficiente de exemplos relevantes
- ✅ Melhoria contínua através de few-shot learning

---

## 📦 Dependências

### 1. sentence-transformers==2.2.2
**Propósito:** Geração de embeddings multilíngues

**Características:**
- Modelo: `paraphrase-multilingual-MiniLM-L12-v2`
- Dimensão: 384
- Suporta 50+ idiomas incluindo português
- Otimizado para busca semântica

**Uso:**
```python
from sentence_transformers import SentenceTransformer

model = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')
embeddings = model.encode(["Texto em português", "Another text"])
```

### 2. faiss-cpu==1.7.4
**Propósito:** Busca vetorial rápida e eficiente

**Características:**
- Versão CPU (compatibilidade universal)
- Busca de vizinhos mais próximos em O(log n)
- Suporta milhões de vetores
- Desenvolvido pelo Facebook AI Research

**Uso:**
```python
import faiss
import numpy as np

dimension = 384
index = faiss.IndexFlatL2(dimension)
index.add(vectors)  # Adicionar vetores
distances, indices = index.search(query, k=5)  # Buscar top-5
```

### 3. spacy==3.7.2
**Propósito:** Processamento de linguagem natural

**Características:**
- NLP industrial-grade
- Modelo português: `pt_core_news_sm`
- Tokenização, POS tagging, NER
- Pipeline customizável

**Uso:**
```python
import spacy

nlp = spacy.load('pt_core_news_sm')
doc = nlp("Texto para processar")
tokens = [token.text for token in doc]
```

---

## 🚀 Instalação Automática

### Opção 1: Script Batch (Windows)

```batch
cd C:\Users\André\Documents\Agent_Solution_BI
scripts\INSTALAR_RAG.bat
```

Este script:
1. ✅ Verifica dependências existentes
2. ✅ Instala pacotes faltantes
3. ✅ Baixa modelo spacy português
4. ✅ Atualiza `requirements.txt`
5. ✅ Valida instalação com testes

### Opção 2: Script Python

```bash
python scripts/install_rag_dependencies.py
```

---

## 🔧 Instalação Manual

### Passo 1: Instalar Pacotes

```bash
# Ativar ambiente virtual (recomendado)
venv\Scripts\activate

# Instalar dependências
pip install sentence-transformers==2.2.2
pip install faiss-cpu==1.7.4
pip install spacy==3.7.2
```

### Passo 2: Baixar Modelo Spacy

```bash
python -m spacy download pt_core_news_sm
```

### Passo 3: Atualizar requirements.txt

Adicionar ao arquivo `requirements.txt`:

```
sentence-transformers==2.2.2
faiss-cpu==1.7.4
spacy==3.7.2
```

### Passo 4: Verificar Instalação

```bash
python -c "from sentence_transformers import SentenceTransformer; print('✅ OK')"
python -c "import faiss; print('✅ OK')"
python -c "import spacy; nlp = spacy.load('pt_core_news_sm'); print('✅ OK')"
```

---

## ✅ Validação

### Teste Rápido

```bash
python tests/test_rag_dependencies.py
```

### Testes Incluídos

1. **sentence-transformers**
   - Import e carregamento de modelo
   - Geração de embeddings
   - Verificação de dimensões

2. **faiss-cpu**
   - Criação de índice
   - Adição de vetores
   - Busca de similaridade

3. **spacy**
   - Carregamento de modelo português
   - Tokenização
   - POS tagging e NER

4. **Integração**
   - Pipeline RAG completo
   - Processamento → Embedding → Busca

### Exemplo de Saída

```
🚀 VALIDAÇÃO DE DEPENDÊNCIAS RAG
============================================================
Data: 2025-10-24 14:30:00
Python: 3.11.5

🧪 TESTE: sentence-transformers
============================================================
✅ Import bem-sucedido
📥 Carregando modelo multilíngue...
✅ Modelo carregado
🔄 Gerando embeddings para 3 textos...
✅ Embeddings gerados: shape=(3, 384)

[... mais testes ...]

📊 RELATÓRIO FINAL
============================================================
✅ Testes aprovados: 4/4
✅ sentence-transformers: OK
✅ faiss-cpu: OK
✅ spacy: OK
✅ integration: Integração RAG OK

🎉 TODAS AS DEPENDÊNCIAS RAG VALIDADAS COM SUCESSO!
```

---

## 🔍 Troubleshooting

### Erro: "No module named 'sentence_transformers'"

**Solução:**
```bash
pip install --upgrade sentence-transformers==2.2.2
```

### Erro: "Could not find a version that satisfies faiss-cpu"

**Possíveis causas:**
- Python muito antigo (requer 3.7+)
- Ambiente Windows ARM (não suportado)

**Solução:**
```bash
# Verificar versão Python
python --version  # Deve ser >= 3.7

# Instalar versão compatível
pip install faiss-cpu==1.7.4 --no-cache-dir
```

### Erro: "Can't find model 'pt_core_news_sm'"

**Solução:**
```bash
# Download direto
python -m spacy download pt_core_news_sm

# Se falhar, instalar via link
pip install https://github.com/explosion/spacy-models/releases/download/pt_core_news_sm-3.7.0/pt_core_news_sm-3.7.0-py3-none-any.whl
```

### Erro: "ModuleNotFoundError: No module named 'torch'"

**Causa:** sentence-transformers requer PyTorch

**Solução:**
```bash
# CPU only (mais leve)
pip install torch --index-url https://download.pytorch.org/whl/cpu

# Ou instalar sentence-transformers (instala PyTorch automaticamente)
pip install sentence-transformers==2.2.2
```

### Performance Lenta no Primeiro Uso

**Causa:** Download de modelos pré-treinados

**Solução:**
- É normal na primeira execução
- Modelos são cacheados em `~/.cache/huggingface`
- Uso subsequente será rápido

### Erro de Memória ao Carregar Modelos

**Solução:**
```python
# Usar modelo menor
from sentence_transformers import SentenceTransformer
model = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')  # 120MB
# ao invés de
# model = SentenceTransformer('paraphrase-multilingual-mpnet-base-v2')  # 420MB
```

---

## 📊 Versões Testadas

| Componente | Versão | Python | Status |
|------------|--------|--------|--------|
| sentence-transformers | 2.2.2 | 3.11.5 | ✅ OK |
| faiss-cpu | 1.7.4 | 3.11.5 | ✅ OK |
| spacy | 3.7.2 | 3.11.5 | ✅ OK |
| pt_core_news_sm | 3.7.0 | 3.11.5 | ✅ OK |

---

## 🔗 Referências

- [sentence-transformers Docs](https://www.sbert.net/)
- [FAISS Wiki](https://github.com/facebookresearch/faiss/wiki)
- [spaCy Docs](https://spacy.io/usage)
- [Modelos spaCy Português](https://spacy.io/models/pt)

---

## 📝 Notas Importantes

1. **Versões Específicas:** Use as versões exatas especificadas para garantir compatibilidade

2. **faiss-cpu vs faiss-gpu:** Use `faiss-cpu` para desenvolvimento e compatibilidade universal. GPU requer CUDA.

3. **Modelo Multilíngue:** `paraphrase-multilingual-MiniLM-L12-v2` suporta português nativamente.

4. **Cache de Modelos:** Modelos são baixados uma vez e cacheados. Primeiro uso requer internet.

5. **Espaço em Disco:** Reservar ~500MB para modelos pré-treinados.

---

## ✅ Checklist de Instalação

- [ ] Ambiente virtual ativado
- [ ] sentence-transformers==2.2.2 instalado
- [ ] faiss-cpu==1.7.4 instalado
- [ ] spacy==3.7.2 instalado
- [ ] Modelo pt_core_news_sm baixado
- [ ] requirements.txt atualizado
- [ ] Testes de validação executados
- [ ] Todos os imports funcionando
- [ ] Pipeline RAG testado

---

**Última atualização:** 2025-10-24
**Mantido por:** Code Agent
