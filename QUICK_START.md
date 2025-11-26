# Guia Rápido de Inicialização - Agent Solution BI

## ✅ Status Atual do Sistema

### Backend (Porta 8000)
- **Status**: ✅ **RODANDO**
- **URL**: http://localhost:8000
- **Health**: ✅ Respondendo
- **Login API**: ✅ Funcionando

### Frontend (Porta 3000)
- **Status**: ❌ **NÃO INICIADO**
- **URL**: http://localhost:3000
- **Ação Necessária**: Iniciar o frontend

---

## 🚀 Como Iniciar o Frontend

### Opção 1: Iniciar Apenas o Frontend (Recomendado)

Abra um **NOVO terminal** (PowerShell ou CMD) e execute:

```bash
cd C:\Users\André\Documents\Agent_Solution_BI
python run.py --frontend-only
```

### Opção 2: Reiniciar Tudo (Backend + Frontend)

Se preferir reiniciar tudo junto:

1. **Pare o backend atual**: Pressione `Ctrl+C` no terminal onde está rodando
2. **Execute**:
   ```bash
   python run.py
   ```

---

## 🔐 Credenciais de Login

```
Usuário: admin
Senha: Admin@2024
```

> ⚠️ **Importante**: A senha é case-sensitive (A maiúsculo)

---

## 📋 Checklist de Inicialização

- [x] Backend rodando na porta 8000
- [x] Backend respondendo ao health check
- [x] Login API funcionando
- [ ] Frontend rodando na porta 3000
- [ ] Navegador aberto em http://localhost:3000
- [ ] Login realizado com sucesso

---

## 🔧 Comandos Úteis

### Verificar se Backend está Rodando
```bash
curl http://localhost:8000/health
```

### Testar Login via API
```bash
python test_login.py
```

### Verificar Portas em Uso
```bash
# Backend (8000)
netstat -ano | findstr :8000

# Frontend (3000)
netstat -ano | findstr :3000
```

### Diagnóstico Completo
```bash
python diagnose_system.py
```

---

## ⚡ Próximo Passo

**Inicie o frontend agora**:

```bash
python run.py --frontend-only
```

Depois acesse: http://localhost:3000/login

---

## 💡 Dicas

1. **Mantenha o terminal do backend aberto** - Não feche a janela onde o backend está rodando
2. **Use um novo terminal para o frontend** - Abra uma nova janela PowerShell/CMD
3. **Aguarde o frontend compilar** - Next.js pode levar 30-60 segundos para iniciar
4. **O navegador abrirá automaticamente** - Quando o frontend estiver pronto

---

## ❓ Problemas Comuns

### "Porta 3000 já está em uso"
```bash
python kill_port.py 3000
python run.py --frontend-only
```

### "Backend não está disponível" (no navegador)
- Verifique se o backend ainda está rodando
- Execute: `curl http://localhost:8000/health`
- Se necessário, reinicie: `python run.py --backend-only`

### "Credenciais inválidas"
- Certifique-se de usar `Admin@2024` (com A maiúsculo)
- Não use `admin123` ou `admin`
