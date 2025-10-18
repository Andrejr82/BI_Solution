# Scripts de Diagnóstico

Este diretório contém scripts para diagnóstico e análise do sistema.

## Scripts Disponíveis:

### Python
- `diagnostico_sugestoes_automaticas.py` - Diagnóstico de sugestões automáticas
- `diagnostico_transferencias_unes.py` - Diagnóstico de transferências entre UNEs
- `analyze_une1_data.py` - Análise de dados da UNE1

### Batch
- `DIAGNOSTICO_TRANSFERENCIAS.bat` - Script batch para diagnóstico de transferências

## Uso:

```bash
# Executar script Python
python scripts/diagnostics/diagnostico_sugestoes_automaticas.py

# Executar script Batch (Windows)
scripts\diagnostics\DIAGNOSTICO_TRANSFERENCIAS.bat
```

## Notas:
- Todos os scripts devem ser executados a partir da raiz do projeto
- Certifique-se de ter as dependências instaladas
- Logs são salvos em `data/learning/`
