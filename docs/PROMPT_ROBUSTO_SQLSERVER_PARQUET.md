# 🛡️ PROMPT ROBUSTO - SQL SERVER + PARQUET HÍBRIDO

**Propósito:** Garantir que futuras alterações no sistema não quebrem a integração SQL Server + Parquet
**Data:** 04/10/2025
**Autor:** Claude Code

---

## ⚠️ REGRAS CRÍTICAS - NUNCA QUEBRAR

### **1. HybridDataAdapter é OBRIGATÓRIO**

❌ **NUNCA FAÇA:**
```python
# ERRADO: Criar ParquetAdapter diretamente
adapter = ParquetAdapter('data/parquet/admmat.parquet')
```

✅ **SEMPRE FAÇA:**
```python
# CORRETO: Usar HybridDataAdapter
from core.connectivity.hybrid_adapter import HybridDataAdapter
adapter = HybridDataAdapter()  # Tenta SQL Server, fallback Parquet automático
```

---

### **2. Compatibilidade de Interface**

O `HybridDataAdapter` DEVE implementar os mesmos métodos que `ParquetAdapter`:

```python
class HybridDataAdapter:
    def connect(self):
        """Conecta ao adapter ativo."""
        pass

    def disconnect(self):
        """Desconecta adapter ativo."""
        pass

    def execute_query(self, query_filters: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Executa query com fallback automático."""
        pass

    def get_schema(self) -> str:
        """Retorna schema da fonte ativa."""
        pass

    def get_status(self) -> Dict[str, Any]:
        """Status do adapter (debugging)."""
        pass

    # Propriedades para compatibilidade com DirectQueryEngine
    @property
    def _dataframe(self):
        """Retorna DataFrame do parquet_adapter."""
        pass

    def _load_dataframe(self):
        """Carrega DataFrame (delega para parquet_adapter)."""
        pass
```

**SE ADICIONAR NOVOS MÉTODOS EM `ParquetAdapter`, ADICIONE TAMBÉM EM `HybridDataAdapter`!**

---

### **3. Mapeamento de Colunas SQL Server ↔ Parquet**

**Tabela SQL Server: `ADMMATAO` (colunas MAIÚSCULAS)**
**Parquet: `admmat.parquet` (colunas minúsculas)**

**Mapeamento crítico:**
```python
column_mapping = {
    # SQL Server → Parquet
    'UNE': 'une',
    'PRODUTO': 'codigo',
    'NOME': 'nome_produto',
    'UNE_NOME': 'une_nome',
    'NOMESEGMENTO': 'nomesegmento',
    'LIQUIDO_38': 'preco_38_percent',
    'MES_01': 'mes_01',
    'MES_02': 'mes_02',
    # ... (95 colunas no total)
    'ESTOQUE_UNE': 'estoque_atual',
    'VENDA_30DD': 'venda_30_d',
}
```

**SE ADICIONAR/REMOVER COLUNAS:**
1. Atualizar `export_sqlserver_to_parquet.py` (linha ~120)
2. Atualizar `HybridDataAdapter._build_sql_query()` (linha ~220)
3. Exportar novo Parquet: `python scripts/export_sqlserver_to_parquet.py`

---

### **4. Configuração .env OBRIGATÓRIA**

**Variáveis críticas:**
```env
# Flag principal
USE_SQL_SERVER=true  # ou false

# Conexão SQL Server (obrigatórias se USE_SQL_SERVER=true)
MSSQL_SERVER=FAMILIA\SQLJR,1433
MSSQL_DATABASE=Projeto_Caculinha
MSSQL_USER=AgenteVirtual
MSSQL_PASSWORD=Cacula@2020
DB_DRIVER=ODBC Driver 17 for SQL Server
DB_TRUST_SERVER_CERTIFICATE=yes

# Segurança
SQL_SERVER_TIMEOUT=10            # Timeout em segundos
FALLBACK_TO_PARQUET=true         # NUNCA false em produção!
```

**NUNCA comite `.env` com credenciais!**
**SEMPRE use `.env.example` como template.**

---

### **5. Parquet SEMPRE Disponível**

O sistema DEVE funcionar mesmo se SQL Server falhar.

