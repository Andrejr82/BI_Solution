# 📁 Estrutura do Projeto Agent_Solution_BI

Organização atualizada em: **2025-10-02**

---

## 🎯 Visão Geral

Estrutura organizada profissionalmente com separação clara de responsabilidades.

```
Agent_Solution_BI/
├── 📚 docs/              # Documentação técnica
├── 📊 reports/           # Relatórios e investigações
├── 🧪 tests/             # Testes automatizados
├── ⚙️ config/            # Configurações e templates
├── 🔧 scripts/           # Scripts de manutenção
├── 🎯 core/              # Código principal da aplicação
├── 📄 pages/             # Páginas Streamlit
├── 💾 data/              # Dados do projeto
├── 🎨 ui/                # Componentes de UI
├── streamlit_app.py      # Aplicação principal
├── main.py               # Backend FastAPI
└── requirements.txt      # Dependências Python
```

---

## 📚 docs/ - Documentação

```
docs/
├── README.md                      # Índice de documentação
├── CLAUDE.md                      # Instruções para Claude Code
├── DEPLOY_STREAMLIT_CLOUD.md     # Guia de deploy
├── guides/                        # Guias específicos
└── archive/                       # Documentação antiga
```

**Propósito:** Toda documentação técnica do projeto.

**Arquivos principais:**
- **CLAUDE.md** - Visão geral, comandos, arquitetura, padrões
- **DEPLOY_STREAMLIT_CLOUD.md** - Deploy, secrets, troubleshooting

---

## 📊 reports/ - Relatórios

```
reports/
├── README.md
├── investigation/               # Investigações de bugs
│   ├── INVESTIGATION_REPORT.md
│   └── TROUBLESHOOTING_UNE_QUERY.md
└── code_analysis/              # Análises técnicas
    ├── relatorio_codigo_completo.md
    ├── relatorio_integracao_projeto.md
    ├── relatorio_limpeza.md
    └── relatorio_teste_completo.md
```

**Propósito:** Documentação de investigações, bugs e análises.

