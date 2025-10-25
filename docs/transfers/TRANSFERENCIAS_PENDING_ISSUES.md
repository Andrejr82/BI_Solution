# ⚠️ Transferências - Problemas Pendentes

**Data:** 2025-10-15
**Status:** 🔴 PENDENTE (Prioridade: BAIXA)
**Decisão:** Prosseguir com Pilar 2, retornar posteriormente

---

## 📋 Problemas Identificados

### 1. Produtos não carregam (Principal)
**Sintoma:**
```
⚠️ Nenhum produto com estoque encontrado nas UNEs selecionadas
```

**Afeta:** Todas as UNEs
**Causa Raiz:** Performance do ParquetAdapter (3+ minutos, timeouts)
**Tentativas:** Conversão pd.to_numeric(), cache clear, SQL Server migration

### 2. Segmento TECIDOS ausente
**Sintoma:** Filtro de segmentos não mostra "TECIDOS"
**Causa:** Provável encoding (existe nos dados brutos)
**Status:** Não investigado completamente

### 3. Sugestões Automáticas vazias
**Sintoma:** Sempre retorna "✓ Nenhuma oportunidade identificada"
**Causa:** Função `sugerir_transferencias_automaticas()` em `une_tools.py`
**Status:** Performance issue (carrega dataset completo)

---

## 🔧 Soluções Tentadas

1. ✅ Conversão de tipos: `pd.to_numeric(estoque_atual)`
2. ✅ Limpeza de cache: Scripts automáticos criados
3. ✅ Carregamento de UNEs: Fixado (42 UNEs aparecem)
4. ❌ Migration para SQL Server: Parcial (HybridAdapter habilitado)
5. ❌ Push-down filters no Parquet: Ainda lento

---

## 📁 Arquivos Relacionados

- `pages/7_📦_Transferências.py` - Interface principal
- `core/tools/une_tools.py` - Lógica de sugestões
- `core/connectivity/parquet_adapter.py` - Adapter lento
- `data/parquet/admmat_extended.parquet` - Fonte de dados (1.1M+ registros)
- `limpar_cache.py` / `limpar_cache.bat` - Scripts de limpeza

---

## 🎯 Próximos Passos (Quando Retornar)

1. **Otimizar ParquetAdapter**
   - Implementar indexação/particionamento
   - Considerar DuckDB para queries rápidas em Parquet

2. **Migração SQL Server Completa**
   - Criar views otimizadas para transferências
   - Índices em `ESTOQUE_UNE`, `PRODUTO`, `UNE`

3. **Fix TECIDOS Encoding**
   - Normalizar strings UTF-8 no filtro
   - Verificar `nomesegmento` no Parquet

4. **Otimizar Sugestões**
   - Pre-computar oportunidades (batch job)
   - Armazenar em tabela separada

---

## 💡 Recomendações

- **Curto Prazo:** Desabilitar "Sugestões Automáticas" (não funciona)
- **Médio Prazo:** Migration completa para SQL Server
- **Longo Prazo:** Sistema de cache distribuído (Redis)

---

**Nota:** Decidido em 2025-10-15 priorizar **Pilar 2: Few-Shot Learning** conforme roadmap.
Transferências será retomado após entrega do Pilar 2.