**Teste obrigatório antes de qualquer deploy:**
```bash
# 1. SQL Server desligado → app funciona?
USE_SQL_SERVER=false
streamlit run streamlit_app.py

# 2. SQL Server ligado → app funciona?
USE_SQL_SERVER=true
streamlit run streamlit_app.py

# 3. SQL Server cai durante execução → fallback funciona?
python scripts/test_hybrid_connection.py
```

---

## 📝 CHECKLIST DE ALTERAÇÕES SEGURAS

Antes de modificar qualquer arquivo relacionado:

### **A. Modificar `HybridDataAdapter`:**
- [ ] Testar com SQL Server ON: `USE_SQL_SERVER=true`
- [ ] Testar com SQL Server OFF: `USE_SQL_SERVER=false`
- [ ] Executar: `python scripts/test_hybrid_connection.py`
- [ ] Verificar fallback automático funciona
- [ ] Não quebrou compatibilidade com `DirectQueryEngine`

### **B. Modificar `streamlit_app.py`:**
- [ ] HybridDataAdapter continua sendo usado (linha ~186)
- [ ] Backend retorna `parquet_adapter` (que é HybridDataAdapter)
- [ ] Status mostrado no sidebar (admin only)
- [ ] Fallback transparente em `query_backend()`

### **C. Adicionar/Remover Colunas:**
- [ ] Atualizar mapeamento em `export_sqlserver_to_parquet.py`
- [ ] Atualizar mapeamento em `HybridDataAdapter._build_sql_query()`
- [ ] Exportar novo Parquet: `python scripts/export_sqlserver_to_parquet.py`
- [ ] Validar Parquet: `python -c "import pandas as pd; df = pd.read_parquet('data/parquet/admmat.parquet'); print(df.columns)"`
- [ ] Testar consultas antigas ainda funcionam

### **D. Modificar Configurações SQL Server:**
- [ ] Atualizar `.env`
- [ ] Testar conexão: `python scripts/test_hybrid_connection.py`
- [ ] Se mudar estrutura de tabela, exportar novo Parquet
- [ ] Validar em ambiente de teste ANTES de produção

---

## 🚨 ERROS COMUNS E COMO EVITAR

### **Erro 1: ImportError: cannot import name 'HybridDataAdapter'**

**Causa:** Código importando ParquetAdapter ao invés de HybridDataAdapter

**Solução:**
```python
# ANTES (errado)
from core.connectivity.parquet_adapter import ParquetAdapter
adapter = ParquetAdapter(...)

# DEPOIS (correto)
from core.connectivity.hybrid_adapter import HybridDataAdapter
adapter = HybridDataAdapter()
```

---

### **Erro 2: KeyError: 'parquet_adapter' not found**

**Causa:** Backend não retornou `parquet_adapter` (HybridDataAdapter)

**Solução:**
```python
# streamlit_app.py linha ~265
return {
    "llm_adapter": llm_adapter,
    "parquet_adapter": data_adapter,  # ← DEVE ser HybridDataAdapter!
    "code_gen_agent": code_gen_agent,
    "agent_graph": agent_graph,
    "query_history": query_history
}
```

---

### **Erro 3: SQL Server conecta mas retorna dados vazios**

**Causa:** Query SQL malformada ou colunas mapeadas incorretamente

**Debug:**
```python
# HybridDataAdapter._build_sql_query()
# Adicionar log:
logger.info(f"SQL Query: {sql_query}")

# Testar query diretamente:
python -c "
import pyodbc
conn = pyodbc.connect('...')
cursor = conn.cursor()
cursor.execute('SELECT TOP 10 * FROM ADMMATAO WHERE UNE = 261')
print(cursor.fetchall())
"
```

---

### **Erro 4: Fallback não funciona**

**Causa:** `FALLBACK_TO_PARQUET=false` ou Parquet corrompido

**Solução:**
```bash
# 1. Verificar .env
grep FALLBACK_TO_PARQUET .env
# Deve ser: FALLBACK_TO_PARQUET=true

# 2. Validar Parquet
python -c "import pandas as pd; df = pd.read_parquet('data/parquet/admmat.parquet'); print(len(df))"

# 3. Restaurar backup se necessário
copy data\parquet\admmat_backup_*.parquet data\parquet\admmat.parquet
```

---

## 🔧 MANUTENÇÃO PERIÓDICA