**Categorias:**
- **investigation/** - Troubleshooting e resolução de problemas
- **code_analysis/** - Análises técnicas e métricas

---

## 🧪 tests/ - Testes

```
tests/
├── README.md                   # Guia de testes
├── pytest.ini                  # Configuração pytest
├── test_llm_fix.py            # Valida LLM adapters
├── test_une_query.py          # Valida queries UNE
└── unit/                      # Testes unitários (pytest)
```

**Propósito:** Testes automatizados e diagnósticos.

**Como executar:**
```bash
# Testes de diagnóstico
python tests/test_llm_fix.py
python tests/test_une_query.py

# Testes unitários
pytest
pytest tests/unit/
```

---

## ⚙️ config/ - Configurações

```
config/
├── README.md                   # Guia de configuração
├── streamlit_secrets.toml      # Template de secrets
├── runtime.txt                 # Versão Python (3.11.9)
└── database/                   # Configs de banco (opcional)
    ├── alembic.ini            # Alembic migrations
    └── migrations/            # Database migrations
```

**Propósito:** Templates e configurações para diferentes ambientes.

**Arquivos principais:**
- **streamlit_secrets.toml** - Template para Streamlit Cloud
- **runtime.txt** - Versão Python para deploy
- **database/** - Migrations SQL Server (opcional)

**Uso de migrations:**
```bash
cd config/database
alembic upgrade head
```

---

## 🔧 scripts/ - Scripts de Manutenção

```
scripts/
├── README.md
└── cleanup_project.ps1        # Limpeza e reorganização
```

**Propósito:** Scripts utilitários para manutenção.

**Como executar:**
```powershell
.\scripts\cleanup_project.ps1
```

⚠️ Scripts fazem mudanças em arquivos - usar com cuidado!

---

## 🎯 core/ - Código Principal

```
core/
├── agents/                    # Agentes de IA especializados
├── business_intelligence/     # Motor de consultas BI
├── config/                    # Gerenciamento de configurações
├── connectivity/              # Adaptadores de dados (Parquet, SQL)
├── database/                  # Autenticação e DB
├── factory/                   # Fábrica de componentes
├── graph/                     # LangGraph workflows
├── llm_adapter.py            # Adapters Gemini/DeepSeek
├── tools/                     # Ferramentas utilitárias
├── utils/                     # Utilidades comuns
└── visualization/             # Geração de gráficos
```

**Propósito:** Lógica principal da aplicação.

**Arquitetura:** Clean Architecture com padrões Factory e State Machine.

---

## 📄 pages/ - Páginas Streamlit

```
pages/
├── 1_Página_Inicial.py
├── 4_Monitoramento.py
├── 6_Painel_de_Administração.py
└── 7_Gerenciar_Catalogo.py
```

**Propósito:** Interface multi-página do Streamlit.

---

## 💾 data/ - Dados

```
data/
├── parquet/                   # Arquivos de dados
│   └── admmat.parquet        # Dataset principal (252K produtos)
├── catalog_focused.json       # Catálogo de dados
├── config.json               # Configuração da app
└── query_history/            # Histórico de queries
```

**Propósito:** Dados da aplicação e configurações.

**Dataset principal:**
- **admmat.parquet** - 252,077 produtos, 5 UNEs, 95 colunas

---

## 🎨 ui/ - Componentes de UI

```
ui/
└── components/               # Componentes reutilizáveis
```

**Propósito:** Componentes de interface reutilizáveis.

---

## 📝 Arquivos na Raiz

### Aplicação
- **streamlit_app.py** - Aplicação principal Streamlit
- **main.py** - Backend FastAPI (opcional)

### Dependências
- **requirements.txt** - Dependências Python compiladas
- **requirements.in** - Dependências fonte

### Configuração
- **README.md** - Documentação principal do projeto
- **.env.example** - Template de variáveis de ambiente
- **.gitignore** - Arquivos ignorados pelo Git

### Estilo
- **style.css** - Estilos customizados

---

## 📊 Estatísticas

### Organização (2025-10-02)

**Arquivos Movidos:** 15 total
- 2 → docs/
- 6 → reports/ (2 investigation + 4 code_analysis)
- 2 → tests/
- 2 → config/
- 1 → scripts/
- 2 → config/database/ (alembic + migrations/)

**READMEs Criados:** 7
- docs/README.md
- reports/README.md
- tests/README.md
- config/README.md
- scripts/README.md
- PROJECT_STRUCTURE.md (este arquivo)

**Resultado:**
- ✅ Raiz limpa e organizada
- ✅ Documentação categorizada
- ✅ Fácil navegação
- ✅ Profissional e escalável

---

## 🔗 Links Rápidos

- [Documentação Principal](docs/README.md)
- [Guia de Deploy](docs/DEPLOY_STREAMLIT_CLOUD.md)
- [Instruções Claude](docs/CLAUDE.md)
- [Relatórios de Investigação](reports/investigation/)
- [Guia de Testes](tests/README.md)
- [Configuração](config/README.md)

---

## 📋 Convenções

### Nomenclatura de Pastas
- **Lowercase com underline:** `core/`, `business_intelligence/`
- **Sem acentos:** Usar apenas ASCII
- **Descritivas:** Nome reflete conteúdo

### Nomenclatura de Arquivos
- **Python:** `snake_case.py`
- **Markdown:** `UPPERCASE.md` (docs) ou `lowercase.md` (reports)
- **Config:** `lowercase.toml`, `lowercase.ini`

### READMEs
- **Obrigatório:** Toda pasta principal tem README
- **Formato:** Markdown com emojis
- **Conteúdo:** Propósito, estrutura, como usar, links

---

## ✅ Compatibilidade

### Streamlit Cloud
✅ Arquivos principais na raiz (`streamlit_app.py`, `requirements.txt`)
✅ Configurações em `config/` (detectado automaticamente)
✅ Secrets via dashboard (template em `config/streamlit_secrets.toml`)

### Pytest
✅ `pytest.ini` em `tests/` (encontrado automaticamente)
✅ Executar da raiz: `pytest`
✅ Executar pasta específica: `pytest tests/unit/`

### Alembic (Opcional)
✅ Configs em `config/database/`
✅ Executar: `cd config/database && alembic upgrade head`

### Scripts
✅ Organizados em `scripts/`
✅ Executar: `.\scripts\script_name.ps1`

---

**Última atualização:** 2025-10-02
**Commits relacionados:** d7947f9, f8bed42, 5c5528f
