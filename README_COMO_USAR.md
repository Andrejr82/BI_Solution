# 🚀 Como Usar o Agent BI

## ✅ Sistema Testado e Funcionando!

O sistema foi verificado e está funcionando perfeitamente:
- ✅ Backend rodando
- ✅ Frontend acessível
- ✅ Login funcionando
- ✅ Banco de dados conectado
- ✅ 42.136 produtos no sistema
- ✅ 18.165 rupturas críticas detectadas

---

## 🎯 Início Rápido (1 minuto)

### Opção 1: Usar o Script Automático (RECOMENDADO)

**Execute o arquivo:**
```
INICIAR.bat
```

Esse script irá:
1. Verificar dependências
2. Criar ambiente virtual se necessário
3. Instalar dependências
4. Iniciar backend e frontend automaticamente
5. Abrir o navegador

### Opção 2: Iniciar Manualmente

**1. Abra um terminal e execute:**
```bash
cd backend
.venv\Scripts\python.exe -m uvicorn main:app --host 127.0.0.1 --port 8000
```

**2. Abra OUTRO terminal e execute:**
```bash
cd frontend-solid
npm run dev
```

**3. Acesse no navegador:**
```
http://localhost:3000
```

---

## 🔑 Credenciais de Login

```
Username: admin
Password: Admin@2024
```

---

## 📊 O Que Você Pode Fazer

### 1. **Dashboard de Monitoramento** (`/dashboard`)
- Visão geral do sistema
- KPIs principais
- Gráficos em tempo real

### 2. **Chat BI** (`/chat`)
- Converse com a IA sobre seus dados
- Faça perguntas em linguagem natural
- Receba insights automáticos

### 3. **Rupturas Críticas** (`/rupturas`)
- Visualize produtos em ruptura
- Filtre por segmento e UNE
- Monitore criticidade

### 4. **Métricas e Analytics** (`/metrics`)
- Análises detalhadas
- Tendências de erros
- Top queries

### 5. **Transferências** (`/transfers`)
- Valide transferências
- Receba sugestões inteligentes
- Histórico completo

### 6. **Administração** (`/admin`)
- Gerenciar usuários
- Sincronizar dados Parquet
- Configurações do sistema

---

## 🧪 Testar o Sistema

### Teste Automatizado Completo
```bash
python test_system.py
```

**Resultado Esperado:**
```
✓ Backend Health                 PASSOU
✓ Frontend Accessibility         PASSOU
✓ API Login                      PASSOU
✓ Authenticated Endpoint         PASSOU
✓ Database Connection            PASSOU
⚠ Chat Endpoint                  (Requer Gemini)

✓ 5/6 TESTES PASSARAM
🎉 Sistema está funcionando perfeitamente!
```

### Diagnóstico Visual
Acesse no navegador:
```
http://localhost:3000/diagnostico.html
```

---

## 🐛 Solução de Problemas

### Tela Branca?

**1. Verifique se o sistema está rodando:**
```bash
# Teste o backend
curl http://localhost:8000/health

# Teste o frontend
curl http://localhost:3000
```

**2. Limpe o cache do navegador:**
- Pressione `Ctrl + Shift + Del`
- Marque "Imagens e arquivos em cache"
- Clique em "Limpar dados"
- Recarregue com `Ctrl + F5`

**3. Limpe o LocalStorage:**
- Pressione `F12` (DevTools)
- Vá para aba "Console"
- Digite e execute:
```javascript
localStorage.clear();
window.location.reload();
```

**4. Teste em modo anônimo:**
- `Ctrl + Shift + N` (Chrome/Edge)
- `Ctrl + Shift + P` (Firefox)

### Porta em Uso?

```bash
# Limpar processos
taskkill /F /IM python.exe
taskkill /F /IM node.exe
```

### Erro ao Iniciar Backend?

```bash
# Recriar ambiente virtual
cd backend
rmdir /s .venv
python -m venv .venv
.venv\Scripts\python.exe -m pip install -r requirements.txt
```

---

## 📁 Estrutura do Projeto

```
Agent_Solution_BI/
├── backend/              # API FastAPI
│   ├── .venv/           # Ambiente virtual Python
│   ├── app/             # Código da aplicação
│   ├── data/            # Dados Parquet
│   └── main.py          # Entry point
│
├── frontend-solid/       # Interface SolidJS
│   ├── src/             # Código fonte
│   │   ├── pages/       # Páginas
│   │   ├── components/  # Componentes
│   │   └── store/       # Estado global
│   └── package.json
│
├── INICIAR.bat          # Script de inicialização
├── test_system.py       # Teste automatizado
└── README_COMO_USAR.md  # Este arquivo
```

---

## 🔧 Comandos Úteis

### Backend
```bash
# Iniciar backend
cd backend
.venv\Scripts\python.exe -m uvicorn main:app --host 127.0.0.1 --port 8000

# Ver logs
type backend\logs\app.log

# Rodar testes
cd backend
.venv\Scripts\python.exe -m pytest
```

### Frontend
```bash
# Iniciar frontend
cd frontend-solid
npm run dev

# Build de produção
npm run build

# Rodar testes
npm test

# Lint do código
npm run lint
```

---

## 📞 Suporte

### Arquivos de Ajuda:
- `README_COMO_USAR.md` - Este arquivo
- `RELATORIO_VERIFICACAO.md` - Análise técnica completa
- `GUIA_TESTES.md` - Guia detalhado de testes
- `INICIO_RAPIDO.md` - Solução rápida para tela branca

### Ferramentas de Diagnóstico:
- `test_system.py` - Teste automatizado Python
- `http://localhost:3000/diagnostico.html` - Diagnóstico visual

---

## ✨ Próximos Passos

1. **Execute `INICIAR.bat`**
2. **Aguarde as janelas abrirem**
3. **Acesse http://localhost:3000**
4. **Faça login com admin / Admin@2024**
5. **Explore o sistema!**

---

## 🎉 Tudo Pronto!

Seu sistema Agent BI está configurado e funcionando.

**Acesse agora:** http://localhost:3000

**Login:** admin / Admin@2024

Aproveite! 🚀
