# 🚀 COMO USAR - Launcher Único

## ⚡ Início Rápido

### Windows
```
Duplo clique em: start.bat
```

### Linux/Mac
```bash
chmod +x start.sh  # Primeira vez
./start.sh
```

### Qualquer Sistema
```bash
python start_all.py
```

---

## 📋 Menu

Ao executar, você verá um menu com 5 opções:

```
1. React Frontend     - Interface moderna (produção)
2. Streamlit          - Interface rápida (desenvolvimento)
3. API FastAPI        - API REST para integração
4. TODAS as interfaces - Inicia as 3 ao mesmo tempo
5. Sair
```

---

## 🎯 Qual Escolher?

### Use Opção 1 (React) se:
- ✅ Quer interface profissional
- ✅ Vai usar em produção
- ✅ Precisa de múltiplas páginas

**Acesso**: http://localhost:8080

### Use Opção 2 (Streamlit) se:
- ✅ Quer algo rápido
- ✅ Está desenvolvendo/testando
- ✅ Precisa de protótipo

**Acesso**: http://localhost:8501

### Use Opção 3 (API) se:
- ✅ Vai integrar com outro sistema
- ✅ Precisa apenas dos endpoints REST
- ✅ Quer ver documentação da API

**Acesso**: http://localhost:5000/docs

### Use Opção 4 (TODAS) se:
- ✅ Quer testar tudo
- ✅ Comparar interfaces
- ✅ Demonstração completa

---

## ⚙️ Configuração (Primeira Vez)

1. **Instalar dependências Python**:
```bash
pip install -r requirements.txt
```

2. **Configurar API Key**:
Criar arquivo `.env` na raiz:
```env
GEMINI_API_KEY=sua_chave_aqui
```

3. **Executar launcher**:
```bash
python start_all.py
```

Pronto! O launcher faz o resto automaticamente.

---

## 🛑 Como Encerrar

Pressione `Ctrl+C` no terminal.

O launcher encerrará TODOS os serviços automaticamente.

---

## ❓ Problemas?

### Erro: "FastAPI não instalado"
```bash
pip install -r requirements.txt
```

### Erro: "GEMINI_API_KEY não configurada"
Criar arquivo `.env` com:
```env
GEMINI_API_KEY=sua_chave
```

### Erro: "npm não encontrado" (apenas React)
Instalar Node.js: https://nodejs.org

---

## 📚 Documentação Completa

Ver: [DOCUMENTACAO_LAUNCHER.md](DOCUMENTACAO_LAUNCHER.md)

---

**Versão**: 1.0.0
**Data**: 2025-10-25
