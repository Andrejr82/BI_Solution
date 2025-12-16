# 🛒 Agent Solution BI - Lojas Caçula

**Sistema de Business Intelligence conversacional com tecnologia Gemini para a rede Lojas Caçula.**

Uma aplicação full-stack moderna que combina um frontend reativo em **SolidJS** com um backend robusto em **FastAPI**, permitindo análise de dados através de linguagem natural.

---

## 🚀 Início Rápido

### Pré-requisitos
- Python 3.11+
- Node.js 20+
- Chave de API do Google Gemini

### Instalação e Execução

```bash
# 1. Clone o repositório
git clone https://github.com/Andrejr82/BI_Solution.git
cd BI_Solution

# 2. Configure o backend
cd backend
python -m venv .venv
.venv\Scripts\activate  # Windows
pip install -r requirements.txt

# 3. Configure o .env (crie backend/.env)
# GEMINI_API_KEY=sua_chave_aqui
# SECRET_KEY=gere_uma_chave_segura

# 4. Inicie a aplicação (volta para raiz)
cd ..
start.bat   # Windows - inicia backend + frontend
```

**Acesse:** http://localhost:3000

---

## 🏗️ Arquitetura

| Camada | Tecnologia | Descrição |
|--------|------------|-----------|
| **Frontend** | SolidJS + TailwindCSS | Interface reativa com tema Lojas Caçula |
| **Backend** | FastAPI (Python 3.11+) | API REST com autenticação JWT |
| **IA** | Google Gemini 2.5 Flash | Agente conversacional para BI |
| **Dados** | Parquet + Polars | Análise de alta performance |
| **Auth** | Supabase + Parquet fallback | Autenticação híbrida |

---

## ✨ Funcionalidades

### 💬 Chat BI Inteligente
Converse com seus dados em linguagem natural. O assistente entende perguntas sobre vendas, estoque, produtos e gera gráficos automaticamente.

### 📊 Dashboard
Painéis de controle com KPIs em tempo real:
- Top produtos por vendas
- Distribuição por categoria
- Indicadores de estoque

### 🔴 Análise de Rupturas
Identificação proativa de produtos críticos:
- **Top Grupos em Ruptura** - Categorias com mais produtos críticos
- **Drill-down por Grupo** - Clique para ver produtos detalhados
- **Filtros por UNE** - Análise por unidade de negócio
- **Gerar Pedido de Compra** - Exportação formatada para reposição

### 📈 Analytics Avançado
- Vendas por categoria
- Giro de estoque
- Curva ABC (Pareto)

### 🔄 Transferências
Sugestões automáticas de transferência entre UNEs para evitar rupturas.

---

## 🎨 Tema Visual

O sistema utiliza a paleta de cores oficial **Lojas Caçula - Light Mode**:

| Cor | Hex | Uso |
|-----|-----|-----|
| Marrom Caçula | `#8B7355` | Cor primária |
| Dourado/Bronze | `#C9A961` | Destaques |
| Verde Oliva | `#2D7A3E` | Sucesso/Ações |
| Vermelho Terroso | `#B94343` | Alertas críticos |
| Fundo | `#FAFAFA` | Background principal |

---

## 📁 Estrutura do Projeto

```
BI_Solution/
├── backend/              # API FastAPI
│   ├── app/
│   │   ├── api/          # Endpoints REST
│   │   ├── core/         # Serviços (auth, agents, data)
│   │   └── config/       # Configurações
│   └── data/parquet/     # Dados analíticos
├── frontend-solid/       # App SolidJS
│   ├── src/
│   │   ├── pages/        # Dashboard, Chat, Rupturas, Analytics
│   │   ├── components/   # PlotlyChart, etc.
│   │   └── lib/          # API client
├── docs/                 # Documentação
├── scripts/              # Scripts de utilidade
└── start.bat             # Script de inicialização
```

---

## 🔐 Segurança

- **Autenticação JWT** com tokens seguros
- **Controle de Acesso por Segmento** - Usuários veem apenas dados de seus segmentos permitidos
- **Mascaramento de PII** - CPF, e-mail e telefone são protegidos
- **Execução Segura de Código** - Código gerado pela IA é executado em ambiente controlado

---

## 👥 Usuários de Teste

| Usuário | Senha | Acesso |
|---------|-------|--------|
| `admin` | `admin` | Todos os segmentos |
| `hugo.mendes` | `123456` | ARMARINHO E CONFECÇÃO |

---

## 📝 Variáveis de Ambiente

Crie o arquivo `backend/.env`:

```env
PROJECT_NAME="Agent BI"
API_V1_STR="/api/v1"

# IA
GEMINI_API_KEY="sua_chave_api"
LLM_MODEL_NAME="models/gemini-2.5-flash-preview-05-20"

# Segurança
SECRET_KEY="gere_uma_chave_segura"
ACCESS_TOKEN_EXPIRE_MINUTES=60

# Supabase (opcional)
USE_SUPABASE_AUTH=true
SUPABASE_URL="https://xxx.supabase.co"
SUPABASE_ANON_KEY="xxx"
SUPABASE_SERVICE_ROLE_KEY="xxx"
```

---

## 🛠️ Desenvolvimento

```bash
# Backend apenas
npm run dev:backend

# Frontend apenas
npm run dev:frontend

# Ambos
npm run dev
```

---

## 📄 Licença

Projeto proprietário - Lojas Caçula © 2024-2025
