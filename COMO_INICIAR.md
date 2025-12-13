# Como Iniciar o Sistema - Agent Solution BI

## Problema Resolvido

O sistema não iniciava corretamente através do `run.bat` devido a:
1. **Ambiente virtual do Poetry corrompido/incompleto**
2. **Poetry não instalado no PATH global**
3. **Falta de verificação e configuração automática do ambiente**

## Solução Implementada

Foi criado um sistema robusto de inicialização que:
- ✓ Detecta e cria automaticamente o ambiente virtual Python
- ✓ Instala todas as dependências do backend via `requirements.txt`
- ✓ Verifica Node.js e instala dependências do frontend
- ✓ Limpa portas ocupadas automaticamente
- ✓ Trata erros de forma clara e informativa

## Como Usar

### ⚡ Opção 1: Script Python run.py (Mais Confiável)

```bash
python run.py
```

Este é o método **RECOMENDADO** pois:
- Configura automaticamente o ambiente virtual
- Instala todas as dependências
- Gerencia as portas automaticamente
- Inicia backend e frontend simultaneamente

Opções disponíveis:
- `python run.py --backend-only` - Inicia apenas o backend
- `python run.py --frontend-only` - Inicia apenas o frontend
- `python run.py --dev` - Modo desenvolvimento com logs verbosos

### 📦 Opção 2: Instalação Manual das Dependências

**Se a Opção 1 falhar ou você preferir instalar manualmente:**

#### Passo 1: Instalar Dependências do Backend

```bash
cd backend
.venv\Scripts\python.exe -m pip install -r requirements.txt
cd ..
```

**⏱️ Tempo estimado**: 5-15 minutos (depende da velocidade da internet)
**📊 Tamanho total**: ~1.5 GB de pacotes

**Pacotes principais que serão instalados:**
- FastAPI + Uvicorn (servidor web)
- LangChain + LangGraph (IA e agentes)
- Pandas, NumPy, Polars (análise de dados)
- PyTorch (machine learning)
- Plotly, Matplotlib, Seaborn (visualizações)
- E muitos outros...

#### Passo 2: Instalar Dependências do Frontend

```bash
cd frontend-solid
pnpm install
# OU se não tiver pnpm:
npm install
cd ..
```

**⏱️ Tempo estimado**: 2-3 minutos

#### Passo 3: Iniciar o Sistema

Após instalar as dependências, execute:

```bash
python run.py
```

### 🪟 Opção 3: Arquivo run.bat (Windows)

```batch
run.bat
```

Este comando irá:
1. Verificar Node.js e Python
2. Limpar processos antigos
3. Limpar cache Python
4. Instalar/verificar dependências do Node.js
5. Configurar ambiente virtual do backend
6. Limpar portas 8000 e 3000
7. Iniciar backend e frontend simultaneamente

### 🔧 Opção 4: Backend Manual (Separado)

```bash
cd backend
python setup_and_run.py
```

Este script irá:
1. Verificar versão do Python (3.11+ necessário)
2. Criar ambiente virtual se não existir
3. Instalar dependências do requirements.txt
4. Iniciar o servidor FastAPI com uvicorn

## Arquivos Criados/Modificados

### Novos Arquivos

1. **backend/setup_and_run.py**
   - Script robusto de configuração e inicialização do backend
   - Gerenciamento automático do ambiente virtual
   - Instalação automática de dependências
   - Tratamento de erros melhorado

2. **COMO_INICIAR.md** (este arquivo)
   - Documentação completa do sistema de inicialização

### Arquivos Modificados

1. **package.json**
   - Atualizado `dev:backend` para usar `setup_and_run.py`
   - Comando: `cd backend && python setup_and_run.py`

2. **run.bat**
   - Melhorias no tratamento de erros
   - Verificação do ambiente virtual do backend
   - Feedback mais claro sobre o progresso
   - Numeração correta dos passos (6 etapas)

## Requisitos do Sistema

### Backend
- **Python 3.11+** instalado e no PATH
- Bibliotecas listadas em `backend/requirements.txt`

### Frontend
- **Node.js 20+** instalado e no PATH
- **npm** ou **pnpm** disponível

## URLs do Sistema

Após iniciar o sistema, acesse:

- **Frontend**: http://localhost:3000
- **Backend**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs

## Credenciais Padrão

```
Username: admin
Senha: Admin@2024
```

## Troubleshooting

### Problema: "Python 3.11+ required"
**Solução**: Instale Python 3.11 ou superior de https://python.org

### Problema: "Node.js não encontrado"
**Solução**: Instale Node.js 20+ de https://nodejs.org

### Problema: "Porta 8000 ou 3000 ocupada"
**Solução**: O script `clean-port.js` é executado automaticamente. Se persistir:
```bash
node scripts/clean-port.js
```

### Problema: "Failed to install dependencies"
**Solução**: Execute manualmente:
```bash
cd backend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

### Problema: Backend não inicia
**Solução**:
1. Verifique os logs no terminal
2. Tente recriar o ambiente virtual:
```bash
cd backend
rmdir /s /q .venv
python setup_and_run.py
```

## Estrutura de Logs

O sistema exibe logs coloridos para facilitar o acompanhamento:
- **[BACKEND]** - Mensagens do backend (azul)
- **[FRONTEND]** - Mensagens do frontend (verde)
- **[OK]** - Operações bem-sucedidas (verde)
- **[INFO]** - Informações (azul)
- **[AVISO]** - Avisos (amarelo)
- **[ERRO]** - Erros (vermelho)

## Próximos Passos

Se tudo estiver funcionando:
1. Acesse http://localhost:3000
2. Faça login com as credenciais padrão
3. Comece a usar o sistema!

## Suporte

Em caso de problemas persistentes:
1. Verifique se Python 3.11+ e Node.js 20+ estão instalados
2. Execute `python --version` e `node --version`
3. Tente limpar tudo e reinstalar:
   ```batch
   taskkill /F /IM python.exe
   taskkill /F /IM node.exe
   cd backend
   rmdir /s /q .venv
   cd ..
   run.bat
   ```
