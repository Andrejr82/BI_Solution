# Guia Rápido para Desenvolvedores
**Data:** 2025-10-29
**Público:** Desenvolvedores que trabalham com o projeto Cacula BI

---

## ÍNDICE
1. [Configuração Rápida](#configuração-rápida)
2. [Estrutura do Projeto](#estrutura-do-projeto)
3. [Desenvolvimento Local](#desenvolvimento-local)
4. [Padrões de Código](#padrões-de-código)
5. [Debugging](#debugging)
6. [Deploy](#deploy)
7. [Comandos Úteis](#comandos-úteis)

---

## CONFIGURAÇÃO RÁPIDA

### 1. Clonar Repositório
```bash
git clone <repo-url>
cd Agent_Solution_BI
```

### 2. Criar Ambiente Virtual
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/Mac
python3 -m venv venv
source venv/bin/activate
```

### 3. Instalar Dependências
```bash
pip install -r requirements.txt
pip install -r requirements-dev.txt  # Para desenvolvimento
```

### 4. Configurar Variáveis de Ambiente
```bash
# Copiar arquivo de template
cp .env.template .env

# Editar .env com suas credenciais
# DATABASE_URL=mssql+pyodbc://seu_banco_de_dados
# API_KEY=sua_chave_api
```

### 5. Iniciar Aplicação
```bash
streamlit run streamlit_app.py
```

---

## ESTRUTURA DO PROJETO

```
Agent_Solution_BI/
├── core/
│   ├── agents/              # Agentes IA (LLM, Code Gen)
│   │   ├── bi_agent_nodes.py
│   │   └── code_gen_agent.py
│   ├── business_intelligence/  # Motor BI
│   │   ├── agent_graph_cache.py
│   │   └── direct_query_engine_backup.py
│   ├── connectivity/        # Conexão com dados
│   │   └── polars_dask_adapter.py
│   ├── config/             # Configurações
│   │   ├── column_mapping.py
│   │   └── une_mapping.py
│   ├── learning/           # Sistema de aprendizado
│   │   └── self_healing_system.py
│   ├── auth.py             # Autenticação
│   └── utils/              # Utilidades
│
├── data/
│   ├── cache/              # Cache de queries
│   ├── learning/           # Dados de aprendizado
│   └── query_history/      # Histórico de queries
│
├── docs/                   # Documentação
├── scripts/                # Scripts auxiliares
├── tests/                  # Testes
└── streamlit_app.py        # Aplicação principal
```

---

## DESENVOLVIMENTO LOCAL

### Estrutura de um Novo Recurso

```
feature/
├── core/new_feature.py      # Implementação
├── tests/test_new_feature.py # Testes
├── docs/NEW_FEATURE.md       # Documentação
└── requirements.txt          # Deps (se necessário)
```

### Workflow de Desenvolvimento

```bash
# 1. Criar branch
git checkout -b feature/sua-feature

# 2. Implementar
# Editar arquivos...

# 3. Testar localmente
pytest tests/ -v

# 4. Executar linter
flake8 core/
black core/
mypy core/

# 5. Documentar
# Atualizar README ou criar doc nova

# 6. Commit e Push
git add .
git commit -m "feat: Sua feature aqui"
git push origin feature/sua-feature

# 7. Criar Pull Request
```

### Padrão de Commits

```
feat:   Nova funcionalidade
fix:    Correção de bug
docs:   Documentação
style:  Formatação de código
refactor: Refatoração
perf:   Melhoria de performance
test:   Testes
chore:  Tarefas de manutenção
```

Exemplo:
```bash
git commit -m "feat: Implementar novo tipo de gráfico em Plotly"
```

---

## PADRÕES DE CÓDIGO

### Python

```python
# 1. Imports
from typing import Optional, List, Dict
import logging
from core.utils.logger import get_logger

# 2. Logger
logger = get_logger(__name__)

# 3. Classe
class MyFeature:
    """
    Descrição breve da classe.

    Descrição longa se necessário.

    Attributes:
        param1: Descrição do parâmetro
        param2: Descrição do parâmetro
    """

    def __init__(self, param1: str, param2: int = 10):
        self.param1 = param1
        self.param2 = param2

    def my_method(self, arg: str) -> Optional[Dict]:
        """
        Descrição do método.

        Args:
            arg: Descrição do argumento

        Returns:
            Descrição do retorno

        Raises:
            ValueError: Quando algo está errado
        """
        try:
            logger.info(f"Executando com arg={arg}")
            # Implementação
            return {"resultado": "ok"}
        except Exception as e:
            logger.error(f"Erro em my_method: {str(e)}", exc_info=True)
            raise
```

### Docstrings

```python
def funcao_exemplo(parametro1: str, parametro2: int = 5) -> str:
    """
    Descrição em uma linha.

    Descrição mais longa explicando em detalhes o que a função faz,
    quando usar, e qualquer contexto importante.

    Args:
        parametro1: Descrição do primeiro parâmetro.
        parametro2: Descrição do segundo parâmetro. Padrão é 5.

    Returns:
        Descrição do que é retornado.

    Raises:
        ValueError: Descrição de quando é levantado.
        KeyError: Descrição de quando é levantado.

    Example:
        >>> resultado = funcao_exemplo("test")
        >>> print(resultado)
        "test processado"
    """
    pass
```

---

## DEBUGGING

### Logs

```bash
# Ver logs da aplicação
tail -f logs/app.log

# Ver logs de erro
tail -f logs/error.log

# Ver logs de banco de dados
tail -f logs/database.log
```

### Modo Debug no Streamlit

```bash
streamlit run streamlit_app.py --logger.level=debug
```

### Debug com Print Statements

```python
import logging
logger = logging.getLogger(__name__)

logger.debug(f"Valor de x: {x}")
logger.info("Operação iniciada")
logger.warning("Aviso: algo pode estar errado")
logger.error("Erro: algo deu errado", exc_info=True)
```

### Debugger Python

```python
import pdb

def minha_funcao():
    x = 10
    pdb.set_trace()  # O programa pausará aqui
    y = x + 5
    return y

# Comandos no pdb:
# n - próxima linha
# c - continuar
# l - listar código
# p variavel - imprimir variável
# pp variavel - pretty print
# w - mostrar onde você está
```

### Teste Unitário

```bash
# Executar todos os testes
pytest tests/ -v

# Executar teste específico
pytest tests/test_my_feature.py::test_caso_especifico -v

# Com coverage
pytest tests/ --cov=core --cov-report=html
```

---

## DEPLOY

### Pré-Deploy

```bash
# 1. Executar testes
pytest tests/ -v

# 2. Verificar linting
flake8 core/ --max-line-length=100

# 3. Verificar type hints
mypy core/

# 4. Build
python setup.py build
```

### Deploy em Produção

```bash
# 1. Tag versão
git tag -a v1.0.0 -m "Release v1.0.0"

# 2. Push
git push origin v1.0.0

# 3. Deploy (conforme seu pipeline)
./deploy.sh production
```

### Verificar Deploy

```bash
# Testes pós-deploy
curl https://seu-app.com/health
python scripts/test_deployment.py
```

---

## COMANDOS ÚTEIS

### Git

```bash
# Ver branches
git branch -a

# Atualizar fork
git pull upstream main

# Rebase interativo
git rebase -i HEAD~3

# Ver diferenças
git diff main..feature/sua-feature

# Limpar branches locais
git branch -d branch_local
```

### Python

```bash
# Verificar versão
python --version

# Listar pacotes instalados
pip list

# Atualizar pacote
pip install --upgrade package_name

# Exportar requirements
pip freeze > requirements.txt

# Verificar dependências não usadas
pip-audit
```

### Streamlit

```bash
# Cache clear
streamlit cache clear

# Run com argumentos
streamlit run streamlit_app.py --server.port 8081

# Run em modo development
streamlit run streamlit_app.py --logger.level=debug --client.showErrorDetails=true
```

### Database

```bash
# Teste de conexão
python -c "from core.connectivity.polars_dask_adapter import PolarsAdapter; PolarsAdapter().test_connection()"

# Query rápida
python scripts/quick_query.py "SELECT TOP 10 * FROM tabela"

# Listar UNEs
python scripts/query_unes_from_db.py
```

---

## CHECKLIST ANTES DE FAZER COMMIT

- [ ] Código testado localmente
- [ ] Testes unitários passam
- [ ] Linter passou
- [ ] Type hints adicionados
- [ ] Docstrings completas
- [ ] Sem secrets nos commits (use .env)
- [ ] Mensagem de commit clara e descritiva
- [ ] Nenhum arquivo temporário incluído
- [ ] README atualizado (se necessário)

---

## RECURSOS ÚTEIS

- **Documentação Principal:** `docs/README.md`
- **API Reference:** `docs/API_REFERENCE.md`
- **Issues Abertos:** GitHub Issues
- **Discussões:** GitHub Discussions
- **Wiki:** GitHub Wiki

---

## SUPORTE

- Dúvidas gerais? Consulte `/docs`
- Erro? Confira `/docs/TROUBLESHOOTING.md`
- Novo desenvolvedor? Leia `/docs/ONBOARDING.md`
- Help? Abra uma issue no GitHub!

---

**Última atualização:** 2025-10-29
**Versão:** 1.0.0
