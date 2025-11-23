# 🚀 Guia Rápido: Criar Nova API Key do Gemini

## ⏱️ Tempo Estimado: 3 minutos

---

## Passo 1: Acesse o Google AI Studio

**Link:** https://aistudio.google.com/app/apikey

Faça login com sua conta Google.

---

## Passo 2: Delete Chaves Antigas (IMPORTANTE!)

Procure por chaves com status:
- "expired" (expirada)
- "leaked" (vazada)
- "invalid" (inválida)

**Ação:** Clique no ícone de **lixeira** 🗑️ ao lado de cada chave antiga.

---

## Passo 3: Criar Nova Chave

1. Clique no botão azul **"Create API Key"**

2. Escolha uma das opções:
   - **"Create API key in new project"** (recomendado para novos usuários)
   - OU selecione um projeto existente

3. A chave será gerada INSTANTANEAMENTE

---

## Passo 4: Copiar a Chave CORRETAMENTE

⚠️ **MUITO IMPORTANTE:**

1. Você verá algo assim:
   ```
   AIzaSyDdI0hCZtE6vySjMm-WEfRq3CPzqKqqsHI
   ```

2. **NÃO digite manualmente!**

3. Clique no ícone de **copiar** 📋 ao lado da chave

4. A chave completa será copiada para sua área de transferência

**Características da chave:**
- Começa com `AIza`
- Tem cerca de 39 caracteres
- Contém letras maiúsculas, minúsculas, números e símbolos

---

## Passo 5: Atualizar Configuração

### 5.1 Abrir o arquivo de configuração

**Caminho:** `.streamlit/secrets.toml`

**Como abrir:**
- No VS Code: File → Open File → Navegue até `.streamlit/secrets.toml`
- No Notepad++: Arquivo → Abrir → Selecione o arquivo

### 5.2 Localizar a linha da API Key

Procure por:
```toml
GEMINI_API_KEY = "alguma_chave_antiga_aqui"
```

### 5.3 Substituir pela nova chave

**ANTES:**
```toml
GEMINI_API_KEY = "AIza...chave_antiga..."
```

**DEPOIS:**
```toml
GEMINI_API_KEY = "AIzaSyDdI0hCZtE6vySjMm-WEfRq3CPzqKqqsHI"
```

(Use SUA chave, não o exemplo acima!)

### 5.4 Salvar o arquivo

- **VS Code:** Ctrl+S
- **Notepad++:** Ctrl+S ou Arquivo → Salvar

---

## Passo 6: Reiniciar o Streamlit

### No terminal onde o Streamlit está rodando:

1. **Parar o Streamlit:**
   ```
   Pressione: Ctrl+C
   ```

2. **Iniciar novamente:**
   ```bash
   streamlit run streamlit_app.py
   ```

3. **Aguardar:** O navegador abrirá automaticamente

---

## Passo 7: Testar

### Teste Automatizado (Recomendado):

No terminal:
```bash
python test_api_connection.py
```

**Resultado esperado:**
```
[OK] API Key encontrada
[OK] Resposta recebida
[SUCESSO] TODOS OS TESTES PASSARAM!
```

### Teste Manual na Interface:

1. Abra o Streamlit no navegador
2. Faça login
3. Digite: "Olá, bom dia!"
4. Pressione Enter

**Resultado esperado:**
- Sua pergunta aparece
- Resposta do agente aparece abaixo

---

## ❌ Erros Comuns e Soluções

### Erro: "API key expired"

**Causa:** Você copiou uma chave antiga ou expirada

**Solução:**
1. Volte ao Google AI Studio
2. **DELETE** a chave que você acabou de criar
3. Crie uma NOVA chave
4. Repita os passos 4-6

---

### Erro: "Invalid API key format"

**Causa:** Chave foi copiada incorretamente (incompleta ou com espaços)

**Solução:**
1. Volte ao Google AI Studio
2. **Copie novamente** usando o botão de copiar 📋
3. Cole novamente no arquivo `.streamlit/secrets.toml`
4. Certifique-se de que NÃO há:
   - Espaços no início ou fim
   - Quebras de linha
   - Caracteres extras

Exemplo CORRETO:
```toml
GEMINI_API_KEY = "AIzaSyDdI0hCZtE6vySjMm-WEfRq3CPzqKqqsHI"
```

Exemplo ERRADO:
```toml
GEMINI_API_KEY = " AIzaSyDdI0hCZtE6vySjMm-WEfRq3CPzqKqqsHI "  ← espaços
GEMINI_API_KEY = "AIzaSyDdI0hCZtE6vySj
Mm-WEfRq3CPzqKqqsHI"  ← quebra de linha
```

---

### Erro: "Permission denied" ou "leaked"

**Causa:** Google detectou que a chave foi exposta publicamente

**Solução:**
1. **NUNCA** compartilhe a chave
2. **NUNCA** commite a chave no Git
3. Crie uma nova chave
4. Mantenha o arquivo `.streamlit/secrets.toml` seguro

---

## ✅ Checklist Final

Antes de dizer "funcionou", verifique:

- [ ] Deletei TODAS as chaves antigas no Google AI Studio
- [ ] Criei uma NOVA API Key
- [ ] Copiei usando o botão de copiar 📋 (não digitei)
- [ ] Colei no arquivo `.streamlit/secrets.toml`
- [ ] A chave está entre aspas duplas
- [ ] NÃO há espaços antes ou depois da chave
- [ ] Salvei o arquivo (Ctrl+S)
- [ ] Reiniciei o Streamlit (Ctrl+C e rerun)
- [ ] Testei com `python test_api_connection.py`

---

## 🎉 Sucesso!

Se o teste passar, você verá:

```
[SUCESSO] TODOS OS TESTES PASSARAM!
A interface esta pronta para uso.
```

Agora você pode usar o sistema normalmente! 🚀

---

## 📞 Ainda com Problemas?

Se seguiu TODOS os passos e ainda não funciona:

1. Execute o teste: `python test_api_connection.py`
2. Copie a mensagem de erro COMPLETA
3. Compartilhe o erro (SEM compartilhar a API key!)

---

**Criado em:** 22/11/2025
**Última atualização:** 22/11/2025 - 09:51h
