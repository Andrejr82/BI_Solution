# ⚡ Quick Start - Agent Solution BI (FastAPI + React + Streamlit)

## 🎯 Início Rápido em 5 Minutos

Sistema com **3 interfaces**: React (moderno), Streamlit (rápido), API (integração)

## ✅ Pré-requisitos

```bash
python --version   # Precisa 3.11+
node --version     # Precisa 18+ (apenas se usar React)
```

## 🚀 Instalação Express

### 1. Clone e Instale Backend

```bash
git clone <repo_url> Agent_Solution_BI
cd Agent_Solution_BI

# Criar ambiente virtual
python -m venv venv

# Ativar
venv\Scripts\activate  # Windows
source venv/bin/activate  # Linux/Mac

# Instalar dependências (FastAPI já incluído!)
pip install -r requirements.txt
```

### 2. Configure API Key

Criar `.env` na raiz:

```env
GEMINI_API_KEY=sua_chave_aqui
```

> 💡 **Obter chave**: https://makersuite.google.com/app/apikey

### 3. Escolha Sua Interface

## Opção A: 🎨 Frontend React (Recomendado para Produção)

```bash
# Instalar Node.js dependencies
cd frontend
npm install
cd ..

# Terminal 1 - API
python api_server.py

# Terminal 2 - Frontend
cd frontend && npm run dev
```

**Acessar**: http://localhost:8080

## Opção B: ⚡ Streamlit (Recomendado para Dev/Protótipo)

```bash
streamlit run streamlit_app.py
```

**Acessar**: http://localhost:8501

## Opção C: 🔌 API FastAPI (Para Integração)

```bash
python api_server.py
```

**Acessar**:
- API: http://localhost:5000
- Docs: http://localhost:5000/docs
- Redoc: http://localhost:5000/redoc

## 🎮 Primeiro Teste

### No React (Port 8080):
1. Abrir http://localhost:8080
2. Digitar no chat: `Top 10 produtos mais vendidos`
3. Ver gráfico gerado!

### No Streamlit (Port 8501):
1. Abrir http://localhost:8501
2. Digitar no chat: `Ranking de vendas por UNE`
3. Ver análise completa!

### Via API (Port 5000):
```bash
curl -X POST http://localhost:5000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Top 10 produtos", "session_id": "test"}'
```

## 📊 Comparação Rápida

| Interface | Quando Usar | Porta |
|-----------|-------------|-------|
| **React** | Produção, múltiplos usuários | 8080 |
| **Streamlit** | Dev, demos, análises rápidas | 8501 |
| **API** | Integração, mobile, webhooks | 5000 |

## 🔧 Troubleshooting Rápido

### API não inicia?

```bash
# Verificar se FastAPI está instalado
pip show fastapi uvicorn

# Se não estiver:
pip install fastapi uvicorn
```

### Frontend erro?

```bash
cd frontend
npm install
npm run dev
```

### Streamlit erro?

```bash
pip install streamlit
streamlit run streamlit_app.py
```

### Porta em uso?

```bash
# Alterar porta da API
export PORT=5001
python api_server.py

# Alterar porta do Frontend (vite.config.ts)
server: { port: 3000 }
```

## 🎉 Próximos Passos

1. ✅ Testar as 3 interfaces
2. ✅ Escolher a principal para seu caso
3. ✅ Explorar funcionalidades
4. ✅ Ver documentação completa

## 📚 Documentação

- 📘 [Arquitetura Multi-Interface](ARQUITETURA_MULTI_INTERFACE.md)
- 📗 [Frontend React](frontend/README_FRONTEND.md)
- 📙 [API FastAPI](api_server.py) - Ver docstrings
- 📕 [Streamlit](streamlit_app.py) - Ver comentários

## 🆘 Ajuda

Ver [ARQUITETURA_MULTI_INTERFACE.md](ARQUITETURA_MULTI_INTERFACE.md) para detalhes completos.

---

**Tempo**: 5-10 min
**Dificuldade**: ⭐ Fácil
**Última atualização**: 2025-10-25 (FastAPI)
