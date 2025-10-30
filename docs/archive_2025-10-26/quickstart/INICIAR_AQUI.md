# 🚀 INICIAR SISTEMA - Agent BI React

## ⚡ Início Rápido (2 minutos)

### 1️⃣ Execute o Script de Inicialização

```bash
# Windows (RECOMENDADO)
start_react_system_fixed.bat
```

**O script vai automaticamente:**
- ✅ Verificar Python e Node.js
- ✅ Instalar dependências (se necessário)
- ✅ Liberar portas 5000 e 8080
- ✅ Iniciar Backend FastAPI (porta 5000)
- ✅ Iniciar Frontend React (porta 8080)
- ✅ Abrir em janelas separadas

---

### 2️⃣ Acesse o Sistema

Aguarde ~10 segundos e acesse:

**🌐 Frontend React**: http://localhost:8080

---

### 3️⃣ Faça Login

Credenciais de teste:
- **Usuário**: `admin`
- **Senha**: `admin123`

---

## 🎯 Pronto! O sistema está rodando.

---

## 📚 Documentação Completa

Para mais detalhes, consulte:
- **GUIA_REACT_COMPLETO.md** - Documentação completa
- **SOLUCOES_IMPLEMENTADAS.md** - Problemas resolvidos
- **README_NOVO.md** - Visão geral do projeto

---

## ❓ Problemas?

### Backend não inicia?
```bash
# Verificar se porta 5000 está livre
netstat -ano | findstr :5000
# Se ocupada, matar processo
taskkill /F /PID <PID>
```

### Frontend não inicia?
```bash
# Verificar se porta 8080 está livre
netstat -ano | findstr :8080
# Se ocupada, matar processo
taskkill /F /PID <PID>
```

### Erro "Module not found"?
```bash
cd frontend
npm install
```

---

## 🔄 Reiniciar Sistema

1. Pressione `Ctrl+C` nas janelas do backend e frontend
2. Execute novamente: `start_react_system_fixed.bat`

---

**✅ Sistema pronto para uso! Bom trabalho!**
