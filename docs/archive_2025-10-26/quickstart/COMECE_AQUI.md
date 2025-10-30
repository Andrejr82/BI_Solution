# 🚀 COMECE AQUI - Agent Solution BI

## ⚡ Você tem 3 opções de interface!

Escolha a que mais se adequa ao seu caso:

---

## 1️⃣ Frontend React (🎨 Interface Moderna - **RECOMENDADO**)

**Para**: Produção, múltiplos usuários, interface profissional

```bash
# Terminal 1 - Iniciar API
python api_server.py

# Terminal 2 - Iniciar Frontend
cd frontend
npm install  # Apenas primeira vez
npm run dev
```

**Acessar**: http://localhost:8080

**Funcionalidades**:
- ✅ 14 páginas completas
- ✅ Chat BI com IA
- ✅ Dashboards interativos
- ✅ Painel admin
- ✅ Diagnóstico sistema
- ✅ Gemini playground

---

## 2️⃣ Streamlit (⚡ Interface Rápida)

**Para**: Protótipos, demos, desenvolvimento interno

```bash
streamlit run streamlit_app.py
```

**Acessar**: http://localhost:8501

**Funcionalidades**:
- ✅ Chat BI simplificado
- ✅ Gráficos rápidos
- ✅ Zero configuração
- ✅ Python puro

---

## 3️⃣ API FastAPI (🔌 Para Integração)

**Para**: Integrar com outros sistemas, mobile apps, scripts

```bash
python api_server.py
```

**Acessar**:
- Documentação: http://localhost:5000/docs
- API: http://localhost:5000

**Funcionalidades**:
- ✅ REST API completa
- ✅ Swagger docs
- ✅ 11 endpoints
- ✅ Fácil consumo

---

## ⚙️ Configuração Inicial (IMPORTANTE!)

Antes de executar qualquer opção, criar arquivo `.env` na raiz:

```bash
# Windows
echo GEMINI_API_KEY=sua_chave_aqui > .env

# Linux/Mac
echo "GEMINI_API_KEY=sua_chave_aqui" > .env
```

**Obter chave Gemini**: https://makersuite.google.com/app/apikey

---

## 📊 Qual interface escolher?

### Use React se:
- ✅ Precisa de produção
- ✅ Quer interface profissional
- ✅ Múltiplos usuários
- ✅ Funcionalidades completas

### Use Streamlit se:
- ✅ Prototipagem rápida
- ✅ Demos internas
- ✅ Análises exploratórias
- ✅ Desenvolvimento interno

### Use API se:
- ✅ Integrar com outro sistema
- ✅ Mobile app
- ✅ Scripts automatizados
- ✅ Webhooks

---

## 🆘 Problemas?

### API não inicia?
```bash
pip install fastapi uvicorn
```

### Frontend erro?
```bash
cd frontend
npm install
```

### Streamlit erro?
```bash
pip install streamlit
```

### GEMINI_API_KEY não encontrada?
Verificar se arquivo `.env` existe na raiz com a chave

---

## 📚 Documentação Completa

- [Quick Start Completo](QUICK_START_ATUALIZADO.md)
- [Arquitetura Multi-Interface](ARQUITETURA_MULTI_INTERFACE.md)
- [Sumário da Implementação](SUMARIO_IMPLEMENTACAO_FASTAPI.md)
- [Frontend React](frontend/README_FRONTEND.md)

---

## 🎯 Primeiro Teste

Depois de iniciar uma das interfaces, teste:

```
"Top 10 produtos mais vendidos"
```

Deve retornar gráfico + tabela + análise!

---

**Versão**: 1.0.0
**Data**: 2025-10-25
**Status**: ✅ Pronto para usar!

**Dúvidas?** Ver documentação completa nos links acima.
