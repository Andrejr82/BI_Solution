# 📁 Estrutura do Projeto Agent_Solution_BI

**Data de Atualização:** 2025-10-18
**Versão:** 2.0 (Reorganizada)

---

## 📊 Visão Geral

O projeto foi reorganizado para melhor manutenibilidade e navegação. Todos os arquivos foram movidos da raiz para diretórios apropriados.

---

## 🗂️ Estrutura de Diretórios

### 📁 Raiz do Projeto
```
Agent_Solution_BI/
├── main.py                  # Backend FastAPI
├── streamlit_app.py         # Frontend Streamlit (entrada principal)
├── README.md                # Documentação principal
├── requirements.txt         # Dependências Python
├── .env                     # Variáveis de ambiente (local)
├── .gitignore              # Arquivos ignorados pelo Git
│
├── core/                    # Código fonte principal
├── pages/                   # Páginas Streamlit
├── data/                    # Dados e configurações
├── docs/                    # Documentação organizada
├── scripts/                 # Scripts auxiliares
├── tests/                   # Testes automatizados
├── ui/                      # Componentes de UI
└── api/                     # Endpoints FastAPI
```

---

## 📚 Documentação (docs/)

### docs/reports/
**Relatórios técnicos e análises**
- `AUDIT_REPORT.md` - Relatório de auditoria do projeto
- `AUDIT_REPORT_20251017.md` - Auditoria anterior
- `RELATORIO_EXECUTIVO_COMPLETO.md` - Relatório executivo
- `RELATORIO_FINAL_LIMPEZA.md` - Relatório de limpeza
- `DIFF_VALIDADORES_UNE_TOOLS.md` - Comparação de validadores

### docs/guides/
**Guias e tutoriais**
- `COMECE_AQUI.txt` - Guia de início rápido
- `README_FEW_SHOT.md` - Documentação do Few-Shot Learning
- `README_LIMPEZA_PROJETO.md` - Guia de limpeza
- `LIMPEZA_README.md` - Instruções de limpeza
- `GIT_CLEANUP_INSTRUCTIONS.md` - Instruções Git
- `GEMINI.md` - Documentação do LLM Gemini

### docs/planning/
**Planejamento e roadmaps**
- `PLANO_FINALIZACAO.md` - Roadmap de implementações
- `RESUMO_FINALIZACAO.md` - Estado atual do projeto
- `IMPLEMENTACAO_COMPLETA_UNE_TOOLS.md` - Implementação UNE Tools
- `INTEGRACAO_FEW_SHOT.md` - Integração Few-Shot
- `RECOMENDACOES_POS_INTEGRACAO.md` - Recomendações técnicas

### docs/releases/
**Notas de release e entregas**
- `ENTREGA_PILAR_2.md` - Entrega do Pilar 2
- `PILAR_2_IMPLEMENTADO.md` - Documentação do Pilar 2
- `RELEASE_NOTES_PILAR_2.md` - Release notes

### docs/indexes/
**Índices e listagens**
- `INDICE_LIMPEZA.md` - Índice de limpeza
- `INDICE_PILAR_2.md` - Índice do Pilar 2
- `LISTA_COMPLETA_ARQUIVOS.md` - Lista de arquivos

### docs/temp/
**Documentos temporários** (podem ser removidos)
- `.cleanup_report.md` - Relatório de limpeza temporário
- `RESUMO_PILAR_2.txt` - Resumo temporário
- `SUMARIO_LIMPEZA.md` - Sumário temporário

---

## 🛠️ Scripts (scripts/)

### scripts/cleanup/
**Scripts de limpeza e organização**
- `CLEAN_TEMP_FILES.py` - Limpa arquivos temporários
- `cleanup_project.py` - Limpeza do projeto
- `preview_cleanup.py` - Preview de limpeza
- `EXECUTAR_LIMPEZA.bat` - Batch de limpeza (Windows)

### scripts/utils/
**Scripts utilitários**
- `run_fase1_tests.py` - Executa testes da Fase 1
- `run_streamlit.py` - Inicia aplicação Streamlit
- `start_app.py` - Script de inicialização
- `verify_cleanup.py` - Verifica limpeza
- `run_streamlit.bat` - Batch Streamlit (Windows)
- `start_app.bat` - Batch de inicialização (Windows)
- `start_app.sh` - Shell script de inicialização (Linux/Mac)

### scripts/data_processing/
**Scripts de processamento de dados**
- `process_admmat_extended.py` - Processa dados admmat
- `process_admmat_extended_v2.py` - Versão 2 do processador
- `test_validadores_funcionando.py` - Testa validadores

---

## 💻 Código Fonte (core/)

### core/agents/
**Agentes especializados de IA**
- `code_gen_agent.py` - Agente de geração de código
- `bi_agent.py` - Agente de Business Intelligence
- Outros agentes especializados

