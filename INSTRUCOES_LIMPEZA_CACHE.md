# 🔥 INSTRUÇÕES URGENTES - Limpeza de Cache

## ⚠️ PROBLEMA IDENTIFICADO

O log mostra:
```
role: "user"           ← ERRADO
allowed_segments: []   ← VAZIO
```

**Causa:** Token antigo em cache (criado ANTES das correções)

**Parquet verificado:** Admin está CORRETO (role="admin", allowed_segments="[\"*\"]")

---

## ✅ SOLUÇÃO: LIMPAR TOKEN ANTIGO

### **MÉTODO 1: Hard Refresh (Recomendado)**

**Execute EXATAMENTE nesta ordem:**

1. Abra F12 (DevTools)
2. Cole no Console:
```javascript
localStorage.clear();
sessionStorage.clear();
console.log('✅ Cache limpo!');
```
3. Feche TODAS as abas do localhost:3000
4. Feche o navegador COMPLETAMENTE
5. Reabra o navegador
6. Acesse http://localhost:3000
7. Login: `admin` / `admin`

**Console deve mostrar:**
```
✅ Login successful. User: {
  username: "admin",
  role: "admin",
  allowed_segments: ["*"]
}
```

---

### **MÉTODO 2: Navegação Anônima (Teste Rápido)**

1. Ctrl+Shift+N (janela anônima)
2. http://localhost:3000
3. Login: admin / admin
4. Verificar console

Se funcionar → Problema é cache do navegador normal

---

### **MÉTODO 3: Forçar via Script**

**No console (F12):**

```javascript
// 1. Limpar tudo
localStorage.clear();
sessionStorage.clear();

// 2. Remover cookies
document.cookie.split(";").forEach(c => {
  document.cookie = c.replace(/^ +/, "").replace(/=.*/, "=;expires=" + new Date().toUTCString() + ";path=/");
});

// 3. Recarregar
location.href = '/login';
```

---

## 🔍 VERIFICAÇÃO PÓS-LOGIN

**Console deve mostrar:**

```javascript
✅ Login successful. User: Object
  username: "admin"
  role: "admin"              ← DEVE SER "admin"
  email: "admin@agentbi.com"
  allowed_segments: Array(1) ← DEVE TER ["*"]
    0: "*"
```

**Sidebar deve mostrar:**
- Monitoramento
- Métricas
- Chat BI
- Analytics
- Rupturas
- Transferências
- Ajuda
- Aprendizado

---

## 🚨 SE AINDA MOSTRAR role="user"

Execute este comando no backend:

```bash
cd backend
.venv\Scripts\python.exe -c "
import polars as pl
df = pl.read_parquet('data/parquet/users.parquet')
admin = df.filter(pl.col('username') == 'admin')

# Forçar correção
df = df.with_columns(
    pl.when(pl.col('username') == 'admin')
    .then(pl.lit('admin'))
    .otherwise(pl.col('role'))
    .alias('role')
)

df.write_parquet('data/parquet/users.parquet')
print('Admin corrigido!')
"
```

Depois:
1. Reinicie o backend
2. Limpe cache do navegador
3. Login novamente

---

## ✅ CHECKLIST

- [ ] Executei `localStorage.clear()`
- [ ] Fechei TODAS as abas
- [ ] Fechei o navegador
- [ ] Reabri e acessei novamente
- [ ] Fiz login com admin/admin
- [ ] Console mostra role="admin"
- [ ] Console mostra allowed_segments=["*"]
- [ ] Sidebar mostra TODAS as páginas
- [ ] Dados aparecem sem filtros de segmento

---

**Status:** Aguardando execução dos passos acima
**Próximo Passo:** Me reporte o que aparece no console após seguir MÉTODO 1
