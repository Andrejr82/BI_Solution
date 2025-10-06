# 🐛 BUG: SQL Server - Colunas Maiúsculas vs Minúsculas

**Data:** 04/10/2025 22:20
**Status:** 🔴 PENDENTE CORREÇÃO (amanhã 05/10)
**Severidade:** ALTA (sistema não funciona com SQL Server)

---

## 🔍 PROBLEMA

**SQL Server retorna colunas MAIÚSCULAS:**
- MES_01, MES_02, MES_03, etc.
- UNE, PRODUTO, NOME, etc.

**DirectQueryEngine espera minúsculas:**
- mes_01, mes_02, mes_03, etc.
- une, codigo, nome_produto, etc.

**Resultado:**
- Queries SQL Server: dados não encontrados
- Respostas vazias/repetidas
- 5 perguntas diferentes → 2 respostas únicas (FALHA)

---

## 📊 EVIDÊNCIA

```
Query types retornados: 5
Query types unicos: 4
Resultados diferentes: 2  ← PROBLEMA!

Esperado: 5 resultados únicos
Obtido: 2 resultados únicos
```

---

## ✅ SOLUÇÃO (Implementar amanhã)

### Opção 1: Normalizar no HybridDataAdapter (Recomendada)

**Arquivo:** `core/connectivity/hybrid_adapter.py`

```python
def execute_query(self, query_filters: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Executa query com fallback automático."""

    if self.current_source == "sqlserver" and self.sql_adapter:
        try:
            sql_query = self._build_sql_query(query_filters)
            result = self.sql_adapter.execute_query(sql_query)

            # ✨ NOVO: Normalizar colunas MAIÚSCULAS → minúsculas
            if result and len(result) > 0:
                normalized_result = []
                for row in result:
                    normalized_row = {
                        key.lower(): value
                        for key, value in row.items()
                    }
                    normalized_result.append(normalized_row)
                result = normalized_result

            logger.info(f"[OK] Query via SQL Server ({len(result)} rows)")
            return result
```

**Estimativa:** 10 linhas código, 1 teste, ~1,500 tokens

---

### Opção 2: Normalizar no SQLServerAdapter

**Arquivo:** `core/connectivity/sql_server_adapter.py`

```python
def execute_query(self, query: str) -> List[Dict[str, Any]]:
    if not self._cursor:
        self.connect()

    self._cursor.execute(query)
    columns = [column[0].lower() for column in self._cursor.description]  # ✨ .lower()
    results = [dict(zip(columns, row)) for row in self._cursor.fetchall()]
    return results
```

**Estimativa:** 1 linha código, 1 teste, ~800 tokens

---

## 🔧 TESTE DE VALIDAÇÃO

**Antes da correção:**
```bash
python scripts/validate_no_mock_data.py
# Resultado: 2/5 únicos (FALHA)
```

**Depois da correção:**
```bash
python scripts/validate_no_mock_data.py
# Resultado esperado: 5/5 únicos (SUCESSO)
```

---

## 📋 CHECKLIST CORREÇÃO (Amanhã 05/10)

- [ ] Implementar Opção 2 (mais simples)
- [ ] Testar: `python scripts/test_hybrid_connection.py`
- [ ] Validar: `python scripts/validate_no_mock_data.py`
- [ ] Habilitar SQL Server: `.env` → `USE_SQL_SERVER=true`
- [ ] Testar 10 perguntas no Streamlit
- [ ] Confirmar: 10 respostas únicas ✅

**Tempo estimado:** 30-45 minutos

---

## 🚨 STATUS ATUAL (Hoje 04/10)

**SQL Server:** ❌ Desabilitado temporariamente
**Parquet:** ✅ Funcionando (252k registros)
**Sistema:** ✅ 100% operacional para testes

**Configuração atual (.env):**
```env
USE_SQL_SERVER=false  # Temporariamente desabilitado
```

**Para apresentação segunda:**
- SQL Server corrigido amanhã
- Fallback Parquet sempre disponível
- Zero risco de dados mockados

---

## 📞 PRÓXIMOS PASSOS

**Hoje (04/10 - noite):**
1. ✅ Bug documentado
2. ✅ Sistema funcionando com Parquet
3. ⏳ Testar Streamlit

**Amanhã (05/10 - manhã):**
1. Corrigir normalização colunas
2. Testar SQL Server
3. Validar 20 perguntas
4. Sistema pronto para segunda!

---

**Autor:** Claude Code
**Prioridade:** Alta (mas não bloqueante)
