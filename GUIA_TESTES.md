# 🧪 Guia de Testes - Agent BI

## 📋 Testes Disponíveis

### 1️⃣ Teste Robusto do Sistema (Python)

**Arquivo:** `test_system.py`

**O que faz:**
- ✅ Verifica se o backend está rodando
- ✅ Verifica se o frontend está acessível
- ✅ Testa o login na API
- ✅ Testa endpoints autenticados
- ✅ Testa conexão com banco de dados
- ✅ Testa o endpoint de chat

**Como executar:**
```bash
python test_system.py
```

**Pré-requisito:** O sistema deve estar rodando (`run.bat`)

---

### 2️⃣ Página de Diagnóstico (HTML)

**URL:** http://localhost:3000/diagnostico.html

**O que faz:**
- 🔍 Testa conectividade com backend
- 🔍 Testa API de login
- 🔍 Verifica LocalStorage
- 🔍 Verifica suporte a JavaScript/ES6
- 🔍 Fornece diagnóstico visual no navegador

**Como acessar:**
1. Inicie o sistema com `run.bat`
2. Abra o navegador em http://localhost:3000/diagnostico.html
3. Os testes serão executados automaticamente

---

### 3️⃣ Testes Unitários (Vitest)

**Arquivos:**
- `frontend-solid/src/__tests__/App.test.tsx`
- `frontend-solid/src/__tests__/Layout.test.tsx`
- `frontend-solid/src/__tests__/ErrorBoundary.test.tsx`

**Como executar:**
```bash
cd frontend-solid
npm test
```

**Para ver UI de testes:**
```bash
cd frontend-solid
npm run test:ui
```

**Para ver cobertura:**
```bash
cd frontend-solid
npm run test:coverage
```

---

## 🐛 Solucionando Tela Branca

Se você está vendo uma tela branca, siga este checklist:

### ✅ Checklist de Diagnóstico

1. **Backend está rodando?**
   ```bash
   # Teste manualmente
   curl http://localhost:8000/health
   ```

2. **Frontend está rodando?**
   ```bash
   # Verifique se o Vite está ativo na porta 3000
   netstat -an | findstr :3000
   ```

3. **Console do navegador tem erros?**
   - Pressione F12
   - Vá para a aba "Console"
   - Procure por mensagens em vermelho

4. **LocalStorage está bloqueado?**
   - Abra http://localhost:3000/diagnostico.html
   - Verifique se o teste de LocalStorage passa

5. **Credenciais corretas?**
   - Username: `admin`
   - Password: `Admin@2024`

### 🔧 Soluções Comuns

#### Problema: Backend não está rodando
**Solução:**
```bash
run.bat
```

#### Problema: Porta 3000 ou 8000 em uso
**Solução:**
```bash
# Limpar processos
taskkill /F /IM python.exe
taskkill /F /IM node.exe
```

#### Problema: Cache corrompido
**Solução:**
1. Pressione Ctrl+Shift+Del no navegador
2. Limpe "Cached images and files"
3. Ou acesse http://localhost:3000/diagnostico.html e clique em "Limpar Cache"

#### Problema: Versão do navegador antiga
**Solução:**
- Atualize para a versão mais recente do Chrome, Firefox ou Edge

#### Problema: Erro 401 (Unauthorized)
**Solução:**
```javascript
// No console do navegador (F12)
localStorage.clear();
window.location.href = '/login';
```

---

## 🚀 Teste Rápido

Execute todos os testes de uma vez:

```bash
# 1. Limpar processos
taskkill /F /IM python.exe 2>nul
taskkill /F /IM node.exe 2>nul

# 2. Iniciar sistema
run.bat

# 3. Em outro terminal, executar testes
python test_system.py
```

---

## 📊 Interpretando Resultados

### ✅ Todos os testes passaram
🎉 Sistema está funcionando perfeitamente!
- Acesse: http://localhost:3000
- Login: admin / Admin@2024

### ⚠️ Alguns testes falharam
Sistema parcialmente funcional:
- Se falhar "Chat Endpoint": Verifique configuração do Gemini
- Se falhar "Database": Verifique arquivos Parquet em `backend/data/`

### ❌ Muitos testes falharam
Sistema não está funcionando:
1. Verifique se `run.bat` foi executado
2. Verifique logs no terminal
3. Execute `python test_system.py` para diagnóstico detalhado

---

## 🔍 Debug Avançado

### Ver logs do backend
```bash
# Windows
type backend\logs\app.log

# Linux/Mac
tail -f backend/logs/app.log
```

### Verificar se o Vite compilou corretamente
```bash
cd frontend-solid
npm run build
```

### Teste manual do endpoint de login
```bash
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d "{\"username\":\"admin\",\"password\":\"Admin@2024\"}"
```

---

## 📞 Ainda com problemas?

1. Execute o diagnóstico HTML: http://localhost:3000/diagnostico.html
2. Execute o teste Python: `python test_system.py`
3. Verifique o console do navegador (F12)
4. Verifique se há erros nos logs do backend

Se o problema persistir, capture:
- Screenshot da tela branca
- Console do navegador (F12)
- Resultado de `python test_system.py`
- Logs do terminal onde rodou `run.bat`
