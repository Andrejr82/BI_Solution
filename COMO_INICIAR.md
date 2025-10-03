# 🚀 Como Iniciar o Agent_BI Localmente

Este guia mostra como iniciar a aplicação **Agent_BI - Agente de Negócios** no seu computador.

---

## 📋 Pré-requisitos

Antes de iniciar, certifique-se de ter:

1. ✅ **Python 3.11+** instalado
2. ✅ **Ambiente virtual** criado (`.venv`)
3. ✅ **Dependências** instaladas (`pip install -r requirements.txt`)
4. ✅ **Arquivo `.env`** configurado com suas credenciais

---

## 🖥️ Windows

### Opção 1: Script BAT (Recomendado)

Duplo clique no arquivo ou execute no terminal:

```cmd
start_app.bat
```

**O que acontece**:
1. ✅ Ativa o ambiente virtual
2. ✅ Inicia o Backend FastAPI em background (porta 8000)
3. ✅ Aguarda backend estar 100% pronto
4. ✅ Inicia o Frontend Streamlit na mesma janela (porta 8501)
5. ✅ Ctrl+C encerra tudo (backend + frontend)

**Acessar**:
- Frontend: http://localhost:8501
- Backend API: http://localhost:8000
- Docs API: http://localhost:8000/docs

### Opção 2: Script Python

```cmd
python start_app.py
```

---

## 🐧 Linux / macOS

### Opção 1: Script SH

```bash
./start_app.sh
```

Se der erro de permissão:
```bash
chmod +x start_app.sh
./start_app.sh
```

### Opção 2: Script Python (Multiplataforma)

```bash
python start_app.py
```

---

## 🎯 Ordem de Inicialização

Os scripts garantem a ordem correta:

```
1. Ambiente Virtual ✅
2. Backend FastAPI  ✅ (inicia primeiro)
3. Health Check     ✅ (aguarda backend estar pronto)
4. Frontend Streamlit ✅ (inicia após backend OK)
```

---

## 🛑 Como Parar a Aplicação

### Todas as plataformas:
- Pressione `Ctrl+C` no terminal
- O script encerra automaticamente backend e frontend

---

## ⚙️ Modo Manual (Sem Scripts)

Se preferir iniciar manualmente:

### 1. Ativar Ambiente Virtual

**Windows:**
```cmd
.venv\Scripts\activate
```

**Linux/macOS:**
```bash
source .venv/bin/activate
```

### 2. Iniciar Backend (Terminal 1)

```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

### 3. Iniciar Frontend (Terminal 2)

```bash
streamlit run streamlit_app.py
```

---

## 🔍 Verificação de Saúde

### Backend Health Check
```bash
curl http://localhost:8000/health
```

Resposta esperada:
```json
{"status": "healthy"}
```

### Frontend
Abra o navegador em: http://localhost:8501

---

## ❌ Solução de Problemas

### Erro: "Porta já em uso"

**Backend (8000)**:
```bash
# Windows
netstat -ano | findstr :8000
taskkill /PID <PID> /F

# Linux/macOS
lsof -ti:8000 | xargs kill -9
```

**Frontend (8501)**:
```bash
# Windows
netstat -ano | findstr :8501
taskkill /PID <PID> /F

# Linux/macOS
lsof -ti:8501 | xargs kill -9
```

### Erro: "Ambiente virtual não encontrado"

Crie o ambiente virtual:
```bash
python -m venv .venv
```

### Erro: "Módulo não encontrado"

Instale as dependências:
```bash
pip install -r requirements.txt
```

### Erro: "Credenciais LLM não encontradas"

Configure o arquivo `.env`:
```bash
cp .env.example .env
# Edite o .env com suas chaves de API
```

---

## 📊 Arquivos de Inicialização

| Arquivo | Plataforma | Descrição |
|---------|-----------|-----------|
| `start_app.bat` | Windows | Script batch com janelas separadas |
| `start_app.py` | Todas | Script Python multiplataforma |
| `start_app.sh` | Linux/macOS | Script bash com health check |

---

## 🎓 Credenciais de Teste

**Desenvolvimento (bypass)**:
- Usuário: `admin`
- Senha: `bypass`

**Usuário padrão**:
- Usuário: `cacula`
- Senha: `cacula123`

---

## 📚 Documentação Adicional

- 📖 [README.md](README.md) - Documentação completa do projeto
- 🔧 [MELHORIAS_IMPLEMENTADAS.md](MELHORIAS_IMPLEMENTADAS.md) - Changelog v1.1.0
- 🐛 [INVESTIGACAO_RESOLVIDA.md](INVESTIGACAO_RESOLVIDA.md) - Bugs corrigidos

---

## 💡 Dicas

1. **Sempre use os scripts** para garantir ordem correta de inicialização
2. **Aguarde o backend** estar pronto antes de acessar o frontend
3. **Monitore os logs** nas janelas de terminal para debug
4. **Use Ctrl+C** para encerrar graciosamente

---

**Status**: ✅ Pronto para uso local

**Última atualização**: Outubro de 2025
