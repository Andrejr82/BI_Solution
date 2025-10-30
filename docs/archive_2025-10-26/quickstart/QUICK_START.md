# ⚡ Quick Start - Agent Solution BI

## 🎯 Início Rápido em 5 Minutos

Este guia te ajuda a ter o sistema funcionando rapidamente.

## ✅ Pré-requisitos Rápidos

```bash
# Verificar instalações
python --version   # Precisa 3.11+
node --version     # Precisa 18+
npm --version      # Precisa 9+
```

Se algo faltar:
- Python: https://www.python.org/downloads/
- Node.js: https://nodejs.org/

## 🚀 Instalação Express (5 passos)

### 1. Clone e Entre no Projeto

```bash
git clone <repo_url> Agent_Solution_BI
cd Agent_Solution_BI
```

### 2. Configure o Backend

```bash
# Criar ambiente virtual
python -m venv venv

# Ativar
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Instalar dependências
pip install -r requirements.txt

# Adicionar Flask
pip install flask flask-cors
```

### 3. Configure as Variáveis

Criar arquivo `.env` na raiz:

```env
GEMINI_API_KEY=sua_chave_aqui
```

> 💡 **Obter chave Gemini**: https://makersuite.google.com/app/apikey

### 4. Configure o Frontend

```bash
cd frontend
npm install
cd ..
```

### 5. Inicie o Sistema

**Opção A - Dois Terminais:**

Terminal 1 (Backend):
```bash
python backend_api.py
```

Terminal 2 (Frontend):
```bash
cd frontend
npm run dev
```

**Opção B - Script Único (Windows):**

Criar `start.bat`:
```batch
@echo off
start cmd /k "python backend_api.py"
timeout /t 3
start cmd /k "cd frontend && npm run dev"
```

Executar:
```bash
start.bat
```

**Opção B - Script Único (Linux/Mac):**

Criar `start.sh`:
```bash
#!/bin/bash
python backend_api.py &
sleep 3
cd frontend && npm run dev
```

Tornar executável e executar:
```bash
chmod +x start.sh
./start.sh
```

## 🌐 Acessar o Sistema

1. **Frontend**: http://localhost:8080
2. **API**: http://localhost:5000
3. **Health Check**: http://localhost:5000/api/health

## 🎮 Primeiro Teste

1. Abrir http://localhost:8080
2. Fazer login (usuário: admin, senha: admin)
3. No chat, perguntar:
   ```
   Top 10 produtos mais vendidos
   ```
4. Aguardar resposta com gráfico!

## 📊 Páginas Disponíveis

Após login, explorar:

- **Chat BI** (/) - Converse com a IA
- **Métricas** (/metricas) - Dashboard
- **Gráficos** (/graficos-salvos) - Salvos
- **Exemplos** (/exemplos) - Templates
- **Admin** (/admin) - Configurações

## 🔧 Troubleshooting Rápido

### Backend não inicia?

```bash
pip install flask flask-cors
```

### Frontend erro CORS?

Verificar se backend está em http://localhost:5000

### Porta em uso?

Alterar em `frontend/vite.config.ts`:
```typescript
server: {
  port: 3000  // trocar de 8080 para 3000
}
```

### GEMINI_API_KEY não encontrada?

Verificar se arquivo `.env` existe na raiz do projeto com:
```env
GEMINI_API_KEY=sua_chave_aqui
```

## 📚 Próximos Passos

1. ✅ Explorar todas as páginas
2. ✅ Testar diferentes perguntas
3. ✅ Salvar gráficos no dashboard
4. ✅ Ver [INSTALACAO_COMPLETA.md](INSTALACAO_COMPLETA.md) para detalhes

## 🆘 Precisa de Ajuda?

- 📘 [Instalação Completa](INSTALACAO_COMPLETA.md)
- 📗 [Documentação Frontend](frontend/README_FRONTEND.md)
- 📙 [README Completo](README_PROJETO_COMPLETO.md)
- 🐛 [Troubleshooting Detalhado](INSTALACAO_COMPLETA.md#troubleshooting)

## 🎉 Parabéns!

Sistema funcionando! Agora você pode:
- ✨ Fazer perguntas em linguagem natural
- 📊 Gerar gráficos automaticamente
- 💾 Salvar visualizações
- 🤖 Aproveitar a IA para análises

---

**Tempo estimado**: 5-10 minutos
**Dificuldade**: ⭐ Fácil
**Última atualização**: 2025-10-25
