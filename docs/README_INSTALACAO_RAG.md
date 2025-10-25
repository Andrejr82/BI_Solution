# 🚀 Instalação Rápida - Dependências RAG

## TL;DR - Para Usuários Apressados

```batch
# Windows - Execução com um clique
scripts\INSTALAR_RAG.bat
```

**Pronto!** O script faz tudo automaticamente.

---

## 📋 O Que Será Instalado

### 1. sentence-transformers 2.2.2
- Embeddings multilíngues (384 dimensões)
- Suporte nativo a português
- ~500MB de download (primeira vez)

### 2. faiss-cpu 1.7.4
- Busca vetorial ultra-rápida
- CPU-only (universal)
- ~20MB

### 3. spacy 3.7.2 + pt_core_news_sm
- NLP para português
- Tokenização, POS, NER
- ~40MB

**Total:** ~560MB de download + ~1.5GB temporário durante instalação

---

## ⚡ Guia Rápido de Instalação

### Pré-requisitos

```batch
# 1. Verificar pré-requisitos (opcional)
python scripts/check_rag_prerequisites.py

# 2. Instalar tudo
scripts\INSTALAR_RAG.bat

# 3. Validar instalação
python tests/test_rag_dependencies.py
```

### Tempos Estimados

- ⏱️ Verificação de pré-requisitos: 10s
- ⏱️ Instalação completa: 2-5 min (primeira vez)
- ⏱️ Validação: 30-60s

---

## 🔧 Instalação Manual (Se Preferir)

```bash
# Ativar ambiente virtual
venv\Scripts\activate

# Instalar dependências
pip install sentence-transformers==2.2.2
pip install faiss-cpu==1.7.4
pip install spacy==3.7.2

# Baixar modelo português
python -m spacy download pt_core_news_sm

# Testar
python -c "from sentence_transformers import SentenceTransformer; print('OK')"
python -c "import faiss; print('OK')"
python -c "import spacy; nlp = spacy.load('pt_core_news_sm'); print('OK')"
```

---

## ✅ Como Saber se Funcionou

### Teste Rápido

```python
# Execute no Python interativo
from sentence_transformers import SentenceTransformer
import faiss
import spacy

# Se não deu erro, está tudo OK!
print("✅ RAG dependencies instaladas com sucesso!")
```

### Teste Completo

```bash
python tests/test_rag_dependencies.py
```

**Saída esperada:**
```
🎉 TODAS AS DEPENDÊNCIAS RAG VALIDADAS COM SUCESSO!
✅ Testes aprovados: 4/4
```

---

## 🐛 Problemas Comuns

### "No module named 'sentence_transformers'"

**Solução:**
```bash
pip install --upgrade sentence-transformers==2.2.2
```

### "Can't find model 'pt_core_news_sm'"

**Solução:**
```bash
python -m spacy download pt_core_news_sm
```

### Timeout durante download

**Solução:**
```bash
# Aumentar timeout do pip
pip install --timeout=300 sentence-transformers==2.2.2
```

### Erro de SSL/Certificado

**Solução:**
```bash
pip install --trusted-host pypi.org --trusted-host files.pythonhosted.org sentence-transformers==2.2.2
```

---

## 📚 Documentação Completa

Para detalhes completos, veja:
- [docs/guides/INSTALACAO_RAG.md](docs/guides/INSTALACAO_RAG.md) - Documentação completa
- [tests/test_rag_dependencies.py](tests/test_rag_dependencies.py) - Código dos testes

---

## 🎯 Próximos Passos

Após instalação bem-sucedida:

1. ✅ Dependências RAG instaladas
2. ➡️ Configurar sistema RAG
3. ➡️ Integrar com Caculinha BI
4. ➡️ Treinar com dados específicos

---

## 📞 Suporte

Problemas? Verifique:
1. [Troubleshooting](docs/guides/INSTALACAO_RAG.md#troubleshooting)
2. Logs em `reports/rag_installation_report.json`
3. Execute `python scripts/check_rag_prerequisites.py`

---

**Criado por:** Code Agent
**Data:** 2025-10-24
**Versão:** 1.0.0
