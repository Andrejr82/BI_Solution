"""
Script de Atualização Automática do Parquet
Atualiza o arquivo admmat.parquet a partir do SQL Server.

Uso:
    python scripts/update_parquet_from_sql.py

Agendamento recomendado:
    - 03:00h (madrugada - baixa atividade)
    - 15:00h (tarde - atualização intermediária)
"""
import os
import sys
from pathlib import Path
from datetime import datetime
import logging

# Adicionar diretório raiz ao path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)s | %(message)s',
    handlers=[
        logging.FileHandler('logs/parquet_update.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def generate_daily_report(stats: dict, success: bool):
    """Gera relatório diário da atualização do Parquet."""
    from datetime import datetime

    # Criar diretório de relatórios
    report_dir = Path("reports/parquet_updates")
    report_dir.mkdir(parents=True, exist_ok=True)

    # Nome do arquivo de relatório
    today = datetime.now().strftime("%Y%m%d")
    report_path = report_dir / f"relatorio_{today}.md"

    # Status da atualização
    status_emoji = "[OK]" if success else "[ERRO]"
    status_text = "SUCESSO" if success else "FALHA"

    # Construir relatório
    report = f"""# Relatório de Atualização do Parquet - {datetime.now().strftime("%d/%m/%Y %H:%M:%S")}

## Status: {status_emoji} {status_text}

## Estatísticas da Atualização

### Dados Processados
- **Linhas atualizadas**: {stats.get('total_linhas', 0):,}
- **Colunas**: {stats.get('total_colunas', 0)}
- **Tamanho do arquivo**: {stats.get('tamanho_mb', 0):.2f} MB
- **Tempo de execução**: {stats.get('tempo_total', 0):.2f}s

### Performance
- **Tempo de leitura SQL**: {stats.get('tempo_leitura', 0):.2f}s
- **Tempo de gravação Parquet**: {stats.get('tempo_gravacao', 0):.2f}s
- **Velocidade**: {stats.get('linhas_por_segundo', 0):,.0f} linhas/s

### Comparação com Versão Anterior
- **Linhas adicionadas**: {stats.get('linhas_adicionadas', 0):,}
- **Linhas removidas**: {stats.get('linhas_removidas', 0):,}
- **Variação**: {stats.get('variacao_percentual', 0):+.2f}%

### Backup
- **Backup criado**: {stats.get('backup_criado', 'N/A')}
- **Backups mantidos**: {stats.get('total_backups', 0)}

## Detalhes Técnicos

### Conexão SQL Server
- **Host**: {stats.get('db_host', 'N/A')}
- **Database**: {stats.get('db_name', 'N/A')}
- **Tabela**: ADMMATAO

### Chunks Processados
- **Total de chunks**: {stats.get('total_chunks', 0)}
- **Tamanho do chunk**: {stats.get('chunk_size', 0):,} linhas

## Erros e Avisos

{stats.get('erros', '_Nenhum erro registrado_')}

## Logs Completos

Ver arquivo: `logs/parquet_update.log`

---

**Próxima atualização**: Amanhã às 03:00h
**Gerado automaticamente pelo Agent_BI**
"""

    # Salvar relatório
    report_path.write_text(report, encoding='utf-8')
    logger.info(f"[OK] Relatório diário salvo: {report_path}")

    # Limpar relatórios antigos (manter últimos 30 dias)
    cleanup_old_reports(report_dir, keep_count=30)

    return report_path

def cleanup_old_reports(report_dir: Path, keep_count: int = 30):
    """Remove relatórios antigos, mantendo apenas os N mais recentes."""
    try:
        reports = sorted(
            report_dir.glob("relatorio_*.md"),
            key=lambda p: p.stat().st_mtime,
            reverse=True
        )

        if len(reports) > keep_count:
            for old_report in reports[keep_count:]:
                logger.info(f"Removendo relatório antigo: {old_report.name}")
                old_report.unlink()

    except Exception as e:
        logger.warning(f"Erro ao limpar relatórios: {e}")

def update_parquet():
    """Atualiza o arquivo Parquet a partir do SQL Server."""
    logger.info("="*70)
    logger.info("INÍCIO DA ATUALIZAÇÃO DO PARQUET")
    logger.info("="*70)

    # Dicionário para estatísticas
    stats = {
        'tempo_total': 0,
        'tempo_leitura': 0,
        'tempo_gravacao': 0,
        'total_linhas': 0,
        'total_colunas': 0,
        'tamanho_mb': 0,
        'linhas_adicionadas': 0,
        'linhas_removidas': 0,
        'variacao_percentual': 0,
        'total_chunks': 0,
        'chunk_size': 50000,
        'backup_criado': 'Não',
        'total_backups': 0,
        'erros': '',
        'db_host': '',
        'db_name': ''
    }

    start_time_total = datetime.now()

    try:
        # Carregar variáveis de ambiente
        from dotenv import load_dotenv
        load_dotenv()

        # Importar dependências
        import pandas as pd
        import pyodbc
        from sqlalchemy import create_engine
        from urllib.parse import quote_plus

        # Verificar se SQL Server está configurado
        db_host = os.getenv("DB_HOST")
        db_name = os.getenv("DB_NAME")
        db_user = os.getenv("DB_USER")
        db_password = os.getenv("DB_PASSWORD")
        db_driver = os.getenv("DB_DRIVER", "ODBC Driver 17 for SQL Server")

        if not all([db_host, db_name, db_user, db_password]):
            raise ValueError("Variáveis de ambiente SQL Server não configuradas")

        # Armazenar info de conexão para relatório
        stats['db_host'] = db_host
        stats['db_name'] = db_name

        logger.info(f"Conectando ao SQL Server: {db_host}/{db_name}")

        # Construir connection string usando SQLAlchemy (mais rápido e recomendado)
        conn_str = (
            f"mssql+pyodbc://{db_user}:{quote_plus(db_password)}@"
            f"{db_host}/{db_name}?driver={quote_plus(db_driver)}&"
            f"TrustServerCertificate=yes"
        )

        # Criar engine SQLAlchemy
        engine = create_engine(conn_str, fast_executemany=True)
        logger.info("[OK] Conectado ao SQL Server")

        # Ler dados da tabela ADMMATAO em chunks (mais eficiente)
        logger.info("Lendo dados da tabela ADMMATAO em chunks...")
        query = "SELECT * FROM ADMMATAO"

        start_time = datetime.now()

        # Ler em chunks de 50k linhas para não sobrecarregar memória
        chunks = []
        chunk_size = 50000
        for i, chunk in enumerate(pd.read_sql(query, engine, chunksize=chunk_size)):
            chunks.append(chunk)
            logger.info(f"  Chunk {i+1}: {len(chunk):,} linhas lidas")

        # Concatenar todos os chunks
        df = pd.concat(chunks, ignore_index=True)
        duration = (datetime.now() - start_time).total_seconds()

        # Estatísticas de leitura
        stats['tempo_leitura'] = duration
        stats['total_linhas'] = len(df)
        stats['total_colunas'] = len(df.columns)
        stats['total_chunks'] = len(chunks)

        logger.info(f"[OK] Dados lidos: {len(df):,} linhas em {duration:.2f}s")

        # Engine será fechado automaticamente

        # Salvar como Parquet
        parquet_path = Path("data/parquet/admmat.parquet")
        parquet_path.parent.mkdir(parents=True, exist_ok=True)

        # Backup do arquivo anterior (se existir)
        linhas_anteriores = 0
        if parquet_path.exists():
            # Ler versão anterior para comparação
            try:
                df_anterior = pd.read_parquet(parquet_path)
                linhas_anteriores = len(df_anterior)
            except Exception as e:
                logger.warning(f"Não foi possível ler Parquet anterior: {e}")

            backup_path = parquet_path.with_suffix(f".backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.parquet")
            logger.info(f"Criando backup: {backup_path.name}")
            parquet_path.rename(backup_path)
            stats['backup_criado'] = backup_path.name

        # Calcular variação
        if linhas_anteriores > 0:
            stats['linhas_adicionadas'] = max(0, len(df) - linhas_anteriores)
            stats['linhas_removidas'] = max(0, linhas_anteriores - len(df))
            stats['variacao_percentual'] = ((len(df) - linhas_anteriores) / linhas_anteriores) * 100

        logger.info("Salvando novo arquivo Parquet...")
        start_gravacao = datetime.now()
        df.to_parquet(parquet_path, engine='pyarrow', compression='snappy', index=False)
        stats['tempo_gravacao'] = (datetime.now() - start_gravacao).total_seconds()

        file_size_mb = parquet_path.stat().st_size / (1024 * 1024)
        stats['tamanho_mb'] = file_size_mb
        logger.info(f"[OK] Parquet atualizado: {file_size_mb:.2f} MB")

        # Estatísticas
        logger.info("-" * 70)
        logger.info("ESTATÍSTICAS:")
        logger.info(f"  Linhas: {len(df):,}")
        logger.info(f"  Colunas: {len(df.columns)}")
        logger.info(f"  Tamanho: {file_size_mb:.2f} MB")
        logger.info(f"  Tempo total: {duration:.2f}s")
        logger.info("-" * 70)

        # Limpar backups antigos (manter apenas últimos 7)
        cleanup_old_backups(parquet_path.parent, keep_count=7)

        # Contar backups restantes
        backups = list(parquet_path.parent.glob("admmat.backup_*.parquet"))
        stats['total_backups'] = len(backups)

        # Calcular estatísticas finais
        stats['tempo_total'] = (datetime.now() - start_time_total).total_seconds()
        if stats['tempo_leitura'] > 0:
            stats['linhas_por_segundo'] = stats['total_linhas'] / stats['tempo_leitura']

        logger.info("="*70)
        logger.info("ATUALIZAÇÃO CONCLUÍDA COM SUCESSO!")
        logger.info("="*70)

        # Gerar relatório diário
        generate_daily_report(stats, success=True)

        return True

    except Exception as e:
        logger.error("="*70)
        logger.error(f"ERRO NA ATUALIZAÇÃO: {e}")
        logger.error("="*70)
        import traceback
        error_trace = traceback.format_exc()
        traceback.print_exc()

        # Gerar relatório de erro
        stats['erros'] = f"```\n{str(e)}\n\n{error_trace}\n```"
        stats['tempo_total'] = (datetime.now() - start_time_total).total_seconds()
        generate_daily_report(stats, success=False)

        return False

def cleanup_old_backups(backup_dir: Path, keep_count: int = 7):
    """Remove backups antigos, mantendo apenas os N mais recentes."""
    try:
        backups = sorted(
            backup_dir.glob("admmat.backup_*.parquet"),
            key=lambda p: p.stat().st_mtime,
            reverse=True
        )

        if len(backups) > keep_count:
            for old_backup in backups[keep_count:]:
                logger.info(f"Removendo backup antigo: {old_backup.name}")
                old_backup.unlink()

    except Exception as e:
        logger.warning(f"Erro ao limpar backups: {e}")

if __name__ == "__main__":
    # Criar diretório de logs se não existir
    Path("logs").mkdir(exist_ok=True)

    success = update_parquet()
    sys.exit(0 if success else 1)