### core/learning/
**Sistema de aprendizado (Few-Shot Learning)**
- `few_shot_manager.py` (350 linhas) - Gerenciador Few-Shot
- `pattern_matcher.py` (328 linhas) - Identificador de padrões
- Sistema de aprendizado com queries bem-sucedidas

### core/validation/
**Sistema de validação**
- `code_validator.py` (199 linhas) - Validador de código
- 10 regras de validação
- Auto-fix de problemas comuns

### core/graph/
**Workflow LangGraph**
- Máquina de estados para orquestração
- Nós de processamento de consultas

### core/connectivity/
**Adaptadores de dados**
- `parquet_adapter.py` - Adaptador Parquet
- `sql_adapter.py` - Adaptador SQL Server
- Sistema híbrido de consultas

### core/business_intelligence/
**Motor de BI**
- `direct_query_engine.py` - Engine de consultas diretas
- `hybrid_query_engine.py` - Engine híbrida
- Processamento de análises

---

## 🎨 Interface (pages/)

**Páginas Streamlit multi-página**
- `01_🏠_Home.py` - Página inicial
- `02_📊_Analytics.py` - Analytics e dashboards
- `03_🔍_Query.py` - Interface de consultas
- `04_⚙️_Settings.py` - Configurações
- Outras páginas especializadas

---

## 📦 Dados (data/)

### data/parquet/
**Arquivos de dados**
- `admmat.parquet` - Dataset principal
- Outros arquivos parquet

### data/learning/
**Histórico de aprendizado**
- `successful_queries_*.jsonl` - Queries bem-sucedidas
- Logs de feedback

### data/
**Configurações**
- `config.json` - Configuração da aplicação
- `data_catalog.json` - Catálogo de dados
- `query_patterns.json` - Padrões de queries

---

## 🧪 Testes (tests/)

**Testes automatizados**
- Testes unitários
- Testes de integração
- Testes de validação

---

## 🚀 Como Usar

### Iniciar a Aplicação

#### Método 1: Streamlit (Recomendado)
```bash
# Linha de comando
streamlit run streamlit_app.py

# Ou usando script auxiliar
python scripts/utils/run_streamlit.py

# Windows
scripts/utils/run_streamlit.bat
```

#### Método 2: FastAPI Backend
```bash
python main.py

# Ou
uvicorn main:app --reload
```

### Scripts Úteis

**Limpeza do projeto:**
```bash
python scripts/cleanup/CLEAN_TEMP_FILES.py --execute
```

**Testes:**
```bash
python scripts/utils/run_fase1_tests.py
pytest
```

**Processamento de dados:**
```bash
python scripts/data_processing/process_admmat_extended.py
```

---

## 📈 Estatísticas

### Antes da Reorganização
- **43 arquivos** na raiz do projeto
- Difícil navegação
- Estrutura confusa

### Depois da Reorganização
- **4 arquivos** na raiz (apenas essenciais)
- Estrutura clara e organizada
- Fácil navegação
- Documentação categorizada

### Arquivos Movidos
- **Relatórios:** 5 arquivos → `docs/reports/`
- **Guias:** 6 arquivos → `docs/guides/`
- **Planejamento:** 6 arquivos → `docs/planning/`
- **Scripts de limpeza:** 4 arquivos → `scripts/cleanup/`
- **Scripts utilitários:** 7 arquivos → `scripts/utils/`
- **Processamento:** 3 arquivos → `scripts/data_processing/`
- **Temporários:** 3 arquivos → `docs/temp/`

**Total:** 34+ arquivos reorganizados

---

## 🔍 Localização Rápida

### "Onde encontro...?"

**Documentação sobre Few-Shot Learning?**
→ `docs/guides/README_FEW_SHOT.md`

**Roadmap de implementações?**
→ `docs/planning/PLANO_FINALIZACAO.md`

**Como começar?**
→ `docs/guides/COMECE_AQUI.txt`

**Scripts de limpeza?**
→ `scripts/cleanup/`

**Relatórios técnicos?**
→ `docs/reports/`

**Código do Few-Shot?**
→ `core/learning/few_shot_manager.py`

**Validador de código?**
→ `core/validation/code_validator.py`

**Iniciar aplicação?**
→ `streamlit_app.py` ou `scripts/utils/`

---

## 🎯 Próximos Passos

1. **Revisar documentos temporários** em `docs/temp/` e decidir se mantém ou remove
2. **Implementar Pilar 4** (Análise de Logs) conforme `docs/planning/PLANO_FINALIZACAO.md`
3. **Manter estrutura organizada** ao adicionar novos arquivos

---

## 📝 Notas

- Todos os imports no código foram mantidos funcionais
- Caminhos relativos ajustados automaticamente
- Git rastreia as movimentações corretamente
- Estrutura segue padrões Python/Streamlit

---

**Versão:** 2.0
**Data:** 2025-10-18
**Autor:** Claude Code
**Status:** ✅ Reorganização Completa