### **Semanal:**
- [ ] Executar: `python scripts/export_sqlserver_to_parquet.py`
- [ ] Validar Parquet atualizado com dados SQL Server
- [ ] Testar diagnóstico: `python scripts/test_hybrid_connection.py`

### **Mensal:**
- [ ] Revisar logs de fallback (quantas vezes SQL Server caiu?)
- [ ] Otimizar queries lentas
- [ ] Limpar backups antigos de Parquet (`admmat_backup_*.parquet`)

### **Antes de cada Apresentação:**
- [ ] Executar diagnóstico completo
- [ ] Validar SQL Server conecta
- [ ] Testar 10 perguntas aleatórias das 80
- [ ] Preparar Plano B (rollback .env)

---

## 📋 TEMPLATE DE PULL REQUEST

Ao submeter alterações relacionadas ao HybridDataAdapter:

```markdown
## Descrição
[Descrever mudança]

## Checklist Obrigatório
- [ ] Testado com `USE_SQL_SERVER=true`
- [ ] Testado com `USE_SQL_SERVER=false`
- [ ] Executado `python scripts/test_hybrid_connection.py` (sucesso)
- [ ] Fallback automático validado
- [ ] Compatibilidade com DirectQueryEngine OK
- [ ] Nenhuma credencial commitada

## Testes Realizados
```bash
# Comandos executados:
python scripts/test_hybrid_connection.py
streamlit run streamlit_app.py
# ... adicionar outros testes
```

## Rollback Plan
[Como desfazer se quebrar?]
```

---

## 🎯 PROMPT PARA FUTURAS IMPLEMENTAÇÕES

**Use este prompt ao pedir alterações ao sistema:**

```
Preciso [DESCRIÇÃO DA MUDANÇA].

IMPORTANTE: Este sistema usa HybridDataAdapter (SQL Server + Parquet fallback).

REGRAS CRÍTICAS:
1. NUNCA quebrar compatibilidade com HybridDataAdapter
2. SEMPRE manter Parquet como fallback funcional
3. SEMPRE atualizar mapeamento de colunas se necessário
4. SEMPRE testar com SQL Server ON e OFF
5. SEMPRE executar python scripts/test_hybrid_connection.py após mudanças

Arquivos críticos:
- core/connectivity/hybrid_adapter.py (não quebrar interface)
- streamlit_app.py (linha ~186: usa HybridDataAdapter)
- scripts/export_sqlserver_to_parquet.py (mapeamento de colunas)
- scripts/test_hybrid_connection.py (validação)

Documentação:
- docs/GUIA_MIGRACAO_SQLSERVER_COMPLETO.md
- docs/PROMPT_ROBUSTO_SQLSERVER_PARQUET.md (este arquivo)

Por favor, implemente a mudança seguindo essas regras e forneça:
1. Código modificado
2. Testes executados
3. Plano de rollback se quebrar
```

---

## ✅ VALIDAÇÃO FINAL

Antes de considerar qualquer alteração completa:

```bash
# 1. Diagnóstico completo
python scripts/test_hybrid_connection.py

# 2. Exportar Parquet atualizado
python scripts/export_sqlserver_to_parquet.py

# 3. Iniciar aplicação
streamlit run streamlit_app.py

# 4. Testar 10 perguntas
# - Produto mais vendido
# - Top 10 produtos UNE 261
# - Ranking de vendas por UNE
# - Vendas totais de cada UNE
# - Top 10 produtos segmento TECIDOS
# - Evolução vendas últimos 12 meses
# - Produtos sem movimento
# - Análise ABC
# - Comparação de segmentos
# - Estoque alto

# 5. Validar status no sidebar (admin)
# Deve mostrar:
# - Fonte de dados (SQL Server ou Parquet)
# - Status de conexão
# - Número de produtos e UNEs
```

**SUCESSO:** Todas as 10 perguntas respondem em <2s sem erros.

---

## 🎉 CONCLUSÃO

Este documento garante que:
- ✅ Futuras alterações não quebrem o sistema
- ✅ SQL Server + Parquet continuam funcionando em harmonia
- ✅ Fallback automático sempre disponível
- ✅ Zero downtime em produção
- ✅ Fácil manutenção e debug

**Mantenha este documento atualizado ao fazer alterações!**
