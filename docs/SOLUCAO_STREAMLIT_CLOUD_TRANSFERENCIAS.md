# Solução para Transferências no Streamlit Cloud

## Problema Identificado

Os arquivos Parquet (`admmat.parquet` e `admmat_extended.parquet`) são muito grandes (94-100 MB) e estão no `.gitignore`, portanto **não sobem para o Streamlit Cloud**.

## Solução Implementada

### 1. Fallback Automático de Arquivos

O código agora detecta automaticamente qual arquivo está disponível:

```python
# Tenta usar extended, se não existir usa o padrão
if os.path.exists(PARQUET_PATH_EXTENDED):
    PARQUET_PATH = PARQUET_PATH_EXTENDED  # Local development
elif os.path.exists(PARQUET_PATH_DEFAULT):
    PARQUET_PATH = PARQUET_PATH_DEFAULT   # Streamlit Cloud
```

### 2. Mapeamento de Colunas

Como `admmat.parquet` tem nomes de colunas diferentes:
- `estoque_lv` → `linha_verde`
- `media_considerada_lv` → `mc`

Foi implementada função `_normalize_dataframe()` que faz o mapeamento automaticamente.

### 3. Compatibilidade Total

Ambas as ferramentas agora funcionam com qualquer um dos arquivos:
- ✅ `validar_transferencia_produto()`
- ✅ `sugerir_transferencias_automaticas()`

## Opções para Streamlit Cloud

### Opção 1: Usar Parquet (Atual) ⚠️

**Prós:**
- Já implementado e funcionando
- Rápido (dados em cache)

**Contras:**
- Arquivo grande (94 MB)
- Dados podem ficar desatualizados
- Requer upload manual do arquivo

**Como fazer:**
```bash
# Remover apenas extended do .gitignore (manter admmat.parquet)
# Editar .gitignore linha 63:
# De:
data/parquet/

# Para:
data/parquet/admmat_extended.parquet
data/parquet_cleaned/
```

### Opção 2: Usar SQL Server Direto (Recomendado) ✅

**Prós:**
- Dados sempre atualizados
- Não ocupa espaço no repositório
- Mesma fonte que HybridAdapter usa

**Contras:**
- Requer conexão com banco
- Um pouco mais lento

**Implementação:**

Criar `core/tools/une_tools_sql.py` que usa o mesmo SQL Server do `HybridAdapter`:

```python
from core.connectivity.hybrid_adapter import HybridDataAdapter

def _get_data_from_sql(filters: dict = None):
    """Busca dados do SQL Server"""
    adapter = HybridDataAdapter()
    # Usar método interno do adapter
    df = adapter.execute_query(filters or {})
    return df
```

### Opção 3: GitHub LFS (Large File Storage) 💡

**Prós:**
- Git gerencia o arquivo
- Dados no repositório
- Deploy automático

**Contras:**
- Requer configuração LFS
- Limites de tamanho/bandwidth

**Como fazer:**
```bash
# Instalar Git LFS
git lfs install

# Rastrear arquivos Parquet
git lfs track "data/parquet/admmat.parquet"

# Adicionar e comitar
git add .gitattributes
git add data/parquet/admmat.parquet
git commit -m "Add Parquet via LFS"
git push
```

## Recomendação Final

**Para PRODUÇÃO:** Use **Opção 2 (SQL Server direto)**

Vantagens:
1. Dados sempre atualizados em tempo real
2. Não adiciona peso ao repositório
3. Usa mesma infraestrutura que já funciona
4. Mais profissional e escalável

**Para DESENVOLVIMENTO:** Mantenha Parquet local para testes rápidos

## Próximos Passos

Se quiser implementar Opção 2 (SQL), posso criar:

1. `une_tools_sql.py` - Versão que usa SQL direto
2. Configuração automática de fallback: Parquet local → SQL em cloud
3. Cache inteligente das consultas SQL
4. Testes de integração

**O que prefere?**
